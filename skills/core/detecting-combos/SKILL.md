---
name: detecting-combos
description: Identifica productos que forman parte de un combo (oferta conjunta de dos productos por un precio único) y los registra correctamente en el JSON. Asigna el rol de Principal o Secundario, completa el campo carrier en el secundario con la descripción del principal, y maneja el caso de combos donde el secundario es de una marca o categoría no contratada por GDSnet. Usar cuando una imagen muestra dos o más productos vendidos juntos con un solo precio.
---

# Detección de Combos

## Rol

Cuando una imagen del catálogo muestra dos productos vendidos juntos por un precio único (un "combo"), tu trabajo es identificar el rol de cada uno y registrarlos según las convenciones de GDSnet.

## Cómo se reconoce un combo

Buscá señales visuales explícitas:
- La palabra **"Combo"** o **"Combiná"** en el bloque.
- Un símbolo de unión: **"+"** entre dos productos.
- Un **precio único** asociado a dos productos visibles.
- Layout que agrupa visualmente dos productos como una sola unidad de oferta.

**Si no hay señales explícitas, no asumas que es combo.** Dos productos en la misma página con el mismo precio pueden ser productos independientes, no combo.

## La regla de Principal y Secundario

Un combo siempre tiene un **Principal** (el SKU más relevante de la oferta) y un **Secundario** (el que acompaña).

### Cómo identificar al Principal

David lo definió en orden de prioridad:

1. **Por precio:** el SKU con mayor valor / precio. Si "Ramazzotti 750ml" cuesta $10500 solo y "Mumm" cuesta $3500 solo, el Principal es Ramazzotti.

2. **Si no hay precios visibles individuales:** vale el orden de la descripción en el catálogo. El primero que se nombra es el Principal.

   Ejemplo: el folder dice "Combo: Cerveza Heineken + Maní Sturla" sin desglose de precios → Heineken es Principal (se nombra primero), Maní Sturla es Secundario.

### Reglas de registro en el JSON

**El Principal:**
- `combo: "Principal"`
- `precio_oferta`: el precio del combo completo
- `carrier`: `null` (el principal no necesita carrier)
- Resto de campos: como cualquier producto extraído normalmente

**El Secundario:**
- `combo: "Secundario"`
- `precio_oferta`: `0` (su valor está incluido en el precio del Principal)
- `carrier`: la **descripción canónica del Principal** (ej: `"RAMAZZOTTI 750CC"`)
- Resto de campos: como cualquier producto extraído normalmente

### Ejemplo concreto

Folder muestra: "Ramazzotti 750ml + Mumm. Por $10500".

```json
[
  {
    "categoria": "APERITIVOS C/ALCOHOL",
    "marca": "RAMAZZOTTI",
    "descripcion": "RAMAZZOTTI 750CC",
    "medida": 750,
    "u_medida": "CC",
    "precio_oferta": 10500,
    "combo": "Principal",
    "carrier": null,
    ...
  },
  {
    "categoria": "ESPUMANTES",
    "marca": "MUMM",
    "descripcion": "MUMM",
    "medida": null,
    "u_medida": null,
    "precio_oferta": 0,
    "combo": "Secundario",
    "carrier": "RAMAZZOTTI 750CC",
    ...
  }
]
```

## Caso especial: Secundario de categoría no contratada

David lo aclaró textualmente: *"sólo se toman aquellos que forman parte de las categorías contratadas"*.

**Si el Secundario es de una categoría que GDSnet NO procesa para esta cadena:**

- **Solo se registra el Principal.**
- En el `carrier` del Principal, se anota la descripción del Secundario como referencia para el revisor humano.
- El Secundario NO se registra como producto separado.

**Cómo se ve en JSON:**

```json
[
  {
    "marca": "RAMAZZOTTI",
    "descripcion": "RAMAZZOTTI 750CC",
    "precio_oferta": 10500,
    "combo": "Principal",
    "carrier": "MUMM (combo, no contratada)",
    ...
  }
]
```

(El campo `carrier` excepcionalmente se completa en el Principal cuando el Secundario no se carga, para dejar trazabilidad).

**Cuándo aplica esto:**
- En la PoC actual, no tenemos la lista de categorías contratadas por cadena. Por defecto, **registrar siempre los dos productos del combo** (Principal y Secundario), y dejar que el pipeline de integración filtre downstream.
- Cuando esté disponible un mapeo de categorías por cadena (extensión futura de la skill `categorias-canonicas`), aplicar el filtro acá.

## Caso especial: Combos con más de 2 productos

Si un combo agrupa 3 o más productos:
1. **Identificar el Principal** (el de mayor precio, o el primero nombrado).
2. **Cada otro producto se registra como Secundario** con `carrier = descripción del Principal` y `precio_oferta = 0`.

## Casos que NO son combos

### Variedades del mismo producto en bloque

Una imagen con 4 latas de gaseosa Coca Cola distintas (Original, Zero, Light, Sin Azúcar) con un único precio "8X6" **NO es un combo**. Son **variedades** o **líneas distintas** según corresponda. Ver `extracting-multiple-products-per-image`.

### Productos del mismo fabricante en una Publicación

Un bloque "Kellogg's" con varios cereales del mismo fabricante con una promoción común NO es un combo. Es una **Publicación**. Ver `classifying-ad-type` y `handling-closed-brand-categories`.

### Dos productos en la misma página por casualidad

Dos productos lado a lado con precios distintos NO son un combo, son productos independientes. Solo es combo si hay señales explícitas (palabra "combo", símbolo "+", precio único).

## Coherencia con otras skills

- El campo `combo` interactúa directo con `carrier`: si `combo = "Secundario"` entonces `carrier` debe tener un valor; si `combo = null` entonces `carrier` debe ser `null`.
- El campo `precio_oferta` del Secundario es siempre `0` (no `null`), porque el precio existe pero está incluido en el Principal.

## Notas de diseño

### Por qué el Secundario lleva precio 0 y no null

`null` significa "no vimos un precio". `0` significa "el precio existe y es cero porque está absorbido por el Principal". David usa `0` explícito para los Secundarios en su Excel canónico — mantenemos esa convención.

### Por qué el carrier va en el Secundario y no en el Principal

David lo definió así: el Secundario referencia al Principal vía carrier. El Principal no necesita saber que es combo más allá del campo `combo: "Principal"`. La excepción es cuando el Secundario no se carga (categoría no contratada) — ahí el carrier va en el Principal para dejar trazabilidad.

### Por qué el orden de descripción es desempate cuando no hay precios

Es la regla que David escribió textualmente en el comentario del campo COMBO del Excel: *"Si no esta el precio vale el orden de la descripcion"*. No es interpretación nuestra.
