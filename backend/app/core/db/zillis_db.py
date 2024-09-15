# vector_db/vector_db.py

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter # Import the ZillizDB class
from langchain_voyageai import VoyageAIEmbeddings
from dotenv import load_dotenv, dotenv_values 
import os
load_dotenv() 

# Initialize your embedding model and vector store
embedding_model = VoyageAIEmbeddings(api_key="your_voyage_ai_api_key", model="voyage-law-2")  # Replace with your actual API key if needed
docs = []
vector_store = Milvus.from_documents(
    docs,
    embedding_model,
    connection_args={
        "uri": "https://in03-978b6940b3a2c78.serverless.gcp-us-west1.cloud.zilliz.com",
        "token": "a1c3f12bfd5a43281bc258f57c2dae7ebe581c0409baf6f19bd353ae06c6ab8c230a266ba5887cde9b193d588f875791c230e6df",  # API key, for serverless clusters which can be used as replacements for user and password
        "secure": True,
    },
)
def add_vector_to_db(text: str, metadata: dict):
    """
    Add a text vector to the ZillizDB database.
    """
    vector = embedding_model.embed(text)
    vector_store.add_vector(vector, metadata)

def search_vectors(query: str, top_k: int):
    """
    Search for similar vectors in the ZillizDB database.
    """
    query_vector = embedding_model.embed(query)
    results = vector_store.search_vectors(query_vector, top_k)
    return results

def get_current_script_marker():
    """
    Get the current script marker from the ZillizDB database.
    """
    results = vector_store.search_vectors("current_script_marker", 1)
    return results[0] if results else None
    