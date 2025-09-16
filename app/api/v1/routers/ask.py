from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import SessionDep, UserDep
from app.models.organization import Organization
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
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}

    # common structured places
    for key in ("usage", "llm_output", "response_metadata", "usage_metadata"):
        part = metadata.get(key)
        if isinstance(part, dict):
            return {
                "input_tokens": part.get("input_tokens") or part.get("input") or part.get("input_tokens_count"),
                "output_tokens": part.get("output_tokens") or part.get("output") or part.get("output_tokens_count"),
                "total_tokens": part.get("total_tokens") or part.get("total") or part.get("total_tokens_count"),
            }

    # fallback: parse raw string like "... 'input_tokens': 123, 'output_tokens': 45 ..."
    raw = metadata.get("raw", "")
    def _find(name):
        m = re.search(rf"['\"]?{name}['\"]?\s*[:=]\s*(\d+)", raw)
        return int(m.group(1)) if m else None

    return {
        "input_tokens": _find("input_tokens"),
        "output_tokens": _find("output_tokens"),
        "total_tokens": _find("total_tokens"),
    }

class AskRequest(BaseModel):
    question: str
    organization: str


@router.post("/ask")
async def ask_route(body: AskRequest, 
                    Session: SessionDep, 
                    current_user: UserDep):
    get_org = select(Organization.id).where(Organization.organization_name == body.organization)
    result = await Session.execute(get_org)
    org_record = result.scalar_one_or_none()  # Gets the first match or None; raises if multiple matches
    
    if org_record is None:
        raise HTTPException(status_code=404, detail=f"Organization '{body.organization}' not found.")
    
    org_id = str(org_record)  # Convert UUID to string for vector_search
    
    if org_id is None:  # This shouldn't happen after the query, but for safety
        raise HTTPException(status_code=400, detail="Invalid organization.")

    vector_results = await vector_search(org_id=org_id, query=body.question, session=Session)

    if not vector_results:
        return {"answer": "I don't know (no indexed documents for your organisation)."}

    # Build a short context; truncate chunk text to avoid token overflow
    context_pieces = []
    for result in vector_results:
        snippet = (result["content"] or "")[:1500]
        context_pieces.append(f"id:{result['id']}]\n{snippet}")


    system = ("You are a helpful assistant. Answer ONLY using the CONTEXT below. "
              "If the answer is not present, say: 'I don't know; please contact support.'")
    prompt = f"{system}\n\nCONTEXT:\n\n" + "\n\n---\n\n".join(context_pieces) + f"\n\nQUESTION:\n{body.question}"

    llm_result = await llm_call(prompt)
    # text to return to client
    answer_text = llm_result["text"]



    return {"answer": answer_text}