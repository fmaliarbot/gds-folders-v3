# CHANGELOG — Update post-feedback David (29-abril-2026)

Este update incorpora los ajustes que David Feinmann (GDSnet) envió por email y en los documentos:

- **Automatización_Folders_-_Ajustes** — reemplaza al documento de ajustes anterior.
- **PLANILLA_DATOS_FOLDERS_PARA_IA** — schema canónico final (33 campos en el Excel, 26 en el agente Agent 2).
- **Publicadores y Links** — pendiente, no recibido aún.

## Resumen ejecutivo

El cambio más grande es **el schema canónico de salida**, que se modificó significativamente. La mayoría de las skills core requirieron actualización para alinearse, y se agregaron 2 skills nuevas. La arquitectura general del agente se mantiene (skills modulares + agent runtime + JSON output).

Adicionalmente, se decidió arquitectura de **2 agentes** a futuro:
- **Agent 1 (Folder Metadata):** descarga catálogos, extrae metadata del folder, asigna ID. Por construir.
- **Agent 2 (Products Extraction):** este. Procesa una página por vez y devuelve productos.

Esta versión del repo construye **solo Agent 2**.

## Cambios al schema canónico

### Estructura general

- El output del agente ahora es solo `{ "productos": [...] }`. La metadata del folder vendrá del Agent 1 (futuro) o del orquestador.
- Cada producto tiene **26 campos** (antes ~13).
- Se agregaron campos para **revisión humana** (`needs_review`, `review_reasons`).

### Campos nuevos agregados

| Campo | Razón |
|---|---|
| `descripcion_literal` | David lo agregó como campo separado (texto del folder sin transformar, para auditoría). |
| `id_sku_interno_spm` | Código interno publicado por la cadena (cuando aparece). Antes no estaba. |
| `ean` | Código de barras visible. Antes no estaba. |
| `medida` (separada) | Antes la medida iba pegada en `unidad_medida`. Ahora son 2 campos. |
| `u_medida` (separada) | Códigos canónicos: GR, KG, CC, ML, L, UNI. |
| `precio_anterior` | Renombre de `precio_regular`. |
| `precio_tarjeta_banco` | Precio aplicando tarjeta bancaria. Antes no estaba. |
| `precio_tarjeta_fidelidad` | Precio aplicando tarjeta de fidelidad. Antes no estaba. |
| `tipo_promocion_oferta` | Renombre de `tipo_promocion`. |
| `tipo_promocion_tarjeta_fidelidad` | Promoción adicional con tarjeta de fidelidad. Antes no estaba. |
| `tipo_promocion_tarjeta_bancos` | Promoción adicional con tarjeta bancaria. Antes no estaba. |
| `tarjeta_bancos` | Nombre de tarjetas bancarias asociadas. Antes no estaba. |
| `tipo_variedad` | "Varios sabores", "Varias fragancias", "Varios tipos". Antes no estaba. |
| `descripcion_variedad` | Categorías afectadas en categorías cerradas. Antes no estaba. |
| `maximo_unidades` | Máximo permitido por la oferta (cuando se especifica). Campo NUEVO que David sumó en esta iteración. |
| `needs_review` | Booleano de control de calidad. |
| `review_reasons` | Array de códigos canónicos de revisión. |

### Campos renombrados

| Antes | Ahora | Notas |
|---|---|---|
| `nombre_categoria` | `categoria` | |
| `precio_regular` | `precio_anterior` | |
| `tipo_imagen` | `tipo_oferta` | |
| `tipo_promocion` | `tipo_promocion_oferta` | |
| `comentarios` | (eliminado) | Reemplazado por `review_reasons`. |

### Cambios en valores canónicos

- **`tipo_oferta`:** antes 3 valores (`regular`, `destacada`, `publicacion`), ahora **4** (`Regular`, `Destacado`, `Publicidad`, `Publicación`). La diferencia clave: `Publicidad` (sin precios) ahora es distinta de `Publicación` (bloque de fabricante con datos).

## Cambios en skills

### Skills actualizadas (10)

1. **extracting-products** — re-escrita con los 26 campos del schema canónico, separación `medida` / `u_medida`, EAN solo si está visible (sin matching contra maestro), `needs_review` y `review_reasons`. Aclara que el matching de EAN no es trabajo del agente.

2. **formatting-output** — re-escrita. Antes era para Excel, ahora produce el JSON estructurado final con todas las reglas de validación.

3. **classifying-ad-type** — actualizada a los 4 valores canónicos. Antes mezclaba `Publicidad` y `Publicación`, ahora son distintas.

4. **detecting-combos** — re-escrita con la regla explícita de Principal / Secundario, Carrier en el secundario, `precio_oferta = 0` para el secundario, y el desempate "si no hay precio, vale el orden de la descripción".

5. **handling-closed-brand-categories** — re-escrita con los 4 casos canónicos: una marca + una categoría, una categoría + varias marcas, varias marcas sin categoría, y caso ESPADOL (marca cerrada sin lista canónica).

6. **extracting-multiple-products-per-image** — re-escrita con la distinción crítica entre **variedades** (1 registro con `tipo_variedad`) y **líneas distintas** (N registros). Esta es la fuente de la inconsistencia que detectamos en el test de Coca Cola Zero / Sabor Liviano.

7. **reading-prices** — actualizada para los 4 campos de precio canónicos. Antes tenía 2 (regular + oferta), ahora 4.

8. **reading-promotions** — actualizada para las 3 dimensiones de promoción. Antes era 1 campo, ahora 3 (oferta + tarjeta_fidelidad + tarjeta_bancos).

9. **building-sku-description** — cambios mínimos. La skill ya estaba alineada con el formato canónico. Se actualizó la referencia a `comentarios` (eliminado) por `review_reasons`.

10. **coto** — actualizada con el formato canónico de campos (mayúsculas, sin acentos), descuentos típicos de Comunidad COTO con la nueva estructura de promociones, mapeo de zonas canónicas, y caso especial CLARIN (cuando el folder es inserción del diario).

### Skills nuevas (2)

1. **classifying-folder-type** — clasifica el folder entre Regular / Especial / Flyers. Idealmente aplica con visibilidad del catálogo completo (función del Agent 1). Para Agent 2 (este agente), aplica solo si el contexto provee suficiente información.

2. **flagging-for-review** — define los códigos canónicos de `review_reasons` y cuándo aplicar cada uno. Lista cerrada de 11 códigos:
   - `PRODUCT_NOT_RECOGNIZED`
   - `BRAND_NOT_RECOGNIZED`
   - `CATEGORY_NOT_DEFINED`
   - `MEASURE_NOT_VISIBLE`
   - `PRICE_AMBIGUOUS`
   - `EAN_NOT_FOUND` (probablemente no se use desde el agente)
   - `METADATA_MISMATCH`
   - `LOW_CONFIDENCE`
   - `MULTIPLE_SKUS_SHARED_CODE`
   - `COMBO_AMBIGUOUS`
   - `CLOSED_BRAND_WITHOUT_CATEGORY_LIST`

## Cambios en references

### References nuevas

1. **`zonas-geograficas.md`** — los 7 códigos de zona canónicos de GDSnet con sus provincias asociadas (CAP Y GBA, CENTRO, ESTE, NEA, NOA, OESTE, SUR).

### References pendientes

- **`publicadores.md`** con frecuencias — David lo mencionó en el email pero no llegó al chat. Pendiente.
- **`marcas-cerradas-sin-categoria.md`** — caso ESPADOL. Necesita lista canónica de GDSnet. Pendiente de la reunión del martes.
- **`categorias-contratadas.md`** — David lo da por hecho pero la lista definitiva no llegó. Las hojas del Excel tienen las categorías reales pero hay que consolidarlas.

## Cambios en `agent/`

- **`system_prompt.md`** — re-escrito para reflejar el alcance restringido (Agent 2 solo, una página por turn, sin metadata extracción).
- **`config.yaml`** — no se modifica en este update (lo recibimos como tal de la versión anterior). Los cambios al config (modelo, network access para web_fetch en casos de bocaditos, etc.) se aplicarán en la consola de Anthropic Managed Agents directamente.

## Decisiones de arquitectura tomadas

1. **Output JSON, no Excel.** El agente devuelve JSON; la conversión a Excel/CSV vive en la integración con GDSnet.

2. **Agente por página, no por catálogo entero.** Sessions individuales paralelizadas por el orquestador. Mejor confiabilidad, debugging y costos.

3. **Metadata opcional, prioridad a la imagen.** Si la metadata contradice la imagen, ganan los ojos del agente y se flagea con `METADATA_MISMATCH`.

4. **No matching contra maestro de SKUs en el agente.** David lo confirmó textualmente: *"este proceso puede no hacerlo el agente y quedar del lado de la integración"*.

5. **Robustez para input manual.** El sistema acepta imágenes de cualquier origen (descarga automática, escaneos, fotos de folletos físicos). Mismo comportamiento en los 3 casos.

## Decisiones diferidas (para discutir el martes con David)

1. **Schema definitivo:** la lista de 26 campos se basa en lo que David envió. Confirmar que el orden y los nombres son los finales antes de hacer el cierre.

2. **Códigos de `review_reasons`:** David usa la nomenclatura "corrección de tipo 2" que sugiere una taxonomía interna en GDSnet. Confirmar si los códigos que definimos coinciden o hay que mapear.

3. **Caso snacks/bocaditos sin descripción:** David dice *"se ingresa al sitio del supermercado"*. Decidir si va en Agent 1 (descarga) o si Agent 2 reactiva `web_fetch` para esos casos.

4. **Lista de marcas cerradas sin categoría (caso ESPADOL):** quién la mantiene, dónde vive, cómo se actualiza.

5. **`tipo_folder` desde una sola página:** ¿lo deduce el agente con contexto parcial, o siempre lo asigna el orquestador / Agent 1?

6. **Arquitectura del Agent 1:** alcance, qué agente decide la frecuencia de descarga, autenticación con sitios de cadenas.

## Próximos pasos

### Inmediato (antes del martes)

- Re-subir las 12 skills al workspace de Anthropic con `upload_skills.py` (la script ya existente, pero filtrada para subir solo las que cambiaron).
- Actualizar el agent en la consola para referenciar las nuevas skill IDs (o crear nuevas versiones).
- Re-correr los 2 tests de COTO (página 8 y foto-2) y validar que ahora respetan el schema nuevo.

### Post-reunión del martes

- Subir `publicadores.md` con frecuencias.
- Decidir caso snacks/bocaditos.
- Construir Agent 1 si David confirma que es necesario.
- Definir la integración GDSnet → flujo del operador (UI / script / Drive automation).
