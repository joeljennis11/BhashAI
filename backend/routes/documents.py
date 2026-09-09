"""
BhashAI Documents Route
Handles educational PDF upload and pedagogical content extraction.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.response_models import DocumentUploadResponse, EducationalContent
from backend.services.document_processor import DocumentProcessor

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads a classroom educational material (PDF), extracts text, and parses structured FLN topics.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF educational materials are supported in V1.")

    try:
        content_bytes = await file.read()
        if not content_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        processor = DocumentProcessor.get_instance()
        doc_result = processor.process_pdf(content_bytes, filename=file.filename)

        return DocumentUploadResponse(
            document_id=doc_result["document_id"],
            filename=doc_result["filename"],
            extracted_text_length=doc_result["extracted_text_length"],
            content=EducationalContent(**doc_result["content"]),
            offline_cached=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing error: {str(e)}")


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """Retrieves processed document content by ID."""
    doc = DocumentProcessor.get_instance().get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc
