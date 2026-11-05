# Contracts: Modelo de Respaldo Local LSEC

**Feature**: `003-modelo-respaldo-local`

## Local Inferences Contract (TFLite Processor Interface)

```kotlin
interface InferenceProcessor {
    fun processClip(clipId: String, durationMs: Long, inputBuffer: ByteBuffer): String
    fun isUsingLocalModel(): Boolean
}
```

## Network Failover Contract

```kotlin
interface ConnectivityObserver {
    fun onConnectionLost()
    fun onConnectionRestored()
}
```
