from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import SessionDep, UserDep
from app.models.ai_audit_logs import AIAuditLogs
from app.models.organization import Organization
from app.models.documents import Documents 
from app.services.similarity_search import vector_search
from app.llm.base import llm_call
import re

router = APIRouter(prefix="/chat", tags=["Chat"])


def _extract_tokens_from_metadata(metadata: dict) -> dict:
    """
    Try common places first (usage or llm_output dict), else simple regex fallback on raw string.
    Returns dict with keys input_tokens, output_tokens, total_tokens (values or None).
    """
    if not metadata:
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None, "model_name": None}

    # common structured places
    for key in ("usage", "llm_output", "response_metadata", "usage_metadata"):
        part = metadata.get(key)
        if isinstance(part, dict):
            return {
                "input_tokens": part.get("input_tokens") or part.get("input") or part.get("input_tokens_count"),
                "output_tokens": part.get("output_tokens") or part.get("output") or part.get("output_tokens_count"),
                "total_tokens": part.get("total_tokens") or part.get("total") or part.get("total_tokens_count"),
                "model_name": part.get("model_name") or part.get("model"),
            }

    raw = metadata.get("raw", "") or ""

    def _find_int(name: str):
        m = re.search(rf"['\"]?{re.escape(name)}['\"]?\s*[:=]\s*(\d+)", raw)
        return int(m.group(1)) if m else None

    def _find_str(name: str):
        # first try quoted string like model_name='gemini-2.5-flash'
        m = re.search(rf"['\"]?{re.escape(name)}['\"]?\s*[:=]\s*['\"](?P<v>[^'\"]+)['\"]", raw)
        if m:
            return m.group("v")
        # fallback: unquoted token
        m = re.search(rf"{re.escape(name)}\s*[:=]\s*([^\s,}}]+)", raw)
        return m.group(1) if m else None

    return {
        "input_tokens": _find_int("input_tokens"),
        "output_tokens": _find_int("output_tokens"),
        "total_tokens": _find_int("total_tokens"),
        "model_name": _find_str("model_name")
    }

class AskRequest(BaseModel):
    question: str
    organization: str


@router.post("/ask")
async def ask_route(body: AskRequest, 
                    session: SessionDep, 
                    current_user: UserDep):
    get_org = select(Organization.id).where(Organization.organization_name == body.organization)
    result = await session.execute(get_org)
    org_record = result.scalar_one_or_none()  # Gets the first match or None; raises if multiple matches
    
    if org_record is None:
        raise HTTPException(status_code=404, detail=f"Organization '{body.organization}' not found.")
    
    org_id = str(org_record)  # Convert UUID to string for vector_search
    
    if org_id is None:  # This shouldn't happen after the query, but for safety
        raise HTTPException(status_code=400, detail="Invalid organization.")

    vector_results = await vector_search(org_id=org_id, query=body.question, session=session)

    if not vector_results:
        return {"answer": "I don't know (no indexed documents for your organisation)."}

    # build sources list (keep traceable metadata like page, source, chunk id)
    sources = []
    context_pieces = []
    for result in vector_results:
        meta = result.get("metadata") or {}
        snippet = (result["content"] or "")[:1500]
        context_pieces.append(f"id:{result['id']}]\n{snippet}")
        sources.append({
            "id": result["id"],
            "document_id": result["document_id"],
            "filename": result.get("filename"),
            "page": meta.get("page"),
            "page_label": meta.get("page_label"),
            "start_index": meta.get("start_index"),
            "total_pages": meta.get("total_pages"),
            "distance": result.get("distance"),
            "snippet": snippet,
        })
        
    system = ("You are a helpful assistant. Answer ONLY using the CONTEXT below. "
              "If the answer is not present, say: 'I don't know; please contact support.'")
    prompt = f"{system}\n\nCONTEXT:\n\n" + "\n\n---\n\n".join(context_pieces) + f"\n\nQUESTION:\n{body.question}"

    llm_result = await llm_call(prompt)
    # text to return to client
    answer_text = llm_result["text"]

    #returns complete llm metadata
    metadata_text = llm_result["metadata"]

    # extract token counts using existing helper
    token_counts = _extract_tokens_from_metadata(metadata_text)

    # Save an audit record for persistence
    # This is persisted to ai_audit_logs for analytics and investigation.
    audit = AIAuditLogs(
        prompt=body.question,
        response_text=answer_text,
        requester_email=current_user.email,
        requester_full_name=current_user.full_name,
        organization_id=org_record,  # use the UUID result from the select
        input_tokens=token_counts.get("input_tokens"),
        output_tokens=token_counts.get("output_tokens"),
        total_tokens=token_counts.get("total_tokens"),
        model_name=token_counts.get("model_name"),
        # ensure JSONB-safe value (converts UUID/datetime -> strings) (THANKS CHATGPT)
        sources=jsonable_encoder(sources)
    )

    session.add(audit)
    await session.commit()
    await session.refresh(audit)

    return {"answer": answer_text}
