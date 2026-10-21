package com.lsec.traductor.controller

import android.content.Context
import android.speech.tts.TextToSpeech
import java.util.Locale

/**
 * Gestor de Text-to-Speech (TTS) en el cliente móvil para generar audio de las traducciones.
 */
class TtsManager(context: Context, private val onInitialized: ((Boolean) -> Unit)? = null) {

    private var tts: TextToSpeech? = null
    var isInitialized: Boolean = false
        private set

    init {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val result = tts?.setLanguage(Locale("es", "EC"))
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    tts?.setLanguage(Locale.SPANISH)
                }
                isInitialized = true
                onInitialized?.invoke(true)
            } else {
                isInitialized = false
                onInitialized?.invoke(false)
            }
        }
    }

    fun reproducirTexto(texto: String) {
        if (isInitialized && texto.isNotBlank()) {
            tts?.speak(texto, TextToSpeech.QUEUE_FLUSH, null, "LSEC_TTS_UTTERANCE")
        }
    }

    fun liberar() {
        tts?.stop()
        tts?.shutdown()
        tts = null
        isInitialized = false
    }
}
