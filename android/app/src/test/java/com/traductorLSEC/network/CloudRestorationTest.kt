package com.traductorLSEC.network

import com.traductorLSEC.model.TipoServicio
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class CloudRestorationTest {

    @Test
    fun testConnectionRestorationReturnsToCloudModel() {
        var cloudModeActive = true
        val observer = object : ConnectivityObserver {
            override fun onConnectionLost() {
                cloudModeActive = false
            }
            override fun onConnectionRestored() {
                cloudModeActive = true
            }
        }

        val manager = ConnectivityManager(observer)
        manager.simulateConnectionLoss()
        assertEquals(TipoServicio.LOCAL, manager.currentState.tipoServicio)

        manager.simulateConnectionRestored()
        assertEquals(TipoServicio.NUBE, manager.currentState.tipoServicio)
        assertNull(manager.currentState.mensajeAdvertencia)
        assertEquals(true, cloudModeActive)
    }
}
