package com.traductorLSEC.network

import java.util.UUID

class StreamSession {
    val sessionId: String = UUID.randomUUID().toString()
    private var startTime: Long = System.currentTimeMillis()
    private var endTime: Long = 0L

    fun getDurationSeconds(): Long {
        val currentTime = if (endTime == 0L) System.currentTimeMillis() else endTime
        return (currentTime - startTime) / 1000
    }

    fun start() {
        startTime = System.currentTimeMillis()
        endTime = 0L
    }

    fun stop() {
        endTime = System.currentTimeMillis()
    }
}
