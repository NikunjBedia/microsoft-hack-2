from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.utils.pdf_parser.pdf_parser import PdfParser
from app.utils.vector_store.vector_store import VectorStore
from app.utils.llm.document_qa import DocumentQA
from app.utils.llm.gemini_llm import LLM
import io

upload_documents_router = APIRouter()

@upload_documents_router.post("")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Read the file as a stream
        pdf_stream = await file.read()  

        # Process the PDF stream
        processor = PdfParser()
        processed_docs = processor.process_pdf_stream(pdf_stream)

        # Create or update vector store
        vector_store = VectorStore()
        vector_store = vector_store.create_vector_store()
        #vector_store.add_documents(processed_docs)
        llm = LLM()
        document_qa = DocumentQA(vector_store,llm)
        topics = document_qa.get_topics()
        print(topics,"8")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
async def get_topic_content(self, topic: str):
        # Retrieve relevant documents from the vector store
        relevant_docs = self.vector_store.similarity_search(topic, k=5)

        # Combine the content of relevant documents
        combined_content = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Prepare the prompt for the LLM
        prompt = f"""Based on the following content related to the topic "{topic}", provide a detailed script describing the key points and information surrounding this topic.
        
Content:
{combined_content}

Please generate a script that:
1. Introduces the topic
2. Explains the main concepts and ideas related to the topic
3. Provides any relevant examples or applications
4. Summarizes the key takeaways

Script:"""

        # Generate response using the LLM
        response = self.llm.generate_response(prompt)
        script = response.content if hasattr(response, 'content') else str(response)

        return script
        # Extract the content from the AI
