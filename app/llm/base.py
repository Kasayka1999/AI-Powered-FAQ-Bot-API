import os
from app.config import llm_settings

os.environ["LANGSMITH_TRACING"] = llm_settings.LANGSMITH_TRACING
os.environ["LANGSMITH_ENDPOINT"] = llm_settings.LANGSMITH_ENDPOINT
os.environ["LANGSMITH_API_KEY"] = llm_settings.LANGSMITH_API_KEY
os.environ["LANGSMITH_PROJECT"] = llm_settings.LANGSMITH_PROJECT


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import asyncio
from typing import Optional, List, Dict, Any

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=llm_settings.GEMINI_API_KEY
)


async def llm_call(prompt: Optional[str] = None, *, system: Optional[str] = None, messages: Optional[List[Dict[str, str]]] = None, **kwargs: Any) -> str:
    """
    Async wrapper for the sync langchain ChatGoogleGenerativeAI instance.

    - Provide either `prompt` (string) or `messages` (list of dicts like {"role":"system"/"user", "content": "..."}).
    - `system` is a shortcut to add a system message before the user prompt.
    - Runs the sync LLM call in a thread to avoid blocking the event loop.
    - Returns plain text extracted from the model result.

    Adapt extraction logic below if your llm returns a different structure.
    """
    if messages is None:
        if prompt is None:
            raise ValueError("either prompt or messages is required")
        # build message objects
        msg_objs = []
        if system:
            msg_objs.append(SystemMessage(content=system))
        msg_objs.append(HumanMessage(content=prompt))
    else:
        # convert simple dict messages to LangChain message objects
        msg_objs = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                msg_objs.append(SystemMessage(content=content))
            else:
                msg_objs.append(HumanMessage(content=content))

    def sync_call():
        # try calling the llm directly (LangChain chat models usually accept message objects)
        try:
            return llm(msg_objs, **kwargs)
        except TypeError:
            # fallback to generate if direct call signature differs
            try:
                return llm.generate([msg_objs], **kwargs)
            except Exception as e:
                raise

    result = await asyncio.to_thread(sync_call)

    # Simple, robust extraction
    text = None
    try:
        if hasattr(result, "generations"):
            gen = result.generations[0][0]
            text = getattr(gen, "text", None) or getattr(gen, "content", None) or str(gen)
        elif isinstance(result, str):
            text = result
        elif isinstance(result, dict):
            text = result.get("text") or result.get("content") or str(result)
        elif hasattr(result, "content"):
            text = str(getattr(result, "content"))
        else:
            text = str(result)
    except Exception:
        text = str(result)

    # Keep metadata minimal and safe to store: include llm_output if available and raw stringified result
    metadata: Dict[str, Any] = {
        "raw": str(result),
        "llm_output": getattr(result, "llm_output", None)
    }

    return {"text": text, "metadata": metadata}