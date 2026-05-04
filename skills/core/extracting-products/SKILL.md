---
name: extracting-products
description: Extrae productos de imágenes de catálogos promocionales de supermercados argentinos, identificando todos los campos visibles (descripción, marca, precios, promociones, unidad de medida, categoría, tipo de oferta, tarjetas, variedades). Esta es la skill principal para procesar cada página de un catálogo. Aplica la regla fundamental de no inventar datos, valida la categoría contra la lista canónica de 74 categorías contratadas, separa medida y unidad de medida en campos distintos, y produce un JSON estructurado con una entrada por producto visible.
---

# Extracción de Productos de Catálogos

## Rol

Actuás como un analista experto en lectura de catálogos promocionales de supermercados argentinos. Tu trabajo es mirar una imagen de una página del folder y extraer todos los productos visibles con sus datos estructurados según el schema canónico de GDSnet.

## Regla absoluta: no inventar datos

Extraé solo lo que ves escrito o impreso en la imagen.

- Si un precio no se ve → `null`
- Si la unidad de medida no se ve → `null` (sin flag automático; ver "Cuándo flagear" más abajo)
- Si el porcentaje de descuento no se ve → `null`
- Si la marca no se ve → `null`
- Si un dato está borroso y no lo podés leer con certeza → `null`

No uses conocimiento general sobre productos argentinos para completar campos. No calcules precios que no están visibles. No derivés porcentajes que no están escritos. Un `null` es siempre mejor que un dato inventado.

### Excepción controlada: matching contra listas canónicas del cliente

La regla de "no inventar" aplica a **datos observables en la imagen**. No aplica a decisiones de matching contra listas canónicas provistas por el cliente, que son reglas de negocio explícitas.

El campo `categoria` se matchea contra `references/categorias-contratadas.md` (74 categorías canónicas) y se asigna el valor literal de esa lista. Si el match no es claro, el comportamiento sigue siendo el mismo: `null` + `CATEGORY_NOT_DEFINED` en `review_reasons`.

## Schema canónico de campos

Cada producto debe producirse con exactamente estos campos. El orden no importa pero los nombres sí (snake_case).

### 1. categoria

**El campo `categoria` debe ser literalmente igual a uno de los valores de `references/categorias-contratadas.md`.** Sin excepciones.

**Cómo asignarla:**
1. Mirar el producto y matchearlo contra la columna `CATEGORIA` del archivo de referencias.
2. Copiar el valor literal de la lista — respetar mayúsculas, acentos, y typos del archivo (`LIUSTRAMUEBLES`, `PREMEZCALAS DULCES`, `CAFÉ` con tilde, etc.).
3. Revisar la columna `NO INCLUYE` para descartar matches erróneos (ej: chocolate para taza NO va a CHOCOLATES; vino Patero NO va a VINOS).

**Si no se puede asignar con certeza:** `null` + agregar `CATEGORY_NOT_DEFINED` a `review_reasons`.

**Importante:** la categoría canónica NO es lo mismo que el título de sección impreso en la página del folder ni que la macro-categoría del footer de un bloque promocional. Si la página dice "GOLOSINAS" pero el producto es un alfajor, `categoria: "ALFAJORES"`. Si la categoría observada no figura en la lista canónica (ej: "BARRAS DE CEREAL", "LECHE LARGA VIDA", "AGUA MINERAL"), el agente debe dejar `categoria: null` y flagear, **no inventar una categoría que no está contratada**.

### 2. marca

La marca tal como aparece en la imagen.

- Mayúsculas, sin acentos, sin diéresis (`MULLER` no `Müller`).
- Si dice "Coca Cola", poner `"COCA COLA"`.
- Si hay múltiples marcas en un mismo bloque (ej: "Miller / Heineken / Imperial"), aplicar la skill `handling-closed-brand-categories`.
- Si no se ve: `null`.
- Si la marca claramente debería estar visible pero no se distingue (logo cortado, texto borroso): `null` + `BRAND_NOT_RECOGNIZED` en `review_reasons`.

### 3. descripcion

El SKU canónico. Construir **siempre** usando la skill `building-sku-description`.

- Formato: `MARCA + PRODUCTO/VARIEDAD + MEDIDA` (ej: `"COCA COLA ZERO 2,25L"`).
- Mayúsculas, sin acentos.
- Coma decimal (no punto).

**Preservar nombres comerciales de línea:** si el folder dice "7UP FREE", el SKU es `7UP FREE 1,5L`, no `7UP S/AZ 1,5L`. Los nombres comerciales (Free, Light, Diet, Zero, Original, Classic, Ultra, Black, etc.) son parte del nombre canónico del producto en la base maestra de GDSnet, y traducirlos rompe el match. Solo aplicar las abreviaciones del diccionario de `building-sku-description` cuando corresponde, pero no traducir nombres comerciales.

### 4. descripcion_literal

El texto del producto exactamente como aparece en el folder, sin normalizar.

- Útil para auditoría y trazabilidad.
- Si el folder dice "Coca Cola Zero — 2,25 lts (lata)", `descripcion_literal: "Coca Cola Zero — 2,25 lts (lata)"`.
- Si no aparece un texto literal claro: `null` (este campo no genera flag de revisión por estar vacío).

### 5. id_sku_interno_spm

Código interno que la cadena le pone al SKU, si está visible en el catálogo (ej: COTO publica códigos cortos como `Cod: 42210`).

- Si está visible: copiar tal cual.
- Si no está visible: `null`. No flagear — es esperable que muchas cadenas no lo publiquen.

### 6. ean

Código de barras (EAN) del producto, **solo si está visible en la imagen**.

- Si está visible: copiar tal cual (13 dígitos típicamente).
- Si no está visible: `null`. **No buscarlo en el maestro de SKUs** — eso es trabajo del pipeline de integración, no del agente.

### 7. medida

Cantidad numérica de la presentación.

- `2.25` para "2,25L"
- `750` para "750ml"
- `190` para "190g"
- Si no está visible: `null`. No flagear automáticamente.

**Importante:** este campo es solo número, sin unidad. La unidad va separada en `u_medida`.

### 8. u_medida

Unidad de medida con código canónico:

- `"GR"` — gramos
- `"KG"` — kilos
- `"CC"` — centímetros cúbicos / mililitros (David usa CC indistintamente con ML para bebidas líquidas)
- `"ML"` — mililitros
- `"L"` — litros
- `"UNI"` — unidades
- Si no se puede identificar: `null`. No flagear automáticamente.

**Si la medida no aparece visible en el frente del producto pero sí en el packaging,** mirar el packaging para extraerla (ej: "150g" impreso en la etiqueta del chocolate). Si tampoco está ahí, `null` sin flag.

### 9. pagina

Número de página del catálogo donde aparece el producto. Lo provee el orquestador en el contexto del prompt.

### 10. tipo_oferta

Cómo se presenta visualmente el producto en la página. Ver `classifying-ad-type`. Cuatro valores: `Regular`, `Destacado`, `Publicidad`, `Publicación`.

### 11. precio_oferta

Precio CON descuento. Solo el número. Si no se ve: `null`.

### 12. precio_anterior

Precio SIN descuento (precio regular o "antes"). Si no se ve: `null`. **Nunca calcularlo** a partir del precio de oferta + porcentaje.

### 13. precio_tarjeta_banco

Precio aplicando alguna tarjeta de banco específica. Si no hay precio asociado a tarjeta de banco visible: `null`.

### 14. precio_tarjeta_fidelidad

Precio aplicando tarjeta de fidelidad de la cadena. Si no hay: `null`.

### 15. tipo_promocion_oferta

Texto de la promoción base, formateado canónicamente. Ver `reading-promotions`. Si no hay: `null`.

### 16. tipo_promocion_tarjeta_fidelidad

Promoción adicional con tarjeta de fidelidad. Si no hay: `null`.

### 17. tipo_promocion_tarjeta_bancos

Promoción adicional con tarjeta bancaria. Si no hay: `null`.

### 18. combo

Si el producto es parte de un combo. Ver `detecting-combos`. Valores: `"Principal"`, `"Secundario"`, o `null`.

### 19. carrier

Si es secundario de combo: descripción del principal. En cualquier otro caso: `null`.

### 20. tarjeta_fidelidad

Nombre de la tarjeta de fidelidad asociada (ej: `"COMUNIDAD COTO"`). Solo registrar si la imagen lo muestra explícito. Si no se ve: `null`.

### 21. tarjeta_bancos

Nombre de las tarjetas bancarias asociadas (ej: `"MERCADO PAGO"`, `"MODO"`). Si no se ve: `null`.

### 22. tipo_variedad

Cuando la imagen presenta más de un SKU del mismo producto pero con distinto tipo, sabor o fragancia.

Valores canónicos: `"Varios sabores"`, `"Varias fragancias"`, `"Varios tipos"`. Si no aplica: `null`.

Ver `extracting-multiple-products-per-image` para la regla de variedades vs líneas distintas.

### 23. descripcion_variedad

Cuando la oferta afecta a categorías cerradas, registrar las categorías afectadas.

Ejemplo: "70% 2da unidad de shampoo y acondicionadores" → `descripcion_variedad: "Shampoo / Acondicionadores"`.

Si no aplica: `null`.

### 24. maximo_unidades

Máximo de unidades que el cliente puede comprar bajo esta promoción, si lo indica la oferta. Solo número. Si no especifica: `null`.

### 25. needs_review

Booleano. `true` si el producto necesita revisión humana, `false` si está completo y confiable.

Reglas:
- Si `review_reasons` está vacío → `needs_review: false`.
- Si `review_reasons` tiene al menos un código → `needs_review: true`.

### 26. review_reasons

Array de códigos canónicos. Ver la skill `flagging-for-review` para la lista completa.

Si no hay nada para revisar: `[]` (array vacío, **no** `null`).

## Cuándo flagear

Esta es la guía rápida de cuándo agregar un código a `review_reasons`. **Por default, no flagear.** Solo flagear cuando el caso encaja en uno de estos:

| Condición | Código a agregar |
|---|---|
| Imagen no permite identificar el producto | `PRODUCT_NOT_RECOGNIZED` |
| Marca claramente debería estar visible pero no se distingue | `BRAND_NOT_RECOGNIZED` |
| Categoría no matchea con ninguna de las 74 canónicas | `CATEGORY_NOT_DEFINED` |
| Hay un precio en la imagen que no se puede leer con certeza | `PRICE_AMBIGUOUS` |
| Marca cerrada sin lista de categorías (caso ESPADOL) | `CLOSED_BRAND_WITHOUT_CATEGORY_LIST` |
| Macro-categoría de footer no matchea con ninguna canónica | `MACRO_CATEGORY_UNMAPPED` |
| Combo donde no queda claro Principal vs Secundario | `COMBO_AMBIGUOUS` |
| Múltiples SKUs visibles compartiendo un solo código | `MULTIPLE_SKUS_SHARED_CODE` |
| Caso borderline general donde el agente tiene dudas | `LOW_CONFIDENCE` |

**Cuándo NO flagear:**
- Una medida no visible en un bloque tipo Publicación es esperado — no flagear.
- `id_sku_interno_spm` en `null` cuando la cadena no publica códigos internos — no flagear.
- `descripcion_literal` en `null` cuando no hay un texto literal claro — no flagear.
- Campos de tarjeta en `null` cuando la imagen no menciona tarjetas — no flagear.

## Situaciones especiales

### Productos sin precio visible (tipo Publicidad)

Crear la entrada con lo que sí se ve. Todos los campos de precio quedan en `null`. El tipo de oferta es `"Publicidad"`. Si hay un texto de promo (ej: "2X1"), igual se registra en `tipo_promocion_oferta`.

### Bloque tipo Publicación de un fabricante

Cuando una imagen presenta varios SKUs del mismo fabricante con datos publicados, ver `extracting-multiple-products-per-image` para distinguir si son **líneas distintas** (N registros) o **variedades** del mismo producto (1 registro con `tipo_variedad`).

### Combos

Ver `detecting-combos`.

### Categorías cerradas y bloques con footer macro-categoría

Ver `handling-closed-brand-categories`. **Cuando un bloque promocional tiene un footer macro-categoría (ej: "EN GOLOSINAS"), el agente debe descomponer la macro en las categorías canónicas que correspondan, generando un registro por cada una con `marca: "VARIAS MARCAS"`.**

### Productos no reconocibles

Si la imagen no permite identificar el producto, crear la entrada con los campos que se puedan leer, dejar el resto en `null`, y agregar `PRODUCT_NOT_RECOGNIZED` a `review_reasons`.

## Formato de respuesta

Ver la skill `formatting-output` para el formato exacto del JSON final.

## Notas de diseño

### Por qué la regla de "no inventar" está tan enfatizada

Los modelos de visión tienden a "completar" información usando conocimiento general. Si ven un producto Copa de Oro, saben que es de 820g aunque no lo lean. Esta tendencia hay que frenarla explícitamente.

### Por qué `categoria` se valida contra una lista cerrada

GDSnet trabaja con 74 categorías contratadas. Cualquier valor fuera de esa lista no tiene match downstream y termina en revisión manual. Validar contra la lista canónica desde la extracción evita generar registros con categorías inventadas (ej: `BARRAS DE CEREAL`, `LECHE LARGA VIDA`).

### Por qué `medida` y `u_medida` se separan

David lo pidió explícito en la última iteración del schema. Antes el campo era ambiguo (`"190g"` vs `"GR"`). Separados, la integración con la base maestra es más robusta.

### Por qué los tres tipos de promoción están separados

Una misma oferta puede tener: (a) descuento base, (b) descuento adicional con tarjeta de fidelidad, (c) descuento adicional con tarjeta bancaria. Mezclados en un solo campo se perdía info.

### Por qué la matching de EAN no es responsabilidad del agente

David lo dijo explícito: *"este proceso puede no hacerlo el agente y quedar del lado de la integración"*. El agente extrae lo que ve.

### Por qué se preservan los nombres comerciales de línea

"Free", "Light", "Zero", "Diet", etc. son parte del nombre del producto en la base maestra de GDS. Traducirlos a equivalentes funcionales (ej: "Free" → "S/AZ") rompe el match aunque la traducción sea semánticamente correcta.

### Por qué `review_reasons` es array y no string

Un mismo producto puede tener varios motivos de revisión. Array permite acumularlos sin perder info.
