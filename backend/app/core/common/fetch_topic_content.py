from app.core.db.mongo_db import MongoDB
from app.utils.llm.document_qa import DocumentQA
from app.utils.llm.gemini_llm import LLM
from app.utils.vector_store.vector_store import VectorStore

class FetchTopicContent:
    def __init__(self):
        self.vector_store = None
        self.llm = None
        self.document_qa = None
        self.db = None

    async def initialize(self):
        self.vector_store = VectorStore()
        self.vector_store = self.vector_store.create_vector_store()
        self.llm = LLM()
        self.document_qa = DocumentQA(self.vector_store, self.llm)
        self.db = MongoDB()
        await self.db.connect()

    async def fetch_topic_content(self, topic: str):
        if not self.document_qa:
            await self.initialize()
        
        script = await self.document_qa.get_topic_content(topic)
        #session_id = await self.db.upload_json_with_session(script)
        resp = {
            "session_id": "session_id",
            "script": script
        }
        return resp