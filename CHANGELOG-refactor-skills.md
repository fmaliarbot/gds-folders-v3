# CHANGELOG — Refactor de Skills (5-mayo-2026, sesión 2)

Quinto update, **refactor profundo** de la base de skills después del análisis exhaustivo posterior al test del 5 de mayo. No es un cambio funcional ni de comportamiento: es una reorganización para reducir duplicación, eliminar skills no aplicables al Agent 2, y centralizar reglas globales.

## Resumen de cambios

| Métrica | Antes (consolidado de 4 updates) | Después (refactor) | Cambio |
|---|---|---|---|
| Cantidad de skills | 12 | 11 | −1 |
| Líneas totales en skills | 2,352 | ~1,950 | −17% |
| Tokens estimados (skills) | ~26,900 | ~22,000 | −18% |
| Skills con regla "no inventar" repetida | 6 | 1 (centralizada) | −5 redundancias |
| Reglas de formato duplicadas en `extracting-products` ↔ `formatting-output` | sí | no | resuelto |

**No hay cambios funcionales en el comportamiento esperado del agente.** Si después de aplicar este refactor el agente se comporta diferente, algo se rompió en la migración y hay que revisarlo.

## Lo que cambia en este zip

```
gds-folders-update-refactor-skills/
├── CHANGELOG-refactor-skills.md
├── agent/
│   └── system_prompt.md                              ← elimina referencia a classifying-folder-type
├── skills/
│   ├── core/
│   │   ├── _DELETIONS/README.md                      ← marker para Claude Code
│   │   ├── extracting-products/SKILL.md              ← REESCRITA — skill central, absorbe reglas globales
│   │   ├── formatting-output/SKILL.md                ← REESCRITA — solo validación sintáctica del JSON
│   │   ├── building-sku-description/SKILL.md         ← CONDENSADA — 271 → 125 líneas
│   │   ├── reading-prices/SKILL.md                   ← LEVE — saca redundancia, referencia a reglas globales
│   │   ├── reading-promotions/SKILL.md               ← LEVE — saca redundancia, referencia a reglas globales
│   │   ├── flagging-for-review/SKILL.md              ← SIN CAMBIOS (ya estaba bien)
│   │   ├── handling-closed-brand-categories/SKILL.md ← SIN CAMBIOS (ya estaba bien)
│   │   └── detecting-combos/SKILL.md                 ← SIN CAMBIOS (ya estaba bien)
│   └── chains/
│       └── coto/SKILL.md                              ← ACOTADA — solo lo que usa Agent 2
```

## Acción requerida en Claude Code

### 1. Skills a sobreescribir (mergear desde el zip)

Las siguientes skills se reemplazan completamente por sus versiones nuevas:

- `skills/core/extracting-products/SKILL.md`
- `skills/core/formatting-output/SKILL.md`
- `skills/core/building-sku-description/SKILL.md`
- `skills/core/reading-prices/SKILL.md`
- `skills/core/reading-promotions/SKILL.md`
- `skills/chains/coto/SKILL.md`
- `agent/system_prompt.md`

### 2. Skills a ELIMINAR del repo

**Borrar la carpeta completa:**

```
skills/core/classifying-folder-type/
```

Razón: la skill clasificaba el tipo de catálogo (Regular / Especial / Flyers), pero esa decisión requiere visibilidad del catálogo completo. El Agent 2 procesa una página por vez y nunca tiene contexto suficiente. El campo `tipo_folder` además NO está en el output del Agent 2 — es metadata que va por el orquestador o un futuro Agent 1.

### 3. Skills sin cambios (ya están bien en el repo, no tocar)

- `skills/core/handling-closed-brand-categories/SKILL.md`
- `skills/core/detecting-combos/SKILL.md`
- `skills/core/flagging-for-review/SKILL.md`
- `skills/core/extracting-multiple-products-per-image/SKILL.md`
- `skills/core/classifying-ad-type/SKILL.md`

Las primeras 3 las incluí en el zip por completitud (pueden sobreescribirse, son idénticas a la versión actual). Las últimas 2 no las incluí — no las toques.

### 4. Marker `_DELETIONS/`

Hay una carpeta `skills/core/_DELETIONS/` con un `README.md` que documenta qué se eliminó y por qué. **NO subir esta carpeta al repo final** — es solo para que vos y Claude Code lo usen como referencia durante el merge. Borrarla después.

## Detalle de los 5 cambios principales

### Cambio 1 — Eliminar `classifying-folder-type`

**Por qué:** la skill no aplica al Agent 2. El campo `tipo_folder` no está en el schema del Agent 2 y la propia skill admitía que no aplica desde una sola página.

**Impacto:** −91 líneas, −1,200 tokens, sin pérdida funcional.

### Cambio 2 — Reorganizar `extracting-products` ↔ `formatting-output`

**Antes:**
- `extracting-products` (328 líneas) tenía reglas semánticas Y reglas de formato Y "no inventar" Y reglas de validación de categoría.
- `formatting-output` (239 líneas) duplicaba reglas de formato (mayúsculas, formato de precios, códigos canónicos de unidades) que ya estaban en `extracting-products`.
- Las dos skills cargadas juntas daban instrucciones contradictorias en detalles sutiles.

**Ahora:**
- `extracting-products` (234 líneas) = **fuente de verdad** del schema y de las reglas globales (no inventar, preservar nombres comerciales, validar categoría, tarjetas por SKU). Define el detalle de los campos que solo cubre esta skill (marca, descripcion_literal, ean, medida, u_medida, etc.).
- `formatting-output` (154 líneas) = **solo validación sintáctica** del JSON final (es JSON válido, los nulls son nulls, los arrays son arrays, los tipos son correctos, los códigos canónicos son canónicos).
- Cada regla de formato semántico vive en **una sola skill** (la que define el campo o concepto).

**Impacto:** −179 líneas combinadas, eliminación de 100% de las contradicciones potenciales.

### Cambio 3 — Condensar `building-sku-description`

**Antes:** 271 líneas con 10 secciones, mucho material teórico que rara vez se aplicaba (Patrón C "TODOS/TODAS" elaborado, sección "Campos pendientes con cliente" que es ruido para el agente, diccionario de abreviaciones extenso).

**Ahora:** 125 líneas enfocadas en lo que el agente realmente necesita:
- Los 3 patrones canónicos con ejemplos concretos.
- Cómo elegir patrón (tabla simple).
- Diccionario de abreviaciones acotado a las frecuentes.
- Reglas de "qué NO hacer" cortas.

Sacado: discusión de campos pendientes con cliente (eso vive en CHANGELOGs), redundancia con regla "preservar nombres comerciales" (ya en extracting-products), notas extensas de diseño.

**Impacto:** −146 líneas, −54%. Sin pérdida funcional — los patrones que el agente realmente usa están todos.

### Cambio 4 — Centralizar la regla "no inventar"

**Antes:** la frase "no inventar datos" aparecía explícita en 6 skills distintas, cada una con sus propias palabras. Al hacer updates, modificábamos una y se quedaban viejas en otras.

**Ahora:** la regla vive **solo en `extracting-products`** (regla 1, sección "Reglas globales del agente"). Las skills auxiliares (reading-prices, reading-promotions) la referencian con una sola línea: *"Las reglas globales del agente (no inventar, ante la duda `null` con flag) están en `extracting-products`."*

**Impacto:** ahorro distribuido, pero más importante: **una sola fuente de verdad** para la regla más importante del agente.

### Cambio 5 — Acotar la skill `coto`

**Antes:** 178 líneas que incluían:
- Tarjeta COMUNIDAD COTO ✓ (relevante)
- Datos fijos de cadena (`nombre_cadena`, `tipo_publicador`) — irrelevante para Agent 2
- Caso especial CLARIN (cambia campos de metadata) — irrelevante
- Zona de cobertura, URLs de catálogos — irrelevante
- Convenciones de SKU específicas — duplicado con building-sku-description
- Tipos de oferta y promoción frecuentes ✓ (relevante)
- Casos especiales (Combiná 8X6, frescos por kg, códigos internos, banners) ✓ (relevante)

**Ahora:** 126 líneas con solo lo que el Agent 2 realmente usa:
- Tarjeta COMUNIDAD COTO con regla crítica y ejemplo Salta Cautiva (defensivo, redundante con extracting-products pero crítico para evitar regresión)
- Tipos de oferta frecuentes en folders COTO
- Tipos de promoción frecuentes
- Casos especiales conocidos

Las secciones de metadata se sacan. Si en el futuro construimos Agent 1, esa info vive ahí.

**Impacto:** −52 líneas, skill más enfocada en su rol real.

## Cambios menores incidentales

- En `reading-prices` se eliminó la sección "Principio general" que repetía la regla "ante la duda null + flag" ya cubierta en `extracting-products`.
- En `reading-prices` y `reading-promotions` se agregó al inicio una línea referenciando que las reglas globales viven en `extracting-products`.

## Lo que NO cambia (importante)

- **Schema de 26 campos** — sin cambios.
- **Comportamiento esperado del agente** — sin cambios. Si las skills se cargan correctamente, el output del agente debería ser idéntico al de la corrida anterior.
- **References** (`categorias-contratadas.md`, `zonas-geograficas.md`, `publicadores.md`) — sin cambios.

## Cómo validar después del merge

Re-correr el test contra la página 8 de COTO Super Finde y comparar contra la última corrida exitosa (la del documento que nos pasaste con `pagina: 5`):

| Validación | Esperado |
|---|---|
| Cantidad de productos | 45 ± 1 |
| ANTARES → tarjeta_fidelidad | `null` |
| SALTA CAUTIVA → tarjeta_fidelidad | `null` (NO regresar a alucinación) |
| GROLSCH/BLUE MOON/WARSTEINER/KUNSTMANN | `"COMUNIDAD COTO"` |
| VILEDA → categoria | `"LIMPIADORES Y MULTIUSOS"` con `LOW_CONFIDENCE` (si ya aplicaste el zip de inferencia) |
| Registros V/M con descripción | `"ALFAJORES"`, `"CARAMELOS"`, etc. (sin V/M) |
| Macro "EN GOLOSINAS" descompuesto | 4 registros (ALFAJORES, CARAMELOS, CHICLES, CHOCOLATES) |
| Categoría "RTD" para Gordon's Latas | `"RTD"` (categoría existe en archivo) |
| `tipo_oferta` | `"Publicación"` (no `"Publicidad"` para bloques con %DTO) |

Si algún punto difiere, hay que investigar — probablemente alguna skill perdió una regla en la migración.

## Lo que sigue pendiente para la reunión con David (martes)

Sin cambios respecto a updates anteriores:

1. Convención `OREO TODAS` vs `OREO GALLETITAS`.
2. Lista canónica de categorías incompleta (CHUPETINES, OBLEAS, VINOS ESPUMANTES, CREMAS DE TRATAMIENTO, CREMAS PEINAR).
3. `publicadores.md` con frecuencias.
4. Marcas cerradas sin categoría (caso ESPADOL).
5. Caso PASO DE LOS TOROS (validar enriquecimiento del archivo de categorías).

## Próximos pasos

### Inmediato

1. Pasar el zip a Claude Code.
2. **Crear branch nuevo:** `git checkout -b refactor-skills`.
3. Pedirle a Claude Code:
   - Sobreescribir las 7 skills + system_prompt del zip.
   - **Eliminar la carpeta `skills/core/classifying-folder-type/`** del repo.
   - **Borrar la carpeta `skills/core/_DELETIONS/`** después de leer su README (es solo guía).
4. Revisar el diff. Es grande pero localizado.
5. Commit + push.
6. Re-subir al workspace de Anthropic con `upload_skills.py` (las 7 skills modificadas — la de classifying-folder-type también hay que removerla del agent en la consola si ya estaba referenciada).
7. Re-correr el test contra la página 8 de COTO. Comparar output vs corrida anterior.

### Si todo OK

Hacer merge a main. Quedás con la base limpia para la reunión del martes con David.

### Si algo se rompe

Compará el JSON output contra la corrida anterior. Probablemente alguna skill auxiliar perdió una regla específica que tocaba un caso particular. Si pasa, mandame el diff y lo arreglamos.
