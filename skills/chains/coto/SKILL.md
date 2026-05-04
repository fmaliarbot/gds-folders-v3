---
name: coto
description: Maneja las particularidades del catálogo de COTO, la cadena de supermercados e hipermercados argentina. Usar siempre que se procese un folder de COTO. Incluye datos fijos de la cadena, reconocimiento de la tarjeta de fidelidad COMUNIDAD COTO, descuentos típicos asociados a esa tarjeta, mapeo de zonas canónicas, y convenciones de formato de SKU específicas de la cadena.
---

# Procesamiento de catálogos de COTO

## Cuándo usar esta skill

Activar esta skill cuando se está procesando cualquier folder de COTO. Provee el contexto específico de la cadena para completar correctamente los campos fijos y resolver las particularidades de naming, formato y promociones.

## Datos fijos de la cadena

Cuando la metadata indica COTO, los siguientes campos se completan con valores canónicos:

| Campo | Valor |
|---|---|
| `nombre_cadena` | `"COTO"` |
| `nombre_publicador` | `"COTO"` (cuando es folder propio de la cadena) |
| `tipo_publicador` | `"Cadena"` |
| `canal` | `"Supermercado"` |

**Caso especial:** cuando el folder es una inserción del diario Clarín (folder "Super Fin de Semana" o similar), los datos cambian:

| Campo | Valor |
|---|---|
| `nombre_publicador` | `"CLARIN"` |
| `nombre_cadena` | `"COTO"` |
| `tipo_publicador` | `"Diario"` |
| `canal` | `"Supermercado"` |

## Tarjeta de fidelidad: COMUNIDAD COTO

COTO tiene una tarjeta de fidelidad propia llamada **Comunidad COTO**. Cuando una promoción aplica con esta tarjeta, completar el campo `tarjeta_fidelidad` con el valor canónico `"COMUNIDAD COTO"` (mayúsculas, sin acentos).

### Patrones de reconocimiento

La tarjeta puede aparecer en el catálogo con distintas variaciones textuales. Identificar como COMUNIDAD COTO cualquiera de:

- "Comunidad COTO" (forma canónica)
- "comunidad coto" (minúsculas)
- "COMUNIDAD" (sola, típicamente en promociones "exclusivas")
- Logo o badge de Comunidad COTO
- Frases tipo "con Comunidad COTO", "exclusivo Comunidad", "precio Comunidad"

En todos los casos, el valor canónico a registrar es `"COMUNIDAD COTO"`.

### Descuentos típicos con Comunidad COTO

Los folders de COTO frecuentemente muestran un descuento adicional con la tarjeta de fidelidad. Patrones observados:

- Promoción base + 5% o 10% adicional con Comunidad COTO.
- Cervezas y aperitivos suelen tener +5%/10% con Comunidad COTO.
- Champagne suele tener 40% DTO solo con Comunidad COTO (sin promo base).

**Cómo registrar:**

```json
{
  "tipo_promocion_oferta": "25%DTO",
  "tipo_promocion_tarjeta_fidelidad": "5% DTO",
  "tarjeta_fidelidad": "COMUNIDAD COTO"
}
```

**Importante:** registrar SOLO si la imagen lo muestra explícito para ese producto. **No asumir** que aplica a todos los productos del folder por ser COTO.

## Zona de cobertura

COTO publica folders por zona. Las zonas canónicas (ver `references/zonas-geograficas.md`) más frecuentes en COTO:

- `"CAP Y GBA"`
- `"ESTE"`
- `"OESTE"`
- `"SUR"`
- `"CAP-GBA-ESTE-OESTE-SUR"` (cuando aplica a varias zonas)

El folder Super Finde típicamente cubre: **CAP-GBA-ESTE-OESTE-SUR**.
El folder Almacén y Bebidas típicamente cubre: **CAP-GBA-ESTE-OESTE-SUR**.

## URLs de catálogos

- Catálogos semanales: `https://coto.com.ar/images/catalogos/revistas/semanal-alimentos/index_mobile.asp`
- Otros formatos: el sitio principal de COTO puede tener variaciones según evento.

## Convención de formato de SKU

COTO sigue convenciones específicas que el equipo de GDSnet usa al cargar manualmente. El agente genera la descripción canónica completa siguiendo `building-sku-description`, y el pipeline de integración resuelve el match contra la base maestra.

### Ejemplos observados

| Descripción del folder | SKU canónico (agente) |
|---|---|
| Cocinero Aceite Mezcla Soja y Girasol PET 900cc | `COCINERO MEZCLA PET 900CC` |
| Morixe Harina Especial Para Pizzas 1kg | `MORIXE PIZZAS 1KG` |
| Heineken Cerveza Porrón 330ml | `HEINEKEN 330ML` |
| Coca Cola Zero 2,25L | `COCA COLA ZERO 2,25L` |

## Tipos de oferta en catálogos de COTO

Los folders de COTO usan los 4 tipos canónicos:

- **Regular:** producto con foto y precio individual, tamaño estándar.
- **Destacado:** producto con foto más grande, generalmente con borde o fondo especial. En COTO suele aparecer en cervezas en formato grande, gaseosas 2,25L, lácteos destacados, frutas/verduras estrella.
- **Publicidad:** banner o imagen sin precios.
- **Publicación:** grupo de productos del mismo fabricante (típico en cervezas, gaseosas, marcas de lácteos).

## Tipos de promoción frecuentes

Las promociones más comunes en COTO:

- Descuentos porcentuales: `25%DTO`, `35%DTO`, `40%DTO`
- Multi-unidad: `2X1`, `3X2`, `4X3`
- Segunda unidad: `70% DTO 2DA U`, `2DO AL 50%`
- Combinaciones con tarjeta: típicamente +5% o +10% adicional con Comunidad COTO

## Casos especiales conocidos en COTO

### Categorías cerradas con banner

COTO frecuentemente presenta familias de productos (vinos, cervezas, lácteos) como un banner de marca con varios SKUs agrupados.

- Si el banner es de un fabricante: `tipo_oferta: "Publicación"`.
- Si es un banner de categoría sin fabricante claro: ver `handling-closed-brand-categories`.
- No inventar precios para cada SKU individual — dejar `precio_oferta` en `null` y registrar `tipo_promocion_oferta` si está visible.

### Bloque "Combiná" (Coca Cola)

Los folders de COTO frecuentemente tienen bloques tipo "Combiná 8X6" con 4 latas de gaseosa de 220ml (Coca Cola, Coca Sin Azúcar, Fanta, Sprite). Ver `extracting-multiple-products-per-image` para la regla — son **líneas distintas** (4 registros), no variedades.

### Frescos por kg (pollo, frutas, verduras)

Frecuentemente aparecen en página 8 (almacén) con precio por kg. La medida es variable (lo paga la balanza), entonces:

- `medida`: `null`
- `u_medida`: `"KG"`

### Códigos internos visibles

COTO publica códigos internos cortos junto a algunos productos (ej: `Cod: 42210`, `Cod: 549 *1`). Si están visibles, copiar a `id_sku_interno_spm`. Si tienen sufijo `*1`, mantener el sufijo.

### Publicidades de portada

La primera página suele ser publicidad con productos pero sin precios. Se registran con `tipo_oferta: "Publicidad"` y los 4 campos de precio en `null`. Si hay un texto de promo (ej: "2X1"), igual se registra en `tipo_promocion_oferta`.
