---
name: classifying-ad-type
description: Clasifica cómo se presenta visualmente un producto dentro de una página del catálogo. Distingue entre 4 tipos de imagen según las convenciones de GDSnet — Regular, Destacado, Publicidad y Publicación. Usar para asignar el campo tipo_oferta de cada producto extraído. Aplica criterios visuales (tamaño relativo, presencia de precios, agrupación por fabricante) y no debe confundirse con tipo de promoción.
---

# Clasificación del Tipo de Imagen

## Rol

Para cada producto que extraés, asignás un valor al campo `tipo_oferta` que describe cómo se presenta visualmente en la página. Es un dato sobre la **presentación** del producto en el folder, no sobre el descuento ni el precio.

## Los 4 valores canónicos

GDSnet usa exactamente estos 4 valores. No inventar otros, no abreviar, no traducir.

### 1. Regular

**Definición:** producto presentado en formato normal, tamaño clásico. Es la mayoría de los productos en cualquier folder regular.

**Cómo identificarlo:**
- Está dentro de una grilla con otros productos de tamaño parecido.
- No se destaca visualmente del resto de la página.
- Tiene precio y/o promoción visible.

**Ejemplo:** una página con 12 productos en una grilla de 3x4, todos con tamaño parecido y precio. Cada uno es `Regular`.

### 2. Destacado

**Definición:** producto que ocupa más espacio que el resto, se destaca visualmente.

**Cómo identificarlo:**
- Su imagen es notablemente más grande que las de los productos vecinos.
- Puede ocupar el doble o más de área que un producto Regular en la misma página.
- Suele estar en el centro, arriba, o a sangre (sin margen) de la página.
- Tiene precio y/o promoción visible.

**Ejemplo:** una página tiene 8 productos, pero uno de ellos (un zapallo, una promoción de cerveza grande, un destacado de gaseosa) ocupa el 30-40% de la página solo.

**Diferencia con Publicación:** un producto Destacado es UN solo SKU presentado en grande. Una Publicación es UN bloque agrupando VARIOS SKUs del mismo fabricante.

### 3. Publicidad

**Definición:** producto que se presenta SIN indicar precios ni porcentajes de descuento.

**Cómo identificarlo:**
- No hay precio visible junto al producto.
- No hay porcentaje de descuento.
- Puede haber un texto promocional genérico ("nuevo sabor", "edición limitada") pero no datos de oferta concretos.
- Se usa para visibilizar el producto sin ofertar precio.

**Ejemplo:** Una marca de yogur aparece grande en la página pero solo dice "Yogur Yoghuísimo - Nuevo" sin precio ni descuento. Es `Publicidad`.

**Importante:** Si el producto tiene un texto de promoción tipo `"2X1"` pero no precio, **sigue siendo Publicidad** (no se ven precios). El `tipo_promocion_oferta` se registra igual.

### 4. Publicación

**Definición:** imagen de un grupo de SKUs que pertenecen a un mismo fabricante, con alguna variable de oferta común.

**Cómo identificarlo:**
- Se presenta un bloque visualmente unificado (mismo fondo, mismo borde, mismo título de marca).
- Dentro del bloque hay varios SKUs distintos del mismo fabricante.
- Hay una promoción común (ej: "35% DTO llevando 2 iguales") que aplica a todos.
- Los SKUs individuales pueden o no tener precios visibles.

**Ejemplo:** un bloque "Kellogg's" con Zucaritas, Froot Loops, Müsli y Choco Krispis, con una sola leyenda "35% DTO llevando 2 iguales" que aplica a todos. Cada cereal individual es `Publicación`.

**Diferencia con Destacado:** Destacado es un solo SKU grande. Publicación es un bloque con varios SKUs del mismo fabricante.

## Árbol de decisión rápido

Para clasificar un producto, hacete estas preguntas en orden:

1. **¿Está dentro de un bloque visualmente unificado del mismo fabricante con otros SKUs?**
   → Sí: `Publicación` (1 registro por cada SKU dentro del bloque, ver `extracting-multiple-products-per-image`).
   → No: seguí.

2. **¿Tiene precio o porcentaje de descuento visible?**
   → No: `Publicidad`.
   → Sí: seguí.

3. **¿Ocupa notablemente más espacio que los productos vecinos?**
   → Sí: `Destacado`.
   → No: `Regular`.

## Casos especiales

### Producto en bloque de un fabricante pero con precio individual

Si un bloque tiene marca de fabricante pero cada SKU dentro tiene su propio precio listado, **sigue siendo Publicación** (es la presentación lo que importa, no si hay precio individual).

### Bloque "Combiná" (8X6 estilo Coca Cola)

Cuando el folder muestra un bloque tipo "Combiná 8X6" con 4 latas de gaseosa (Coca, Coca Sin Azúcar, Fanta, Sprite), todos del mismo fabricante (Coca Cola Co.) y con la misma promoción → `Publicación` para los 4 SKUs.

Ver también `detecting-combos` y `extracting-multiple-products-per-image`.

### Producto sin precio en una grilla normal

Si en una grilla regular hay un producto sin precio (caso raro pero ocurre), clasificarlo como `Publicidad` aunque visualmente esté en formato Regular. **El criterio "sin precios" gana sobre el criterio visual de tamaño.**

### Múltiples destacados en una página

Una página puede tener varios productos clasificados como `Destacado`. No hay límite. Cada uno se evalúa por su tamaño relativo a los Regulars de la misma página.

## Diferencia con tipo_promocion

`tipo_oferta` describe **cómo se ve** el producto. `tipo_promocion_oferta` describe **qué descuento tiene**.

Un producto puede ser `Destacado` (imagen grande) y tener `tipo_promocion_oferta = "3X2"` al mismo tiempo. Son dimensiones independientes.

## Notas de diseño

### Por qué pasamos de 3 a 4 valores

En la versión anterior teníamos `Regular / Destacada / Publicación` (3 valores) y mezclábamos `Publicidad` con `Publicación`. David clarificó en la última iteración que son **4 valores distintos** y que `Publicidad` (sin precios) ≠ `Publicación` (bloque de fabricante con datos).

### Por qué el campo se llama tipo_oferta y no tipo_imagen

Es el nombre que usa David en el Excel canónico. En la versión anterior usábamos `tipo_imagen`. Cambio de nombre, mismo concepto.

### Por qué los nombres mezclan masculino y femenino

`Regular`, `Destacado`, `Publicidad`, `Publicación` — vienen así de los Excel de David. No normalizar el género; usar exactamente esos strings.
