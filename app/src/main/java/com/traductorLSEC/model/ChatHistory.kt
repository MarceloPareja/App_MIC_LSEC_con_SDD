package com.traductorLSEC.model

object ChatHistory {
    private const val MAX_SIZE = 30
    private val messages = mutableListOf<ChatMessage>()

    fun addMessage(message: ChatMessage) {
        messages.add(0, message) // Add to front for chat display
        if (messages.size > MAX_SIZE) {
            messages.removeAt(messages.size - 1)
        }
    }

    fun getMessages(): List<ChatMessage> = messages.toList()

    fun clear() {
        messages.clear()
    }

    fun size(): Int = messages.size
}
