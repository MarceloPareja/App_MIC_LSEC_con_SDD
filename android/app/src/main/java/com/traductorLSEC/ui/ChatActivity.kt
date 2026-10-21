package com.traductorLSEC.ui

import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.traductorLSEC.R
import com.traductorLSEC.model.ChatHistory
import com.traductorLSEC.tts.TTSManager
import com.traductorLSEC.util.ErrorHandler

class ChatActivity : AppCompatActivity() {
    private lateinit var chatRecyclerView: RecyclerView
    private lateinit var btnSpeak: Button
    private lateinit var btnStop: Button
    private lateinit var ttsManager: TTSManager
    private lateinit var chatAdapter: ChatAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        chatRecyclerView = findViewById(R.id.chatRecyclerView)
        btnSpeak = findViewById(R.id.btnSpeak)
        btnStop = findViewById(R.id.btnStop)

        ttsManager = TTSManager(this)
        setupChat()
        setupButtons()
    }

    private fun setupChat() {
        val messages = ChatHistory.getMessages()
        chatAdapter = ChatAdapter(messages)
        chatRecyclerView.layoutManager = LinearLayoutManager(this).apply {
            reverseLayout = true
        }
        chatRecyclerView.adapter = chatAdapter
    }

    private fun setupButtons() {
        btnSpeak.setOnClickListener {
            val messages = ChatHistory.getMessages()
            if (messages.isNotEmpty()) {
                val latestMessage = messages[0]
                ttsManager.speak(latestMessage.text)
            } else {
                Toast.makeText(this, "No hay traducciones para reproducir", Toast.LENGTH_SHORT).show()
            }
        }

        btnStop.setOnClickListener {
            ttsManager.stop()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        ttsManager.shutdown()
    }
}
