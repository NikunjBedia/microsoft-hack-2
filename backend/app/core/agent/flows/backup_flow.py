import os
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import uvicorn
app = FastAPI()

class Script:
    def __init__(self, script_data: List[Dict]):
        self.script_data = script_data
        self.current_index = 0

    def get_next(self):
        if self.current_index < len(self.script_data):
            item = self.script_data[self.current_index]
            self.current_index += 1
            return item
        return None

class BackupFlow:
    def __init__(self, script_data: List[Dict]):
        self.script = Script(script_data)
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY")
        )


    async def script_generation(self):
        while True:
            item = self.script.get_next()
            if item is None:
                break
            yield item
            await asyncio.sleep(1)  # Simulate processing time

    async def question_answer(self, query: str):
        prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="Answer the following question based on the context:\nQuestion: {query}\nContext: {context}\nAnswer:"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt, callbacks=None)
        context = str(self.script.script_data)  # Simplification: using entire script as context
        return await chain.arun(query=query, context=context)

    async def supervising(self, user_query: str = None):
        script_gen = self.script_generation()
        try:
            while True:
                if user_query:
                    answer = await self.question_answer(user_query)
                    yield {"type": "answer", "content": answer}
                    user_query = None
                else:
                    script_item = await anext(script_gen)
                    yield {"type": "script", "content": script_item}
        except StopAsyncIteration:
            pass

class UserQuery(BaseModel):
    query: str

@app.post("/backup_flow")
async def run_backup_flow(script_data: List[Dict]):
    flow = BackupFlow(script_data)
    return {"message": "Backup flow initialized"}

@app.post("/user_query")
async def handle_user_query(user_query: UserQuery):
    # Assuming flow is initialized and stored somewhere accessible
    if not hasattr(app, "flow"):
        raise HTTPException(status_code=400, detail="Backup flow not initialized")
    
    result = await app.flow.question_answer(user_query.query)
    return {"answer": result}

# Initialize the flow when the app starts
@app.on_event("startup")
async def startup_event():
    # Example script data
    script_data = [
        {
            "index": 0,
            "content": "Hello! Today we're diving into Chapter 5: Conservation of Resources. This chapter is all about understanding how we use and manage the resources available to us, and why it's so important to do it sustainably.",
            "pause": "Let's take a moment to think about what resources are."
        },
        {
            "index": 1,
            "content": "Resources are everything we need to survive and thrive. They include things like land, water, forests, minerals, and even the air we breathe.  These resources are vital for our existence, and without them, we wouldn't be able to live.",
            "pause": "But here's the catch: resources aren't infinite."
        },
        {
            "index": 2,
            "content": "We've been using resources for a long time, and sometimes we use them faster than they can be replenished. This can lead to problems like resource depletion, pollution, and even conflict. That's why conservation is so important.",
            "pause": "Let's break down the key concepts of resource conservation."
        },
        {
            "index": 3,
            "content": "Resource conservation is all about using resources wisely and responsibly. It's about making sure we have enough for ourselves and future generations.  There are many ways to conserve resources, like reducing our consumption, recycling, and using renewable energy sources.",
            "pause": "Now, let's talk about resource planning."
        },
        {
            "index": 4,
            "content": "Resource planning is a crucial part of conservation. It involves making decisions about how we use our resources, taking into account both our current needs and the needs of future generations.  This planning process helps us to avoid over-exploitation and ensure that resources are used sustainably.",
            "pause": "Let's look at how resource planning works in India."
        }
    ]
    app.flow = BackupFlow(script_data)

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
