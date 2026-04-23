---
name: reading-promotions
description: Lee e interpreta los tipos de promoción visibles en un catálogo (porcentajes, 2x1, segunda unidad, tarjetas de fidelidad) y los registra correctamente sin calcular valores derivados. Usar siempre que se extraiga un producto con promoción visible. El principio clave es copiar textualmente lo que dice la imagen — no calcular, no normalizar, no interpretar más allá de lo escrito.
---

# Lectura de Promociones

## Problema que resuelve esta skill

Los tipos de promoción en los catálogos varían mucho en cómo se presentan visualmente. El agente debe copiar lo que ve literalmente, no interpretarlo ni calcular valores derivados que no están escritos.

## Principios fundamentales

### Copiar textual

Si dice "70% en la 2da un.", se pone "70% en la 2da un." — no se normaliza, no se expande, no se interpreta.

### Registrar siempre que sea visible

Si un producto muestra "2x1" pero no tiene precios (tipo `publicidad`), el `tipo_promocion` se registra igual. La promoción es un dato visible independiente del precio.

## Tipos de promoción comunes

### Descuento directo

**Cómo aparece:** "35%", "25% OFF", "50% dto.", "Hasta 40%"

**Se extrae:**
- `tipo_promocion`: el texto tal cual ("35%", "25% OFF", etc.)
- `porcentaje_descuento`: el número como decimal (`0.35`, `0.25`, etc.)

### Segunda unidad

**Cómo aparece:** "70% en la 2da unidad", "2do al 50%", "2da un. al 70%"

**Se extrae:**
- `tipo_promocion`: el texto tal cual
- `porcentaje_descuento`: lo que dice el texto como decimal. Si dice "70% en la 2da", poner `0.70`. NO calcular el descuento "real" sobre 2 unidades.

### NxM (multi-unidad)

**Cómo aparece:** "2x1", "3x2", "4x3", "Llevá 3 pagá 2"

**Se extrae:**
- `tipo_promocion`: el texto tal cual
- `porcentaje_descuento`: `null` (no está escrito como porcentaje). NO calcular.

### Precio especial sin descuento explícito

**Cómo aparece:** Solo un precio, sin indicación de descuento ni promo

**Se extrae:**
- `tipo_promocion`: `null`
- `porcentaje_descuento`: `null`

### Banners decorativos sin estructura promocional

**Cómo aparece:** Texto de marketing que destaca visualmente el precio pero no comunica una estructura promocional específica. Por ejemplo, palabras genéricas en banners de color junto al precio que no indican ni porcentaje de descuento, ni mecánica NxM, ni beneficio con tarjeta, ni ningún otro formato estructurado.

**Se extrae:**
- `tipo_promocion`: `null`
- `porcentaje_descuento`: `null`

**Principio:** el campo `tipo_promocion` se reserva para promociones con **estructura identificable** (porcentajes, NxM, segunda unidad a X%, beneficio con tarjeta específica). Un banner que llama la atención sobre el precio pero no comunica una mecánica promocional no cumple ese criterio.

**Ante duda** sobre si un texto es promoción estructurada o banner decorativo, preferir `null`. No inventar un tipo de promoción a partir de adjetivos de marketing.

### Tarjeta de fidelidad

**Cómo aparece:** "Con Comunidad Coto", "Exclusivo Club Dia", "Mi Carrefour", logo de tarjeta

**Se extrae:**
- `tipo_promocion`: el texto de la promo si lo hay (ej: "35% con Comunidad Coto")
- `tarjeta_fidelidad`: nombre canónico de la tarjeta — las skills específicas de cada cadena proveen los nombres canónicos (ver `coto`, `carrefour`, etc.)

## Qué NO hacer

| Situación | Incorrecto | Correcto |
| :---- | :---- | :---- |
| Se ve "70% en la 2da un." | `porcentaje_descuento: 0.35` (calculando sobre 2) | `porcentaje_descuento: 0.70` (lo que dice) |
| Se ve "2x1" | `porcentaje_descuento: 0.50` (calculando) | `porcentaje_descuento: null` (no hay % escrito) |
| Se ve solo precio oferta y precio regular | `tipo_promocion: "25%"` (calculando el %) | `tipo_promocion: null` (no dice %) |
| Se ve "Hasta 40%" | `porcentaje_descuento: 0.40` | `porcentaje_descuento: 0.40` (es lo que dice) |
| No se ve ninguna promo | `tipo_promocion: "Oferta"` | `tipo_promocion: null` |

## Promoción compartida por grupo

Cuando una promoción aplica a todo un bloque de productos (ej: "70% en la 2da unidad" para toda una marca), se copia el mismo `tipo_promocion` en cada producto del bloque.

## Promociones ambiguas

Si el texto de la promoción no es claro o está parcialmente visible:

- Extraer lo que se pueda leer
- Si no se puede leer nada con certeza: `null`
- No adivinar ni completar con supuestos

## Interacción con la skill de cadena

El formato específico y los nombres de tarjetas de fidelidad varían por cadena. Cuando se esté procesando un catálogo de una cadena específica, la skill de esa cadena (ej: `coto`) provee el valor canónico a usar para la tarjeta.
