---
name: building-sku-description
description: Construye el campo `descripcion` de cada producto siguiendo los patrones canónicos de GDSnet (específico con medida, genérico por marca, o por categoría) y aplicando las abreviaciones más usadas. Genera valores como `ALMA MORA MALBEC 750CC` o `MENTOS CARAMELOS 29,5G`. La consistencia del SKU es clave para el matching downstream contra la base maestra de GDSnet.
---

# Construcción de la Descripción del SKU

## Cuándo usar esta skill

Activar siempre que el agente genere el campo `descripcion` de un producto. La descripción es lo que GDSnet usa para matchear contra su base maestra de SKUs, así que la consistencia importa más que la creatividad.

## Reglas globales

Las reglas globales del agente (no inventar, preservar nombres comerciales, mayúsculas sin acentos) están en `extracting-products`. Esta skill las extiende con el detalle específico del campo `descripcion`.

## Los 3 patrones canónicos

Cada producto encaja en uno de estos 3 patrones. Eligir el correcto según lo que muestra el folder.

### Patrón A — Específico con medida

Cuando el folder muestra un envase concreto con su gramaje, volumen o cantidad.

**Formato:** `MARCA + VARIEDAD + MEDIDA`

Ejemplos:
- "Alma Mora Malbec 750ml" → `ALMA MORA MALBEC 750CC`
- "Coca Cola Zero 2,25L" → `COCA COLA ZERO 2,25L`
- "Mentos Caramelos 29,5g" → `MENTOS CARAMELOS 29,5G`
- "Nescafé Gold 95g" → `NESCAFE GOLD 95G`

La medida va pegada a la unidad sin espacio (`750CC`, no `750 CC`). Coma decimal (`2,25L`, no `2.25L` ni `2,25 L`).

### Patrón B — Genérico por marca cuando hay descriptor de tipo

Cuando el folder muestra logo de marca + texto descriptor del tipo de producto, sin especificar variante ni medida.

**Formato:** `MARCA + TIPO`

Ejemplos:
- "Oreo - Galletitas" → `OREO GALLETITAS`
- "Pepitos - Galletitas" → `PEPITOS GALLETITAS`
- "Knorr - Caldos" → `KNORR CALDOS`
- "Cruz de Malta - Yerba" → `CRUZ DE MALTA YERBAS` (plural cuando aplica)

Este patrón es típico en bloques promocionales tipo "70% DTO 2da unidad" donde la promo aplica a toda la línea de la marca.

### Patrón C — Solo nombre de categoría (registros VARIAS MARCAS)

Cuando el agente genera un registro con `marca: "VARIAS MARCAS"` para una categoría cerrada (ver `handling-closed-brand-categories`), el campo `descripcion` es **literalmente el nombre de la categoría canónica**, sin prefijos ni sufijos.

Ejemplos:
- `descripcion: "ALFAJORES"` (no `"V/M ALFAJORES"`)
- `descripcion: "CARAMELOS"` (no `"CARAMELOS TODOS"`)
- `descripcion: "SHAMPOO"` (no `"V/M SHAMPOO"`)
- `descripcion: "VINOS"` (no `"VINOS FINOS TODOS"`)

**Nunca usar prefijos** como `V/M`, `VARIAS MARCAS`, `MULTI`. **Nunca agregar sufijos** como `TODOS`, `TODAS`. La capa de exportación decide después si quiere agregarlos al pasar a Excel.

## Cómo elegir el patrón

| Lo que ves en el folder | Patrón |
|---|---|
| Envase concreto con medida visible | A |
| Logo + descriptor de tipo, sin medida individual | B |
| Bloque genérico "EN GOLOSINAS" sin marca individual | C |

## Diccionario de abreviaciones frecuentes

Solo las abreviaciones que GDSnet usa frecuentemente:

| Texto largo | Abreviación |
|---|---|
| LIQUIDO | LIQ |
| CONCENTRADO | CONC |
| INSTANTÁNEO | INSTANTANEO (sin tilde, no abreviación) |
| LARGA VIDA | LV (en SKUs largos) |
| ULTRA CONCENTRADO | ULTRA CONC |
| BAJAS CALORÍAS | BAJAS CAL |

**Nombres comerciales NO se abrevian ni traducen** (Free, Zero, Light, Diet, etc.) — ver regla 2 en `extracting-products`.

Para palabras no listadas, usar el formato sin abreviar (`KNORR CALDOS` no `KNORR CALD`). El diccionario crece según GDSnet lo defina.

## Ejemplos comparativos

| Folder dice | Descripción canónica |
|---|---|
| Cocinero Aceite Mezcla Soja y Girasol PET 900cc | `COCINERO MEZCLA PET 900CC` |
| Morixe Harina Especial Para Pizzas 1kg | `MORIXE PIZZAS 1KG` |
| Heineken Cerveza Porrón 330ml | `HEINEKEN 330ML` |
| Coca Cola Zero 2,25L | `COCA COLA ZERO 2,25L` |
| Oreo Galletitas (sin medida) | `OREO GALLETITAS` |
| 7UP Sin Azúcar Bot. x 1,5 Lt. | `7UP SIN AZUCAR 1,5L` (preserva "Sin Azúcar" del folder) |
| 7UP Free Bot. x 1,5 Lt. | `7UP FREE 1,5L` (preserva "Free" del folder) |
| (Bloque "EN GOLOSINAS") → categoria ALFAJORES | `ALFAJORES` |

## Qué NO hacer

- **No copiar literal** la descripción del folder con su formato (mayúsculas/minúsculas mezcladas, puntuación extra, palabras no abreviadas).
- **No traducir nombres comerciales** ("Sin Azúcar" del folder se preserva, no se traduce a "S/AZ").
- **No agregar la cadena al SKU** (no escribir "COTO ALMA MORA MALBEC 750CC" — la cadena va en otro campo).
- **No usar prefijos `V/M`** ni similares en registros VARIAS MARCAS.
- **No mezclar patrones** — un SKU es A, B o C, no híbridos.

## Relación con otros campos

- **`marca`:** mayúsculas sin acentos, separada del `descripcion` aunque aparezca al inicio.
- **`medida` y `u_medida`:** campos numéricos separados (ej: `190` y `GR`). En `descripcion` aparecen pegados (`190G`).
- **`descripcion_literal`:** preserva el texto del folder sin transformar. `descripcion` (este campo) es la versión canónica.
- **`tipo_variedad`:** si hay variedades del mismo SKU, ver `extracting-multiple-products-per-image`.

## Notas de diseño

### Por qué hay 3 patrones y no uno solo

La realidad de los folders es heterogénea: a veces hay envases con medida exacta, a veces solo logo + tipo, a veces solo categoría. Forzar un solo formato perdería información o requeriría inventar datos.

### Por qué la medida va pegada a la unidad

Es la convención de GDSnet en su Excel canónico (`750CC`, `190G`, `2,25L`). Romperla rompe el match.

### Por qué los nombres comerciales se preservan

Forman parte del nombre del producto en la base maestra. Traducirlos rompe el matching aunque la traducción sea semánticamente correcta.
