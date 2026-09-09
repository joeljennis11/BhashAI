package com.bhashai.app.data.model

import com.google.gson.annotations.SerializedName

data class TranslationRequestDto(
    @SerializedName("text") val text: String,
    @SerializedName("source_language") val sourceLanguage: String = "hin_Deva",
    @SerializedName("target_language") val targetLanguage: String = "sat_Olck",
    @SerializedName("context") val context: List<String> = emptyList(),
    @SerializedName("lesson_topic") val lessonTopic: String? = null
)

data class TranslationResponseDto(
    @SerializedName("translation") val translation: String,
    @SerializedName("source_language") val sourceLanguage: String,
    @SerializedName("target_language") val targetLanguage: String,
    @SerializedName("review_required") val reviewRequired: Boolean = false,
    @SerializedName("issues") val issues: List<String> = emptyList(),
    @SerializedName("context_applied") val contextApplied: Boolean = false,
    @SerializedName("audio_url") val audioUrl: String? = null
)

data class VoiceTranslationResponseDto(
    @SerializedName("source_text") val sourceText: String,
    @SerializedName("translation") val translation: String,
    @SerializedName("audio_url") val audioUrl: String,
    @SerializedName("review_required") val reviewRequired: Boolean = false,
    @SerializedName("total_latency") val totalLatency: Float = 0f
)

data class TTSRequestDto(
    @SerializedName("text") val text: String,
    @SerializedName("language") val language: String = "sat_Olck",
    @SerializedName("voice_id") val voiceId: String? = "santali_v1"
)

data class TTSResponseDto(
    @SerializedName("audio_url") val audioUrl: String,
    @SerializedName("duration_seconds") val durationSeconds: Float,
    @SerializedName("cached") val cached: Boolean
)

data class WorksheetQuestionDto(
    @SerializedName("id") val id: Int,
    @SerializedName("question_type") val questionType: String,
    @SerializedName("hindi_prompt") val hindiPrompt: String,
    @SerializedName("santali_prompt") val santaliPrompt: String,
    @SerializedName("options_hindi") val optionsHindi: List<String>?,
    @SerializedName("options_santali") val optionsSantali: List<String>?,
    @SerializedName("answer_hindi") val answerHindi: String,
    @SerializedName("answer_santali") val answerSantali: String,
    @SerializedName("source_reference") val sourceReference: String?,
    @SerializedName("audio_url") val audioUrl: String?
)

data class WorksheetResponseDto(
    @SerializedName("worksheet_id") val worksheetId: String,
    @SerializedName("title") val title: String,
    @SerializedName("grade") val grade: Int,
    @SerializedName("subject") val subject: String,
    @SerializedName("topic") val topic: String,
    @SerializedName("status") val status: String,
    @SerializedName("questions") val questions: List<WorksheetQuestionDto>
)

data class FlashcardItemDto(
    @SerializedName("id") val id: Int,
    @SerializedName("hindi_word") val hindiWord: String,
    @SerializedName("santali_word") val santaliWord: String,
    @SerializedName("phonetic") val phonetic: String?,
    @SerializedName("concept") val concept: String,
    @SerializedName("icon") val icon: String,
    @SerializedName("example_hindi") val exampleHindi: String?,
    @SerializedName("example_santali") val exampleSantali: String?,
    @SerializedName("audio_url") val audioUrl: String?
)

data class FlashcardsResponseDto(
    @SerializedName("lesson_id") val lessonId: String,
    @SerializedName("topic") val topic: String,
    @SerializedName("cards") val cards: List<FlashcardItemDto>
)

data class HealthResponseDto(
    @SerializedName("status") val status: String,
    @SerializedName("offline_mode") val offlineMode: Boolean,
    @SerializedName("models") val models: Map<String, ModelStatusItemDto>
)

data class ModelStatusItemDto(
    @SerializedName("name") val name: String,
    @SerializedName("installed") val installed: Boolean,
    @SerializedName("size_mb") val sizeMb: Float,
    @SerializedName("in_memory") val inMemory: Boolean
)
