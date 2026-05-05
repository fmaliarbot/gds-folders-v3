---
name: coto
description: Maneja las particularidades operativas del agente cuando procesa una página de un folder de COTO. Cubre el reconocimiento de la tarjeta de fidelidad COMUNIDAD COTO con su regla crítica (por SKU, no por bloque), descuentos típicos asociados, tipos de oferta y promoción frecuentes, y casos especiales conocidos (combinables 8X6, frescos por kg, códigos internos). NO incluye datos de metadata del folder (cadena, zona, fechas, tipo de folder) — esos campos son responsabilidad del orquestador o del Agent 1, no del Agent 2.
---

# Procesamiento de catálogos COTO — Agent 2

## Cuándo usar esta skill

Activar cuando el orquestador indica que la imagen procesada pertenece a un folder de COTO. Esta skill complementa las reglas globales de `extracting-products` con el contexto específico de cómo COTO presenta sus ofertas.

## Tarjeta de fidelidad: COMUNIDAD COTO

COTO tiene una tarjeta de fidelidad propia llamada **Comunidad COTO**. El valor canónico para `tarjeta_fidelidad` es `"COMUNIDAD COTO"` (mayúsculas, sin acentos).

### Regla crítica — por SKU, no por bloque

Esta es la regla más importante de esta skill. La regla 4 de `extracting-products` (tarjetas por SKU) aplica acá con un ejemplo concreto que el agente debe internalizar.

**El campo `tarjeta_fidelidad: "COMUNIDAD COTO"` se completa SOLO cuando el badge gráfico de Comunidad COTO aparece directamente sobre o junto al SKU concreto.**

#### EJEMPLO CRÍTICO — caso real página 8 COTO Super Finde

Este es un caso real donde el agente alucinó previamente. Estudialo bien.

En el bloque "40% DTO en productos de las siguientes marcas" hay 6 cervezas listadas: **ANTARES, GROLSCH, BLUE MOON, WARSTEINER, KUNSTMANN, SALTA CAUTIVA**.

El badge "10% adicional Comunidad COTO" aparece **SOLO sobre 4 de esas 6**: GROLSCH, BLUE MOON, WARSTEINER, KUNSTMANN.

**ANTARES y SALTA CAUTIVA NO tienen el badge** en la imagen — están en el mismo bloque pero sin el indicador individual.

**Comportamiento correcto:**

| Marca | tarjeta_fidelidad | tipo_promocion_tarjeta_fidelidad |
|---|---|---|
| ANTARES | `null` | `null` |
| GROLSCH | `"COMUNIDAD COTO"` | `"10%DTO"` |
| BLUE MOON | `"COMUNIDAD COTO"` | `"10%DTO"` |
| WARSTEINER | `"COMUNIDAD COTO"` | `"10%DTO"` |
| KUNSTMANN | `"COMUNIDAD COTO"` | `"10%DTO"` |
| **SALTA CAUTIVA** | **`null`** ← caso clásico de alucinación | **`null`** |

**Pregunta de control que el agente debe hacerse para cada SKU:** "¿Veo el badge 'Comunidad COTO' o el ícono `10%` directamente sobre/al lado del logo de esta marca específica?" Si la respuesta es no, `tarjeta_fidelidad: null` aunque marcas vecinas sí lo tengan.

### Patrones de reconocimiento

La tarjeta puede aparecer con distintas variaciones textuales — todas se mapean al valor canónico `"COMUNIDAD COTO"`:

- "Comunidad COTO" (forma canónica)
- "comunidad coto" (minúsculas)
- "COMUNIDAD" (sola, típicamente en promociones "exclusivas")
- Logo o badge de Comunidad COTO
- Frases tipo "con Comunidad COTO", "exclusivo Comunidad", "precio Comunidad"

### Descuentos típicos con Comunidad COTO

Patrones observados frecuentes (siempre que el badge sea visible para el SKU):

- Promoción base + 5% o 10% adicional con Comunidad COTO.
- Cervezas y aperitivos suelen tener +5%/10% con Comunidad COTO.
- Champagne suele tener 40% DTO solo con Comunidad COTO (sin promo base).

**Cómo registrar (cuando el badge ES visible para el SKU):**

```json
{
  "tipo_promocion_oferta": "25%DTO",
  "tipo_promocion_tarjeta_fidelidad": "5% DTO",
  "tarjeta_fidelidad": "COMUNIDAD COTO"
}
```

## Tipos de oferta en folders de COTO

Los folders de COTO usan los 4 tipos canónicos definidos en `classifying-ad-type`:

- **Regular:** producto con foto y precio individual, tamaño estándar.
- **Destacado:** producto con foto más grande, generalmente con borde o fondo especial. En COTO suele aparecer en cervezas grandes, gaseosas 2,25L, lácteos destacados, frutas/verduras estrella.
- **Publicidad:** banner o imagen sin precios.
- **Publicación:** grupo de productos del mismo fabricante con promo común (típico en cervezas, gaseosas, marcas de lácteos).

## Tipos de promoción frecuentes en COTO

- Descuentos porcentuales: `25%DTO`, `35%DTO`, `40%DTO`
- Multi-unidad: `2X1`, `3X2`, `4X3`
- Segunda unidad: `70% DTO 2DA U`, `2DO AL 50%`
- Combinaciones con tarjeta: típicamente +5% o +10% adicional con Comunidad COTO

## Casos especiales conocidos en COTO

### Bloque "Combiná" (Coca Cola Co.)

Los folders de COTO frecuentemente tienen bloques tipo "Combiná 8X6" con 4 latas de gaseosa de 220ml (Coca Cola, Coca Sin Azúcar, Fanta, Sprite). Ver `extracting-multiple-products-per-image` para la regla — son **líneas distintas** (4 registros), no variedades.

### Frescos por kg (pollo, frutas, verduras)

Frecuentemente aparecen en página 8 (almacén) con precio por kg. La medida es variable (lo paga la balanza):

- `medida`: `null`
- `u_medida`: `"KG"`

### Códigos internos visibles

COTO publica códigos internos cortos junto a algunos productos (ej: `Cod: 42210`, `Cod: 549 *1`). Si están visibles, copiar a `id_sku_interno_spm`. Si tienen sufijo `*1`, mantener el sufijo.

### Publicidades de portada

La primera página suele ser publicidad con productos pero sin precios. Se registran con `tipo_oferta: "Publicidad"` y los 4 campos de precio en `null`. Si hay un texto de promo (ej: "2X1"), se registra en `tipo_promocion_oferta`.

### Categorías cerradas con banner

COTO frecuentemente presenta familias de productos (vinos, cervezas, lácteos) como un banner de marca con varios SKUs agrupados.

- Si el banner es de un fabricante: `tipo_oferta: "Publicación"`.
- Si es un banner de categoría sin fabricante claro: ver `handling-closed-brand-categories`.
- No inventar precios para cada SKU individual — dejar `precio_oferta` en `null` y registrar `tipo_promocion_oferta` si está visible.

## Notas de diseño

### Por qué esta skill ya no tiene metadata de cadena

En versiones anteriores incluía `nombre_cadena: "COTO"`, `tipo_publicador: "Cadena"`, datos de zona, URLs, etc. Esos campos son **metadata del folder** y no salen en el output del Agent 2 (que solo extrae productos por página). La metadata es responsabilidad del orquestador o de un futuro Agent 1 de descarga. Esta skill se enfoca solo en lo que el agente realmente decide al procesar productos.

### Por qué la regla del badge se repite acá si ya está en `extracting-products`

La regla está enunciada en `extracting-products` (regla 4), pero el caso COTO con su badge específico de Comunidad COTO es el patrón donde más frecuentemente el agente falla. La redundancia es defensiva — el ejemplo crítico de las 6 cervezas es lo que evita la regresión Salta Cautiva.
