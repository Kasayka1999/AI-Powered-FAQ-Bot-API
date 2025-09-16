from typing import List, Dict, Any
from sqlalchemy import select, bindparam, cast, Float
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.documents import DocumentChunk
from app.services.embedder import embed_text

#return limit search top x result
limit_results: int = 3

async def vector_search(
    org_id: str,
    query: str,
    session: AsyncSession | None = None,
) -> List[Dict[str, Any]]:
    if session is None:
        raise RuntimeError("pass AsyncSession (SessionDep) to vector_search")
    query_embed = await embed_text(query)  # same normalization as indexed vectors

    # build distance expression with SQLAlchemy operator (no raw SQL)
    dist_expr = cast(DocumentChunk.embedding.op("<->")(bindparam("q")), Float)
    stmt = (
        select(
            DocumentChunk.id,
            DocumentChunk.document_id,
            DocumentChunk.content,
            DocumentChunk.organization_id,
            dist_expr.label("distance"),
        )
        .where(DocumentChunk.organization_id == org_id)
        .order_by(dist_expr)
        .limit(limit_results)
    )
    result = await session.execute(stmt, {"q": query_embed})
    rows = []
    for chunk in result.mappings().all():
        rows.append({
            "id": chunk["id"],
            "document_id": chunk["document_id"],
            "content": chunk["content"],
            "metadata": chunk.get("metadata"),
            "distance": float(chunk["distance"]) if chunk.get("distance") is not None else None,
        })
    return rows