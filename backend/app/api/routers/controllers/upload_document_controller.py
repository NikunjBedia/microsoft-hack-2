from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List

upload_documents_router = APIRouter()

@router.post("")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload multiple documents.
    """
    uploaded_files = []
    for file in files:
        try:
            # Perform your file handling here
            content = await file.read()
            # Save file or process content
            uploaded_files.append(file.filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {e}")
    return {"filenames": uploaded_files}
