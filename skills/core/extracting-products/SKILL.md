---
name: extracting-products
description: Extrae productos de imágenes de catálogos promocionales de supermercados argentinos, identificando todos los campos visibles (descripción, marca, precios, promociones, unidad de medida, categoría, tipo de oferta, tarjetas, variedades). Esta es la skill principal para procesar cada página de un catálogo. Aplica la regla fundamental de no inventar datos, separa medida y unidad de medida en campos distintos, soporta tarjetas bancarias y de fidelidad, y produce un JSON estructurado con una entrada por producto visible. Marca productos para revisión humana cuando hay datos faltantes o ambiguos.
---

# Extracción de Productos de Catálogos

## Rol

Actuás como un analista experto en lectura de catálogos promocionales de supermercados argentinos. Tu trabajo es mirar una imagen de una página del folder y extraer todos los productos visibles con sus datos estructurados según el schema canónico de GDSnet.

## Regla absoluta: no inventar datos

Extraé solo lo que ves escrito o impreso en la imagen.

- Si un precio no se ve → `null`
- Si la unidad de medida no se ve → `null`
- Si el porcentaje de descuento no se ve → `null`
- Si la marca no se ve → `null`
- Si un dato está borroso y no lo podés leer con certeza → `null`
- Si tenés que decidir entre dejar `null` o adivinar, dejá `null` y agregá la razón a `review_reasons`.

No uses conocimiento general sobre productos argentinos para completar campos. No calcules precios que no están visibles. No derivés porcentajes que no están escritos. Un `null` es siempre mejor que un dato inventado.

### Excepción controlada: matching contra listas canónicas del cliente

La regla de "no inventar" aplica a **datos observables en la imagen**. No aplica a decisiones de matching contra listas canónicas provistas por el cliente, que son reglas de negocio explícitas.

El único caso en esta skill donde esto aplica es el campo `categoria`: el agente matchea el producto contra la lista oficial de categorías contratadas (cuando esté disponible) y asigna el valor canónico correspondiente, aunque la categoría no esté escrita literal en la imagen. Si el match no es claro, el comportamiento sigue siendo el mismo: `null` y `CATEGORY_NOT_DEFINED` en `review_reasons`.

## Schema canónico de campos

Cada producto debe producirse con exactamente estos campos. El orden no importa pero los nombres sí (snake_case).

### 1. categoria

La categoría canónica de GDSnet (ej: `"GASEOSAS"`, `"CHOCOLATES"`, `"YERBA MATE"`).

**Cómo asignarla:**
1. Mirar el producto y matchearlo contra `references/categorias-contratadas.md` (cuando exista).
2. Copiar el valor literal de la lista (mayúsculas, acentos, typos del archivo, todo igual).
3. Revisar exclusiones de la lista (ej: chocolate para taza NO va a CHOCOLATES; vino Patero NO va a VINOS).

**Si no se puede asignar con certeza:** `null` + agregar `CATEGORY_NOT_DEFINED` a `review_reasons`.

**Importante:** la categoría canónica NO es lo mismo que el título de sección impreso en la página del folder. Si la página dice "Bebidas" pero el producto es un vino, `categoria: "VINOS"`.

### 2. marca

La marca tal como aparece en la imagen.

- Si dice "Coca Cola", poner `"COCA COLA"` (siempre mayúsculas).
- Si hay múltiples marcas en un mismo bloque (ej: "Miller / Heineken / Imperial"), aplicar la skill `handling-closed-brand-categories` y desagregar.
- Si no se ve: `null` + `BRAND_NOT_RECOGNIZED` en `review_reasons` cuando sea relevante (ej: cuando claramente debería haber marca pero no se distingue).

### 3. descripcion

El SKU canónico. Construir **siempre** usando la skill `building-sku-description`.

- Formato: `MARCA + PRODUCTO/VARIEDAD + MEDIDA` (ej: `"COCA COLA ZERO 2,25L"`, `"NESCAFE GOLD 95G"`).
- Mayúsculas, sin acentos.
- Coma decimal (no punto).

Nunca copiar el texto literal del folder sin pasarlo por las convenciones de `building-sku-description`.

### 4. descripcion_literal

El texto del producto exactamente como aparece en el folder, sin normalizar.

- Útil para auditoría y trazabilidad.
- Si el folder dice "Coca Cola Zero — 2,25 lts (lata)", `descripcion_literal: "Coca Cola Zero — 2,25 lts (lata)"`.
- Si no aparece un texto literal claro: `null` (este campo no genera flag de revisión por estar vacío, según David).

### 5. id_sku_interno_spm

Código interno que la cadena le pone al SKU, si está visible en el catálogo (algunas cadenas como YAGUAR los publican explícitamente, ej: `70924`).

- Si está visible: copiar tal cual (puede ser número o string con guiones cuando hay múltiples códigos compartidos, ej: `"86149-86150-86151-86152"`).
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
- `25` para "25 unidades"
- Si no está visible: `null`.

**Importante:** este campo es solo número, sin unidad. La unidad va separada en `u_medida`.

### 8. u_medida

Unidad de medida con código canónico:

- `"GR"` — gramos
- `"KG"` — kilos
- `"CC"` — centímetros cúbicos / mililitros (David usa CC indistintamente con ML; mantener CC cuando se trate de bebidas en líquido envasado, salvo que el folder diga ML explícito)
- `"ML"` — mililitros
- `"L"` — litros
- `"UNI"` — unidades
- Si no se puede identificar: `null` + `MEASURE_NOT_VISIBLE` en `review_reasons`.

**Si la medida no aparece visible en el frente del producto pero sí en el packaging,** mirar el packaging para extraerla (ej: "150g" impreso en la etiqueta del chocolate). Si tampoco está ahí, `null` + flag.

### 9. pagina

Número de página del catálogo donde aparece el producto. Lo provee el orquestador en el contexto del prompt — no lo inferir.

### 10. tipo_oferta

Cómo se presenta visualmente el producto en la página. Ver la skill `classifying-ad-type`. Cuatro valores posibles:

- `"Regular"` — formato normal, tamaño clásico
- `"Destacado"` — tamaño mayor a lo normal, ocupa más espacio
- `"Publicidad"` — sin precios ni porcentajes de descuento
- `"Publicación"` — grupo de SKUs del mismo fabricante con alguna variable de oferta

### 11. precio_oferta

Precio CON descuento. Generalmente el más prominente.

- Solo el número, sin símbolo `$`.
- Aceptar decimales (ej: `4085`, `189.99`, `1799.9`).
- Si no se ve: `null`.

### 12. precio_anterior

Precio SIN descuento (precio regular o "antes").

- Suele aparecer tachado, en chico, o con leyenda "Antes" / "Precio regular" / "P. Lista".
- Si no se ve: `null`. **Nunca calcularlo a partir del precio de oferta + porcentaje.**

### 13. precio_tarjeta_banco

Precio aplicando alguna tarjeta de banco específica (Mercado Pago, Visa, Mastercard, etc.).

- Solo el número.
- Si no hay precio asociado a tarjeta de banco visible: `null`.

### 14. precio_tarjeta_fidelidad

Precio aplicando tarjeta de fidelidad de la cadena (Comunidad Coto, Mi Carrefour, Cencopay, etc.).

- Solo el número.
- Si no hay: `null`.

### 15. tipo_promocion_oferta

Texto de la promoción base (sin tarjeta), tal como aparece en la imagen.

Ejemplos: `"3X2"`, `"35%DTO"`, `"70% DTO 2DA U"`, `"25%DTO LLEVANDO 2"`, `"8X6"`, `"2DO AL 50%"`, `"OFERTA"`.

Si no hay texto de promoción visible: `null`.

**Importante:** Si la imagen muestra una promoción (como "2x1"), registrarla SIEMPRE, incluso si el producto es tipo `"Publicidad"` (sin precios). La promoción es un dato visible independiente del precio.

### 16. tipo_promocion_tarjeta_fidelidad

Texto de la promoción adicional usando tarjeta de fidelidad.

Ejemplos: `"5% DTO"`, `"10%DTO"`, `"4X2"`.

Si no hay: `null`.

### 17. tipo_promocion_tarjeta_bancos

Texto de la promoción adicional usando tarjeta de banco.

Si no hay: `null`.

### 18. combo

Si el producto es parte de un combo. Ver la skill `detecting-combos`.

Valores: `"Principal"`, `"Secundario"`, o `null`.

### 19. carrier

Si el producto es el secundario de un combo, la descripción del SKU principal va acá. Ver la skill `detecting-combos`.

- Si es secundario de combo: descripción del principal.
- En cualquier otro caso: `null`.

### 20. tarjeta_fidelidad

Nombre de la tarjeta de fidelidad asociada a la oferta del producto.

Ejemplos: `"COMUNIDAD COTO"`, `"MI CARREFOUR"`, `"CLUB DIA"`, `"CENCOPAY"`, `"MAXI VOUCHER"`.

Solo registrar si la imagen lo muestra explícitamente para ese producto. **No asumir** que aplica a todos los productos por ser de una cadena. La skill específica de cadena (ej: `coto`) provee los nombres canónicos.

Si no se ve: `null`.

### 21. tarjeta_bancos

Nombre de las tarjetas de bancos asociadas a la oferta.

Ejemplos: `"MERCADO PAGO"`, `"VISA BANCO PROVINCIA"`, `"MODO"`.

Si no se ve: `null`.

### 22. tipo_variedad

Cuando la imagen presenta más de un SKU del mismo producto pero con distinto tipo, sabor o fragancia.

Valores canónicos:
- `"Varios sabores"`
- `"Varias fragancias"`
- `"Varios tipos"`

**Cuándo aplicar:** cuando se ve claramente más de una versión del mismo producto (ej: 3 sabores de Mentos en un mismo bloque) y el catálogo muestra una sola descripción / un solo precio que aplica a todas las variedades.

**Cuándo NO aplicar:** cuando se ven productos distintos del mismo fabricante (ej: Kellogg's Zucaritas + Froot Loops + Müsli → son **líneas distintas**, no variedades). Ver la skill `extracting-multiple-products-per-image` para la regla detallada.

Si no aplica: `null`.

### 23. descripcion_variedad

Cuando la oferta afecta a categorías cerradas, registrar las categorías afectadas.

Ejemplo: "70% 2da unidad de shampoo y acondicionadores" → `descripcion_variedad: "Shampoo / Acondicionadores"`.

Si no aplica: `null`.

### 24. maximo_unidades

Máximo de unidades que el cliente puede comprar bajo esta promoción, si lo indica la oferta.

- Solo número (ej: `4`, `6`).
- Si la oferta no especifica máximo: `null`.

### 25. needs_review

Booleano. `true` si el producto necesita revisión humana por cualquier motivo, `false` si está completo y confiable.

Reglas:
- Si `review_reasons` está vacío → `needs_review: false`.
- Si `review_reasons` tiene al menos un código → `needs_review: true`.

### 26. review_reasons

Array de códigos canónicos que indican por qué el producto va a revisión humana. Ver la skill `flagging-for-review` para la lista completa de códigos.

Códigos más frecuentes:
- `"PRODUCT_NOT_RECOGNIZED"`
- `"BRAND_NOT_RECOGNIZED"`
- `"CATEGORY_NOT_DEFINED"`
- `"MEASURE_NOT_VISIBLE"`
- `"PRICE_AMBIGUOUS"`
- `"METADATA_MISMATCH"`
- `"LOW_CONFIDENCE"`

Si no hay nada para revisar: `[]` (array vacío, **no** `null`).

## Situaciones especiales

### Productos con precio pero sin medida visible

Si el SKU tiene precio pero la unidad de medida no está visible en el frente, mirar el packaging del producto en la imagen para tratar de leer el gramaje. Si tampoco se ve ahí, `medida` y `u_medida` quedan en `null` y se agrega `MEASURE_NOT_VISIBLE` a `review_reasons`.

### Productos sin precio visible (tipo Publicidad)

Crear la entrada con lo que sí se ve (descripción, marca, `tipo_promocion_oferta` si está). Todos los campos de precio quedan en `null`. El tipo de oferta es `"Publicidad"`.

### Bloque tipo Publicación de un fabricante

Cuando una imagen presenta varios SKUs del mismo fabricante con datos publicados, ver la skill `extracting-multiple-products-per-image` para distinguir si son **líneas distintas** (N registros) o **variedades** del mismo producto (1 registro con `tipo_variedad`).

### Combos

Ver la skill `detecting-combos`.

### Categorías cerradas con marca compartida

Ver la skill `handling-closed-brand-categories`.

### Productos no reconocibles

Si la imagen no permite identificar el producto (texto ilegible, imagen recortada, calidad muy baja), crear la entrada con los campos que se puedan leer, dejar el resto en `null`, y agregar `PRODUCT_NOT_RECOGNIZED` a `review_reasons`.

## Formato de respuesta

Ver la skill `formatting-output` para el formato exacto del JSON final con todos los productos.

## Notas de diseño

### Por qué la regla de "no inventar" está tan enfatizada

Los modelos de visión tienden a "completar" información usando conocimiento general. Si ven un producto Copa de Oro, saben que es de 820g aunque no lo lean. Esta tendencia hay que frenarla explícitamente y con repetición.

### Por qué `medida` y `u_medida` se separan

David lo pidió explícito en la última iteración del schema. Antes el campo era ambiguo (`"190g"` vs `"GR"`). Separados, la integración con la base maestra de GDS es más robusta.

### Por qué los tres tipos de promoción están separados

Una misma oferta puede tener: (a) descuento base aplicable a todos, (b) descuento adicional con tarjeta de fidelidad, (c) descuento adicional con tarjeta bancaria. Antes mezclábamos todo en un solo campo y se perdía info. Ahora cada dimensión va en su propio campo.

### Por qué la matching de EAN no es responsabilidad del agente

David lo dijo explícito: *"este proceso puede no hacerlo el agente y quedar del lado de la integración"*. El agente extrae lo que ve. Si no hay EAN visible, deja `null` y el pipeline downstream hace el lookup contra el maestro de SKUs.

### Por qué `review_reasons` es array y no string

Un mismo producto puede tener varios motivos de revisión (ej: precio borroso + medida no visible). Array permite acumularlos sin perder info. Si después David quiere un solo motivo concatenado, se puede serializar al exportar.
