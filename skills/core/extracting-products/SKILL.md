---
name: extracting-products
description: Skill principal del agente. Define el schema de los 26 campos a extraer de cada producto en una imagen de catálogo, las reglas globales de extracción (no inventar, validar categoría contra lista canónica, preservar nombres comerciales), y el formato canónico de los valores. Esta es la primera skill que el agente debe leer y la fuente de verdad para todas las reglas semánticas. Otras skills auxiliares (reading-prices, reading-promotions, etc.) extienden estas reglas con detalle de casos específicos pero no las contradicen.
---

# Extracción de Productos de Catálogos

## Rol

Mirás una imagen de una página de un catálogo promocional argentino y extraés todos los productos visibles, devolviendo un array JSON con un objeto por producto siguiendo el schema canónico de GDSnet.

## Reglas globales del agente

Estas reglas son la base de todo lo que hace el agente. Aplican a **todas las skills** y a **todos los campos del schema** salvo que una skill específica las extienda explícitamente.

### Regla 1 — No inventar datos

Extraé solo lo que ves escrito o impreso en la imagen.

- Precio no visible → `null`
- Unidad de medida no visible → `null`
- Porcentaje de descuento no visible → `null`
- Marca no visible → `null`
- Dato borroso que no podés leer con certeza → `null`

No usés conocimiento general para completar campos observables. No calculés precios que no están visibles. No derivés porcentajes que no están escritos. **Un `null` es siempre mejor que un dato inventado.**

Esta regla aplica universalmente — todas las demás skills la respetan. Si alguna skill parece contradecirla, prevalece esta regla.

#### Excepción controlada — campo `categoria`

La regla "no inventar" aplica a datos observables. **NO aplica a decisiones de matching contra listas canónicas del cliente**, que son reglas de negocio explícitas.

Para el campo `categoria`, el agente puede usar conocimiento general sobre marcas argentinas conocidas si todas estas condiciones se cumplen:

1. La marca es claramente reconocible (logo legible).
2. La marca opera predominantemente en una sola categoría canónica.
3. La categoría inferida figura literalmente en `references/categorias-contratadas.md`.
4. El producto NO tiene descriptor textual ni packaging visible que contradiga la inferencia.

Cuando aplicás esta inferencia, **agregá `LOW_CONFIDENCE` a `review_reasons`**. Marca claramente que la asignación viene de conocimiento del agente, no de evidencia visual directa.

NO inferir cuando la marca opera en múltiples categorías (Nestlé, Unilever, La Serenísima), cuando la marca es desconocida, o cuando la categoría que correspondería NO está en la lista canónica.

**Tabla de ejemplos** (basada en folders reales procesados):

| Marca vista | Razonamiento | Acción |
|---|---|---|
| ANTARES (logo) | Cervecería argentina, opera solo en cerveza | `categoria: "CERVEZA"` + `LOW_CONFIDENCE` |
| VILEDA (logo) | Productos de limpieza | `categoria: "LIMPIADORES Y MULTIUSOS"` + `LOW_CONFIDENCE` |
| PATITO (logo) | Detergentes / jabón blanco | `categoria: "DETERGENTES"` + `LOW_CONFIDENCE` |
| GORDON'S LATAS | Gin Gordon's en lata = bebida lista para tomar | `categoria: "RTD"` + `LOW_CONFIDENCE` |
| FIORENTINA | Marca poco conocida o ambigua | `categoria: null` + `LOW_CONFIDENCE` |
| KOTEX | Higiene femenina, NO contratada | `categoria: "CATEGORIA NO CONTRATADA"` + `CATEGORY_NOT_DEFINED` |
| NUTRILON | Leche infantil, NO contratada | `categoria: "CATEGORIA NO CONTRATADA"` + `CATEGORY_NOT_DEFINED` |
| NESTLÉ PUREZA VITAL | Nestlé es multi-rubro; AGUA MINERAL no está contratada | `categoria: "CATEGORIA NO CONTRATADA"` + `CATEGORY_NOT_DEFINED` |
| LA SERENISIMA | Multi-categoría; LECHE LARGA VIDA no está contratada | `categoria: "CATEGORIA NO CONTRATADA"` + `CATEGORY_NOT_DEFINED` |

### Regla 2 — Preservar nombres comerciales de línea

Si el folder dice "7UP FREE", el SKU es `7UP FREE`, no `7UP S/AZ`. Si dice "Coca Cola Zero", es `COCA COLA ZERO`, no `COCA COLA S/AZ`.

Aunque "Free" y "Zero" sean equivalentes funcionales de "sin azúcar", los nombres comerciales son parte del nombre del producto en la base maestra de GDSnet. Traducirlos rompe el match aunque la traducción sea semánticamente correcta.

Nombres comerciales que SE preservan tal cual: `FREE`, `ZERO`, `LIGHT`, `DIET`, `ULTRA`, `BLACK`, `ORIGINAL`, `CLASSIC`, `MAX`, `PRO`, `PLUS`. Lista no exhaustiva — la regla es "si es un nombre comercial de línea, no traducir".

Las abreviaciones del diccionario (`LIQ` para "Líquido", etc., en `building-sku-description`) sí se aplican, porque son convenciones de naming del agente, no traducciones de nombres comerciales.

### Regla 3 — Validar categoría contra lista canónica

El campo `categoria` debe ser **literalmente** uno de los valores de `references/categorias-contratadas.md` (74 categorías), o el literal `"CATEGORIA NO CONTRATADA"` cuando el producto está fuera de scope. Sin otros valores permitidos.

Respetar mayúsculas, acentos y typos del archivo (ej: `LIUSTRAMUEBLES`, `PREMEZCALAS DULCES`, `CAFÉ` con tilde). Revisar la columna `NO INCLUYE` para descartar matches erróneos (chocolate para taza NO va a CHOCOLATES, vino Patero NO va a VINOS).

**Cómo decidir el valor:**

- Producto matchea claramente con una de las 74 → usar ese valor literal.
- Producto **fuera de las 74** (ej: BARRAS DE CEREAL, LECHE LARGA VIDA, AGUA MINERAL) → `categoria: "CATEGORIA NO CONTRATADA"` + `CATEGORY_NOT_DEFINED` en `review_reasons`.
- Producto cae en una **exclusión explícita** (columna `NO INCLUYE` — chocolate para taza, vino Patero) → también `categoria: "CATEGORIA NO CONTRATADA"` + `CATEGORY_NOT_DEFINED`.
- Categoría **ambigua entre dos opciones de la lista canónica** (no es que esté fuera de scope, no podés decidir cuál de las 74 aplica) → `categoria: null` + `LOW_CONFIDENCE`. Diferenciar de "no contratada".
- Producto no identificable (imagen ilegible) → `categoria: null` + `PRODUCT_NOT_RECOGNIZED` (regla 1, no inventar).

### Regla 4 — Tarjetas de fidelidad y bancos: por SKU, no por bloque

`tarjeta_fidelidad` y `tarjeta_bancos` se completan **SOLO cuando el badge gráfico aparece directamente sobre o junto al SKU concreto**.

- ❌ NO asumir por bloque promocional ni por proximidad
- ❌ NO asumir por ser folder de una cadena que tiene tarjeta (ej: COTO con Comunidad COTO)
- ❌ NO asumir aunque marcas vecinas tengan el badge visible
- ✓ SOLO completar cuando el badge está visible **al lado o sobre el SKU concreto**

Si algunos SKUs de un bloque tienen el badge y otros no, eso es información significativa: la promoción aplica a algunos, no a todos. El agente debe respetar esa distinción literalmente. Ver la skill `coto` para el ejemplo crítico real de este patrón.

### Regla 5 — Por defecto no flagear

`needs_review` y `review_reasons` solo se activan cuando hay un problema concreto y verificable. Un campo en `null` por sí solo NO es un flag — es la respuesta correcta a "el dato no se ve". Ver `flagging-for-review` para los códigos canónicos y cuándo aplicarlos.

## Schema canónico — los 26 campos

El array de productos del JSON final tiene un objeto por producto. Cada objeto debe tener exactamente estos 26 campos. Detalles de cada uno abajo.

| # | Campo | Tipo | Skill que lo cubre |
|---|---|---|---|
| 1 | `categoria` | string \| null | esta skill (validar contra lista canónica) |
| 2 | `marca` | string \| null | esta skill |
| 3 | `descripcion` | string \| null | `building-sku-description` |
| 4 | `descripcion_literal` | string \| null | esta skill |
| 5 | `id_sku_interno_spm` | string \| null | esta skill |
| 6 | `ean` | string \| null | esta skill |
| 7 | `medida` | number \| null | esta skill |
| 8 | `u_medida` | string \| null | esta skill |
| 9 | `pagina` | number | provisto por el orquestador |
| 10 | `tipo_oferta` | string | `classifying-ad-type` |
| 11 | `precio_oferta` | number \| null | `reading-prices` |
| 12 | `precio_anterior` | number \| null | `reading-prices` |
| 13 | `precio_tarjeta_banco` | number \| null | `reading-prices` |
| 14 | `precio_tarjeta_fidelidad` | number \| null | `reading-prices` |
| 15 | `tipo_promocion_oferta` | string \| null | `reading-promotions` |
| 16 | `tipo_promocion_tarjeta_fidelidad` | string \| null | `reading-promotions` |
| 17 | `tipo_promocion_tarjeta_bancos` | string \| null | `reading-promotions` |
| 18 | `combo` | "Principal" \| "Secundario" \| null | `detecting-combos` |
| 19 | `carrier` | string \| null | `detecting-combos` |
| 20 | `tarjeta_fidelidad` | string \| null | esta skill (regla 4) |
| 21 | `tarjeta_bancos` | string \| null | esta skill (regla 4) |
| 22 | `tipo_variedad` | string \| null | `extracting-multiple-products-per-image` |
| 23 | `descripcion_variedad` | string \| null | `handling-closed-brand-categories` |
| 24 | `maximo_unidades` | number \| null | esta skill |
| 25 | `needs_review` | boolean | `flagging-for-review` |
| 26 | `review_reasons` | array | `flagging-for-review` |

## Detalle de los campos cubiertos por esta skill

### marca

La marca como aparece en la imagen, en mayúsculas y sin acentos.

- "Coca Cola" → `"COCA COLA"`
- "Müller" → `"MULLER"`
- Si la marca claramente debería estar visible pero no se distingue (logo cortado, texto borroso): `null` + `BRAND_NOT_RECOGNIZED` en `review_reasons`.
- Si hay múltiples marcas en un mismo bloque, ver `handling-closed-brand-categories`.

### descripcion_literal

Texto del producto exactamente como aparece en el folder, sin normalizar.

- Útil para auditoría y trazabilidad.
- Folder: "Coca Cola Zero — 2,25 lts (lata)" → `descripcion_literal: "Coca Cola Zero — 2,25 lts (lata)"`
- Si no aparece un texto literal claro: `null`. **No genera flag** por estar vacío.

### id_sku_interno_spm

Código interno que la cadena le pone al SKU, si está visible (algunas cadenas como COTO publican códigos cortos, ej: `Cod: 42210`).

- Si está visible: copiar tal cual.
- Si no está visible: `null`. **No flagear** — es esperable que muchas cadenas no lo publiquen.

### ean

Código de barras, **solo si está visible en la imagen**.

- Si está visible: copiar tal cual (13 dígitos típicamente).
- Si no está visible: `null`. **No buscarlo en el maestro de SKUs** — eso es trabajo del pipeline downstream.

### medida y u_medida

Cantidad numérica + unidad, separadas en dos campos.

**`medida`:** número (entero o decimal). Ej: `2.25` para "2,25L", `190` para "190g", `25` para "25 unidades". Si no se ve: `null`.

**`u_medida`:** código canónico:
- `"GR"` — gramos
- `"KG"` — kilos
- `"CC"` — centímetros cúbicos / mililitros (David usa CC indistintamente con ML para bebidas líquidas envasadas)
- `"ML"` — mililitros
- `"L"` — litros
- `"UNI"` — unidades
- Si no se puede identificar: `null`.

Si la medida no aparece visible en el frente del producto pero sí en el packaging, mirar el packaging para extraerla. Si no está ahí tampoco, `null` sin flag (ausencia esperada en muchos bloques tipo Publicación).

### maximo_unidades

Máximo de unidades que el cliente puede comprar bajo esta promoción, si lo indica la oferta. Solo número (ej: `4`, `6`). Si no especifica: `null`.

## Cuándo flagear (resumen)

Solo flagear cuando el caso encaja con un problema concreto:

| Condición | Código a agregar |
|---|---|
| Imagen no permite identificar el producto | `PRODUCT_NOT_RECOGNIZED` |
| Marca claramente debería estar visible pero no se distingue | `BRAND_NOT_RECOGNIZED` |
| Categoría no matchea con ninguna canónica | `CATEGORY_NOT_DEFINED` |
| Categoría inferida por conocimiento general | `LOW_CONFIDENCE` |
| Hay un precio pero no se puede leer con certeza | `PRICE_AMBIGUOUS` |
| Marca cerrada sin lista de categorías (caso ESPADOL) | `CLOSED_BRAND_WITHOUT_CATEGORY_LIST` |
| Macro-categoría de footer no matchea con canónica | `MACRO_CATEGORY_UNMAPPED` |
| Combo donde no queda claro Principal vs Secundario | `COMBO_AMBIGUOUS` |
| Múltiples SKUs visibles compartiendo un solo código | `MULTIPLE_SKUS_SHARED_CODE` |
| Caso borderline general | `LOW_CONFIDENCE` |

Ver `flagging-for-review` para detalle completo de cada código.

**Cuándo NO flagear:**
- Una medida no visible en bloque tipo Publicación.
- `id_sku_interno_spm` en `null` cuando la cadena no publica códigos.
- `descripcion_literal` en `null` cuando no hay texto literal claro.
- Tarjetas en `null` cuando la imagen no muestra badges.

## Skills auxiliares — cuándo cargarlas

El agente carga skills auxiliares según el caso del producto que está procesando:

- **Productos individuales con precio y descripción clara** → solo `extracting-products` + `building-sku-description` + `reading-prices` + `reading-promotions` + `formatting-output`.
- **Productos en combo (2+ productos con precio único)** → además `detecting-combos`.
- **Productos en bloque tipo Publicación o categoría cerrada con marcas listadas** → además `handling-closed-brand-categories` y `extracting-multiple-products-per-image`.
- **Productos en folder de una cadena con skill específica** (ej: COTO) → además la skill de cadena.
- **Productos donde hay que decidir si flagear** → `flagging-for-review`.

## Formato del JSON final

Ver la skill `formatting-output` para la estructura exacta del JSON, validaciones sintácticas, y reglas finales antes de emitir.

## Notas de diseño

### Por qué centralizamos las reglas globales en esta skill

Antes las reglas "no inventar", "preservar nombres comerciales", "tarjetas por SKU", etc. estaban repetidas en 5+ skills distintas. Cuando aplicamos updates las modificábamos en una y se quedaban viejas en otras, generando contradicciones. Ahora viven solo acá.

### Por qué `medida` y `u_medida` se separan

Antes el campo era ambiguo (`"190g"` mezclando número y unidad). Separados, la integración con la base maestra de GDS es más robusta.

### Por qué hay 4 campos de precio y 3 de promoción

Es el schema canónico de GDSnet. Las cadenas argentinas frecuentemente ofrecen tres dimensiones simultáneas: descuento base, descuento adicional con tarjeta de fidelidad, descuento adicional con tarjeta bancaria. Mezclados en un solo campo se perdía info.

### Por qué la matching de EAN no es responsabilidad del agente

David lo dijo explícito: *"este proceso puede no hacerlo el agente y quedar del lado de la integración"*. El agente extrae lo que ve. Si no hay EAN visible, deja `null` y el pipeline downstream hace el lookup.
