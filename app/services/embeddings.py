from typing import List
from datetime import datetime
import tempfile
import logging
import io
import contextlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import aws_settings, llm_settings
from app.utils.s3 import s3_client
from app.models.documents import Documents, DocumentChunk

# mute extra logs on terminal, only if error.
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("unstructured").setLevel(logging.ERROR)
logging.getLogger("pypdf").setLevel(logging.ERROR)


async def process_and_embed_single_document(session: AsyncSession, document: Documents) -> dict:
    """
    Load one document file from S3, split into chunks, embed with Gemini,
    and store chunks+embeddings in document_chunks (FK -> documents.id).

    This is designed to be called right after a successful upload DB insert
    in the /documents/upload route.
    """
    storage_key = document.storage_key
    if not storage_key or not storage_key.lower().endswith(".pdf"):
        # Extend here in future if needed e.g .txt format
        return {"document_id": str(document.id), "chunks": 0, "detail": "Unsupported or missing storage_key"}

    # 1) Download file from S3 to temp file and load pages
    docs = []
    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        s3_client.download_fileobj(aws_settings.AWS_S3_BUCKET, storage_key, tmp)
        tmp.flush()

        pdf_loader = PyPDFLoader(tmp.name)

        # suppress loader stdout/stderr
        f_stdout = io.StringIO()
        f_stderr = io.StringIO()
        with contextlib.redirect_stdout(f_stdout), contextlib.redirect_stderr(f_stderr):
            page_docs = pdf_loader.load()

        # attach metadata
        for i, d in enumerate(page_docs, start=1):
            d.metadata = d.metadata or {}
            # ensure we always store both the S3 storage_key and the original filename
            d.metadata["source"] = d.metadata.get("source") or storage_key
            d.metadata["s3_key"] = d.metadata.get("s3_key") or storage_key
            d.metadata["page"] = d.metadata.get("page") or i
        docs.extend(page_docs)

    if not docs:
        return {"document_id": str(document.id), "chunks": 0, "detail": "No pages extracted"}

    # 2) Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    all_splits = splitter.split_documents(docs)

    # 3) Embed with Gemini
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=llm_settings.GEMINI_API_KEY,
    )

    # Optional: if this function is called on a doc that somehow already has chunks,
    # clean them first (safety; normally not needed because upload route recreates doc row)
    existing_chunks_stmt = select(DocumentChunk).where(DocumentChunk.document_id == document.id)
    existing_result = await session.execute(existing_chunks_stmt)
    existing_chunks = existing_result.scalars().all()
    if existing_chunks:
        for c in existing_chunks:
            session.delete(c)
        await session.commit()

    created = 0
    for i, chunk in enumerate(all_splits):
        text = chunk.page_content.strip()
        # sanitize text: remove NULs and ensure valid UTF-8
        if "\x00" in text:
            # remove NUL bytes that break Postgres UTF-8 encoding
            text = text.replace("\x00", "")
        try:
            # ensure encodable to utf-8, replace invalid sequences
            text = text.encode("utf-8", "replace").decode("utf-8")
        except Exception:
            text = "".join(ch for ch in text if ord(ch) != 0)

        if not text:
            continue

        vector = embeddings.embed_query(text, output_dimensionality=768)  # set dim to 768.

        # basic chunk metadata and indexes (explicit fallbacks so existing None values are replaced)
        chunk_meta = dict(chunk.metadata or {})
        chunk_meta["page"] = chunk_meta.get("page") or chunk_meta.get("page", None)
        chunk_meta["source"] = chunk_meta.get("source") or storage_key
        chunk_meta["s3_key"] = chunk_meta.get("s3_key") or storage_key
        chunk_meta["splitter_start_index"] = chunk_meta.get("splitter_start_index") or getattr(chunk, "start_index", None)

        dc = DocumentChunk(
            document_id=document.id,
            content=text,
            embedding=vector,
            organization_id=document.organization_id,
            raw_metadata=chunk_meta,
            chunk_index=i,
            content_length=len(text),
        )
        session.add(dc)
        created += 1

        # Commit in small batches to keep memory stable
        if created % 200 == 0:
            await session.commit()

    # Mark document as up-to-date after successful embedding
    document.last_embedded_at = datetime.now()
    session.add(document)
    await session.commit()

    return {
        "document_id": str(document.id),
        "chunks": created,
        "last_embedded_at": document.last_embedded_at.isoformat() if document.last_embedded_at else None,
        "detail": "Embedded and stored",
    }
