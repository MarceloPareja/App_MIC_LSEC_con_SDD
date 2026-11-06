# Informe del proyecto **App_MIC_LSEC_con_SDD**

## 1. Introducción

**App_MIC_LSEC_con_SDD** es una aplicación móvil Android nativa orientada a la accesibilidad, cuyo objetivo es traducir la **Lengua de Señas Ecuatoriana (LSEC)** a texto y audio en tiempo real. La aplicación permite capturar señas con la cámara, enviar el video por streaming en paquetes a un modelo de aprendizaje profundo desplegado en la nube, mostrar la traducción en un chat estilo WhatsApp y reproducirla mediante TTS. Está diseñada para funcionar sin inicio de sesión, sin almacenamiento de datos del usuario en la nube y con tolerancia a conexiones de baja calidad.

El proyecto se desarrolló con el enfoque **Spec-Driven Development (SDD)**, utilizando **GitHub Spec Kit 1.2.0** y una extensión de métricas basada en **Puntos de Tarea SDD (PTS)** y **COCOMO II**. El repositorio contiene tres funcionalidades principales, artefactos de especificación, planes, tareas, contratos, pruebas y un pipeline exploratorio en Python para el preprocesamiento de video.

| Dato general | Valor |
|---|---|
| Tipo de aplicación | Móvil Android nativa |
| Dominio | Accesibilidad |
| Metodología | SDD con GitHub Spec Kit |
| Funcionalidades | 3 |
| Historias de usuario | 8 |
| Requisitos funcionales | 25 |
| Periodo analizado | 2026-10-15 a 2026-11-05 |
| Días calendario | 22 |
| Equipo | 2 desarrolladores |
| Modelo de IA registrado | gemini-2.5-pro |

---

# 2. Desarrollo

## 2.1 Descripción de las iteraciones y funcionalidades desarrolladas

El proyecto se organizó en una iteración inicial de preparación metodológica y tres iteraciones funcionales.

| Iteración | Funcionalidad | Periodo | Historias | Requisitos | Tareas | Puntos | Commits |
|---|---|---|---:|---:|---:|---:|---:|
| 000 | Preparación del proyecto, Spec Kit y métricas | 2026-10-20 | 0 | 0 | 0 | 0 | 1 |
| 001 | Prototipo TraductorLSEC | 2026-10-20 a 2026-10-31 | 3 | 10 | 27 | 92 | 9 |
| 002 | App móvil TraductorLSEC | 2026-10-21 a 2026-11-05 | 3 | 10 | 35 | 97 | 3 |
| 003 | Modelo de respaldo local | 2026-11-05 | 2 | 5 | 16 | 46 | 4 |

### Iteración 000 — Preparación metodológica

Se incorporó la infraestructura de **Spec Kit**, los comandos de especificación, planificación, tareas, análisis, checklist y métricas. También se configuró el sistema de medición del proyecto: configuración, factores COCOMO, registro de sesiones y exportación de resúmenes.

Adicionalmente, el 31 de octubre se incorporó el proyecto **vision_pipeline**, un prototipo en Python para el preprocesamiento de video de señas:

- Recorte y redimensionamiento del área de interés.
- Filtro gaussiano separable implementado en TensorFlow.
- Detección de landmarks con **MediaPipe Tasks** en modo pose u holistic.
- Renderizado de esqueleto configurable mediante JSON.
- Salida de video procesado, manifiesto JSONL por frame, keyframes y métricas.

Este pipeline representa aproximadamente **2 925 líneas sobrevivientes** y se contabiliza dentro de la funcionalidad 000. No forma parte directa de la app Android, pero constituye una base exploratoria para el procesamiento visual de LSEC.

### Iteración 001 — Prototipo TraductorLSEC

Primera implementación funcional del concepto. Se definieron la constitución, la especificación, el plan, las tareas y los contratos de la API. En el cliente Android se construyeron los componentes iniciales:

- Estructura del proyecto Android.
- Modelos de mensajes y sesión.
- Captura de cámara con CameraX.
- Streaming de paquetes con identificador de sesión y duración.
- Cliente de red y manejo de respuestas.
- Historial de chat limitado a 30 mensajes.
- Interfaz de chat estilo WhatsApp.
- Integración de TTS en español de Ecuador.
- Manejo de errores y monitoreo de conectividad.

La primera implementación se realizó con una organización tipo MVC y paquete `com.lsec.traductor`, usando Room y Retrofit. Posteriormente fue reorganizada hacia el paquete actual `com.traductorLSEC`. Esta reestructuración explica gran parte del retrabajo de la iteración: de 1 045 líneas agregadas, 511 sobrevivieron y 534 fueron eliminadas o reemplazadas, con una tasa de desperdicio del **51,1 %**.

Aunque el resumen automatizado marca **0 tareas completadas** para 001, el código y el commit de implementación evidencian que el prototipo sí fue construido. La causa es que las casillas de `tasks.md` no se actualizaron. Es una inconsistencia de registro, no necesariamente de implementación.

### Iteración 002 — App móvil TraductorLSEC

Iteración principal del producto. Se refinó la especificación con aclaraciones sobre captura continua, baja conexión, permisos y definición de clip. Las funcionalidades desarrolladas fueron:

- Captura y envío continuo de video mientras el botón de grabación está activo.
- Streaming por paquetes sin almacenamiento local del video completo.
- Envío de duración e identificador único de sesión al modelo remoto.
- Recepción de traducciones en tiempo real.
- Chat con historial máximo de 30 traducciones.
- TTS con permisos de audio.
- Limitación del TTS cuando la conexión es baja.
- Mensajes de error claros: fallo de traducción, error de conexión y archivo no procesable.
- Cierre o bloqueo del flujo cuando faltan permisos de cámara o audio.
- Tareas de convergencia para completar pruebas unitarias faltantes.

La iteración cerró con **35 de 35 tareas completadas** y **97 puntos**. El archivo de estimación de tareas registra 35 tareas y 92 puntos; el consolidado del proyecto registra 97, una diferencia de 5 puntos probablemente asociada a ajustes posteriores de estimación.

### Iteración 003 — Modelo de respaldo local

Iteración orientada a la resiliencia offline. Se planteó un modelo TFLite ligero que sustituya temporalmente al modelo en la nube cuando se pierde la conexión, notificando al usuario sobre la posible pérdida de precisión o velocidad, y restaurando el modelo en la nube al recuperar la conectividad.

Componentes desarrollados:

- Entidad `EstadoConexion` y enumeración `TipoServicio`.
- Contrato `InferenceProcessor`.
- Implementación `LocalModelProcessor` con TensorFlow Lite.
- Contrato `ConnectivityObserver`.
- Gestor `ConnectivityManager` con simulación de pérdida y restauración de conexión.
- Pruebas unitarias `LocalModelTest` y `CloudRestorationTest`.
- Migración de archivos Gradle a Kotlin DSL.
- Corrección del bug de previsualización de cámara.

La iteración registra **16 de 16 tareas completadas** y **46 puntos**. Sin embargo, la integración real está incompleta: el archivo `lsec_model_light.tflite` no está presente en `assets/`, el `LocalModelProcessor` no se instancia desde la app, el `ConnectivityManager` de la funcionalidad 003 no está conectado al flujo principal y no existe un banner visual de advertencia en `activity_main.xml`. Por tanto, se trata de una base de implementación y pruebas, no de una funcionalidad completamente operativa en producción.

---

## 2.2 Comparación de puntos por tarea y tipos de tareas

### Puntos por iteración

| Iteración | Tareas | Puntos | Promedio puntos/tarea | Tareas paralelas | Tareas completadas |
|---|---:|---:|---:|---:|---:|
| 001 | 27 | 92 | 3,41 | 8 | 0 según métrica |
| 002 | 35 | 97 | 2,77 | 10 | 35 |
| 003 | 16 | 46 | 2,88 | 8 | 16 |
| **Total** | **78** | **235** | **3,01** | **26** | **51** |

El promedio de puntos por tarea disminuye de 3,41 en el prototipo inicial a 2,77 en la app móvil y 2,88 en el respaldo local. Esto indica una descomposición progresivamente más fina del trabajo: las iteraciones posteriores usan más tareas de menor tamaño, lo cual facilita el seguimiento y la ejecución incremental.

### Distribución de tareas según su valor en puntos

| Puntos | 001 | 002 | 003 | Total |
|---:|---:|---:|---:|---:|
| 1 | 10 | 11 | 4 | 25 |
| 2 | 1 | 11 | 4 | 16 |
| 3 | 3 | 3 | 4 | 10 |
| 5 | 6 | 10 | 2 | 18 |
| 6 | 1 | 0 | 2 | 3 |
| **Total** | **21** | **35** | **16** | **72** |

La tabla anterior utiliza los archivos `puntos-tarea.csv`. En 001 solo se dispone de 21 tareas clasificadas; las 6 tareas restantes de su `tasks.md` no tienen desglose por tipo y explican los 35 puntos adicionales hasta llegar a los 92 del consolidado. En 002 hay 5 puntos de diferencia entre el archivo de estimación y el resumen global.

### Tipos de tareas por iteración

| Tipo de tarea | 001 tareas/puntos | 002 tareas/puntos | 003 tareas/puntos | Total tareas/puntos |
|---|---:|---:|---:|---:|
| Configuración | 7 / 7 | 9 / 9 | 2 / 2 | 18 / 18 |
| Datos | 3 / 9 | 3 / 9 | 4 / 12 | 10 / 30 |
| Lógica | 4 / 20 | 8 / 40 | 1 / 5 | 13 / 65 |
| Interfaz | 2 / 10 | 2 / 10 | 1 / 5 | 5 / 25 |
| Integración | 1 / 6 | 0 / 0 | 2 / 12 | 3 / 18 |
| Prueba | 1 / 2 | 11 / 22 | 4 / 8 | 16 / 32 |
| Documentación | 3 / 3 | 2 / 2 | 2 / 2 | 7 / 7 |
| **Total clasificado** | **21 / 57** | **35 / 92** | **16 / 46** | **72 / 195** |

Los tipos de tarea muestran una evolución clara:

- **001** está dominada por configuración y lógica, coherente con un prototipo inicial.
- **002** concentra el mayor esfuerzo en lógica y pruebas: 40 puntos de lógica y 22 de prueba, lo que refleja la implementación del flujo principal y las tareas de convergencia TDD.
- **003** es más equilibrada: datos, integración y pruebas concentran la mayor parte de los 46 puntos, propia de una funcionalidad de inferencia local y conmutación de red.

### Complejidad de las tareas

| Complejidad | 001 tareas/puntos | 002 tareas/puntos | 003 tareas/puntos | Total |
|---|---:|---:|---:|---:|
| Baja | 10 / 10 | 11 / 11 | 4 / 4 | 25 / 25 |
| Media | 11 / 47 | 24 / 81 | 12 / 42 | 47 / 170 |
| Alta | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

No se clasificó ninguna tarea como de complejidad alta, aunque varias tareas de integración o de inferencia podrían considerarse candidatas a ello. El 87 % de los puntos clasificados corresponde a complejidad media.

---

## 2.3 Descripción del bug corregido

### Bug: previsualización de cámara en negro

**Identificador:** `video_not_showing`  
**Severidad:** alta  
**Estado:** corregido y verificado  
**Commit:** `d39e3b8 — fix(003): Arreglo para muestra de cámara`

#### Síntoma

Al abrir la aplicación y conceder el permiso de cámara, la vista `PreviewView` permanecía completamente negra. No se mostraba el video en vivo ni aparecía un mensaje de error que explicara la causa.

#### Causa raíz

`CameraStreamer` implementaba el caso de uso `ImageAnalysis` y lo enlazaba al `ProcessCameraProvider`, pero **no configuraba ni enlazaba el caso de uso `Preview`**. Por tanto, el análisis de imágenes podía funcionar, pero no existía una superficie de previsualización conectada al `PreviewView`. Además, la cámara solo se inicializaba al pulsar “Iniciar Traducción”, no al abrir la actividad.

#### Corrección aplicada

| Archivo | Cambio |
|---|---|
| `CameraStreamer.kt` | Se añadió `androidx.camera.core.Preview`, se conectó su `surfaceProvider` al `PreviewView` y se enlazaron conjuntamente `Preview` e `ImageAnalysis`. Se inició la cámara desde el bloque `init`. |
| `MainActivity.kt` | Se pasó el `PreviewView` al constructor de `CameraStreamer`. |

El cambio neto en código de producción fue de aproximadamente **20 líneas agregadas y 2 modificadas**. También se incorporaron los artefactos de evaluación, corrección y verificación del bug en `.specify/bugs/video_not_showing/`.

#### Verificación

La verificación se realizó mediante inspección estructural del enlace de casos de uso de CameraX y revisión de compilación. El documento de pruebas concluye que la previsualización queda correctamente conectada al `PreviewView`. No se añadieron pruebas de instrumentación automatizadas; por ello, la comprobación en emulador o dispositivo físico sigue siendo una recomendación pendiente.

---

## 2.4 Análisis de métricas globales del proyecto

### Resumen general

| Métrica | Valor |
|---|---:|
| Funcionalidades | 3 |
| Historias de usuario | 8 |
| Requisitos funcionales | 25 |
| Criterios de éxito | 15 |
| Escenarios de aceptación | 15 |
| Contratos | 2 |
| Tareas | 78 |
| Tareas completadas | 51 |
| Porcentaje de tareas completadas | 65,4 % |
| Puntos de tarea | 235 |
| Puntos de tareas completadas | 143 |
| Porcentaje de puntos completados | 60,9 % |
| Commits según corte de métricas | 28 |
| Commits reales en Git, incluyendo merges | 31 |
| Días calendario | 22 |
| Días con actividad | 5 |
| Líneas agregadas | 4 086 |
| Líneas eliminadas | 517 |
| Líneas de pruebas agregadas | 450 |
| Porcentaje de LOC de pruebas | 11,0 % |
| LOC sobrevivientes | 3 552 |
| LOC de desperdicio | 534 |
| Tasa de desperdicio | 13,07 % |

### Métricas por funcionalidad

| Funcionalidad | Tareas | Completadas | Puntos | Commits | LOC agregadas | LOC eliminadas | LOC pruebas | LOC sobrevivientes | Desperdicio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 000-proyecto | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 2 925 | 0 |
| 001-traductor-lsec | 27 | 0 | 92 | 9 | 1 045 | 0 | 0 | 511 | 534 |
| 002-traductor-lsec-movil | 35 | 35 | 97 | 3 | 0 | 0 | 0 | 0 | 0 |
| 003-modelo-respaldo-local | 16 | 16 | 46 | 4 | 116 | 3 | 63 | 116 | 0 |
| **Total** | **78** | **51** | **235** | **17 atribuidos** | **1 161** | **3** | **63** | **3 552** | **534** |

La diferencia entre las 1 161 líneas atribuidas por funcionalidad y las 4 086 del resumen global corresponde a código no asignado directamente a una funcionalidad, principalmente el pipeline `vision_pipeline` y artefactos de infraestructura.

### Indicadores de productividad y tamaño

| Indicador | Valor |
|---|---:|
| Puntos por tarea | 3,01 |
| Puntos por tarea en 001 | 3,41 |
| Puntos por tarea en 002 | 2,77 |
| Puntos por tarea en 003 | 2,88 |
| LOC agregadas por punto | 17,39 |
| LOC agregadas por tarea | 52,38 |
| Tareas por día calendario | 3,55 |
| Commits por día con actividad | 6,20 considerando 31 commits |
| LOC de prueba / LOC total | 11,01 % |
| Tasa de desperdicio | 13,07 % |
| Horas humanas registradas | 1,75 h |
| Horas de agente registradas | 0 h |
| Tokens registrados | 0 |
| Persona-mes | 0,0115 |
| TDEV | 0,723 meses |
| Costo humano registrado | USD 0 |
| Costo de IA registrado | USD 0 |
| Sesiones registradas | 6 |

Los indicadores de productividad deben interpretarse con cautela: las horas humanas y los tokens están claramente subregistrados. Un total de **1,75 horas humanas para 78 tareas y 235 puntos** no representa el esfuerzo real del proyecto, sino únicamente las sesiones que quedaron registradas en `metricas/sesiones`. Lo mismo ocurre con el costo, que aparece en cero porque no se registraron tarifas ni consumos.

### Distribución del esfuerzo humano registrado por fase

| Fase | Horas | Porcentaje |
|---|---:|---:|
| Constitución | 0,00 | 0,0 % |
| Visión | 0,00 | 0,0 % |
| Especificar | 0,25 | 14,3 % |
| Aclarar | 0,25 | 14,3 % |
| Planificar | 0,75 | 42,9 % |
| Tareas | 0,25 | 14,3 % |
| Analizar | 0,00 | 0,0 % |
| Implementar | 0,25 | 14,3 % |
| Probar | 0,00 | 0,0 % |
| Verificar en dispositivo | 0,00 | 0,0 % |
| Integrar | 0,00 | 0,0 % |
| Infraestructura | 0,00 | 0,0 % |
| Gestión | 0,00 | 0,0 % |
| Aprendizaje | 0,00 | 0,0 % |
| **Total** | **1,75** | **100 %** |

La mayor parte del tiempo humano registrado se concentra en planificación, lo que es coherente con SDD, pero el registro es demasiado incompleto para extraer conclusiones fuertes sobre el costo real del proyecto.

### Análisis de commits

#### Distribución por tipo de commit

| Tipo | Commits | Porcentaje |
|---|---:|---:|
| `docs` | 14 | 45,2 % |
| `feat` | 8 | 25,8 % |
| `chore` | 4 | 12,9 % |
| `fix` | 2 | 6,5 % |
| Merges y commit inicial | 3 | 9,7 % |
| **Total** | **31** | **100 %** |

#### Distribución por autor

| Autor | Commits | Porcentaje |
|---|---:|---:|
| MarceloPareja | 19 | 61,3 % |
| gablop | 12 | 38,7 % |

#### Distribución temporal

| Fecha | Commits | Hito principal |
|---|---:|---|
| 2026-10-15 | 1 | Commit inicial |
| 2026-10-20 | 13 | Especificaciones, constitución y Spec Kit |
| 2026-10-21 | 9 | Planificación, tareas, prototipo y métricas |
| 2026-10-31 | 1 | Pipeline de visión |
| 2026-11-05 | 7 | Respaldo local, corrección de cámara y métricas |

El historial muestra un patrón de trabajo concentrado en pocos días: **22 de los 31 commits se realizaron el 20 y 21 de octubre**, y otros 7 el 5 de noviembre. Esto refleja una dinámica de ráfagas de trabajo intensivo separadas por periodos sin actividad, más que un flujo continuo.

El proyecto sigue mayoritariamente **Conventional Commits**, con alcances por funcionalidad (`001`, `002`, `003`, `001-app-movil-lsec`). Los dos commits `fix` documentan explícitamente la causa del cambio. Sin embargo, no existen commits de tipo `test` o `refactor`, aunque sí hubo reestructuración de código y pruebas; parte de ese trabajo quedó mezclado dentro de commits `feat` y `docs`.

Solo **17 de los 28 commits del corte** están atribuidos a una funcionalidad en el resumen. El resto corresponde a infraestructura, documentación, merges y preparación del toolkit.

### Observaciones sobre la calidad de las métricas

- El resumen registra **28 commits**, pero el repositorio actual contiene **31**, incluyendo merges y el commit posterior de actualización de métricas.
- La funcionalidad 001 aparece con **0 tareas completadas**, aunque su implementación está evidenciada en el repositorio. Las casillas de `tasks.md` no se actualizaron.
- La funcionalidad 002 registra **0 LOC**, probablemente porque el conteo no capturó correctamente la reestructuración de paquetes y archivos.
- Los puntos de 001 y 002 no coinciden exactamente entre los archivos `puntos-tarea.csv` y el consolidado global.
- No se registraron horas de agente, tokens ni costos de IA, a pesar de existir 6 sesiones y uso declarado de `gemini-2.5-pro`.
- La mayor parte de las pruebas contabilizadas pertenece a `vision_pipeline`; la app Android solo contiene dos archivos de prueba, ambos de la iteración 003, con 63 líneas.
- La funcionalidad 003 está marcada como completa, pero su integración real con la app es parcial.

---

## 2.5 Conclusiones

El proyecto logró aplicar de forma consistente el enfoque **Spec-Driven Development**: cada funcionalidad cuenta con especificación, aclaraciones, plan, tareas, contratos y, en algunos casos, pruebas. Esta trazabilidad permitió dividir un problema complejo en tres iteraciones claras y mantener una relación explícita entre requisitos, tareas y código.

Los principales logros son:

- Construcción de un prototipo Android funcional para captura, streaming, chat, historial y TTS.
- Definición de una arquitectura modular por responsabilidades: cámara, red, modelos, UI, TTS y utilidades.
- Incorporación de una estrategia de resiliencia mediante modelo local de respaldo y conmutación automática.
- Corrección documentada y verificada de un bug crítico de previsualización de cámara.
- Uso de un proceso formal de análisis, corrección y verificación de bugs.
- Baja volatilidad de alcance: no se registraron puntos agregados ni eliminados después de la planificación.

Las principales limitaciones son:

- La aplicación no está lista para producción: el endpoint del modelo remoto es un marcador de posición, el modelo local no está empaquetado y la conmutación a modelo local no está integrada al flujo real.
- La cobertura de pruebas de la app Android es reducida y no hay pruebas de instrumentación para cámara, streaming o TTS.
- Las métricas de esfuerzo, tokens y costo están incompletas, por lo que los indicadores de productividad no son confiables como medida real del trabajo.
- Existen inconsistencias de registro entre `tasks.md`, los archivos de puntos y los resúmenes consolidados.
- La documentación y la planificación concentran gran parte de los commits, mientras que la implementación y las pruebas tienen menor representación en el historial.
- El pipeline de visión, aunque valioso como exploración, no está integrado con la aplicación Android.

Como recomendaciones para siguientes iteraciones se propone:

1. Completar la integración real del modelo local, incluyendo el archivo TFLite y el banner de advertencia.
2. Reemplazar el endpoint de ejemplo por configuración real y externalizarla.
3. Añadir pruebas unitarias e instrumentadas para las funcionalidades 001 y 002.
4. Actualizar las casillas de tareas y corregir el cálculo de commits, LOC y puntos para que las métricas sean reproducibles.
5. Registrar horas de agente, tokens y costos en cada sesión.
6. Incorporar integración continua para compilar y ejecutar pruebas automáticamente.

En síntesis, el proyecto demuestra correctamente el valor de SDD para organizar y documentar el desarrollo de una aplicación de accesibilidad, y entrega un prototipo funcional con una base técnica sólida. No obstante, la brecha entre las tareas marcadas como completadas y el estado real de integración de algunas funcionalidades indica que el siguiente paso debe ser la **verificación funcional en dispositivo y la consolidación de pruebas**, más que la apertura de nuevas funcionalidades.
