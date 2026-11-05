package com.traductorLSEC.network

import com.traductorLSEC.model.EstadoConexion
import com.traductorLSEC.model.TipoServicio

class ConnectivityManager(private val observer: ConnectivityObserver) {
    var currentState: EstadoConexion = EstadoConexion(
        id = "state-1",
        tipoServicio = TipoServicio.NUBE,
        conectado = true,
        mensajeAdvertencia = null
    )
        private set

    fun simulateConnectionLoss() {
        currentState = EstadoConexion(
            id = "state-${System.currentTimeMillis()}",
            tipoServicio = TipoServicio.LOCAL,
            conectado = false,
            mensajeAdvertencia = "Usando modelo local de respaldo: la traducción puede ser más imprecisa o tardar más en videos ya grabados."
        )
        observer.onConnectionLost()
    }

    fun simulateConnectionRestored() {
        currentState = EstadoConexion(
            id = "state-${System.currentTimeMillis()}",
            tipoServicio = TipoServicio.NUBE,
            conectado = true,
            mensajeAdvertencia = null
        )
        observer.onConnectionRestored()
    }
}
