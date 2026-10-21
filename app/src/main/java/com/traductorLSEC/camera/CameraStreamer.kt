package com.traductorLSEC.camera

import android.content.Context
import android.util.Log
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import com.traductorLSEC.network.StreamClient
import com.traductorLSEC.network.StreamSession
import java.nio.ByteBuffer

class CameraStreamer(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val streamClient: StreamClient
) : ImageAnalysis.Analyzer {
    private var session: StreamSession? = null
    private var isStreaming = false
    private val maxDurationSeconds = 600L // 10 minutes

    fun startStreaming() {
        if (isStreaming) return
        session = StreamSession().apply { start() }
        isStreaming = true
        startCamera()
    }

    fun stopStreaming() {
        if (!isStreaming) return
        session?.stop()
        isStreaming = false
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            val imageAnalysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also { it.setAnalyzer(ContextCompat.getMainExecutor(context), this) }

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(lifecycleOwner, cameraSelector, imageAnalysis)
            } catch (exc: Exception) {
                Log.e("CameraStreamer", "Use case binding failed", exc)
            }
        }, ContextCompat.getMainExecutor(context))
    }

    override fun analyze(image: ImageProxy) {
        if (!isStreaming) {
            image.close()
            return
        }

        val currentSession = session ?: run {
            image.close()
            return
        }

        if (currentSession.getDurationSeconds() >= maxDurationSeconds) {
            stopStreaming()
            image.close()
            return
        }

        val buffer: ByteBuffer = image.planes[0].buffer
        val bytes = ByteArray(buffer.remaining())
        buffer.get(bytes)

        streamClient.streamVideo(currentSession, bytes)
        image.close()
    }
}
