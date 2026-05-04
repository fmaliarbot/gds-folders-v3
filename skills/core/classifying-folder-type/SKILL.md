---
name: classifying-folder-type
description: Clasifica el tipo de catálogo (folder) entre los 3 valores canónicos de GDSnet — Regular, Especial o Flyers — basado en su contenido visual y semántica. Útil para el campo tipo_folder de la metadata del catálogo. Cuando el agente solo ve una página individual, esta skill puede no aplicar (el agente no tiene visibilidad del catálogo completo). En ese caso, dejar el campo en null.
---

# Clasificación del Tipo de Folder

## Rol

Asignás al campo `tipo_folder` de la metadata uno de tres valores canónicos según las convenciones de GDSnet. Esta clasificación afecta cómo se procesa el catálogo y cómo se carga en el sistema.

## Los 3 valores canónicos

### 1. Regular

**Definición:** catálogo semanal de una cadena con datos generales de varias categorías.

**Cómo identificarlo:**
- Cubre múltiples categorías de productos (almacén, bebidas, perfumería, lácteos, etc.).
- Se publica con frecuencia regular (semanal, quincenal).
- Es el catálogo "principal" de la cadena.

**Ejemplos:**
- COTO Almacén y Bebidas (semanal)
- COTO Super Finde
- JUMBO Extremo
- DIARCO "Todos pueden comprar"

### 2. Especial

**Definición:** catálogo focalizado, ya sea por categoría, fabricante o evento específico.

**Cómo identificarlo:**
- Se enfoca en **una sola categoría** o un par de categorías que comparten sector (ej: Perfumería + Limpieza, Chocolates + Caramelos, Solo Bebidas).
- Representa **un solo grupo específico de fabricantes** (ej: solo Mondelez, solo Arcor, solo Unilever).
- Cubre **fechas/eventos especiales** (Día de la Madre, Día del Amigo, Mes de los Enamorados, especiales de fiestas).
- **Marcas propias del supermercado** (ej: catálogo "Marcas Coto", "San Remo en Yaguar").

**Ejemplos:**
- "ELEGI NUESTRAS MARCAS PROPIAS" (YAGUAR — son productos San Remo, marca propia del mayorista).
- "DIA DE LA MADRE 2026" (especial por evento).
- "PERFUMERIA Y LIMPIEZA" (especial por categoría).
- "LACTEOS DEL MES" (especial por categoría).

### 3. Flyers

**Definición:** publicación corta y ocasional que pertenece **solamente a un fabricante**.

**Cómo identificarlo:**
- **Solo una marca** o fabricante en todo el folder.
- Generalmente **una o pocas hojas** (1-4 páginas).
- **Ocasional** (no sigue patrón semanal).
- Distribuido por la cadena pero el contenido es 100% del fabricante.

**Ejemplos:**
- "UNILEVER" (folder completo, 1-2 páginas, solo productos Unilever).
- "Promo Coca Cola Verano".

**Diferencia clave con Especial de un fabricante:**
- Un folder **Especial** puede tener varias páginas, ser parte del calendario regular de la cadena, y representar a un fabricante grande con muchas marcas.
- Un folder **Flyers** es ocasional, corto, y muy focalizado.

Si la diferencia es ambigua, el largo y la frecuencia son el desempate: pocas páginas + ocasional → Flyers. Muchas páginas + parte del calendario → Especial.

## Cómo aplicar esta skill

Esta skill **idealmente** se aplica con visibilidad del catálogo completo (cantidad de páginas, distribución de categorías, frecuencia de publicación). Cuando el agente procesa **una sola página** y no tiene esa información, el campo `tipo_folder` debe quedar en `null` y la metadata se completará downstream.

**Casos donde el agente puede inferir desde una sola página:**

- La portada del folder dice explícito "Catálogo semanal" o "Día de la Madre" o el nombre comercial habitual de la cadena (ej: "SUPER FINDE", "JUMBO EXTREMO") — Regular.
- La página completa muestra una sola marca y dice "Flyer" o "Promoción de [marca]" — Flyers.
- La página dice "Marcas propias" o nombra explícito un set de fabricantes específicos — Especial.

En cualquier otro caso desde una sola página: `null`.

## Notas de diseño

### Por qué los 3 nombres son canónicos

Son los strings exactos que David usa en su Excel canónico (`Regulares`, `Especiales`, `Flyers`). Notar que el Excel usa plural (`"Regulares"`) pero el documento de ajustes menciona singular (`"regular"`). Convención: usar **plural en mayúsculas**: `"REGULAR"`, `"ESPECIAL"`, `"FLYERS"`. (Esto se ajusta cuando David confirme en la reunión).

### Por qué "marcas propias del supermercado" caen en Especial y no Flyers

Aunque parezcan Flyers (un solo fabricante = el supermercado mismo), David lo aclaró en el comentario del Excel: *"También son aquellos que se publican en fechas especiales: ... marcas propias del supermercado, etc."*. Caen en Especial.

### Por qué un Flyers puede tener una sola marca pero un Especial también

La diferencia es **el contexto** y **la frecuencia**, no solo el contenido. Un Especial es una pieza del calendario regular de comunicación de la cadena, aunque sea de un solo fabricante (ej: Especial Unilever del mes). Un Flyers es ocasional y no parte del calendario.

Cuando David te confirme la lista de publicadores con sus frecuencias (en `references/publicadores.md`), esta clasificación se vuelve más automática.
