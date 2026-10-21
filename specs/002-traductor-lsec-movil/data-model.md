# Data Model

## Traduccion
- id: string (único)
- texto: string
- timestamp: datetime

## Clip
- id: string (único)
- duracion: int (segundos)
- timestamp: datetime (obtenido por servidor)

## Chat
- traducciones: list[Traduccion] (máx 30)