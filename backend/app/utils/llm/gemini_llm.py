from langchain_google_genai import ChatGoogleGenerativeAI
import os
import asyncio

class LLM:
    def __init__(self):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # other params...
        )

    async def generate_response(self, prompt):
        # Run the synchronous invoke method in a separate thread
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.llm.invoke, prompt)