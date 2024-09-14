# initialize graph using langgraph
# create all nodes and edges
# create human in the loop node
# import START and END nods


import operator
from langchain_core.messages import BaseMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from helpers.utils import create_team_supervisor
from langgraph.graph import END, StateGraph, START
from typing_extensions import TypedDict
from typing import Annotated, List
from app.core.agent.graphs.interruption_graph import interruption_chain


class SuperGraph:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-exp-0827")

        self.supervisor_node = create_team_supervisor(
            self.llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following teams: {team_members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["ScriptGenerationTeam", "QuestionAnsweringTeam"],
        )

    # Top-level graph state
    class State(TypedDict):
        messages: Annotated[List[BaseMessage], operator.add]
        next: str

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
            "QuestionAnsweringTeam", self.get_last_message | interruption_chain | self.join_graph
        )
        super_graph.add_node("supervisor", self.supervisor_node)

        # Define the graph connections, which controls how the logic
        # propagates through the program
        super_graph.add_edge("ScriptGenerationTeam", "supervisor")
        super_graph.add_edge("QuestionAnsweringTeam", "supervisor")
        super_graph.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "ScriptGenerationTeam": "ScriptGenerationTeam",
                "QuestionAnsweringTeam": "QuestionAnsweringTeam",
                "FINISH": END,
            },
        )
        super_graph.add_edge(START, "supervisor")
        return super_graph.compile()