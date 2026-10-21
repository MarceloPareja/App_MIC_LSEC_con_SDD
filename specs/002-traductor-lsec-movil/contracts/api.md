# API Contract

## POST /traducir
Request JSON:
- id: string
- duracion: int
- paquete: base64 video chunk

Response JSON:
- id: string
- texto: string
- timestamp: string