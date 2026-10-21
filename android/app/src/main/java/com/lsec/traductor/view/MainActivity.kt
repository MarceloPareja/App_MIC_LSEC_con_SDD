package com.lsec.traductor.view

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.lsec.traductor.controller.ApiClient
import com.lsec.traductor.controller.ChatViewModel
import com.lsec.traductor.controller.NetworkMonitor
import com.lsec.traductor.controller.NetworkRetryInterceptor
import com.lsec.traductor.controller.StreamingController
import com.lsec.traductor.controller.TtsManager
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

/**
 * Actividad principal (Vista MVC) de TraductorLSEC.
 * Integra la visualización de cámara, chat estilo WhatsApp (historial de 30 mensajes), TTS y estado de red.
 */
class MainActivity : AppCompatActivity() {

    private val chatViewModel: ChatViewModel by viewModels()
    private lateinit var ttsManager: TtsManager
    private lateinit var networkMonitor: NetworkMonitor
    private lateinit var streamingController: StreamingController

    private lateinit var tvEstadoRed: TextView
    private lateinit var tvHistorialChat: TextView
    private lateinit var btnIniciarStreaming: Button

    companion object {
        private const val REQUEST_CODE_PERMISSIONS = 10
        private val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Layout simulado o programático para demostración MVC nativa
        tvEstadoRed = TextView(this).apply { text = "Verificando conexión..." }
        tvHistorialChat = TextView(this).apply { text = "Historial de traducciones (máx 30):\n" }
        btnIniciarStreaming = Button(this).apply { text = "Iniciar Streaming LSEC" }

        val layout = android.widget.LinearLayout(this).apply {
            orientation = android.widget.LinearLayout.VERTICAL
            setPadding(32, 32, 32, 32)
            addView(tvEstadoRed)
            addView(btnIniciarStreaming)
            addView(tvHistorialChat)
        }
        setContentView(layout)

        ttsManager = TtsManager(this)
        networkMonitor = NetworkMonitor(this)

        val translationService = ApiClient.crearServicio(NetworkRetryInterceptor())
        streamingController = StreamingController(this, translationService)

        verificarPermisos()
        observarRed()
        observarChat()

        btnIniciarStreaming.setOnClickListener {
            if (streamingController.isStreamingActive) {
                streamingController.detenerStreaming()
                btnIniciarStreaming.text = "Iniciar Streaming LSEC"
            } else {
                streamingController.iniciarStreaming()
                btnIniciarStreaming.text = "Detener Streaming LSEC"
                // Simulación de traducción entrante para demostración del chat y TTS
                chatViewModel.agregarTraduccion("sesion-demo", "Hola, bienvenido al traductor de LSEC.")
                ttsManager.reproducirTexto("Hola, bienvenido al traductor de LSEC.")
            }
        }
    }

    private fun verificarPermisos() {
        if (!REQUIRED_PERMISSIONS.all { ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED }) {
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS)
        }
    }

    private fun observarRed() {
        lifecycleScope.launch {
            networkMonitor.estadoConexion.collectLatest { conectado ->
                if (conectado) {
                    tvEstadoRed.text = "Estado: Conectado (Óptimo)"
                    tvEstadoRed.setTextColor(android.graphics.Color.GREEN)
                } else {
                    tvEstadoRed.text = "Estado: Baja conexión / Sin internet"
                    tvEstadoRed.setTextColor(android.graphics.Color.RED)
                    ErrorDialogHelper.mostrarErrorAmigable(
                        this@MainActivity,
                        "Conexión limitada",
                        "Se detectó baja conexión. Los paquetes se reintentarán automáticamente."
                    )
                }
            }
        }
    }

    private fun observarChat() {
        lifecycleScope.launch {
            chatViewModel.ultimosMensajes.collectLatest { mensajes ->
                val sb = StringBuilder("Historial de traducciones (${mensajes.size}/30):\n")
                for (msg in mensajes) {
                    sb.append("• ${msg.textoTraducido}\n")
                }
                tvHistorialChat.text = sb.toString()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        ttsManager.liberar()
        streamingController.detenerStreaming()
    }
}
