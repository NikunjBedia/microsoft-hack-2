import json
from typing import List, Dict, Any, TypedDict, Generator
from langgraph.graph import END, StateGraph, START
import os
from astrapy import DataAPIClient
from astrapy.constants import VectorMetric

# Initialize the client and get a "Database" object
client = DataAPIClient(os.environ["ASTRA_DB_TOKEN"])
database = client.get_database(os.environ["ASTRA_DB_API_ENDPOINT"])
print(f"* Database: {database.info().name}\n")

# Define the list of JSON objects
json = {
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





class ScriptState(TypedDict):
    current_id: int
    topic: str
    current_paragraph: str
    end: bool

class ScriptGraph:
    def __init__(self, json: Dict):
        self.json = json
        self.compiled_graph = self.compile_graph()

    def custom_node(self, state: ScriptState) -> Dict[str, Any]:
        print(f"Input state: {state}")  # Debug print
        new_state = state.copy()
        new_state['current_id'] += 1
        script = self.json['content']['script']
        
        if new_state['current_id'] < len(script):
            new_state['current_paragraph'] = script[new_state['current_id']]['paragraph']
            new_state['end'] = False
        else:
            new_state['current_paragraph'] = ""
            new_state['end'] = True

        # Ensure 'topic' is always present
        new_state['topic'] = new_state.get('topic', self.json['topic'])
        
        print(f"Output state: {new_state}")  # Debug print
        return new_state

    def compile_graph(self):
        workflow = StateGraph(ScriptState)

        workflow.add_node("custom", self.custom_node)
        workflow.set_entry_point("custom")

        def router(state: ScriptState):
            return END if state['end'] else "custom"

        workflow.add_conditional_edges(
            "custom",
            router,
            {
                "custom": "custom",
                END: END
            }
        )

        return workflow.compile()

    def run(self, resume_state: ScriptState = None) -> Generator[ScriptState, None, None]:
        initial_state = resume_state or {
            "current_id": -1,
            "topic": self.json['topic'],
            "current_paragraph": "",
            "end": False
        }
        print(f"Initial state: {initial_state}")  # Debug print

        for output in self.compiled_graph.stream(initial_state, {"recursion_limit": 100}):
            if output == END:
                break
            if isinstance(output, dict) and 'custom' in output:
                yield output['custom']  # Yield the state directly, without the 'custom' wrapper
            else:
                yield output

# Global variable to store the current state of the script
current_script_state = None

def script_chain(input_str: str) -> Dict[str, Any]:
    global current_script_state
    script_graph = ScriptGraph(json)
    
    if current_script_state is None or current_script_state.get('end', True):
        state_generator = script_graph.run()
    else:
        state_generator = script_graph.run(current_script_state)
    
    try:
        state = next(state_generator)
        print(f"State in script_chain: {state}")  # Debug print
        if isinstance(state, dict) and 'custom' in state:
            state = state['custom']  # Extract the actual state from the 'custom' key
        current_script_state = state
        return {
            "messages": [{
                "content": f"Topic: {state.get('topic', 'No topic')}\nParagraph: {state.get('current_paragraph', 'No paragraph')}",
                "type": "assistant"
            }]
        }
    except StopIteration:
        current_script_state = None
        return {
            "messages": [{
                "content": "Script has ended.",
                "type": "assistant"
            }]
        }

# Usage example
if __name__ == "__main__":
    for _ in range(5):  # Get the first 5 paragraphs
        try:
            result = script_chain("")
            print(result['messages'][0]['content'])
        except Exception as e:
            print(f"An error occurred: {e}")
        print("---")