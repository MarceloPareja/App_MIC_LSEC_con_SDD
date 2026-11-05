package com.traductorLSEC.model

enum class TipoServicio {
    NUBE,
    LOCAL
}

data class EstadoConexion(
    val id: String,
    val tipoServicio: TipoServicio,
    val conectado: Boolean,
    val mensajeAdvertencia: String?,
    val timestamp: Long = System.currentTimeMillis()
)
