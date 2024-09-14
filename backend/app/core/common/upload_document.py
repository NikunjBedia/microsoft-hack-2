
from app.utils.vector_store.vector_store import VectorStore
from app.utils.llm.gemini_llm import LLM
from app.utils.llm.document_qa import DocumentQA
from app.utils.pdf_parser.pdf_parser import PdfParser


class UploadDocument:
    def __init__(self):
        self.vector_store = VectorStore()
        self.vector_store = self.vector_store.create_vector_store()
        self.llm = LLM()
        self.document_qa = DocumentQA(self.vector_store, self.llm)

    def generate_topics(self, pdf_stream: str):
        processor = PdfParser()

        processed_docs = processor.process_pdf_stream(pdf_stream)

        # Create or update vector store
        vector_store = VectorStore()
        vector_store = vector_store.create_vector_store()
        vector_store.add_documents(processed_docs[:600])
        llm = LLM()
        document_qa = DocumentQA(vector_store,llm)
        topics = document_qa.get_topics()
        return topics
