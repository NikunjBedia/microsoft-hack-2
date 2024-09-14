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
                The script should be structured as a JSON array. Each element in the array should be an object with the following fields:
        - "paragraph": A coherent chunk of the script.
        - "pause": A description of a meaningful pause or transition.

        Ensure the JSON is properly formatted.
        
Content:
{combined_content}

Please generate a script that:
1. Introduces the topic
2. Explains the main concepts and ideas related to the section mentioned in the text
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
        # Retrieve all documents from the vector store
        all_docs = self.vector_store.similarity_search("large font size", k=10000)

        # Filter and sort documents by font size in descending order
        sorted_docs = sorted(
            [doc for doc in all_docs if doc.metadata.get("font_size") is not None],
            key=lambda x: x.metadata["font_size"],
            reverse=True
        )

        # Limit to the top 20 documents
        top_docs = sorted_docs[:20]

        # Extract unique headings with their levels
        headings = set()
        for doc in top_docs:
            headings.add((doc.metadata["font_size"],doc.page_content))
        topics =sorted(list(headings),key=lambda x: x[0], reverse=True)
        return [i[1] for i in topics]
        