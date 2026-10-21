package com.traductorLSEC.network

import android.util.Log
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

class StreamClient {
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val responseHandler = ResponseHandler()

    fun streamVideo(session: StreamSession, videoChunk: ByteArray) {
        val duration = session.getDurationSeconds()
        val sessionId = session.sessionId
        
        // Send chunk with duration and session ID
        val requestBody = videoChunk.toRequestBody("video/mp4".toMediaType())
        val request = Request.Builder()
            .url("https://api.example.com/translate") // Placeholder - external model endpoint
            .addHeader("X-Session-ID", sessionId)
            .addHeader("X-Duration", duration.toString())
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("StreamClient", "Streaming failed", e)
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val translation = response.body?.string() ?: ""
                    responseHandler.handleTranslationResponse(translation)
                }
            }
        })
    }
}
