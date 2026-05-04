# CHANGELOG — Update Categorías y Fixes (4-mayo-2026)

Segundo update, consolida los siguientes cambios discutidos después del primer test contra la corrida manual:

1. **Lista canónica de las 74 categorías contratadas** (David envió `CATEGORIAS_FOLDERS.xlsx`).
2. **Caso E del manejo de categorías cerradas** — bloques promocionales con footer macro-categoría.
3. **Eliminación de auto-flags ruidosos** (`METADATA_MISMATCH`, `MEASURE_NOT_VISIBLE`).
4. **Preservación de nombres comerciales de línea** (no traducir "FREE" a "S/AZ").

## Archivos modificados

```
gds-folders-update-categorias-y-fixes/
├── CHANGELOG-categorias-y-fixes.md
├── agent/
│   └── system_prompt.md                              ← actualizado (referencias al filesystem)
├── references/
│   └── categorias-contratadas.md                     ← NUEVO (las 74)
└── skills/core/
    ├── extracting-products/SKILL.md                  ← validar contra lista canónica + sacar auto-flags
    ├── handling-closed-brand-categories/SKILL.md     ← + Caso E (bloque con macro footer)
    ├── flagging-for-review/SKILL.md                  ← lista actualizada de códigos
    └── building-sku-description/SKILL.md             ← + regla de preservar nombres comerciales
```

7 archivos. Mergea sobre la rama del primer update.

## 1. Categorías canónicas

### Nuevo: `references/categorias-contratadas.md`

Las 74 categorías contratadas por GDSnet, con sus columnas `INCLUYE` y `NO INCLUYE`. Generado a partir del archivo `CATEGORIAS_FOLDERS.xlsx` que David envió.

**Reglas asociadas:**

- El campo `categoria` de cada producto debe ser literalmente uno de los valores de la lista. Sin excepciones.
- Respetar mayúsculas, acentos y typos del archivo original (`LIUSTRAMUEBLES`, `PREMEZCALAS DULCES`, `CAFÉ` con tilde, etc.).
- Si un producto no matchea, `categoria: null` + `CATEGORY_NOT_DEFINED` en review_reasons.
- Si un producto cae en una exclusión explícita (columna `NO INCLUYE`), también va a `null` + flag.

### Cambios en `extracting-products`

Agregada la regla de validación contra la lista canónica. La sección "Cuándo flagear" ahora incluye explícitamente `CATEGORY_NOT_DEFINED` cuando la categoría no matchea con las 74.

Sacado de la skill el auto-flag de `MEASURE_NOT_VISIBLE` cuando la medida no es visible. Ahora simplemente queda en `null` sin flagear.

### Cambios en `system_prompt.md`

Agregada sección "Recursos esperados en filesystem" que explicita que el agente debe consultar `/uploads/references/categorias-contratadas.md`. Si no está disponible, todas las categorías quedan en `null` con flag.

## 2. Caso E: bloques promocionales con footer macro-categoría

### Cambios en `handling-closed-brand-categories`

Agregado el Caso E que describe el patrón observado en folders de COTO (y otras cadenas):

> Un bloque promocional con una promoción dominante (40%, 70%, 3X2), un grupo de marcas listadas, y un footer/banner con una macro-categoría descriptiva ("EN GOLOSINAS", "EN VINOS FINOS, CHAMPAÑAS Y ESPUMANTES").

**Regla de generación:**

1. Por cada marca listada → 1 registro con la promo del bloque.
2. Por cada **categoría canónica** que matchee con la macro del footer → 1 registro con `marca: "VARIAS MARCAS"` y `descripcion: "<CATEGORIA> TODOS"`.

El agente decide el match macro→canónicas usando `references/categorias-contratadas.md` y sentido común. **No hay tabla pre-cargada** de "macro → categorías canónicas" — esa decisión es responsabilidad del agente caso por caso. Si ninguna canónica matchea con razonable certeza, generar 1 solo registro flageado con `MACRO_CATEGORY_UNMAPPED`.

**Ejemplo decisión:**

- "EN GOLOSINAS" → matchea con `ALFAJORES`, `CARAMELOS`, `CHICLES`, `CHOCOLATES` → 4 registros con marca = VARIAS MARCAS.
- "EN ENCURTIDOS Y ESPECIAS" → ninguna canónica matchea → 1 registro con flag.

## 3. Auto-flags ruidosos eliminados

### `METADATA_MISMATCH` removido

Eliminado del catálogo de códigos en `flagging-for-review` y de las menciones en `extracting-products` y `system_prompt.md`. Razón: la metadata no es prioridad en esta versión y el flag generaba ruido en todos los productos.

### `MEASURE_NOT_VISIBLE` removido como auto-flag

Eliminado del catálogo. Razón: la ausencia de medida en bloques tipo Publicación es esperada y no un problema. Si una medida debería estar y no está, eso se detecta downstream o con otros indicadores.

### Filosofía actualizada en `flagging-for-review`

Sección nueva "Filosofía" que explicita: **el default es no flagear**. Solo se flagea cuando el caso encaja en un código específico. Un campo en `null` por sí solo no es un flag — es la respuesta correcta a "el dato no se ve".

## 4. Preservación de nombres comerciales de línea

### Cambios en `building-sku-description`

Sección "Qué NO hacer" actualizada con regla explícita: no traducir nombres comerciales (`FREE`, `ZERO`, `LIGHT`, `DIET`, `ULTRA`, `BLACK`, `ORIGINAL`, `CLASSIC`, etc.) a equivalentes funcionales. Razón: esos nombres son parte del SKU en la base maestra de GDS y traducirlos rompe el match.

**Antes (incorrecto):** folder dice "7UP FREE" → agente generaba `7UP S/AZ 1,5L`.
**Ahora (correcto):** folder dice "7UP FREE" → agente genera `7UP FREE 1,5L`.

Tabla agregada con los nombres comerciales más frecuentes y sus equivalentes funcionales que NO deben usarse.

## Lo que NO cambia

- El schema sigue siendo el mismo (26 campos, mismo orden).
- Las skills que no se mencionan acá (formatting-output, classifying-ad-type, detecting-combos, reading-prices, reading-promotions, classifying-folder-type, extracting-multiple-products-per-image, coto) no se tocan.
- La reference `zonas-geograficas.md` no se toca.

## Lo que queda pendiente

Sigue pendiente para la reunión del martes con David:

1. **Convención de descripción** — la tensión `OREO TODAS` (manual) vs `OREO GALLETITAS` (agente) vs combinada. Postergada hasta validar con David.
2. **`publicadores.md` con frecuencias** — el tercer documento que David mencionó pero no llegó.
3. **Marcas cerradas sin categoría (caso ESPADOL)** — qué tabla provee GDS.
4. **Caso snacks/bocaditos** — Agent 1 vs web_fetch reactivado.
5. **Schema definitivo** — confirmar los 26 campos y nombres canónicos.

## Próximos pasos

### Inmediato

1. Mergear este zip sobre la rama `feedback-david-2026-04-29` (o crear nueva rama).
2. Re-subir las 5 skills modificadas + reference nueva al workspace de Anthropic.
3. Re-correr el test contra la página COTO Super Finde y comparar:
   - ¿Las categorías ahora son canónicas (no más BARRAS DE CEREAL ni LECHE LARGA VIDA)?
   - ¿El bloque "EN GOLOSINAS" se desagrega en ALFAJORES, CARAMELOS, CHICLES, CHOCOLATES?
   - ¿Desapareció el flag METADATA_MISMATCH de todos los productos?
   - ¿7UP FREE se preserva como nombre comercial?

### Post-reunión del martes

Aplicar lo que David confirme sobre los pendientes.
