from langchain_astradb import AstraDBVectorStore
from astrapy.info import CollectionVectorServiceOptions


from app.utils.vector_store.embeddings import Embeddings
import os
class VectorStore:
    def __init__(self):
        self.api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.token = os.getenv("ASTRA_DB_TOKEN")
    def create_vector_store(self):

        service=CollectionVectorServiceOptions(
        provider="nvidia",
        model_name="NV-Embed-QA",
    )
        self.vector_store = AstraDBVectorStore(
            collection_name="curio_collection",
            api_endpoint=self.api_endpoint,
            token=self.token,
            collection_vector_service_options=  service 
        )


        return self.vector_store
    def add_documents(self,docs):
        
        return self.vector_store.add_documents(documents=docs)


    def add_texts(self, texts):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")
        return self.vector_store.add_texts(texts)

    def delete(self, ids):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")
        return self.vector_store.delete(ids)

    def get_relevant_documents(self, query):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")
        return self.vector_store.get_relevant_documents(query)