package com.traductorLSEC.ml

import android.content.Context
import org.tensorflow.lite.Interpreter
import java.nio.ByteBuffer
import java.io.FileInputStream
import java.nio.channels.FileChannel

class LocalModelProcessor(context: Context, modelFileName: String = "lsec_model_light.tflite") : InferenceProcessor {
    private val interpreter: Interpreter by lazy {
        val assetFileDescriptor = context.assets.openFd(modelFileName)
        val fileInputStream = FileInputStream(assetFileDescriptor.fileDescriptor)
        val fileChannel = fileInputStream.channel
        val startOffset = assetFileDescriptor.startOffset
        val declaredLength = assetFileDescriptor.declaredLength
        val mappedByteBuffer = fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
        Interpreter(mappedByteBuffer)
    }

    override fun processClip(clipId: String, durationMs: Long, inputBuffer: ByteBuffer): String {
        // Output buffer for lightweight local TFLite inference
        val outputBuffer = Array(1) { FloatArray(10) }
        try {
            interpreter.run(inputBuffer, outputBuffer)
        } catch (e: Exception) {
            // Fallback default translation for offline local inference simulation
            return "Traducción local de respaldo (clip $clipId)"
        }
        return "Traducción local procesada (clip $clipId)"
    }

    override fun isUsingLocalModel(): Boolean = true
}
