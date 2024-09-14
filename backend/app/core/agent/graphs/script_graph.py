# import operator
# import functools
# from typing import Annotated, List, TypedDict
# from langchain_core.messages import BaseMessage, HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langgraph.graph import END, StateGraph, START
# from langgraph.prebuilt import create_react_agent
# from app.core.agent.helpers.utils import create_team_supervisor, agent_node
# from app.core.agent.flows.qa_flow import section_search,create_greeting, clarify_question
# from app.core.db.zillis_db import get_current_script_marker

# class ScriptFlow():
#     pass

# # Document writing team graph state
# class InterruptionFlowState(TypedDict):
#     # This tracks the team's conversation internally
#     messages: Annotated[List[BaseMessage], operator.add]
#     # This provides each worker with context on the others' skill sets
#     team_members: str
#     # This is how the supervisor tells langgraph who to work next
#     next: str
#     # This tracks the shared directory state
#     current_script: str


# # This will be run before each worker agent begins work
# # It makes it so they are more aware of the current state
# # of the working directory.
# def prelude(state):

#     current_script = get_current_script_marker()
    
#     if current_script is None:
#         return {**state, "current_script": "No current script marker found."}
    
#     return {
#         **state,
#         "current_script": f"Current script marker: {current_script}",
#     }


# llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-exp-0827")

# new_qna_agent = create_react_agent(llm, tools=[section_search])
# # Injects current directory working state before each call
# context_aware_qna_agent = prelude | new_qna_agent
# new_qna_node = functools.partial(
#     agent_node, agent=context_aware_qna_agent, name="NewQnAFlow"
# )

# greeting_agent = create_react_agent(llm, tools=[create_greeting])
# context_aware_greeting_agent = prelude | greeting_agent
# greeting_node = functools.partial(
#     agent_node, agent=context_aware_greeting_agent, name="GreetingFlow"
# )

# clarifying_agent = create_react_agent(llm, tools=[clarify_question])
# context_aware_clarifying_agent = prelude | clarifying_agent
# clarifying_node = functools.partial(
#     agent_node, agent=context_aware_clarifying_agent, name="ClarifyingFlow"
# )

# doc_writing_supervisor = create_team_supervisor(
#     llm,
#     "You are a supervisor tasked with managing a conversation between the"
#     " following workers:  {team_members}. Given the following user request,"
#     " respond with the worker to act next. Each worker will perform a"
#     " task and respond with their results and status. When finished,"
#     " respond with FINISH.",
#     ["NewQnAFlow", "GreetingFlow", "ClarifyingFlow"],
# )

# # Create the graph here:
# # Note that we have unrolled the loop for the sake of this doc
# interruption_graph = StateGraph(InterruptionFlowState)
# interruption_graph.add_node("NewQnAFlow", new_qna_node)
# interruption_graph.add_node("GreetingFlow", greeting_node)
# interruption_graph.add_node("ClarifyingFlow", clarifying_node)
# interruption_graph.add_node("supervisor", doc_writing_supervisor)

# # Add the edges that always occur
# interruption_graph.add_edge("NewQnAFlow", "supervisor")
# interruption_graph.add_edge("GreetingFlow", "supervisor")
# interruption_graph.add_edge("ClarifyingFlow", "supervisor")

# # Add the edges where routing applies
# interruption_graph.add_conditional_edges(
#     "supervisor",
#     lambda x: x["next"],
#     {
#         "NewQnAFlow": "NewQnAFlow",
#         "GreetingFlow": "GreetingFlow",
#         "ClarifyingFlow": "ClarifyingFlow",
#         "FINISH": END,
#     },
# )

# interruption_graph.add_edge(START, "supervisor")
# chain = interruption_graph.compile()


# # The following functions interoperate between the top level graph state
# # and the state of the interruption sub-graph
# # this makes it so that the states of each graph don't get intermixed
# def enter_chain(message: str, members: List[str]):
#     results = {
#         "messages": [HumanMessage(content=message)],
#         "team_members": ", ".join(members),
#     }
#     return results


# # We reuse the enter/exit functions to wrap the graph
# interruption_chain = (
#     functools.partial(enter_chain, members=interruption_graph.nodes)
#     | interruption_graph.compile()
# )



# Define the list of JSON objects
json_list = [
{
    "topic": "Chapter 5: Conservation of Resources",
    "content": {
        "session_id": "session_id",
        "script": [
            {
                "paragraph": "Hello! Today we're diving into Chapter 5: Conservation of Resources. This chapter is all about understanding how we use and manage the resources available to us, and why it's so important to do it sustainably.",
                "pause": "Let's take a moment to think about what resources are."
            },
            {
                "paragraph": "Resources are everything we need to survive and thrive. They include things like land, water, forests, minerals, and even the air we breathe.  These resources are vital for our existence, and without them, we wouldn't be able to live.",
                "pause": "But here's the catch: resources aren't infinite."
            },
            {
                "paragraph": "We've been using resources for a long time, and sometimes we use them faster than they can be replenished. This can lead to problems like resource depletion, pollution, and even conflict. That's why conservation is so important.",
                "pause": "Let's break down the key concepts of resource conservation."
            },
            {
                "paragraph": "Resource conservation is all about using resources wisely and responsibly. It's about making sure we have enough for ourselves and future generations.  There are many ways to conserve resources, like reducing our consumption, recycling, and using renewable energy sources.",
                "pause": "Now, let's talk about resource planning."
            },
            {
                "paragraph": "Resource planning is a crucial part of conservation. It involves making decisions about how we use our resources, taking into account both our current needs and the needs of future generations.  This planning process helps us to avoid over-exploitation and ensure that resources are used sustainably.",
                "pause": "Let's look at how resource planning works in India."
            },
            {
                "paragraph": "India has a diverse range of resources, but it also faces challenges in managing them.  Resource planning in India involves several key aspects, including:",
                "pause": ""
            },
            {
                "paragraph": "1. *Inventory of Resources:*  This involves mapping and understanding the types and quantities of resources available across different regions of the country. This helps us to identify areas where resources are abundant and areas where they are scarce.",
                "pause": ""
            },
            {
                "paragraph": "2. *Evolving a Planning Structure:*  This involves creating a framework for managing resources at different levels, from the national level to the local level. This ensures that resource management is coordinated and effective.",
                "pause": ""
            },
            {
                "paragraph": "3. *Matching Resource Development Plans:*  This involves aligning resource development plans with overall national development goals. This ensures that resource use is sustainable and contributes to the overall well-being of the country.",
                "pause": ""
            },
            {
                "paragraph": "4. *Judicious Use of Resources:*  This involves using resources wisely and avoiding waste. This is essential for ensuring that resources are available for future generations.",
                "pause": ""
            },
            {
                "paragraph": "Let's focus on one of the most important resources: land.",
                "pause": ""
            },
            {
                "paragraph": "Land is a vital resource, and it's used for a variety of purposes, including agriculture, forestry, and urban development.  However, land is also a finite resource, and it's important to manage it sustainably.",
                "pause": ""
            },
            {
                "paragraph": "Land degradation is a major problem in many parts of the world, including India.  This can be caused by factors like deforestation, overgrazing, and soil erosion.  These problems can have serious consequences for the environment and for people's livelihoods.",
                "pause": ""
            },
            {
                "paragraph": "Soil conservation is a crucial aspect of land management.  It involves protecting and improving the quality of soil.  There are many ways to conserve soil, including:",
                "pause": ""
            },
            {
                "paragraph": "1. *Contour Ploughing:*  This involves ploughing along the contours of the land, which helps to slow down the flow of water and reduce soil erosion.",
                "pause": ""
            },
            {
                "paragraph": "2. *Shelter Belts:*  Planting trees and shrubs around fields can help to break the force of the wind and reduce soil erosion.",
                "pause": ""
            },
            {
                "paragraph": "3. *Afforestation:*  Planting trees on degraded land can help to restore soil fertility and prevent erosion.",
                "pause": ""
            },
            {
                "paragraph": "4. *Proper Management of Grazing:*  Controlling the number of animals that graze on a particular area of land can help to prevent overgrazing and soil degradation.",
                "pause": ""
            },
            {
                "paragraph": "Now, let's talk about sustainable development.",
                "pause": ""
            },
            {
                "paragraph": "Sustainable development is a key concept in resource conservation.  It's about meeting the needs of the present generation without compromising the ability of future generations to meet their own needs.  This means using resources in a way that is both environmentally friendly and economically viable.",
                "pause": ""
            },
            {
                "paragraph": "The concept of sustainable development was first introduced in the Brundtland Commission Report in 1987.  This report emphasized the importance of balancing economic growth with environmental protection and social equity.",
                "pause": ""
            },
            {
                "paragraph": "The Rio Earth Summit in 1992 was a landmark event in the history of sustainable development.  At this summit, world leaders adopted Agenda 21, a plan for achieving sustainable development at the global level.",
                "pause": ""
            },
            {
                "paragraph": "Agenda 21 emphasizes the importance of local action in achieving sustainable development.  It calls on local governments to develop their own local Agenda 21 plans, which should address the specific needs and challenges of their communities.",
                "pause": ""
            },
            {
                "paragraph": "In conclusion, resource conservation is essential for ensuring a sustainable future.  It involves using resources wisely, planning for the future, and promoting sustainable development.  By working together, we can protect our resources and create a better world for ourselves and future generations.",
                "pause": ""
            }
        ]
    }
}
]

class ScriptFlow():
    

# Initialize a global variable
global_variable = None

# Loop through the JSON list
for item in json_list:
    # Extract content and id from each item
    for content in item["content"]:
        # Update the global variable based on the current paragraph's id
        global_variable = item["id"]
        
        # Example: process the paragraph (print the paragraph)
        print(f"Processing paragraph for ID: {global_variable}")
        print(f"Paragraph: {content['paragraph']}")
        
        # Show the updated global variable in each iteration
        print(f"Global variable is now set to: {global_variable}")

# After processing all paragraphs, the global variable will reflect the last ID processed
print(f"Final global variable value: {global_variable}")
