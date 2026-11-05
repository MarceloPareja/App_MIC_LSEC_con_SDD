package com.traductorLSEC.ml

import java.nio.ByteBuffer

interface InferenceProcessor {
    fun processClip(clipId: String, durationMs: Long, inputBuffer: ByteBuffer): String
    fun isUsingLocalModel(): Boolean
}
