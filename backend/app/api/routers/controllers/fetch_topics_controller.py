from fastapi import APIRouter, Query
from app.utils.llm.document_qa import DocumentQA
from app.utils.vector_store.vector_store import VectorStore
from app.utils.llm.gemini_llm import LLM

fetch_topics_router = APIRouter()

# Initialize DocumentQA
vector_store = VectorStore()
vector_store = vector_store.create_vector_store()
llm = LLM()
document_qa = DocumentQA(vector_store, llm)



@fetch_topics_router.get("")
async def fetch_topic(topic: str = Query(..., description="The topic to fetch content for")):
    """
    Endpoint to fetch content for a given topic.
    """
    try:
        content = document_qa.get_topic_content(topic)
        return {"topic": topic, "content": content}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}