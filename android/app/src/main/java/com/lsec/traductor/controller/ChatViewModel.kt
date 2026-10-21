package com.lsec.traductor.controller

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.lsec.traductor.model.MensajeDao
import com.lsec.traductor.model.MensajeTraduccion
import com.lsec.traductor.model.TraductorDatabase
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch

/**
 * ViewModel que gestiona el estado del chat y la persistencia local aplicando la política FIFO de 30 mensajes.
 */
class ChatViewModel(application: Application) : AndroidViewModel(application) {

    private val mensajeDao: MensajeDao = TraductorDatabase.obtenerInstancia(application).mensajeDao()
    val ultimosMensajes: Flow<List<MensajeTraduccion>> = mensajeDao.obtenerUltimosMensajes()

    fun agregarTraduccion(idUnico: String, texto: String) {
        viewModelScope.launch {
            val nuevoMensaje = MensajeTraduccion(
                idUnicoClip = idUnico,
                textoTraducido = texto
            )
            mensajeDao.insertarMensaje(nuevoMensaje)
            mensajeDao.aplicarPoliticaFifo30()
        }
    }

    fun limpiarChat() {
        viewModelScope.launch {
            mensajeDao.limpiarHistorial()
        }
    }
}
