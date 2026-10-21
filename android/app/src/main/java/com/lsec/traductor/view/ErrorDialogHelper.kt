package com.lsec.traductor.view

import android.app.AlertDialog
import android.content.Context

/**
 * Utilidad para mostrar mensajes de error intuitivos y amigables al usuario.
 */
object ErrorDialogHelper {

    fun mostrarErrorAmigable(context: Context, titulo: String, mensaje: String, onRetry: (() -> Unit)? = null) {
        val builder = AlertDialog.Builder(context)
            .setTitle(titulo)
            .setMessage(mensaje)
            .setPositiveButton("Entendido") { dialog, _ ->
                dialog.dismiss()
            }

        if (onRetry != null) {
            builder.setNegativeButton("Reintentar") { dialog, _ ->
                dialog.dismiss()
                onRetry()
            }
        }

        builder.create().show()
    }
}
