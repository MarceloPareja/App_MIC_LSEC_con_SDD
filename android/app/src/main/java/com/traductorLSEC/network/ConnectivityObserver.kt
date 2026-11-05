package com.traductorLSEC.network

interface ConnectivityObserver {
    fun onConnectionLost()
    fun onConnectionRestored()
}
