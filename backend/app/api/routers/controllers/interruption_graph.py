from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.agent.core import SuperGraph

interruption_graph_router = APIRouter()
super_graph = SuperGraph()

class GraphRequest(BaseModel):
    user_query: Optional[str] = None
    is_interruption: bool = False
    human_feedback: Optional[str] = None

@interruption_graph_router.post("")
async def handle_graph_request(request: GraphRequest):
    try:
        if request.is_initial:
            result = super_graph.run(request.user_query, is_initial=True)
        elif request.is_interruption:
            result = super_graph.handle_interruption(request.user_query)
        elif request.human_feedback:
            result = super_graph.continue_with_human_feedback(request.human_feedback)
        else:
            result = super_graph.run(request.user_query)

        if result.get("status") == "human_feedback_required":
            return {"response": result["message"], "requires_feedback": True}
        return {"response": result["messages"][-1].content, "requires_feedback": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
