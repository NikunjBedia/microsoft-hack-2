from fastapi import APIRouter, Query

from app.core.fetch_topics import FetchTopicContent
fetch_topics_router = APIRouter()

# Initialize DocumentQA




@fetch_topics_router.get("")
async def fetch_topic_content(topic: str = Query(..., description="The topic to fetch content for")):
    """
    Endpoint to fetch content for a given topic.
    """
    try:
        content = FetchTopicContent().fetch_topic_content(topic)
        return {"topic": topic, "content": content}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}