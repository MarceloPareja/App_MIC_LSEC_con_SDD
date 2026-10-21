package com.lsec.traductor.model

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entidad de Room que representa un mensaje de traducción de LSEC en el historial de chat.
 * Almacena el texto traducido, el identificador único del clip y el estado del audio TTS.
 */
@Entity(tableName = "mensajes_traduccion")
data class MensajeTraduccion(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val idUnicoClip: String,
    val textoTraducido: String,
    val marcaTemporal: Long = System.currentTimeMillis(),
    val estadoAudio: String = "PENDIENTE" // PENDIENTE, REPRODUCIDO, ERROR
)
