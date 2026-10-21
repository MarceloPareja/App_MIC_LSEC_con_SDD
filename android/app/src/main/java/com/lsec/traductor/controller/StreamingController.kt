package com.lsec.traductor.controller

import android.content.Context
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File
import java.util.UUID

/**
 * Controlador encargado de la gestión de streaming de video por paquetes hacia el modelo en la nube.
 */
class StreamingController(
    private val context: Context,
    private val translationService: TranslationService
) {

    private val idUnicoSesion: String = UUID.randomUUID().toString()
    private var duracionAcumuladaMs: Long = 0L
    var isStreamingActive: Boolean = false
        private set

    fun iniciarStreaming() {
        isStreamingActive = true
        duracionAcumuladaMs = 0L
    }

    suspend fun enviarPaqueteVideo(videoFile: File, duracionChunkMs: Long): String? {
        if (!isStreamingActive) return null
        duracionAcumuladaMs += duracionChunkMs

        // Limite maximo de 10 minutos (600,000 ms)
        if (duracionAcumuladaMs > 600000L) {
            detenerStreaming()
            throw IllegalStateException("Se ha alcanzado el límite máximo de 10 minutos de streaming continuo.")
        }

        val idUnicoBody = idUnicoSesion.toRequestBody("text/plain".toMediaTypeOrNull())
        val duracionBody = duracionAcumuladaMs.toString().toRequestBody("text/plain".toMediaTypeOrNull())

        val requestFile = videoFile.asRequestBody("video/mp4".toMediaTypeOrNull())
        val body = MultipartBody.Part.createFormData("video_chunk", videoFile.name, requestFile)

        val response = translationService.enviarChunkVideo(idUnicoBody, duracionBody, body)
        if (response.isSuccessful && response.body() != null) {
            return response.body()?.texto_traducido
        }
        return null
    }

    fun detenerStreaming() {
        isStreamingActive = false
    }
}
