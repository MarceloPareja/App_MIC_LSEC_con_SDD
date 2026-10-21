package com.traductorLSEC.network

import com.traductorLSEC.model.ChatHistory
import com.traductorLSEC.model.ChatMessage

class ResponseHandler {
    fun handleTranslationResponse(text: String) {
        if (text.isNotBlank()) {
            val message = ChatMessage(text = text)
            ChatHistory.addMessage(message)
        }
    }
}
