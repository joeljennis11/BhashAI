"""
BhashAI Worksheets Route
Handles vernacular worksheet generation, teacher review updates, and PDF exports.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
from pathlib import Path

from backend.models.request_models import WorksheetGenerateRequest, WorksheetUpdateRequest
from backend.models.response_models import WorksheetResponse
from backend.services.worksheet_generator import WorksheetGenerator
from backend.services.document_processor import DocumentProcessor

router = APIRouter(prefix="/api/worksheets", tags=["Worksheets"])


@router.post("/generate", response_model=WorksheetResponse)
async def generate_worksheet(request: WorksheetGenerateRequest):
    """
    Generates a new source-grounded bilingual FLN worksheet (initial status: DRAFT).
    """
    try:
        doc_proc = DocumentProcessor.get_instance()
        generator = WorksheetGenerator.get_instance()

        if request.lesson_id:
            doc = doc_proc.get_document(request.lesson_id)
            if not doc:
                raise HTTPException(status_code=404, detail="Referenced lesson_id not found.")
            edu_content = doc["content"]
        elif request.lesson_text or request.topic:
            # Topic vocabulary dictionary
            topic_vocab_dict = {
                "फल": ["आम", "सेब", "केला", "अंगूर", "संतरा", "अमरूद"],
                "fruits": ["आम", "सेब", "केला", "अंगूर", "संतरा", "अमरूद"],
                "संख्याएँ": ["एक", "दो", "तीन", "चार", "पाँच"],
                "numbers": ["एक", "दो", "तीन", "चार", "पाँच"],
                "पशु": ["गाय", "बकरी", "पेड़", "पत्ता", "दूध"],
                "animals": ["गाय", "बकरी", "पेड़", "पत्ता", "दूध"],
                "प्रकृति": ["पेड़", "पत्ता", "फूल", "घास", "नदी"],
                "nature": ["पेड़", "पत्ता", "फूल", "घास", "नदी"],
                "कक्षा": ["किताब", "कलम", "कापी", "मित्र", "नाम"],
                "classroom": ["किताब", "कलम", "कापी", "मित्र", "नाम"],
            }

            topic_key = (request.topic or "").lower()
            matching_words = []
            for k, words in topic_vocab_dict.items():
                if k in topic_key:
                    matching_words = words
                    break

            if request.lesson_text:
                extracted_words = request.lesson_text.split()
            elif matching_words:
                extracted_words = matching_words
            else:
                extracted_words = ["आम", "सेब", "केला", "पेड़", "पत्ता", "किताब"]

            edu_content = {
                "title": f"कक्षा {request.grade} अभ्यास पत्रक: {request.topic or 'बुनियादी साक्षरता'}",
                "grade": request.grade,
                "subject": request.subject,
                "topic": request.topic or "FLN अभ्यास",
                "vocabulary": [{"word_hindi": w} for w in extracted_words[:request.num_questions]],
                "source_document": f"Topic: {request.topic or 'Classroom FLN'}"
            }
        else:
            raise HTTPException(status_code=400, detail="Must provide either lesson_id, lesson_text, or topic.")


        ws_data = generator.generate_worksheet(
            educational_content=edu_content,
            worksheet_type=request.worksheet_type,
            num_questions=request.num_questions,
            grade=request.grade,
            subject=request.subject
        )

        return WorksheetResponse(**ws_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Worksheet generation error: {str(e)}")


@router.get("/{worksheet_id}", response_model=WorksheetResponse)
async def get_worksheet(worksheet_id: str):
    """Retrieves generated worksheet data by ID."""
    ws = WorksheetGenerator.get_instance().get_worksheet(worksheet_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Worksheet not found.")
    return WorksheetResponse(**ws)


@router.put("/{worksheet_id}", response_model=WorksheetResponse)
async def update_worksheet(worksheet_id: str, request: WorksheetUpdateRequest):
    """
    Teacher review endpoint: update questions, edit prompts/answers, approve worksheet.
    Status can transition: DRAFT -> REVIEWED -> APPROVED.
    """
    try:
        generator = WorksheetGenerator.get_instance()
        updates = request.model_dump(exclude_unset=True)
        updated_ws = generator.update_worksheet(worksheet_id, updates)
        return WorksheetResponse(**updated_ws)
    except KeyError:
        raise HTTPException(status_code=404, detail="Worksheet not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Worksheet update error: {str(e)}")


@router.get("/{worksheet_id}/export")
async def export_worksheet_pdf(
    worksheet_id: str,
    type: str = Query(default="student", description="student or answer_key"),
    mode: str = Query(default="bilingual", description="hindi, santali, or bilingual")
):
    """
    Exports and streams printable A4 PDF worksheet for classroom distribution.
    """
    try:
        generator = WorksheetGenerator.get_instance()
        is_answer_key = (type.lower() == "answer_key")
        pdf_path = generator.export_pdf(
            worksheet_id=worksheet_id,
            export_mode=mode.lower(),
            is_answer_key=is_answer_key
        )

        filename = Path(pdf_path).name
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=filename
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Worksheet not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export error: {str(e)}")
