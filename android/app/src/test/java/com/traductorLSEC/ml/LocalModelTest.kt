package com.traductorLSEC.ml

import com.traductorLSEC.model.TipoServicio
import com.traductorLSEC.network.ConnectivityManager
import com.traductorLSEC.network.ConnectivityObserver
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Test

class LocalModelTest {

    @Test
    fun testConnectionLossTriggersLocalFailover() {
        var localModeActive = false
        val observer = object : ConnectivityObserver {
            override fun onConnectionLost() {
                localModeActive = true
            }
            override fun onConnectionRestored() {
                localModeActive = false
            }
        }

        val manager = ConnectivityManager(observer)
        assertEquals(TipoServicio.NUBE, manager.currentState.tipoServicio)

        manager.simulateConnectionLoss()
        assertEquals(TipoServicio.LOCAL, manager.currentState.tipoServicio)
        assertNotNull(manager.currentState.mensajeAdvertencia)
        assertEquals(true, localModeActive)
    }
}
