from app.core.db.mongo_db import MongoDB
from app.utils.llm.document_qa import DocumentQA
from app.utils.llm.gemini_llm import LLM
from app.utils.vector_store.vector_store import VectorStore

class FetchTopicContent:
    def __init__(self):
        self.vector_store = VectorStore()
        self.vector_store = self.vector_store.create_vector_store()
        self.llm = LLM()
        self.document_qa = DocumentQA(self.vector_store, self.llm)
        self.db = MongoDB()
        self.db.connect()

    def fetch_topic_content(self, topic: str):
        script = self.document_qa.get_topic_content(topic)
        session_id = self.db.upload_json_with_session(script)
        resp ={
            "session_id": session_id,
            "script" : script
        }
        return resp