# vector_db/vector_db.py

from langchain.vectorstores.lancedb import LanceDB  # Import the LanceDB class
from langchain.embeddings.voyage import VoyageAI  # Import the Voyage AI class
from dotenv import load_dotenv, dotenv_values 
import os
load_dotenv() 
 
# accessing and printing value
print(os.getenv("MY_KEY"))
# Initialize your embedding model and vector store
embedding_model = VoyageAI(api_key="your_voyage_ai_api_key")  # Replace with your actual API key if needed
vector_store = LanceDB(
    uri=db_url,
    api_key=os.getenv("ZILLIZ_API_KEY"),
    region=region,
    embedding=embeddings,
    table_name='langchain_test'
    )
def add_vector_to_db(text: str, metadata: dict):
    """
    Add a text vector to the LanceDB database.
    """
    vector = embedding_model.embed(text)
    vector_store.add_vector(vector, metadata)

def search_vectors(query: str, top_k: int):
    """
    Search for similar vectors in the LanceDB database.
    """
    query_vector = embedding_model.embed(query)
    results = vector_store.search_vectors(query_vector, top_k)
    return results
