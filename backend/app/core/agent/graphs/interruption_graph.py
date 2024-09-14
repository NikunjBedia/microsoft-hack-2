import operator
import functools
from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent
from app.core.agent.helpers.utils import create_team_supervisor, agent_node
from app.core.agent.flows.qa_flow import section_search,create_greeting, clarify_question
from app.core.db.zillis_db import get_current_script_marker


# Document writing team graph state
class InterruptionFlowState(TypedDict):
    # This tracks the team's conversation internally
    messages: Annotated[List[BaseMessage], operator.add]
    # This provides each worker with context on the others' skill sets
    team_members: str
    # This is how the supervisor tells langgraph who to work next
    next: str
    # This tracks the shared directory state
    current_script: str


# This will be run before each worker agent begins work
# It makes it so they are more aware of the current state
# of the working directory.
def prelude(state):

    current_script = get_current_script_marker()
    
    if current_script is None:
        return {**state, "current_script": "No current script marker found."}
    
    return {
        **state,
        "current_script": f"Current script marker: {current_script}",
    }


llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-exp-0827")

new_qna_agent = create_react_agent(llm, tools=[section_search])
# Injects current directory working state before each call
context_aware_qna_agent = prelude | new_qna_agent
new_qna_node = functools.partial(
    agent_node, agent=context_aware_qna_agent, name="NewQnAFlow"
)

greeting_agent = create_react_agent(llm, tools=[create_greeting])
context_aware_greeting_agent = prelude | greeting_agent
greeting_node = functools.partial(
    agent_node, agent=context_aware_greeting_agent, name="GreetingFlow"
)

clarifying_agent = create_react_agent(llm, tools=[clarify_question])
context_aware_clarifying_agent = prelude | clarifying_agent
clarifying_node = functools.partial(
    agent_node, agent=context_aware_clarifying_agent, name="ClarifyingFlow"
)

doc_writing_supervisor = create_team_supervisor(
    llm,
    "You are a supervisor tasked with managing a conversation between the"
    " following workers:  {team_members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH.",
    ["NewQnAFlow", "GreetingFlow", "ClarifyingFlow"],
)

# Create the graph here:
# Note that we have unrolled the loop for the sake of this doc
interruption_graph = StateGraph(InterruptionFlowState)
interruption_graph.add_node("NewQnAFlow", new_qna_node)
interruption_graph.add_node("GreetingFlow", greeting_node)
interruption_graph.add_node("ClarifyingFlow", clarifying_node)
interruption_graph.add_node("supervisor", doc_writing_supervisor)

# Add the edges that always occur
interruption_graph.add_edge("NewQnAFlow", "supervisor")
interruption_graph.add_edge("GreetingFlow", "supervisor")
interruption_graph.add_edge("ClarifyingFlow", "supervisor")

# Add the edges where routing applies
interruption_graph.add_conditional_edges(
    "supervisor",
    lambda x: x["next"],
    {
        "NewQnAFlow": "NewQnAFlow",
        "GreetingFlow": "GreetingFlow",
        "ClarifyingFlow": "ClarifyingFlow",
        "FINISH": END,
    },
)

interruption_graph.add_edge(START, "supervisor")
chain = interruption_graph.compile()


# The following functions interoperate between the top level graph state
# and the state of the interruption sub-graph
# this makes it so that the states of each graph don't get intermixed
def enter_chain(message: str, members: List[str]):
    results = {
        "messages": [HumanMessage(content=message)],
        "team_members": ", ".join(members),
    }
    return results


# We reuse the enter/exit functions to wrap the graph
interruption_chain = (
    functools.partial(enter_chain, members=interruption_graph.nodes)
    | interruption_graph.compile()
)