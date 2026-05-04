---
name: flagging-for-review
description: Define los códigos canónicos del campo review_reasons y las condiciones para asignar cada uno. Esta skill estandariza cómo el agente marca productos para revisión humana, evitando que cada extracción use textos libres distintos para el mismo problema. Usar siempre que el agente necesite marcar un producto como needs_review.
---

# Flagging para Revisión Humana

## Rol

El agente debe marcar productos para revisión humana cuando hay datos faltantes, ambiguos o de baja confianza. Esta skill define los códigos canónicos que se usan en el campo `review_reasons` y cuándo aplicar cada uno.

## Por qué códigos canónicos y no texto libre

Si un producto va a revisión, el operador humano debe saber **qué** revisar y **por qué**. Si cada extracción genera textos libres distintos para el mismo problema (`"falta peso"`, `"sin gramaje"`, `"medida ilegible"`), el filtrado y priorización se vuelve imposible.

Códigos canónicos permiten:
- Filtrar productos por tipo de problema.
- Priorizar (ej: `EAN_NOT_FOUND` es revisión barata; `PRODUCT_NOT_RECOGNIZED` es cara).
- Agrupar para análisis (qué tipo de error es más frecuente).
- Automatizar reglas de routing (algunas revisiones puede hacer un junior, otras requieren un senior).

## Códigos canónicos

Los códigos van en SCREAMING_SNAKE_CASE.

### PRODUCT_NOT_RECOGNIZED

**Cuándo aplicar:** la imagen no permite identificar de qué producto se trata. Texto ilegible, imagen recortada, calidad muy baja, o el producto está parcialmente tapado por otro elemento gráfico.

**Acción típica del revisor:** mirar la página original, identificar el producto manualmente, completar campos faltantes.

### BRAND_NOT_RECOGNIZED

**Cuándo aplicar:** se ve que hay un producto pero la marca no es legible (logo cortado, texto borroso). El campo `marca` queda en `null`.

**No aplicar** si el producto claramente no tiene marca visible y eso es esperado (ej: frutas sueltas, productos genéricos).

### CATEGORY_NOT_DEFINED

**Cuándo aplicar:** no se puede asignar la categoría canónica del producto. Casos típicos:
- El producto cae fuera de la lista de categorías contratadas.
- La marca es cerrada sin categoría informada (caso ESPADOL — sin lista canónica).
- La categoría canónica genera ambigüedad entre dos opciones.

**Acción típica del revisor:** consultar la base maestra de GDSnet y asignar la categoría correcta.

### MEASURE_NOT_VISIBLE

**Cuándo aplicar:** no se puede leer la medida ni la unidad de medida del producto, ni en el folder ni en el packaging visible.

**No aplicar** si la unidad NO ES REQUERIDA (ej: categoría cerrada del tipo "yerbas todas" donde la medida no aplica).

### PRICE_AMBIGUOUS

**Cuándo aplicar:** hay un precio en la imagen pero:
- No se puede leer con certeza (números borrosos).
- No queda claro a qué producto pertenece.
- Hay múltiples precios sin contexto que permita asignarlos a los campos correctos.

### EAN_NOT_FOUND

**Cuándo aplicar:** el folder NO muestra el EAN visible Y el agente fue instruido para hacer matching contra el maestro de SKUs (no es el caso default — David indicó que el matching va en pipeline downstream).

**Estado actual:** **probablemente no se use desde el agente.** Lo dejamos en la lista por consistencia con el documento de David, pero en la arquitectura actual el matching vive en la integración. Revisar en la reunión del martes.

### METADATA_MISMATCH

**Cuándo aplicar:** la metadata recibida en el contexto del prompt contradice lo que se ve en la imagen. Casos típicos:
- Metadata dice `cadena: "COTO"` pero el logo en la imagen es de Carrefour.
- Metadata dice `pagina: 8` pero la imagen muestra un número distinto.
- Metadata da fechas pero la portada visible muestra otras.

**Acción típica del revisor:** verificar que la imagen corresponda al folder declarado.

### LOW_CONFIDENCE

**Cuándo aplicar:** caso "default" cuando el agente tiene dudas sobre la extracción pero no encaja en otro código específico. Ejemplos:
- Decisión borderline entre variedad y línea distinta.
- Abreviación ad-hoc en `descripcion` que no está en el diccionario canónico.
- Cualquier punto donde el agente "podría estar equivocándose pero no está seguro".

**Uso preferido:** combinarlo con un código más específico cuando aplique. Solo, sin contexto, es vago.

### MULTIPLE_SKUS_SHARED_CODE

**Cuándo aplicar:** la imagen muestra múltiples SKUs distintos compartiendo un mismo código de SKU interno (caso "Combiná 8X6" de Coca Cola con 4 productos y 2 códigos publicados).

**Acción típica del revisor:** confirmar qué SKU corresponde a cada código en la base maestra.

### COMBO_AMBIGUOUS

**Cuándo aplicar:** se detecta que dos productos están vendidos juntos pero no queda claro:
- Cuál es el Principal y cuál el Secundario.
- Si realmente es un combo o son productos independientes con precios cercanos.

### CLOSED_BRAND_WITHOUT_CATEGORY_LIST

**Cuándo aplicar:** caso ESPADOL — marca cerrada sin lista canónica de sus categorías. El agente registra una sola línea con `categoria: null` y agrega este código.

## Reglas de uso

### Combinación de códigos

Un producto puede tener múltiples códigos a la vez. Ejemplos válidos:

```json
"review_reasons": ["PRODUCT_NOT_RECOGNIZED", "MEASURE_NOT_VISIBLE"]
"review_reasons": ["LOW_CONFIDENCE", "COMBO_AMBIGUOUS"]
"review_reasons": ["BRAND_NOT_RECOGNIZED"]
```

### Coherencia con `needs_review`

- Si `review_reasons` está vacío → `needs_review: false`.
- Si `review_reasons` tiene al menos un código → `needs_review: true`.

### Cuándo NO marcar para revisión

No flagear un producto solo por preferencia o duda subjetiva. El producto debe tener un problema concreto y verificable. Algunos casos donde NO corresponde flag:

- El campo `descripcion_literal` está en `null` (David lo definió como opcional).
- Algunos campos de tarjeta están en `null` y la imagen claramente no menciona tarjetas.
- `id_sku_interno_spm` en `null` cuando la cadena no publica códigos internos.

### Códigos no listados

Si el agente identifica un caso problemático que no encaja en los códigos canónicos:

1. Usar `LOW_CONFIDENCE` como código.
2. Reportar el caso en la documentación del proyecto (CHANGELOG, issues).

**No inventar códigos nuevos en el output.** La lista canónica se actualiza explícitamente, no por extracciones individuales.

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

### Ejemplo 2: producto con datos completos pero medida no visible

```json
{
  "marca": "ARCOR",
  "descripcion": "ARCOR CARAMELOS",
  "medida": null,
  "u_medida": null,
  "precio_oferta": 850,
  "needs_review": true,
  "review_reasons": ["MEASURE_NOT_VISIBLE"]
}
```

### Ejemplo 3: combo ambiguo

```json
{
  "marca": "RAMAZZOTTI",
  "descripcion": "RAMAZZOTTI 750CC",
  "combo": "Principal",
  "needs_review": true,
  "review_reasons": ["COMBO_AMBIGUOUS"]
}
```

### Ejemplo 4: producto sin problemas

```json
{
  "marca": "COCA COLA",
  "descripcion": "COCA COLA ZERO 2,25L",
  "precio_oferta": 4085,
  "needs_review": false,
  "review_reasons": []
}
```

## Notas de diseño

### Por qué SCREAMING_SNAKE_CASE

Convención común para enums en sistemas backend. No tiene ambigüedad de mayúsculas/minúsculas, no tiene espacios, es procesable como key.

### Por qué array y no string concatenado

Múltiples problemas pueden coexistir. Array preserva la estructura. Si después la integración con GDS necesita un string, se concatena con join al exportar.

### Por qué algunos códigos se solapan

`LOW_CONFIDENCE` se solapa con casi todos los demás. Es intencional — sirve como fallback cuando el caso es borderline y permite combinar con otro código más específico para dar contexto.

### Por qué la lista es cerrada y no abierta

David tiene una nomenclatura interna ("corrección de tipo 2") que sugiere que en GDSnet hay una taxonomía formal de tipos de error. Cuando él confirme su esquema, alineamos los códigos canónicos. Hasta entonces, esta lista refleja lo que sabemos hoy.
