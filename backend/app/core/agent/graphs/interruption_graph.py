import operator
import functools
from typing import Annotated, List, TypedDict
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph, START, MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from app.core.agent.helpers.utils import create_team_supervisor, agent_node
from app.core.agent.flows.qa_flow import section_search, create_greeting, clarify_question
from dotenv import load_dotenv
import os

load_dotenv()

class InterruptionFlowState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    team_members: str
    next: str
    current_script: str
    interruption_question: str
    human_feedback_required: bool
@tool
def _section_search_with_state(query: str):
    """
    Perform a section search based on the query and current state.
    
    Args:
        query (str): The user's query.
    
    Returns:
        str: The result of the section search.
    """
    # conversation_history = [msg.content for msg in state["messages"]]
    conversation_history = []
    # current_script = state["current_script"]
    current_script = []
    response = section_search(query, conversation_history, current_script)
    return response

@tool 
def _create_greeting_with_state(query: str):
    """
    Create a greeting based on the query and current state.
    
    Args:
        query (str): The user's query.
    
    Returns:
        str: The generated greeting.
    """
    # conversation_history = [msg.content for msg in state["messages"]]
    # current_script = state["current_script"]
    # response = create_greeting(query, conversation_history, current_script)
    context = f"""
    Current script: Hey there! Today we're diving into Chapter 5: Conservation of Resources. This chapter is all about understanding how we use and manage the resources available to us, and why it's so important to do it wisely.Resources are everything we need to survive and thrive. They're the things we use to build our homes, grow our food, power our industries, and even enjoy our leisure time.  Think about it: the air we breathe, the water we drink, the land we live on, the minerals we extract, and the energy we use are all resources. 
    User query: {query}
    """

    # Generate a greeting based on the query, conversation history, and current script
    prompt = f"""
    Based on the following context, generate a friendly and contextually appropriate greeting:

    {context}

    The greeting should acknowledge any relevant information from the conversation history
    and current script, if applicable. Make sure the greeting is welcoming and sets a positive tone for the interaction.
    """
    llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY")
        )
    response = llm.invoke(prompt)
    return response
@tool
def _clarify_question_with_state(query: str):
    """
    Clarify a question based on the query and current state.
    
    Args:
        query (str): The user's query.
    
    Returns:
        str: The clarified question.
    """
     # conversation_history = [msg.content for msg in state["messages"]]
    conversation_history = []
    # current_script = state["current_script"]
    current_script = []
    response = clarify_question(query, conversation_history, current_script)
    return response
class InterruptionGraph:
    def __init__(self):
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.graph = self.create_graph()
        # self.compiled_graph = self.graph.compile()
        # self.awaiting_feedback = False
        # self.conversation_started = False

    def _prelude(self, state):
        """Prepare the initial state with the current script."""
        current_script = "Hey there! Today we're diving into Chapter 5: Conservation of Resources. This chapter is all about understanding how we use and manage the resources available to us, and why it's so important to do it wisely.Resources are everything we need to survive and thrive. They're the things we use to build our homes, grow our food, power our industries, and even enjoy our leisure time.  Think about it: the air we breathe, the water we drink, the land we live on, the minerals we extract, and the energy we use are all resources. "
        if current_script is None:
            return {**state, "current_script": "No current script marker found."}
        return {**state, "current_script": f"This is the current script that is being spoken: {current_script}"}


    def ask_human(self, state):
        pass

    def create_graph(self):
        new_qna_agent = create_react_agent(self.llm, tools=[_section_search_with_state])
        context_aware_qna_agent = self._prelude | new_qna_agent
        new_qna_node = functools.partial(agent_node, agent=context_aware_qna_agent, name="NewQnAFlow")

        greeting_agent = create_react_agent(self.llm, tools=[_create_greeting_with_state])
        context_aware_greeting_agent = self._prelude | greeting_agent
        greeting_node = functools.partial(agent_node, agent=context_aware_greeting_agent, name="GreetingFlow")

        clarifying_agent = create_react_agent(self.llm, tools=[_clarify_question_with_state])
        context_aware_clarifying_agent = self._prelude | clarifying_agent
        clarifying_node = functools.partial(agent_node, agent=context_aware_clarifying_agent, name="ClarifyingFlow")

        interruption_graph_supervisor = create_team_supervisor(
            self.llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following workers: {team_members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["NewQnAFlow", "GreetingFlow", "ClarifyingFlow"],
        )

        graph = StateGraph(InterruptionFlowState)
        graph.add_node("NewQnAFlow", new_qna_node)
        graph.add_node("GreetingFlow", greeting_node)
        graph.add_node("ClarifyingFlow", clarifying_node)
        graph.add_node("supervisor", interruption_graph_supervisor)
        graph.add_node("HumanFeedback", self.human_feedback_node)
        graph.add_node("AskHuman", self.ask_human)

        graph.add_edge("NewQnAFlow", "AskHuman")
        graph.add_edge("ClarifyingFlow", "AskHuman")
        graph.add_edge("GreetingFlow", "AskHuman")
        graph.add_edge("AskHuman", "HumanFeedback")


        graph.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "NewQnAFlow": "NewQnAFlow",
                "GreetingFlow": "GreetingFlow",
                "ClarifyingFlow": "ClarifyingFlow",
                "FINISH": END,
            },
        )
        graph.add_conditional_edges(
            "HumanFeedback",
            lambda x: x["next"],
            {
                "FINISH": END,
                "CONTINUE": "supervisor",
            },
        )

        graph.add_edge(START, "supervisor")

        memory_saver = MemorySaver() 

        builder_graph = graph.compile(checkpointer=memory_saver, interrupt_before=["HumanFeedback"])


        return builder_graph
    def human_feedback_node(self, state: InterruptionFlowState):
        # Initialize the LLM
        llm = self.llm

        # Prepare the context for the LLM
        context = f"""
        Current state of the conversation:
        Messages: {state['messages']}
        Current script: {state['current_script']}
        User Interruption: {state['interruption_question']}
        """

        # Generate a prompt for the LLM
        prompt = f"""
        Based on the following context, determine if the user is satisfied with the response given:

        Context:
        {context}

        If the user appears satisfied with the recent response, respond with "FINISH".
        If the user seems to require further clarification or assistance, respond with "CONTINUE".

        Respond with either "FINISH" or "CONTINUE".
        """

        # Get the LLM's decision
        response = llm.invoke(prompt)
        decision = response.content.strip()
        if "FINISH" in decision:
            
            decision = "FINISH"
        else:
            decision = "CONTINUE"
        return {**state, "next": decision}

    def enter_chain(self, message: str):
      results = {
          "messages": [HumanMessage(content=message)],
      }
      return results 
    
    def run(self):

      interruption_chain = self.enter_chain | self.graph

      return interruption_chain

# interruption_graph = InterruptionGraph()