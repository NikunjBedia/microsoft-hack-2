import operator
import functools
from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent
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
    human_feedback_required: bool

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
        self.graph = self._create_graph()
        self.compiled_graph = self.graph.compile()
        self.awaiting_feedback = False
        self.conversation_started = False

    def _prelude(self, state):
        """Prepare the initial state with the current script."""
        current_script = "Hey there! Today we're diving into Chapter 5: Conservation of Resources. This chapter is all about understanding how we use and manage the resources available to us, and why it's so important to do it wisely.Resources are everything we need to survive and thrive. They're the things we use to build our homes, grow our food, power our industries, and even enjoy our leisure time.  Think about it: the air we breathe, the water we drink, the land we live on, the minerals we extract, and the energy we use are all resources. "
        if current_script is None:
            return {**state, "current_script": "No current script marker found."}
        return {**state, "current_script": f"This is the current script that is being spoken: {current_script}"}

    def _section_search_with_state(self, query: str, state: InterruptionFlowState):
        """
        Perform a section search based on the query and current state.
        
        Args:
            query (str): The user's query.
            state (InterruptionFlowState): The current state of the conversation.
        
        Returns:
            str: The result of the section search.
        """
        conversation_history = [msg.content for msg in state["messages"]]
        current_script = state["current_script"]
        return section_search(query, conversation_history, current_script)

    def _create_greeting_with_state(self, query: str, state: InterruptionFlowState):
        """
        Create a greeting based on the query and current state.
        
        Args:
            query (str): The user's query.
            state (InterruptionFlowState): The current state of the conversation.
        
        Returns:
            str: The generated greeting.
        """
        conversation_history = [msg.content for msg in state["messages"]]
        current_script = state["current_script"]
        return create_greeting(query, conversation_history, current_script)

    def _clarify_question_with_state(self, query: str, state: InterruptionFlowState):
        """
        Clarify a question based on the query and current state.
        
        Args:
            query (str): The user's query.
            state (InterruptionFlowState): The current state of the conversation.
        
        Returns:
            str: The clarified question.
        """
        conversation_history = [msg.content for msg in state["messages"]]
        current_script = state["current_script"]
        return clarify_question(query, conversation_history, current_script)

    def _create_graph(self):
        new_qna_agent = create_react_agent(self.llm, tools=[self._section_search_with_state])
        context_aware_qna_agent = self._prelude | new_qna_agent
        new_qna_node = functools.partial(agent_node, agent=context_aware_qna_agent, name="NewQnAFlow")

        greeting_agent = create_react_agent(self.llm, tools=[self._create_greeting_with_state])
        context_aware_greeting_agent = self._prelude | greeting_agent
        greeting_node = functools.partial(agent_node, agent=context_aware_greeting_agent, name="GreetingFlow")

        clarifying_agent = create_react_agent(self.llm, tools=[self._clarify_question_with_state])
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
        graph.add_node("HumanFeedback", self._human_feedback_node)

        graph.add_edge("NewQnAFlow", "HumanFeedback")
        graph.add_edge("GreetingFlow", "HumanFeedback")
        graph.add_edge("ClarifyingFlow", "HumanFeedback")

        graph.add_conditional_edges(
            "HumanFeedback",
            lambda x: x["next"],
            {
                "supervisor": "supervisor",
                "FINISH": END,
            },
        )

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

        graph.add_edge(START, "supervisor")

        return graph

    @staticmethod
    def _human_feedback_node(state: InterruptionFlowState):
        """
        Handle the human feedback node in the graph.
        
        Args:
            state (InterruptionFlowState): The current state of the conversation.
        
        Returns:
            dict: The updated state indicating human feedback is required.
        """
        return {"human_feedback_required": True, "next": "supervisor"}

    def awaiting_feedback(self):
        return self.awaiting_feedback

    def start_conversation(self, message: str):
        """
        Start a new conversation with the initial message.
        """
        self.conversation_started = True
        self.awaiting_feedback = False
        return self.run_interruption_chain(message)

    def run_interruption_chain(self, message: str):
        """
        Run the interruption chain with a given message.
        """
        if not self.conversation_started:
            raise ValueError("Conversation not started. Use start_conversation first.")
        
        state = self.enter_chain(message)
        
        for output in self.compiled_graph(state):
            if output.get("human_feedback_required", False):
                self.awaiting_feedback = True
                return {"status": "human_feedback_required", "state": output}
            if output["next"] == END:
                return {"status": "finished", "state": output}
        
        return {"status": "error", "state": output}

    def continue_with_feedback(self, state: dict, feedback: str):
        """
        Continue the conversation with human feedback.
        """
        if not self.awaiting_feedback:
            raise ValueError("No feedback was requested.")
        
        self.awaiting_feedback = False
        state["messages"].append(HumanMessage(content=feedback))
        state["human_feedback_required"] = False
        
        for output in self.compiled_graph(state):
            if output.get("human_feedback_required", False):
                self.awaiting_feedback = True
                return {"status": "human_feedback_required", "state": output}
            if output["next"] == END:
                return {"status": "finished", "state": output}
        
        return {"status": "error", "state": output}

    def handle_interruption(self, message: str):
        """
        Handle an interruption message.
        """
        if not self.conversation_started:
            raise ValueError("Conversation not started. Use start_conversation first.")
        
        return self.run_interruption_chain(message)

# interruption_graph = InterruptionGraph()