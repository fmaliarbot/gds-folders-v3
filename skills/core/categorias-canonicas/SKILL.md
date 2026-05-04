---
name: categorias-canonicas
description: Provee la lista canónica de las 74 categorías de productos contratadas por GDSnet. El campo `categoria` de cada producto extraído debe ser literalmente uno de los valores de esta lista. Cargar esta skill siempre que se necesite asignar o validar el campo `categoria` (típicamente desde extracting-products o desde handling-closed-brand-categories cuando se descomponen macro-categorías de footer).
---

# Categorías Canónicas Contratadas — GDSnet

## Rol

Esta skill no define lógica — provee **datos canónicos**: la lista de las 74 categorías de productos que GDSnet procesa por contrato. La fuente está en `categorias-contratadas.md` (en el bundle de esta skill) y se generó del archivo `CATEGORIAS_FOLDERS.xlsx` que envió David Feinmann.

## Cómo usarla

Leer `categorias-contratadas.md`. La tabla canónica tiene tres columnas:

- **CATEGORIA** — el valor literal a usar en el campo `categoria` de cualquier producto extraído. Respetar mayúsculas, acentos y typos exactamente (`LIUSTRAMUEBLES`, `PREMEZCALAS DULCES`, `CAFÉ` con tilde).
- **INCLUYE** — qué tipo de productos caen en la categoría.
- **NO INCLUYE** — exclusiones explícitas (productos que parecen pertenecer pero no).

## Reglas de uso

- El campo `categoria` de cualquier producto extraído **debe** ser literalmente uno de los valores de la columna `CATEGORIA`. Sin excepciones.
- Si un producto no matchea con ninguna categoría: `categoria: null` + `CATEGORY_NOT_DEFINED` en `review_reasons`.
- Si un producto cae en una exclusión explícita (columna `NO INCLUYE`): también `null` + flag.
- Categorías frecuentes que NO están en la lista (no inventarlas): `BARRAS DE CEREAL`, `LECHE LARGA VIDA`, `AGUA MINERAL`. Si aparecen, dejar `null` + `CATEGORY_NOT_DEFINED`.

## Cuándo cargar esta skill

Siempre que se necesite asignar el campo `categoria` de un producto. En la práctica:

- `extracting-products` la consulta para validar el campo en cada producto.
- `handling-closed-brand-categories` la consulta cuando descompone una macro-categoría de footer (Caso E) para identificar qué categorías canónicas matchean.

## Mantenimiento

Cuando GDSnet actualice el contrato (David envía un nuevo `CATEGORIAS_FOLDERS.xlsx`), regenerar `categorias-contratadas.md` y versionar este skill. El resto de las skills no necesitan tocarse.
