---
name: reading-prices
description: Lee e interpreta precios en formato argentino desde catálogos, convirtiendo correctamente miles, decimales y símbolos a números para el output JSON. Usar siempre que se extraiga un producto con precios visibles. Distingue entre precio regular y precio de oferta por su presentación visual (tachado, tamaño, posición), y aplica reglas específicas cuando solo hay un precio visible.
---

# Lectura de Precios

## Problema que resuelve esta skill

Los precios argentinos tienen un formato particular que puede confundir al modelo si no se lo maneja explícitamente. Además, los catálogos presentan los precios de distintas formas (regular vs oferta) que requieren identificación visual. El agente debe leer los precios correctamente y saber cuándo NO inventar precios que no están visibles.

## Formato de precios argentinos

- Separador de miles: punto (`.`)
- Separador decimal: coma (`,`)
- Símbolo: `$` (a veces omitido en el catálogo)
- Ejemplos: "$3.299", "$2.143,90", "$14.567,90", "$700,90"

## Cómo convertir al output JSON

1. Quitar el símbolo `$`
2. Quitar el punto de miles
3. Reemplazar la coma decimal por punto
4. Resultado: número (sin comillas)

| En la imagen | En el JSON |
| :---- | :---- |
| $3.299 | `3299` |
| $2.143,90 | `2143.9` |
| $14.567,90 | `14567.9` |
| $700,90 | `700.9` |
| $10.500 | `10500` |

## Precio regular vs precio de oferta

### Precio regular (sin descuento)

**Cómo aparece visualmente:**

- Tachado con una línea
- En letra más chica que el precio de oferta
- Con leyenda "Antes", "P. Lista", "Precio regular"
- A veces en color más claro o gris

### Precio de oferta (con descuento)

**Cómo aparece visualmente:**

- Número más grande y prominente
- Color llamativo (rojo, amarillo, etc.)
- Con leyenda "Ahora", "Oferta", "Precio especial"
- A veces dentro de un sticker o badge

## Reglas de lectura

### Si se ven los dos precios

- `precio_regular`: el tachado o más chico
- `precio_oferta`: el grande o prominente

### Si se ve solo un precio y hay descuento visible

- Ese precio es el `precio_oferta`
- `precio_regular`: `null` — NO calcularlo a partir del descuento

### Si se ve solo un precio y no hay descuento

- Ese precio puede ser regular u oferta (no se puede saber con certeza)
- Ponerlo en `precio_oferta` (es el precio vigente al momento)
- `precio_regular`: `null`

### Si no se ve ningún precio

- Ambos campos en `null`
- Probablemente es `tipo_imagen: "publicidad"`

## Qué NO hacer

| Situación | Incorrecto | Correcto |
| :---- | :---- | :---- |
| Se ve $2.143,90 y 35% | Calcular regular: `2143.9 / 0.65 = 3298.3` | `precio_regular: null, precio_oferta: 2143.9` |
| Precio borroso, parece $3.2?? | Poner `3200` (adivinando) | `null` |
| Se ve un precio en una esquina lejana | Asignar a un producto cercano | `null` (no está claro a cuál pertenece) |
| Precio con centavos: $2.143,90 | `2143.90` | `2143.9` (ambos son válidos en JSON, preferir la forma corta) |

## Precios de combo

Ver la skill `detecting-combos` para la lógica completa. Resumen:

- El precio del combo va completo al producto principal en `precio_oferta`
- El producto secundario lleva `precio_oferta: 0`
- `precio_regular` es `null` en ambos (no existe un "precio regular" de un combo)

## Principio general

Ante la duda, `null`. Es mejor un campo vacío que un número inventado o mal interpretado. El cruce contra la base maestra y la revisión humana pueden completar lo faltante — un número incorrecto que pasa como válido es mucho más difícil de detectar y corregir después.
