package com.lsec.traductor.controller

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

/**
 * Interfaz Retrofit para el servicio de traducción del modelo TFLite en la nube.
 */
interface TranslationService {

    @Multipart
    @POST("v1/traduccion/chunk")
    suspend fun enviarChunkVideo(
        @Part("id_unico") idUnico: RequestBody,
        @Part("duracion_clip_ms") duracionClipMs: RequestBody,
        @Part videoChunk: MultipartBody.Part
    ): Response<TraduccionResponseDto>
}

data class TraduccionResponseDto(
    val id_unico: String,
    val estado: String,
    val texto_traducido: String,
    val marca_temporal: Long
)
