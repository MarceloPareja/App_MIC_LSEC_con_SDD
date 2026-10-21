package com.lsec.traductor.controller

import okhttp3.Interceptor
import okhttp3.Response
import java.io.IOException

/**
 * Interceptor de OkHttp para reintentar solicitudes HTTP ante baja conectividad o fallos transitorios.
 */
class NetworkRetryInterceptor(private val maxRetries: Int = 3) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        var response: Response? = null
        var attempt = 0
        var lastException: IOException? = null

        while (attempt < maxRetries) {
            try {
                response = chain.proceed(request)
                if (response.isSuccessful) {
                    return response
                }
                response.close()
            } catch (e: IOException) {
                lastException = e
            }
            attempt++
            try {
                Thread.sleep((1000 * attempt).toLong()) // Backoff exponencial simple
            } catch (ie: InterruptedException) {
                Thread.currentThread().interrupt()
                throw IOException("Interrumpido durante el reintento de red", ie)
            }
        }
        throw lastException ?: IOException("Error de red tras $maxRetries intentos.")
    }
}
