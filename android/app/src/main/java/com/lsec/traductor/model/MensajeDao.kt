package com.lsec.traductor.model

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object (DAO) para gestionar las operaciones de base de datos del historial de chat.
 * Implementa la política FIFO para mantener estrictamente un máximo de 30 mensajes.
 */
@Dao
interface MensajeDao {

    @Query("SELECT * FROM mensajes_traduccion ORDER BY marcaTemporal DESC LIMIT 30")
    fun obtenerUltimosMensajes(): Flow<List<MensajeTraduccion>>

    @Insert
    suspend fun insertarMensaje(mensaje: MensajeTraduccion)

    @Query("DELETE FROM mensajes_traduccion WHERE id NOT IN (SELECT id FROM mensajes_traduccion ORDER BY marcaTemporal DESC LIMIT 30)")
    suspend fun aplicarPoliticaFifo30()

    @Query("DELETE FROM mensajes_traduccion")
    suspend fun limpiarHistorial()
}
