from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
#from app.core.agent.core import SuperGraph

interruption_graph_router = APIRouter()
#super_graph = SuperGraph()

class GraphRequest(BaseModel):
    user_message: str
    is_initial: bool = False

@interruption_graph_router.post("")
async def handle_graph_request(request: GraphRequest):
    try:
        # if request.is_initial:
        #     result = super_graph.start_conversation(request.user_message)
        # elif super_graph.awaiting_feedback():
        #     result = super_graph.continue_with_human_feedback(request.user_message)
        # else:
        #     result = super_graph.handle_interruption(request.user_message)
        result ="des"

        if result.get("status") == "human_feedback_required":
            return {"response": result.get("message", "Human feedback required."), "requires_feedback": True}
        elif result.get("status") == "finished":
            return {"response": result.get("state", {}).get("messages", [])[-1].content, "requires_feedback": False}
        else:
            return {"response": "An unexpected error occurred.", "requires_feedback": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
