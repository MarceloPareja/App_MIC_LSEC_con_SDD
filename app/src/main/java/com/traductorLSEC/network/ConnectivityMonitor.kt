package com.traductorLSEC.network

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.os.Build

class ConnectivityMonitor(context: Context) {
    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    private var isConnected = false
    private var listener: ((Boolean) -> Unit)? = null

    init {
        registerNetworkCallback()
    }

    private fun registerNetworkCallback() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            val networkRequest = NetworkRequest.Builder()
                .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
                .build()

            connectivityManager.registerNetworkCallback(networkRequest, object : ConnectivityManager.NetworkCallback() {
                override fun onAvailable(network: Network) {
                    isConnected = true
                    listener?.invoke(true)
                }

                override fun onLost(network: Network) {
                    isConnected = false
                    listener?.invoke(false)
                }
            })
        }
    }

    fun setListener(listener: (Boolean) -> Unit) {
        this.listener = listener
    }

    fun isCurrentlyConnected(): Boolean = isConnected
}
