---
name: handling-closed-brand-categories
description: Maneja casos donde la oferta del catálogo aplica a una categoría cerrada de marca o de tipo de producto en lugar de a un SKU específico. Cubre 5 patrones: una marca con una categoría, una categoría con varias marcas, categoría sin marca específica, marca cerrada sin categoría informada, y bloques promocionales con footer macro-categoría que requieren descomposición. Genera registros con SKU genérico (marca = "VARIAS MARCAS") cuando corresponde y desagrega macros del folder en categorías canónicas usando references/categorias-contratadas.md.
---

# Manejo de Categorías Cerradas

## Rol

Hay catálogos donde la oferta no aplica a un SKU específico, sino a un grupo de productos definido por marca, tipo o categoría. Esta skill cubre cómo detectar estos casos y generar los registros adecuados.

## Qué es una "categoría cerrada"

Una **categoría cerrada** es cuando la oferta aplica a un grupo de productos definido por marca, tipo o categoría, **sin especificar un SKU concreto**.

Ejemplos típicos:
- "Yerbas Cruz de Malta" (no especifica gramaje, aplica a todas las yerbas Cruz de Malta).
- "Tabletas Milka" (todas las tabletas, sin especificar variedad).
- "EN GOLOSINAS" como footer de un bloque promocional (cubre múltiples categorías canónicas).
- "Aceites todos" (en Maxiconsumo).

## Tipos de categoría cerrada

### Caso A: Una categoría, una marca

La oferta cubre una marca dentro de una categoría específica.

**Ejemplo:** "Yerbas Cruz de Malta" con 70% en la 2da unidad.

**Registro: 1 SKU genérico.**

```json
{
  "categoria": "YERBA MATE",
  "marca": "CRUZ DE MALTA",
  "descripcion": "CRUZ DE MALTA YERBAS",
  "descripcion_literal": "Yerbas Cruz de Malta",
  "medida": null,
  "u_medida": null,
  "tipo_promocion_oferta": "70% DTO 2DA U",
  ...
}
```

### Caso B: Una categoría, varias marcas (categoría cerrada con desagregación por marca)

La oferta cubre una categoría con múltiples marcas mostradas en un mismo bloque.

**Ejemplo:** Un bloque "Yerbas y mate cocido" muestra Nobleza Gaucha, Cruz de Malta y Taraguí, con la misma promoción "3X2".

**Registro: 1 línea por marca.**

```json
[
  {
    "categoria": "YERBA MATE",
    "marca": "NOBLEZA GAUCHA",
    "descripcion": "NOBLEZA GAUCHA YERBAS",
    "tipo_promocion_oferta": "3X2",
    ...
  },
  {
    "categoria": "YERBA MATE",
    "marca": "CRUZ DE MALTA",
    "descripcion": "CRUZ DE MALTA YERBAS",
    "tipo_promocion_oferta": "3X2",
    ...
  },
  {
    "categoria": "YERBA MATE",
    "marca": "TARAGUI",
    "descripcion": "TARAGUI YERBAS",
    "tipo_promocion_oferta": "3X2",
    ...
  }
]
```

### Caso C: Categoría cerrada sin marca específica

La oferta cubre una categoría amplia sin marca. Típico de mayoristas como Maxiconsumo con vouchers de descuento.

**Ejemplo:** "20% DTO con MAXI VOUCHER en CHOCOLATES TODOS".

**Registro: 1 SKU genérico con marca = "VARIAS MARCAS".**

```json
{
  "categoria": "CHOCOLATES",
  "marca": "VARIAS MARCAS",
  "descripcion": "CHOCOLATES",
  "tipo_promocion_oferta": null,
  "tipo_promocion_tarjeta_fidelidad": "20%DTO",
  "tarjeta_fidelidad": "MAXI VOUCHER",
  ...
}
```

**Convención de descripción para registros con `marca: "VARIAS MARCAS"`:**

El campo `descripcion` debe ser **literalmente el nombre de la categoría canónica**, sin prefijos ni sufijos artificiales.

- ✓ Correcto: `"ALFAJORES"`, `"CARAMELOS"`, `"CHOCOLATES"`, `"SHAMPOO"`, `"VINOS"`, `"CHAMPAGNE"`
- ✗ Incorrecto: `"V/M ALFAJORES"`, `"VARIAS MARCAS CARAMELOS"`, `"MULTI CHOCOLATES"`

**Nunca usar prefijos como `V/M`, `VARIAS MARCAS`, `MULTI`, ni similares en el campo `descripcion`.** El indicador de "varias marcas" ya está en el campo `marca`. Duplicarlo en `descripcion` es ruido.

### Caso D: Una marca cerrada sin categoría informada (caso ESPADOL)

La oferta cubre toda una marca, y la marca cubre productos de varias categorías. El catálogo no especifica las categorías.

**Ejemplo:** Folder muestra "ESPADOL todos los productos al 30%".

**Regla:** sin lista canónica de marcas con sus categorías, generar **1 registro con `categoria: null`** y agregar `CATEGORY_NOT_DEFINED` a `review_reasons`.

```json
{
  "categoria": null,
  "marca": "ESPADOL",
  "descripcion": "ESPADOL TODOS",
  "tipo_promocion_oferta": "30%DTO",
  "needs_review": true,
  "review_reasons": ["CATEGORY_NOT_DEFINED"],
  ...
}
```

### Caso E: Bloque promocional con footer macro-categoría (NUEVO)

Patrón frecuente en folders de COTO, Carrefour y otros: un **bloque promocional** que tiene:

1. **Una promoción dominante** (ej: "40% DTO", "70% 2da unidad llevando 2 iguales", "3X2 igual marca y variedad").
2. **Un grupo de marcas listadas** con sus logos.
3. **Un footer/banner** que indica una **macro-categoría** del folder (ej: "EN GOLOSINAS", "EN VINOS FINOS, CHAMPAÑAS Y ESPUMANTES", "EN SHAMPOO, ACONDICIONADOR Y TRATAMIENTOS CAPILARES", "EN ENCURTIDOS Y ESPECIAS").

**Importante:** las macro-categorías del folder **no son categorías canónicas de GDSnet**. Son etiquetas descriptivas del folder que pueden cubrir varias categorías canónicas reales.

**Regla de generación de registros:**

Para un bloque con N marcas listadas y un footer macro:

#### Paso 1 — Generar registros por marca listada

Por cada marca dentro del bloque, generar 1 registro siguiendo el patrón habitual:
- `marca: <marca>`
- `descripcion: <marca> + tipo de producto leído de la imagen` (ver `building-sku-description`)
- `categoria: <categoria canónica del producto>` (matcheada contra `references/categorias-contratadas.md`)
- Promociones del bloque aplicadas a `tipo_promocion_oferta` (y a `tipo_promocion_tarjeta_fidelidad` cuando corresponda).

#### Paso 2 — Descomponer la macro-categoría del footer

Mirá la macro-categoría del footer (ej: "EN GOLOSINAS"). Buscá en `references/categorias-contratadas.md` qué categorías canónicas razonablemente caen dentro de esa macro.

**Ejemplos de razonamiento:**

- "EN GOLOSINAS" → matchea con `ALFAJORES`, `CARAMELOS`, `CHICLES`, `CHOCOLATES` (las 4 categorías de la lista canónica que naturalmente son golosinas).
- "EN VINOS FINOS, CHAMPAÑAS Y ESPUMANTES" → matchea con `VINOS`, `CHAMPAGNE`. Si "ESPUMANTES" no matchea con ninguna categoría canónica, no generar un registro adicional para esa palabra.
- "EN SHAMPOO, ACONDICIONADOR Y TRATAMIENTOS CAPILARES" → matchea con `SHAMPOO`, `ACONDICIONADOR`, `BALSAMOS` (porque `BALSAMOS` incluye "tratamiento, serum, ampollas" según la columna INCLUYE).
- "EN ENCURTIDOS Y ESPECIAS" → ninguna de las 74 categorías canónicas matchea con encurtidos ni especias.

Por cada categoría canónica encontrada en el match, generar 1 registro:

```json
{
  "categoria": "<CATEGORIA CANONICA>",
  "marca": "VARIAS MARCAS",
  "descripcion": "<CATEGORIA CANONICA>",
  "tipo_promocion_oferta": "<promo del bloque>",
  ...
}
```

**Importante:** el campo `descripcion` es literalmente el nombre de la categoría canónica. Sin prefijos (`V/M`, `MULTI`), sin sufijos (`TODOS`, `TODAS`). Si la categoría canónica es `ALFAJORES`, la descripción es `ALFAJORES`. La convención de cuándo agregar `TODOS` o `TODAS` es decisión de la capa de exportación a Excel/CSV, no del agente.

#### Paso 3 — Si la macro no matchea con ninguna categoría canónica

Si después de revisar la macro contra `references/categorias-contratadas.md` **ninguna** categoría canónica matchea con razonable certeza, generar **1 solo registro** flageado para revisión humana:

```json
{
  "categoria": null,
  "marca": "VARIAS MARCAS",
  "descripcion": null,
  "descripcion_literal": "EN ENCURTIDOS Y ESPECIAS",
  "tipo_promocion_oferta": "<promo del bloque>",
  "needs_review": true,
  "review_reasons": ["MACRO_CATEGORY_UNMAPPED"],
  ...
}
```

#### Ejemplo completo del Caso E

**Imagen:** bloque promocional con "3X2 igual marca y variedad", marcas Pepitos, Milka, Terrabusi, Oreo, Knorr, La Serenísima, Las Tres Niñas, Dove, Villavicencio, Swift, Gordon's, Crowie, NotCo, footer "EN GOLOSINAS".

**Registros generados (esquema, no completo):**

```json
[
  // Paso 1 - una línea por marca:
  {"marca": "PEPITOS", "categoria": "GALLETAS DULCES", "descripcion": "PEPITOS GALLETITAS", ...},
  {"marca": "MILKA", "categoria": "GALLETAS DULCES", "descripcion": "MILKA GALLETITAS", ...},
  {"marca": "TERRABUSI", "categoria": "GALLETAS DULCES", "descripcion": "TERRABUSI GALLETITAS", ...},
  {"marca": "OREO", "categoria": "GALLETAS DULCES", "descripcion": "OREO GALLETITAS", ...},
  {"marca": "KNORR", "categoria": "CALDOS", "descripcion": "KNORR CALDOS", ...},
  // ... más marcas...

  // Paso 2 - desagregación de "EN GOLOSINAS":
  {"marca": "VARIAS MARCAS", "categoria": "ALFAJORES", "descripcion": "ALFAJORES", ...},
  {"marca": "VARIAS MARCAS", "categoria": "CARAMELOS", "descripcion": "CARAMELOS", ...},
  {"marca": "VARIAS MARCAS", "categoria": "CHICLES", "descripcion": "CHICLES", ...},
  {"marca": "VARIAS MARCAS", "categoria": "CHOCOLATES", "descripcion": "CHOCOLATES", ...}
]
```

## Cómo decidir si es categoría cerrada o productos individuales

Pregunta clave: **¿el folder muestra SKUs específicos con sus medidas, o está hablando de "todos los productos de X"?**

**Es categoría cerrada cuando:**
- El texto dice "todas las yerbas X", "todos los chocolates X".
- La imagen muestra varios envases de la misma marca pero sin destacar uno con precio individual.
- El precio o promoción aplica al conjunto, no a un envase específico.
- Hay un footer macro-categoría aplicable a todo el bloque (Caso E).

**Es producto individual (no categoría cerrada) cuando:**
- El folder muestra un envase con su gramaje y precio específico.
- La descripción es precisa sobre la variante (ej: "Cruz de Malta 1kg").

## Diferencia con otros casos

### Diferencia con bloque tipo Publicación de un fabricante

Un bloque "Kellogg's" con Zucaritas, Froot Loops, Müsli y Choco Krispis es un caso de **Publicación** (varios SKUs distintos del mismo fabricante), no de categoría cerrada. Cada cereal es una **línea distinta** y se registra individualmente. Ver `extracting-multiple-products-per-image`.

### Diferencia con variedades

"Yerbas Amanda" donde Amanda solo tiene un tipo de yerba (con/sin palo, con stevia, etc.) puede ser variedades — un solo registro con `tipo_variedad: "Varios tipos"`.

## Notas de diseño

### Por qué desagregamos por marca en el Caso B

David lo escribió textualmente en el documento de ajustes: *"se genera un sku genérico llamado 'yerbas y mate cocido' y se graban 3 líneas, uno para cada marca"*. Es la convención de GDSnet para que cada marca sea trazable individualmente en su base maestra.

### Por qué descomponemos macro-categorías en el Caso E

Las macro-categorías del folder ("GOLOSINAS", "VINOS FINOS, CHAMPAÑAS Y ESPUMANTES") son etiquetas comerciales del folder, no categorías canónicas de GDSnet. La base maestra trabaja con las 74 categorías de `references/categorias-contratadas.md`. Si el agente carga "GOLOSINAS" como categoría, ese registro queda huérfano porque "GOLOSINAS" no existe en el sistema de GDS.

### Por qué el agente decide el match macro→categorías sin tabla pre-cargada

GDSnet no provee una tabla canónica de "macro → [categorías]". Pretender una tabla mantenida por nosotros sería inventar reglas de negocio. El agente decide caso por caso usando la lista canónica de las 74 categorías y el sentido común sobre qué cae dentro de cada macro.

Si el agente no encuentra match razonable, flagea `MACRO_CATEGORY_UNMAPPED` para revisión humana en lugar de inventar una categoría.

### Por qué usamos "VARIAS MARCAS" como marca

Es el valor que David usa en su Excel canónico para ofertas de tipo "todos los chocolates" sin marca específica.
