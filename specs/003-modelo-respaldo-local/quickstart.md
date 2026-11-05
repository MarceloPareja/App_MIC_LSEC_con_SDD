# Quickstart Guide: Modelo de Respaldo Local LSEC

**Feature**: `003-modelo-respaldo-local`

## Prerrequisitos
- Android Studio Iguana / Koala o superior.
- SDK de Android (minSdk 24, targetSdk 34).
- Gradle 8.x con soporte para Kotlin DSL (`build.gradle.kts`).

## Configuración del Modelo Local (TFLite)
1. Colocar el archivo del modelo ligero `.tflite` en `android/app/src/main/assets/lsec_model_light.tflite`.
2. Verificar las dependencias en `android/app/build.gradle.kts`:
   ```kotlin
   dependencies {
       implementation("org.tensorflow:tensorflow-lite:2.14.0")
       implementation("org.tensorflow:tensorflow-lite-support:0.4.4")
   }
   ```

## Validación End-to-End en Android Studio
1. Abrir el proyecto en Android Studio.
2. Sincronizar el proyecto con los archivos Gradle (`Sync Project with Gradle Files`).
3. Ejecutar los tests unitarios e instrumentados:
   ```bash
   ./gradlew test
   ./gradlew connectedAndroidTest
   ```
4. Simular la pérdida de red en el emulador / dispositivo de prueba y verificar la conmutación al modelo local con su respectiva advertencia visual.
