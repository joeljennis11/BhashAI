"""
BhashAI Response Models
Defines Pydantic schemas for all outgoing API responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TranscribeResponse(BaseModel):
    text: str
    language: str = "hin_Deva"
    duration_seconds: Optional[float] = None
    confidence: Optional[float] = None


class TranslationResponse(BaseModel):
    translation: str
    source_language: str = "hin_Deva"
    target_language: str = "sat_Olck"
    review_required: bool = False
    issues: List[str] = Field(default_factory=list)
    context_applied: bool = False
    detected_topic: Optional[str] = None
    audio_url: Optional[str] = None
    phonetic_text: Optional[str] = None


class VoiceTranslationResponse(BaseModel):
    source_text: str
    translation: str
    audio_url: str
    source_language: str = "hin_Deva"
    target_language: str = "sat_Olck"
    review_required: bool = False
    issues: List[str] = Field(default_factory=list)
    asr_latency: float
    translation_latency: float
    tts_latency: float
    total_latency: float
    phonetic_text: Optional[str] = None


class TTSResponse(BaseModel):
    audio_url: str
    duration_seconds: float
    sample_rate: int
    channels: int
    cached: bool
    phonetic_text: Optional[str] = None


class EducationalContent(BaseModel):
    title: str
    grade: int
    subject: str
    topic: str
    learning_objective: str
    vocabulary: List[Dict[str, str]] = Field(default_factory=list)
    instructions: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)
    source_document: Optional[str] = None
    total_pages: int = 1


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    extracted_text_length: int
    content: EducationalContent
    offline_cached: bool = True


class WorksheetQuestion(BaseModel):
    id: int
    question_type: str
    hindi_prompt: str
    santali_prompt: str
    phonetic_prompt: Optional[str] = None
    options_hindi: Optional[List[str]] = None
    options_santali: Optional[List[str]] = None
    answer_hindi: str
    answer_santali: str
    phonetic_answer: Optional[str] = None
    source_reference: Optional[str] = None
    audio_url: Optional[str] = None


class WorksheetResponse(BaseModel):
    worksheet_id: str
    title: str
    grade: int
    subject: str
    topic: str
    language: str
    target_language: str
    status: str = "DRAFT"  # DRAFT, REVIEWED, APPROVED
    questions: List[WorksheetQuestion]
    created_at: str
    student_pdf_url: Optional[str] = None
    answer_key_pdf_url: Optional[str] = None


class FlashcardItem(BaseModel):
    id: int
    hindi_word: str
    santali_word: str
    phonetic: Optional[str] = None
    concept: str
    icon: str
    example_hindi: Optional[str] = None
    example_santali: Optional[str] = None
    audio_url: Optional[str] = None


class FlashcardsResponse(BaseModel):
    lesson_id: str
    topic: str
    total_cards: int
    cards: List[FlashcardItem]


class ModelStatusItem(BaseModel):
    name: str
    type: str  # asr, translation, tts
    installed: bool
    size_mb: float
    path: Optional[str] = None
    in_memory: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str
    offline_mode: bool
    models: Dict[str, ModelStatusItem]
    memory: Dict[str, Any]
