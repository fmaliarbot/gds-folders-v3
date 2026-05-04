# Zonas Geográficas Canónicas

Las zonas que GDSnet usa para clasificar el alcance geográfico de un folder. Cada folder puede aplicar a una zona o a varias.

Fuente: documento "Automatización Folders – Ajustes" de David Feinmann (GDSnet), abril 2026.

## Las 7 zonas canónicas

| Código canónico | Provincias incluidas |
|---|---|
| **CAP Y GBA** | Capital Federal, Gran Buenos Aires |
| **CENTRO** | Córdoba, San Luis |
| **ESTE** | Entre Ríos, Santa Fe |
| **NEA** | Chaco, Corrientes, Misiones, Formosa |
| **NOA** | Tucumán, Jujuy, Salta, Catamarca, La Rioja, Santiago del Estero |
| **OESTE** | Mendoza, San Juan |
| **SUR** | Buenos Aires (Provincia), Chubut, Neuquén, Río Negro, La Pampa, Santa Cruz, Tierra del Fuego |

## Reglas de uso

### Aplicación a varias zonas

Un mismo folder puede aplicar a varias zonas a la vez. Ejemplos del Excel canónico de GDSnet:

- `"CAP-GBA-CENTRO-ESTE-NOA-OESTE-SUR"` (JUMBO Extremo)
- `"CAP-GBA-ESTE-OESTE-SUR"` (COTO Super Finde)
- `"NOA-NEA-SUR-ESTE"` (DIARCO)
- `"SUR-CENTRO-CAP-GBA-ESTE"` (YAGUAR)

En el JSON estructurado del agente, la zona puede representarse como:
- **Array de códigos:** `["CAP Y GBA", "ESTE", "OESTE", "SUR"]` (preferido para JSON).
- **String concatenado:** `"CAP-GBA-ESTE-OESTE-SUR"` (formato del Excel canónico).

La conversión entre los dos formatos la hace la capa de exportación.

### Aplicación a todo el país

Cuando un folder aplica a todo el país, registrar **las 7 zonas** en el array, o el string `"TOTAL PAIS"`.

Ejemplo: Maxiconsumo "Solo por Hoy" → `"TOTAL PAIS"`.

### Cuando solo aplica a una provincia

Algunas cadenas operan en una sola provincia (ej: Cordiez solo en Córdoba). En ese caso, asignar la zona que corresponda según las provincias listadas arriba (Cordiez → `"CENTRO"`).

### Cuando la zona no está visible

Si el folder no muestra explícitamente su zona de cobertura:

1. Intentar deducirla del contexto del publicador (URL del catálogo, dirección del comercio, dominio web).
2. Si no se puede deducir, dejar el campo en `null` y agregar `LOW_CONFIDENCE` o un código específico al `review_reasons` general del catálogo.
3. La asignación final es responsabilidad del Agent 1 (descarga + metadata) o del operador humano.

## Convenciones de naming

- Mayúsculas siempre.
- "CAP Y GBA" lleva la "Y" mayúscula y los espacios (es como aparece en el Excel canónico).
- Cuando se concatenan varias zonas con guiones, usar `-` sin espacios entre las zonas. Pero en algunos casos del Excel se ve `"CAP-GBA"` como abreviación de `"CAP Y GBA"`. Mantener consistencia con el formato del Excel cuando se exporte.

## Notas

- Esta lista refleja las zonas que GDSnet usa hoy. Si en el futuro se agregan zonas nuevas (ej: Patagonia split, sub-zonas dentro de GBA), David tiene que actualizar este archivo y comunicarlo al equipo.
- Las cadenas que solo operan en una región pueden no usar todas las zonas. Maxiconsumo opera con un solo folder a nivel país. Cordiez con uno solo en Centro. Esto se refleja en la frecuencia y zona del folder, no en una zona "exclusiva".
