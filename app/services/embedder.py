from typing import List
import math
from app.config import llm_settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

EMBED_DIM = 768  # keep in sync with model + DB (also gemini-embedding-001)

# create one place to call embeddings & normalize
_embeddings = None

def _get_embedder():
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=llm_settings.GEMINI_API_KEY,
        )
    return _embeddings

async def embed_text(text: str) -> List[float]:
    embedder = _get_embedder()
    vec = embedder.embed_query(text, output_dimensionality=768)  # #set dim to 768 for gemini-embedding-001
    # validate
    if len(vec) != EMBED_DIM:
        raise ValueError(f"unexpected embedding dim: {len(vec)} != {EMBED_DIM}")
    # normalize for cosine if you plan to use cosine; otherwise skip
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec