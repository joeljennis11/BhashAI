package com.bhashai.app.data.api

import com.bhashai.app.data.model.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface BhashAIApiService {

    @POST("api/translate")
    suspend fun translateText(
        @Body request: TranslationRequestDto
    ): Response<TranslationResponseDto>

    @Multipart
    @POST("api/translate/voice")
    suspend fun translateVoice(
        @Part file: MultipartBody.Part,
        @Part("source_language") sourceLang: RequestBody,
        @Part("target_language") targetLang: RequestBody,
        @Part("lesson_topic") lessonTopic: RequestBody? = null
    ): Response<VoiceTranslationResponseDto>

    @POST("api/tts")
    suspend fun synthesizeSpeech(
        @Body request: TTSRequestDto
    ): Response<TTSResponseDto>

    @GET("api/health")
    suspend fun getHealth(): Response<HealthResponseDto>

    @POST("api/models/prepare-offline")
    suspend fun prepareOfflineMode(): Response<Map<String, Any>>

    @GET("api/worksheets/{id}")
    suspend fun getWorksheet(@Path("id") id: String): Response<WorksheetResponseDto>

    @GET("api/flashcards/lesson/{id}")
    suspend fun getFlashcards(@Path("id") id: String): Response<FlashcardsResponseDto>
}
