package com.traductorLSEC.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.traductorLSEC.R
import com.traductorLSEC.camera.CameraStreamer
import com.traductorLSEC.network.ConnectivityMonitor
import com.traductorLSEC.network.StreamClient
import com.traductorLSEC.util.ErrorHandler

class MainActivity : AppCompatActivity() {
    private lateinit var previewView: PreviewView
    private lateinit var btnStart: Button
    private lateinit var btnStop: Button
    private lateinit var btnChat: Button
    private lateinit var statusText: TextView
    private lateinit var cameraStreamer: CameraStreamer
    private lateinit var streamClient: StreamClient
    private lateinit var connectivityMonitor: ConnectivityMonitor
    private val REQUEST_CAMERA_PERMISSION = 1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        previewView = findViewById(R.id.previewView)
        btnStart = findViewById(R.id.btnStart)
        btnStop = findViewById(R.id.btnStop)
        btnChat = findViewById(R.id.btnChat)
        statusText = findViewById(R.id.statusText)

        streamClient = StreamClient()
        cameraStreamer = CameraStreamer(this, this, streamClient)
        connectivityMonitor = ConnectivityMonitor(this)

        setupConnectivityMonitor()
        setupButtons()
        checkCameraPermission()
    }

    private fun setupConnectivityMonitor() {
        connectivityMonitor.setListener { connected ->
            if (!connected) {
                statusText.text = "Sin conexión a internet"
                Toast.makeText(this, ErrorHandler.getUserFriendlyErrorMessage("NETWORK_ERROR"), Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun setupButtons() {
        btnStart.setOnClickListener {
            if (!checkCameraPermission()) {
                requestCameraPermission()
                return@setOnClickListener
            }
            if (!ErrorHandler.isNetworkAvailable(this)) {
                Toast.makeText(this, ErrorHandler.getUserFriendlyErrorMessage("NETWORK_ERROR"), Toast.LENGTH_LONG).show()
                return@setOnClickListener
            }
            cameraStreamer.startStreaming()
            statusText.text = "Transmisión en curso..."
        }

        btnStop.setOnClickListener {
            cameraStreamer.stopStreaming()
            statusText.text = "Transmisión detenida"
        }

        btnChat.setOnClickListener {
            val intent = Intent(this, ChatActivity::class.java)
            startActivity(intent)
        }
    }

    private fun checkCameraPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestCameraPermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.CAMERA),
            REQUEST_CAMERA_PERMISSION
        )
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_CAMERA_PERMISSION) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Permiso de cámara concedido", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, ErrorHandler.getUserFriendlyErrorMessage("CAMERA_ERROR"), Toast.LENGTH_LONG).show()
            }
        }
    }
}
