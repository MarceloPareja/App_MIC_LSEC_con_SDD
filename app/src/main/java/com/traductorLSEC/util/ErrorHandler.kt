package com.traductorLSEC.util

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build

object ErrorHandler {
    fun isNetworkAvailable(context: Context): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val network = connectivityManager.activeNetwork ?: return false
            val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
            return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                   capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
                   capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)
        } else {
            @Suppress("DEPRECATION")
            val activeNetworkInfo = connectivityManager.activeNetworkInfo
            return activeNetworkInfo != null && activeNetworkInfo.isConnected
        }
    }

    fun getUserFriendlyErrorMessage(errorCode: String): String {
        return when (errorCode) {
            "NETWORK_ERROR" -> "Error de conexión. Verifica tu internet e intenta nuevamente."
            "CAMERA_ERROR" -> "Error al acceder a la cámara. Verifica los permisos."
            "TTS_ERROR" -> "Error en el audio. El texto seguirá disponible."
            "STREAM_ERROR" -> "Error al transmitir el video. Intenta nuevamente."
            else -> "Ha ocurrido un error. Intenta nuevamente."
        }
    }
}
