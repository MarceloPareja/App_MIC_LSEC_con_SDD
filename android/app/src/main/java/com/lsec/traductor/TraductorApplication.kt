package com.lsec.traductor

import android.app.Application

/**
 * Clase Application base para inicializar dependencias globales en TraductorLSEC.
 */
class TraductorApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        // Inicializaciones globales si fuesen necesarias
    }
}
