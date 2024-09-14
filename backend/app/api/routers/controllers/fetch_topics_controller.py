from fastapi import APIRouter

fetch_topics_router = APIRouter()

@fetch_topics_router.get("")
async def fetch_topics():
    """
    Endpoint to fetch a list of topics.
    """
    # Example topics - replace with actual logic to retrieve topics
    topics = ["Technology", "Science", "Health", "Education"]
    return {"topics": topics}
