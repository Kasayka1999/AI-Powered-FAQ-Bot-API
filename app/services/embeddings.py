
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import llm_settings
from app.services.document_processing import all_splits

def build_embeddings():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=llm_settings.GEMINI_API_KEY,
    )

    empty_list = []
    for page in all_splits:
        vector = embeddings.embed_query(page.page_content)
        empty_list.append(vector)

    if len(empty_list) > 1:
        print(len(empty_list[1]))

    return empty_list

if __name__ == "__main__":
    build_embeddings()




