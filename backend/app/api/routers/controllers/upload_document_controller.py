from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.core.upload_document import UploadDocument
from app.utils.pdf_parser.pdf_parser import PdfParser
from app.utils.vector_store.vector_store import VectorStore
from app.utils.llm.document_qa import DocumentQA
from app.utils.llm.gemini_llm import LLM
import io

upload_documents_router = APIRouter()

@upload_documents_router.post("",status_code=201)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Read the file as a stream
        pdf_stream = await file.read()  

        topics = UploadDocument().generate_topics(pdf_stream)
        return topics


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

