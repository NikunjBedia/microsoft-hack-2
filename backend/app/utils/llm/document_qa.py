import json
from app.utils.vector_store.vector_store import VectorStore
from app.utils.llm.gemini_llm import LLM

class DocumentQA:
    def __init__(self, vector_store: VectorStore, llm: LLM):
        self.vector_store = vector_store
        self.llm = llm
    def get_topic_content(self, topic: str):
        relevant_docs = self.vector_store.similarity_search(topic, k=1000)

        # Combine the content of relevant documents
        combined_content = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Prepare the prompt for the LLM
        prompt = f"""Based on the following content related to the section heading "{topic}", provide a detailed script describing the key points and information surrounding this section as a personal teacher explaining the content to a student.
                The script should be structured as a JSON array. Each element in the array should be an object that has the infromation of sub section like(1 Country - topic, 1.1 State -section, 1.1.1 City -sub section). with the following fields:
        - "paragraph": A coherent chunk of the script.
        - "pause": A description of a meaningful pause or transition.

        Ensure the JSON is properly formatted.
        
Content:
{combined_content}

Please generate a script that:
1. Introduces the topic
2. Clear indepth explanation of the topic divided subsection wise(subsections should represent json item)
4. Summarizes the key takeaways
5.Don't hallucinate and Content should be the source of truth. Don't make stuff up.
6. Generates a structured script in JSON format for the given topic.


Script:"""

        # Generate response using the LLM
        response = self.llm.generate_response(prompt)

        # Extract the content from the AIMessage object
        script = response.content if hasattr(response, 'content') else str(response)
        script=script.strip().replace('```json', '').replace('```', '')
        try:
            # Parse the JSON response
            script_json = json.loads(script)
            
            # Validate that it's a list of dictionaries
            if isinstance(script_json, list) and all(isinstance(item, dict) for item in script_json):
                return script_json
            else:
                raise ValueError("The response is not a valid JSON array of objects.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}") from e
        
        return script
    def get_topics(self):
        """
        Uses the LLM to fetch topics (chapters) from the vector store.
        """
        # Retrieve all documents from the vector store
        all_docs = self.vector_store.similarity_search("table of contents", k=10000)

        # Combine the content of all documents
        combined_content = "\n\n".join([doc.page_content for doc in all_docs])

        # Prepare the prompt for the LLM to extract chapters
        prompt = f"""
        Based on the following content, extract the chapters of the textbook. The chapters should be listed in order and each chapter should be a single line and include only the chapter name for example Chapter 1: Himalayas, Chapter 2: Indian Ocean.

        Content:
        {combined_content}

        Chapters:
        """

        # Generate response using the LLM
        response = self.llm.generate_response(prompt)

        # Extract the content from the response object
        chapters_text = response.content if hasattr(response, 'content') else str(response)

        # Split the chapters into a list
        chapters = [line.strip() for line in chapters_text.split('\n') if line.strip()]

        return chapters
        