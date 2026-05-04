---
name: handling-closed-brand-categories
description: Maneja casos donde la oferta del catálogo aplica a una categoría cerrada de marca o de tipo de producto, en lugar de a un SKU específico. Genera registros de "SKU genérico" para representar la oferta y desagrega por marca cuando la categoría cerrada incluye productos de varias marcas. Esencial para que GDSnet pueda cargar correctamente las ofertas que no tienen un SKU exacto asociado.
---

# Manejo de Categorías Cerradas

## Rol

Hay catálogos donde la oferta no aplica a un SKU específico, sino a una categoría completa o a un set de productos compartidos por una marca. Tu trabajo es detectar estos casos y generar los registros adecuados según las convenciones de GDSnet.

## Qué es una "categoría cerrada"

Una **categoría cerrada** es cuando la oferta aplica a un grupo de productos definido por marca, tipo o categoría, **sin especificar un SKU concreto**.

Ejemplos típicos:
- "Yerbas Cruz de Malta" (no especifica gramaje, aplica a todas las yerbas Cruz de Malta).
- "Tabletas Milka" (todas las tabletas, sin especificar variedad).
- "Aceites todos" (en Maxiconsumo).
- "Galletitas Cadbury" (todas las variedades).

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
  "descripcion": "CHOCOLATES TODOS",
  "tipo_promocion_oferta": null,
  "tipo_promocion_tarjeta_fidelidad": "20%DTO",
  "tarjeta_fidelidad": "MAXI VOUCHER",
  ...
}
```

### Caso D: Una marca cerrada sin categoría informada (caso ESPADOL)

La oferta cubre toda una marca, y la marca cubre productos de varias categorías. El catálogo no especifica las categorías.

**Ejemplo:** Folder muestra "ESPADOL todos los productos al 30%". ESPADOL tiene productos en JABONES DE TOCADOR, ALCOHOL EN GEL, ANTISÉPTICOS, etc.

**Regla:** generar tantos registros como categorías tenga la marca. Si está disponible `references/marcas-cerradas-sin-categoria.md` con el mapeo, usar esa lista. Si no está disponible, generar **1 registro con `categoria: null`** y agregar `CATEGORY_NOT_DEFINED` a `review_reasons`.

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

**Nota:** la lista canónica de marcas cerradas con sus categorías es responsabilidad de GDSnet (vía David). Hasta que esté disponible, dejar `null` y flagear.

## Cómo decidir si es categoría cerrada o productos individuales

Pregunta clave: **¿el folder muestra SKUs específicos con sus medidas, o está hablando de "todos los productos de X"?**

**Es categoría cerrada cuando:**
- El texto dice "todas las yerbas X", "todos los chocolates X", "todas las galletitas X".
- La imagen muestra varios envases de la misma marca pero sin destacar uno con precio individual.
- El precio o promoción aplica al conjunto, no a un envase específico.

**Es producto individual (no categoría cerrada) cuando:**
- El folder muestra un envase con su gramaje y precio específico.
- La descripción es precisa sobre la variante (ej: "Cruz de Malta 1kg").

## Diferencia con otros casos

### Diferencia con bloque tipo Publicación de un fabricante

Un bloque "Kellogg's" con Zucaritas, Froot Loops, Müsli y Choco Krispis es un caso de **Publicación** (varios SKUs distintos del mismo fabricante), no de categoría cerrada. Cada cereal es una **línea distinta** y se registra individualmente. Ver `extracting-multiple-products-per-image`.

### Diferencia con variedades

"Yerbas Amanda" donde Amanda solo tiene un tipo de yerba (con/sin palo, con stevia, etc.) puede ser variedades — un solo registro con `tipo_variedad: "Varios tipos"`. La diferencia es: ¿son SKUs claramente distintos o variedades del mismo producto base?

## Notas de diseño

### Por qué desagregamos por marca en el Caso B

David lo escribió textualmente en el documento de ajustes: *"se genera un sku genérico llamado 'yerbas y mate cocido' y se graban 3 líneas, uno para cada marca: Nobleza gaucha, Cruz Malta y Taraguí"*.

Es la convención de GDSnet para que cada marca sea trazable individualmente en su base maestra.

### Por qué el caso ESPADOL es especial

Porque el conocimiento de "qué categorías tiene cada marca" no está en el catálogo — está en la base interna de GDSnet. El agente no puede inferirlo solo. Por eso, sin la lista canónica, dejamos `null` y flagueamos para revisión humana.

### Por qué usamos "VARIAS MARCAS" como marca cuando aplica

Es el valor que David usa en su Excel canónico para ofertas de tipo "todos los chocolates" sin marca específica. Lo respetamos como string literal.
