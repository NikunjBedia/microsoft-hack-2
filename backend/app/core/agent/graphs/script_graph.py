import json
from typing import List, Dict, Any, TypedDict, Generator
from langgraph.graph import END, StateGraph, START

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

class ScriptState(TypedDict, total=False):
    topic: str
    script_index: int
    current_paragraph: str
    end: bool

class ScriptGraph:
    def __init__(self, json: Dict):
        self.json = json
        self.compiled_graph = self.compile_graph()

    def custom_node(self, state: ScriptState) -> Dict[str, Any]:
        print("Entering custom_node")
        print(f"Initial state: {state}")

        new_state = state.copy()  # Create a new state object

        if 'topic' not in new_state or not new_state['topic']:
            new_state['topic'] = self.json['topic']
            print(f"Updated topic: {new_state['topic']}")

        if 'script_index' not in new_state:
            new_state['script_index'] = -1
            print("Initialized script_index to -1")

        script = self.json['content']['script']
        
        # Increment the index before fetching the paragraph
        new_state['script_index'] += 1
        print(f"Incremented script_index to {new_state['script_index']}")

        if new_state['script_index'] < len(script):
            new_state['current_paragraph'] = script[new_state['script_index']]['paragraph']
            new_state['end'] = False
            print(f"Updated paragraph: {new_state['current_paragraph'][:50]}...")
        else:
            new_state['current_paragraph'] = ""
            new_state['end'] = True
            print("Reached end of script")

        result = {k: v for k, v in new_state.items() if k in ['topic', 'script_index', 'current_paragraph', 'end']}
        print(f"Returning: {result}")
        print("Exiting custom_node")
        return result

        # # Update the input state
        # if 'topic' not in state or not state['topic']:
        #     state['topic'] = self.json['topic']
        
        # if 'script_index' not in state:
        #     state['script_index'] = -1
        
        # state['script_index'] += 1

        # script = self.json['content']['script']
        
        # if state['script_index'] < len(script):
        #     state['current_paragraph'] = script[state['script_index']]['paragraph']
        #     state['end'] = False
        # else:
        #     state['current_paragraph'] = ""
        #     state['end'] = True

        # # Create and return a new state with updates
        # return {
        #     'topic': state['topic'],
        #     'script_index': state['script_index'],
        #     'current_paragraph': state['current_paragraph'],
        #     'end': state['end']
        # }

    def compile_graph(self):
        workflow = StateGraph(ScriptState)

        workflow.add_node("custom", self.custom_node)
        workflow.set_entry_point("custom")

        def router(state: ScriptState):
            return END if state.get('end', False) else "custom"

        workflow.add_conditional_edges(
            "custom",
            router,
            {
                "custom": "custom",
                END: END
            }
        )

        return workflow.compile()

    def run(self, resume_state=None):
        initial_state: ScriptState = resume_state or {
            "topic": "",
            "script_index": -1,
            "current_paragraph": "",
            "end": False
        }

        for output in self.compiled_graph.stream(initial_state, {"recursion_limit": 100}):
            if output == END:
                break
            yield output

# Usage example
if __name__ == "__main__":
    script_graph = ScriptGraph(json)
    
    for state in script_graph.run():
        print(f"Topic: {state.get('topic', 'No topic')}")
        print(f"Index: {state.get('script_index', -1)}")
        print(f"Paragraph: {state.get('current_paragraph', 'No paragraph')}")
        print("---")
    print("Script graph finished.")


