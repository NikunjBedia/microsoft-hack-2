from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_astradb import AstraDBVectorStore
from astrapy.info import CollectionVectorServiceOptions

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
    def add_documents(self, docs):
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")

        # Split the documents into chunks of 10
        doc_chunks = [docs[i:i + 10] for i in range(0, len(docs), 10)]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for chunk in doc_chunks:
                future = executor.submit(self._add_document_chunk, chunk)
                futures.append(future)

            # Wait for all futures to complete
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.extend(result)
                except Exception as e:
                    print(f"An error occurred while adding documents: {str(e)}")

        return results

    def _add_document_chunk(self, chunk):
        return self.vector_store.add_documents(documents=chunk)


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