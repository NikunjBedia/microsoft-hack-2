import os
import operator
from langchain_core.messages import BaseMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph, START
from typing_extensions import TypedDict
from typing import Annotated, List
from app.core.agent.helpers.utils import create_team_supervisor
from app.core.agent.graphs.interruption_graph import InterruptionGraph
from app.core.agent.graphs.script_graph import script_chain

class SuperGraph:
    def __init__(self):
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.environ.get("GROQ_API_KEY"),
        )

        self.supervisor_node = create_team_supervisor(
            self.llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following teams: {team_members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["ScriptGenerationTeam", "QuestionAnsweringTeam"],
        )

        self.current_state = None
        self.is_first_run = True
        self.interruption_state = None
        self.interruption_graph = InterruptionGraph()
        self.compiled_graph = self.compile_graph()
        self.script_generation_state = None
        self.is_interruption = False
        self.awaiting_feedback = False

    # Top-level graph state
    class State(TypedDict):
        messages: Annotated[List[BaseMessage], operator.add]
        next: str
        last_team: str  # Track which team acted last

    @staticmethod
    def get_last_message(state: State) -> str:
        return state["messages"][-1].content

    @staticmethod
    def join_graph(response: dict):
        return {"messages": [response["messages"][-1]]}

    def compile_graph(self):
        # Define the graph.
        super_graph = StateGraph(self.State)
        # First add the nodes, which will do the work
        super_graph.add_node("ScriptGenerationTeam", self.get_last_message | script_chain | self.join_graph)
        super_graph.add_node(
            "QuestionAnsweringTeam", self.get_last_message | self.interruption_graph.run_interruption_chain | self.join_graph
        )
        super_graph.add_node("supervisor", self.supervisor_node)

        # Define the graph connections, which controls how the logic
        # propagates through the program
        super_graph.add_edge("ScriptGenerationTeam", "supervisor")
        super_graph.add_edge("QuestionAnsweringTeam", "supervisor")

        # New function to handle the transitions
        def handle_team_finish(state: self.State):
            if state["next"] == "FINISH":
                if state["last_team"] == "QuestionAnsweringTeam":
                    return {"next": "ScriptGenerationTeam", "last_team": "QuestionAnsweringTeam"}
                elif state["last_team"] == "ScriptGenerationTeam":
                    return {"next": "FINISH"}
            return {"next": state["next"], "last_team": state["next"]}

        super_graph.add_conditional_edges(
            "supervisor",
            handle_team_finish,
            {
                "ScriptGenerationTeam": "ScriptGenerationTeam",
                "QuestionAnsweringTeam": "QuestionAnsweringTeam",
                "FINISH": END,
            },
        )
        super_graph.add_edge(START, "supervisor")
        return super_graph.compile()

    def run(self, input_message, is_initial=False):
        if is_initial:
            self.current_state = {"messages": [input_message], "next": "ScriptGenerationTeam", "last_team": ""}
            self.is_first_run = False
        elif self.is_interruption:
            self.current_state["messages"].append(input_message)
            self.current_state["next"] = "QuestionAnsweringTeam"
        else:
            # Continue with script generation
            self.current_state = self.script_generation_state
            self.current_state["messages"].append(input_message)
            self.current_state["next"] = "ScriptGenerationTeam"

        for output in self.compiled_graph.stream(self.current_state, {"recursion_limit": 100}):
            self.current_state = output
            if output["next"] == "ScriptGenerationTeam":
                self.script_generation_state = self.current_state.copy()
            if output["next"] == END:
                break
        
        self.is_interruption = False
        return self.current_state

    def handle_interruption(self, interruption_message):
        self.is_interruption = True
        interruption_result = self.interruption_graph.run_interruption_chain(interruption_message)
        
        if interruption_result["status"] == "human_feedback_required":
            self.interruption_state = interruption_result["state"]
            return {"status": "human_feedback_required", "message": "Human feedback is required."}
        
        return self.run(interruption_message)

    def continue_with_human_feedback(self, feedback):
        if self.interruption_state is None:
            return {"status": "error", "message": "No interruption state found."}
        
        continuation_result = self.interruption_graph.continue_with_feedback(self.interruption_state, feedback)
        self.interruption_state = None
        
        if continuation_result["status"] == "finished":
            return self.run(feedback)  # This will continue with ScriptGenerationTeam
        elif continuation_result["status"] == "human_feedback_required":
            self.interruption_state = continuation_result["state"]
            return {"status": "human_feedback_required", "message": "Additional human feedback is required."}
        
        return continuation_result

    def awaiting_feedback(self):
        return self.awaiting_feedback

    def start_conversation(self, message: str):
        self.awaiting_feedback = False
        return self.run(message, is_initial=True)

    def handle_interruption(self, message: str):
        result = self.interruption_graph.handle_interruption(message)
        if result.get("status") == "human_feedback_required":
            self.awaiting_feedback = True
        return result

    def continue_with_human_feedback(self, feedback: str):
        if not self.awaiting_feedback:
            raise ValueError("No feedback was requested.")
        
        self.awaiting_feedback = False
        result = self.interruption_graph.continue_with_feedback(feedback)
        if result.get("status") == "human_feedback_required":
            self.awaiting_feedback = True
        return result