# CHANGELOG — Literal "CATEGORIA NO CONTRATADA" (8-mayo-2026)

Cambio de output cuando un producto cae fuera de las 74 categorías contratadas.

## Motivación

Hasta ahora, cuando un producto no matcheaba ninguna de las 74 categorías canónicas, el agente devolvía `categoria: null` + `CATEGORY_NOT_DEFINED` en `review_reasons`. Eso obliga al pipeline downstream a hacer dos checks (`IS NULL` + flag) y mezcla en un solo `null` dos situaciones semánticamente distintas: "fuera de scope contratado" vs "no se pudo determinar la categoría".

Esta versión introduce un valor literal `"CATEGORIA NO CONTRATADA"` para el primer caso (fuera de scope), preservando `null` para los demás motivos genuinos de indeterminación.

## Comportamiento nuevo

| Situación | `categoria` | `review_reasons` |
|---|---|---|
| Producto matchea con una de las 74 | `"<CATEGORIA CANONICA>"` | `[]` |
| Producto fuera de las 74 (ej: BARRAS DE CEREAL, KOTEX) | `"CATEGORIA NO CONTRATADA"` | `["CATEGORY_NOT_DEFINED"]` |
| Producto cae en exclusión explícita (chocolate para taza, vino Patero) | `"CATEGORIA NO CONTRATADA"` | `["CATEGORY_NOT_DEFINED"]` |
| Categoría ambigua entre 2 de las 74 | `null` | `["LOW_CONFIDENCE"]` |
| Imagen ilegible | `null` | `["PRODUCT_NOT_RECOGNIZED"]` |
| Marca cerrada con categorías mixtas (ESPADOL) | `null` | `["CLOSED_BRAND_WITHOUT_CATEGORY_LIST"]` |
| Macro de footer sin match canónico | `null` | `["MACRO_CATEGORY_UNMAPPED"]` |

## Archivos modificados

- `agent/system_prompt.md` — Recursos esperados en filesystem.
- `references/categorias-contratadas.md` — Reglas de uso + sección "Categorías que no están en la lista".
- `skills/core/extracting-products/SKILL.md` — Regla 3 + tabla de marcas con inferencia.
- `skills/core/flagging-for-review/SKILL.md` — Sección `CATEGORY_NOT_DEFINED` + Ejemplo 2.
- `skills/core/handling-closed-brand-categories/SKILL.md` — Caso D (ESPADOL): cambio del flag de `CATEGORY_NOT_DEFINED` a `CLOSED_BRAND_WITHOUT_CATEGORY_LIST` para que la nueva semántica sea consistente — ESPADOL no es "fuera de scope" sino "marca con productos en múltiples categorías sin info para discriminar".

## Implicaciones para downstream

El pipeline que consume el JSON del agente debe actualizar:
- Queries que filtran por `categoria IS NULL` para detectar productos no contratados → ahora deben filtrar por `categoria = 'CATEGORIA NO CONTRATADA'`. Las queries por `IS NULL` siguen capturando ambigüedad real (ESPADOL, macro sin match, imagen ilegible).
- Tablas/dashboards que cuentan "productos no contratados" pueden hacerlo sin joinear contra `review_reasons`.

## Compatibilidad

Los productos extraídos antes de este deploy mantienen su valor histórico (`categoria: null` + flag). Si se quiere normalizar el histórico, hay que correr una migration sobre la tabla de extractions.
