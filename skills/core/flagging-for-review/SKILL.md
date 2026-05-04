---
name: flagging-for-review
description: Define los códigos canónicos del campo review_reasons y las condiciones para asignar cada uno. Esta skill estandariza cómo el agente marca productos para revisión humana, evitando que cada extracción use textos libres distintos para el mismo problema. Los códigos solo se aplican cuando el caso encaja con un problema concreto y verificable, no por cualquier campo en null.
---

# Flagging para Revisión Humana

## Rol

El agente marca productos para revisión humana cuando hay datos faltantes, ambiguos o de baja confianza **pero solo cuando el caso encaja con un problema concreto**. El default es no flagear: si un campo no es visible en la imagen, simplemente queda en `null` y se sigue.

## Filosofía

Si cada `null` generara un flag, el output del agente quedaría 100% flageado y la revisión humana pierde sentido. Los flags son señales: "acá hay algo que el agente vio pero no resolvió". No son señales de "acá hay algo que el agente no vio".

**No se flagea por:**
- Campos opcionales en `null` (descripcion_literal, id_sku_interno_spm, ean cuando no se publican).
- Medida o unidad no visibles en bloques tipo Publicación (es esperado).
- Tarjetas en `null` cuando la imagen no menciona tarjetas.
- Cualquier campo donde la ausencia es la señal correcta.

**Se flagea por:**
- El agente vio el producto pero no pudo resolver algún dato crítico (ej: marca borrosa).
- El agente detectó una situación que requiere conocimiento humano (ej: macro-categoría sin match canónico).
- El agente tomó una decisión que no está 100% seguro (ej: borderline entre variedad y línea distinta).

## Códigos canónicos

Lista cerrada. SCREAMING_SNAKE_CASE.

### PRODUCT_NOT_RECOGNIZED

**Cuándo aplicar:** la imagen no permite identificar de qué producto se trata. Texto ilegible, imagen recortada, calidad muy baja, o el producto está parcialmente tapado.

**Acción típica:** revisor mira la página original e identifica el producto manualmente.

### BRAND_NOT_RECOGNIZED

**Cuándo aplicar:** se ve que hay un producto pero la marca no es legible (logo cortado, texto borroso). El campo `marca` queda en `null`.

**No aplicar** si el producto claramente no tiene marca visible y eso es esperado (ej: frutas sueltas, productos genéricos).

### CATEGORY_NOT_DEFINED

**Cuándo aplicar:** no se puede asignar la categoría canónica del producto contra la lista de la skill `categorias-canonicas`. Casos típicos:
- El producto cae fuera de la lista de 74 categorías contratadas (ej: BARRAS DE CEREAL, LECHE LARGA VIDA).
- La categoría es ambigua entre dos opciones de la lista canónica.
- El producto cae en una exclusión explícita (columna NO INCLUYE).

**Acción típica:** revisor consulta la base maestra y asigna la categoría correcta o descarta el producto si no es contratada.

### PRICE_AMBIGUOUS

**Cuándo aplicar:** hay un precio en la imagen pero:
- No se puede leer con certeza (números borrosos).
- No queda claro a qué producto pertenece.
- Hay múltiples precios sin contexto que permita asignarlos a los campos correctos.

### MACRO_CATEGORY_UNMAPPED

**Cuándo aplicar:** el agente vio una macro-categoría en un footer de bloque promocional (ej: "EN ENCURTIDOS Y ESPECIAS") y al revisar la lista de la skill `categorias-canonicas` no encontró ninguna categoría canónica que corresponda razonablemente.

**Acción típica:** revisor decide si esa macro corresponde a una categoría canónica que el agente no detectó, o si simplemente no se carga porque GDS no la tiene contratada.

### COMBO_AMBIGUOUS

**Cuándo aplicar:** se detecta que dos productos están vendidos juntos pero no queda claro:
- Cuál es el Principal y cuál el Secundario.
- Si realmente es un combo o son productos independientes con precios cercanos.

### CLOSED_BRAND_WITHOUT_CATEGORY_LIST

**Cuándo aplicar:** caso ESPADOL — marca cerrada sin lista canónica de sus categorías. El agente registra una sola línea con `categoria: null` y agrega este código.

### MULTIPLE_SKUS_SHARED_CODE

**Cuándo aplicar:** la imagen muestra múltiples SKUs distintos compartiendo un mismo código de SKU interno (caso "Combiná 8X6" de Coca Cola con 4 productos y 2 códigos publicados).

**Acción típica:** revisor confirma qué SKU corresponde a cada código en la base maestra.

### LOW_CONFIDENCE

**Cuándo aplicar:** caso "default" cuando el agente tiene dudas sobre la extracción pero no encaja en otro código específico. Ejemplos:
- Decisión borderline entre variedad y línea distinta.
- Abreviación ad-hoc en `descripcion` que no está en el diccionario canónico.
- Cualquier punto donde el agente "podría estar equivocándose pero no está seguro".

**Uso preferido:** combinarlo con un código más específico cuando aplique. Solo, sin contexto, es vago.

## Reglas de uso

### Combinación de códigos

Un producto puede tener múltiples códigos a la vez. Ejemplos válidos:

```json
"review_reasons": ["PRODUCT_NOT_RECOGNIZED", "BRAND_NOT_RECOGNIZED"]
"review_reasons": ["LOW_CONFIDENCE", "COMBO_AMBIGUOUS"]
"review_reasons": ["CATEGORY_NOT_DEFINED"]
```

### Coherencia con `needs_review`

- Si `review_reasons` está vacío → `needs_review: false`.
- Si `review_reasons` tiene al menos un código → `needs_review: true`.

### Códigos no listados

Si el agente identifica un caso problemático que no encaja en los códigos canónicos:

1. Usar `LOW_CONFIDENCE` como código.
2. Reportar el caso en la documentación del proyecto (CHANGELOG, issues).

**No inventar códigos nuevos en el output.** La lista canónica se actualiza explícitamente.

## Ejemplos de uso

### Ejemplo 1: producto con texto borroso

```json
{
  "marca": null,
  "descripcion": null,
  "precio_oferta": 1500,
  "needs_review": true,
  "review_reasons": ["PRODUCT_NOT_RECOGNIZED", "BRAND_NOT_RECOGNIZED"]
}
```

### Ejemplo 2: producto con datos completos pero categoría no contratada

```json
{
  "categoria": null,
  "marca": "LA SERENISIMA",
  "descripcion": "LA SERENISIMA LECHES LARGA VIDA",
  "precio_oferta": null,
  "tipo_promocion_oferta": "3X2",
  "needs_review": true,
  "review_reasons": ["CATEGORY_NOT_DEFINED"]
}
```

### Ejemplo 3: macro-categoría sin match canónico

```json
{
  "categoria": null,
  "marca": "VARIAS MARCAS",
  "descripcion": null,
  "descripcion_literal": "EN ENCURTIDOS Y ESPECIAS",
  "tipo_promocion_oferta": "40%DTO",
  "needs_review": true,
  "review_reasons": ["MACRO_CATEGORY_UNMAPPED"]
}
```

### Ejemplo 4: producto sin problemas

```json
{
  "categoria": "GASEOSAS",
  "marca": "COCA COLA",
  "descripcion": "COCA COLA ZERO 2,25L",
  "precio_oferta": 4085,
  "needs_review": false,
  "review_reasons": []
}
```

### Ejemplo 5: producto en bloque Publicación sin medida visible

Esto **no se flagea** porque la falta de medida en bloques de Publicación es esperada:

```json
{
  "categoria": "CERVEZA",
  "marca": "ANTARES",
  "descripcion": "ANTARES CERVEZAS",
  "medida": null,
  "u_medida": null,
  "tipo_oferta": "Publicación",
  "tipo_promocion_oferta": "40%DTO",
  "needs_review": false,
  "review_reasons": []
}
```

## Notas de diseño

### Por qué eliminamos METADATA_MISMATCH

En la versión anterior el agente flageaba cuando la metadata recibida del orquestador no coincidía con lo visible en la imagen. Esto generaba demasiado ruido (todos los productos del mismo folder llevaban el flag) y la metadata como concepto fue descartada para esta versión del agente.

### Por qué eliminamos MEASURE_NOT_VISIBLE como auto-flag

La ausencia de medida no es un problema en sí. En bloques tipo Publicación las medidas no se publican y eso es esperado. Si después en producción aparece un caso donde la medida debería estar y no está, lo agregamos como flag específico, pero no como default.

### Por qué SCREAMING_SNAKE_CASE

Convención común para enums. No tiene ambigüedad de mayúsculas, no tiene espacios.

### Por qué array y no string concatenado

Múltiples problemas pueden coexistir. Array preserva la estructura.
