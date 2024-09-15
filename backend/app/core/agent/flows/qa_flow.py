import os
from langchain_core.tools import tool
from langchain_groq import ChatGroq
# from app.core.db.zillis_db import vector_store, embedding_model

@tool
def section_search(query: str, conversation_history: list, current_script: str):
    """
    Search for a section in the script based on the query using KNNSimilaritySearch with Zilliz DB and VoyageAI embeddings.
    """
    # Embed the query using VoyageAI embeddings
    # query_embedding = embedding_model.embed_query(query)
    
    # Perform KNN similarity search using Zilliz DB
    # results = vector_store.similarity_search_by_vector(query_embedding, k=5)
    
    # Process and return the results
    # sections = [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]
    sections = [{"content": "First, we'll talk about the *East India Company*. This company was originally a trading company, but it gradually gained political power and eventually became the dominant force in India.", "metadata": {}}]
    return sections

@tool
def create_greeting(query: str, conversation_history: list, current_script: str):
    """
    Create a greeting based on the query, conversation history, and current script using an LLM.
    """
    # Initialize the LLM
    llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # Prepare the context for the LLM
    context = f"""
    Conversation history: {conversation_history}
    Current script: {current_script}
    User query: {query}
    """

    # Generate a greeting based on the query, conversation history, and current script
    prompt = f"""
    Based on the following context, generate a friendly and contextually appropriate greeting:

    {context}

    The greeting should acknowledge any relevant information from the conversation history
    and current script, if applicable. Make sure the greeting is welcoming and sets a positive tone for the interaction.
    """

    response = llm.invoke(prompt)

    return response.content

@tool
def clarify_question(query: str, conversation_history: list, current_script: str):
    """
    Clarify the question based on the query, conversation history, and current script using an LLM.
    """
    # Initialize the LLM
    llm = ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # Prepare the context for the LLM
    context = f"""
    Conversation history: {conversation_history}
    Current script: {current_script}
    User query: {query}
    """

    # Generate a clarification prompt
    prompt = f"""
    Based on the following context, please clarify what the user is having a doubt about:

    {context}

    Provide a clear and concise clarification of the user's question or doubt.
    """

    # Generate the clarification
    response = llm.invoke(prompt)

    return response.content