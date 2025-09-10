from datetime import datetime
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.api.dependencies import SessionDep, UserDep
from app.models.documents import Documents
from app.utils.s3 import delete_file_from_s3, download_file_from_s3, file_exists_in_s3, upload_file_to_s3
from app.services.embeddings import process_and_embed_single_document  # NEW



router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}

def is_allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

@router.post("/upload")
async def upload_document(session: SessionDep,
                          current_user: UserDep,
                          file: UploadFile = File(...),
                          confirm: bool = False):
    if current_user.organization_id is None:
        raise HTTPException(status_code=406, detail="Your don't have an organisation, create first")
    if not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed.")
    
    new_storage_key = f'{current_user.organization_id}_{file.filename}'
    if file_exists_in_s3(new_storage_key) and not confirm:
        # Ask for confirmation
        raise HTTPException(
            status_code=409,
            detail=f'File already exists: {file.filename}. Send confirm=true to replace.'
        )
    
    try:
        """
        If confirm to replace, to delete the existing row from db,
        to not keep multiple duplicated rows with same storage_key but different id.
        """
        if file_exists_in_s3(new_storage_key) and confirm:
            old_doc_stmt = select(Documents).where(
                Documents.organization_id == current_user.organization_id,
                Documents.file_name == file.filename)
            old_doc_result = await session.execute(old_doc_stmt)
            old_doc = old_doc_result.scalars().first()
            if old_doc:
                # Delete DB entry; S3 file will be overwritten below
                await session.delete(old_doc)
                await session.commit()
        
        # Upload to AWS S3 (overwrites if exists)
        upload_file_to_s3(file.file, new_storage_key)

        # Persist new document row
        new_document = Documents(
            file_name=file.filename,
            upload_by=current_user.username,
            organization_id=current_user.organization_id,
            uploaded_at=datetime.now(),
            storage_key=new_storage_key
        )
        session.add(new_document)
        await session.commit()
        await session.refresh(new_document)

        # Embed-on-upload: chunk + embed + store chunks (cascades on future delete)
        await process_and_embed_single_document(session, new_document)

        return new_document
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my_documents")
async def show_documents(session: SessionDep, current_user: UserDep):
    # Return per-document freshness info using last_embedded_at vs uploaded_at
    docs_stmt = select(Documents).where(Documents.organization_id == current_user.organization_id)
    docs_result = await session.execute(docs_stmt)
    docs = docs_result.scalars().all()

    payload = []
    for doc in docs:
        up_to_date = bool(doc.last_embedded_at and doc.uploaded_at and doc.last_embedded_at >= doc.uploaded_at)
        payload.append({
            "file_name": doc.file_name,
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            "last_embedded_at": doc.last_embedded_at.isoformat() if doc.last_embedded_at else None,
            "up_to_date": up_to_date,
        })
    return {"Documents": payload}

@router.post("/download")
async def download_document(session: SessionDep, curret_user: UserDep, filename: str):
    try:
        doc_statement = select(Documents.storage_key).where(
            Documents.organization_id == curret_user.organization_id,
            Documents.file_name == filename)
        doc_result = await session.execute(doc_statement)
        download_doc = doc_result.scalars().first()
        
        if not download_doc:
            raise HTTPException(status_code=409, detail=f"File with name: {filename} not found, tip: check /documents/my_documents")
        
        if not file_exists_in_s3(download_doc):
            raise HTTPException(status_code=409, detail=f"File with name: {filename} not found, tip: check /documents/my_documents")
        file_content = download_file_from_s3(download_doc)
        return StreamingResponse(
            iter([file_content]),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete")
async def delete_document(filename: str,
                          session: SessionDep,
                          current_user: UserDep,
                          confirm: bool = False):
    if not confirm:
        return {"detail": "Are you sure you want to delete? Send confirm=True to proceed."}
    
    doc_stm = select(Documents).where(
        Documents.organization_id == current_user.organization_id,
        Documents.file_name == filename)
    doc_result = await session.execute(doc_stm)
    doc = doc_result.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=409, detail=f"Failed: Document with {filename} not found.")
    
    # Delete from S3 first (best effort)
    delete_file_from_s3(doc.storage_key)
    # Delete DB row; chunks are removed via ON DELETE CASCADE
    await session.delete(doc)
    await session.commit()
    return {"detail": f"Success: Document {filename} deleted (including all chunks/embeddings)."}
