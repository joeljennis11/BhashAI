"""
BhashAI Request Models
Defines Pydantic schemas for all incoming API requests.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TranscribeRequest(BaseModel):
    language: str = Field(default="hin_Deva", description="Source spoken language code")


class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate", min_length=1)
    source_language: str = Field(default="hin_Deva", description="Source FLORES language code")
    target_language: str = Field(default="sat_Olck", description="Target FLORES language code")
    context: List[str] = Field(default_factory=list, description="Recent conversation / lesson context sentences")
    lesson_topic: Optional[str] = Field(default=None, description="Current FLN lesson topic (e.g. 'Fruits', 'Numbers')")


class TTSRequest(BaseModel):
    text: str = Field(..., description="Santali Ol Chiki text to synthesize into audio", min_length=1)
    language: str = Field(default="sat_Olck", description="Target language code")
    voice_id: Optional[str] = Field(default="santali_v1", description="Voice profile identifier")


class ContextUpdateRequest(BaseModel):
    sentence: str = Field(..., description="Sentence to add to context buffer")
    translation: Optional[str] = Field(default=None, description="Santali translation to associate")
    topic: Optional[str] = Field(default=None, description="Topic or lesson theme")


class WorksheetGenerateRequest(BaseModel):
    lesson_id: Optional[str] = Field(default=None, description="ID of previously processed lesson")
    lesson_text: Optional[str] = Field(default=None, description="Raw lesson text if generating directly")
    grade: int = Field(default=1, ge=1, le=8, description="Class / Grade level (1 to 5 for FLN)")
    subject: str = Field(default="Foundational Literacy", description="Subject area")
    topic: Optional[str] = Field(default="FLN Lesson", description="Topic title")
    language: str = Field(default="hin_Deva", description="Source language")
    target_language: str = Field(default="sat_Olck", description="Target vernacular language")
    worksheet_type: str = Field(default="Mixed", description="Worksheet question pattern: FillInTheBlanks, Match, MCQ, TrueFalse, PictureID, CountWrite, Vocabulary, OralPractice, Mixed")
    num_questions: int = Field(default=5, ge=1, le=25, description="Number of questions to generate")
    difficulty: str = Field(default="Easy", description="Easy, Medium, Hard")


class WorksheetQuestionUpdate(BaseModel):
    id: int
    question_type: str
    hindi_prompt: str
    santali_prompt: str
    options_hindi: Optional[List[str]] = None
    options_santali: Optional[List[str]] = None
    answer_hindi: str
    answer_santali: str
    source_reference: Optional[str] = None


class WorksheetUpdateRequest(BaseModel):
    title: Optional[str] = None
    status: str = Field(default="REVIEWED", description="DRAFT, REVIEWED, APPROVED")
    questions: Optional[List[WorksheetQuestionUpdate]] = None
    teacher_notes: Optional[str] = None
