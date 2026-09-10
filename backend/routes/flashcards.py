"""
BhashAI Flashcards Route
Provides bilingual visual flashcards with Ol Chiki script and audio playback.
"""

from fastapi import APIRouter, HTTPException
from backend.models.response_models import FlashcardsResponse, FlashcardItem
from backend.services.document_processor import DocumentProcessor
from backend.services.flashcard_generator import FlashcardGenerator

router = APIRouter(prefix="/api/flashcards", tags=["Flashcards"])


@router.get("/default", response_model=FlashcardsResponse)
async def get_default_flashcards():
    """
    Retrieves starter vocabulary flashcards across classroom categories.
    """
    generator = FlashcardGenerator.get_instance()
    cards = generator.get_default_flashcards()

    return FlashcardsResponse(
        lesson_id="default_fln",
        topic="Classroom FLN Vocabulary",
        total_cards=len(cards),
        cards=[FlashcardItem(**c) for c in cards]
    )


@router.get("/lesson/{doc_id}", response_model=FlashcardsResponse)
async def get_lesson_flashcards(doc_id: str):
    """
    Retrieves visual flashcards derived from the uploaded educational document.
    """
    doc_proc = DocumentProcessor.get_instance()
    doc = doc_proc.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Referenced lesson_id not found.")

    edu_content = doc["content"]
    generator = FlashcardGenerator.get_instance()
    cards = generator.generate_flashcards(edu_content)

    return FlashcardsResponse(
        lesson_id=doc_id,
        topic=edu_content.get("topic", "FLN Lesson"),
        total_cards=len(cards),
        cards=[FlashcardItem(**c) for c in cards]
    )

