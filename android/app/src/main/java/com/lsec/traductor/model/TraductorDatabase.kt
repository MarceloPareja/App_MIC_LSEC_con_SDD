package com.lsec.traductor.model

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

/**
 * Base de datos local Room para TraductorLSEC.
 */
@Database(entities = [MensajeTraduccion::class], version = 1, exportSchema = false)
abstract class TraductorDatabase : RoomDatabase() {

    abstract fun mensajeDao(): MensajeDao

    companion object {
        @Volatile
        private var INSTANCE: TraductorDatabase? = null

        fun obtenerInstancia(context: Context): TraductorDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    TraductorDatabase::class.java,
                    "traductor_lsec_db"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
