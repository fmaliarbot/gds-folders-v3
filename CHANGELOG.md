# Changelog — GDS Folders

## v3.11 — Test ciego MAXICONSUMO: hallazgos documentados (Abril 2026)

### Sin cambios en skills

Se corrió un test ciego con MAXICONSUMO (folder "SOLO POR HOY" del 13/04/2026). El resultado reveló inconsistencias importantes entre la metodología de carga manual de GDSnet y el principio de extracción del agente, pero **estas inconsistencias no ameritan cambios en las skills** — son decisiones de diseño del cliente que deben ser resueltas por David y el área Comercial de GDSnet.

### Hallazgo principal

El manual de MAXICONSUMO incluye **19 filas** de las cuales:

- **4 son productos reales con precio** (Choclo Marolio, Knorr Caldo, Plusbelle, Netic)
- **15 son "pseudo-productos"** generados a partir del banner MAXI VOUCHER 20% — una fila por cada categoría afectada por el voucher, sin SKU/precio/marca/medida específicos

El test ciego (una instancia nueva de Claude aplicando las skills) extrajo **correctamente los 4 productos** y documentó su decisión conservadora de no desdoblar el banner de voucher en filas de producto (ya que eso violaría el principio "solo registrar si está explícitamente para ese producto").

### Calidad del test ciego

El agente demostró robustez en múltiples dimensiones:
- Separación correcta `tarjeta_fidelidad` (no aplicó MAXI VOUCHER por no estar atado a productos) vs `tarjeta_bancos` (aplicó MERCADO PAGO a cada producto)
- Promos en campos correctos: `tipo_promocion_tarjeta_bancos: "5%DTO SIN TOPE"`, no en `tipo_promocion` general
- Aplicación exitosa de la señal de códigos múltiples (v3.10): identificó variedades en Knorr (3 códigos → 3 sabores) y Plusbelle (6 códigos → 6 variantes)
- Aplicación estricta de "no inventar variedades desde colores" en Plusbelle (variedades visibles sin texto legible → `tipo_variedad: null`)
- Decisión honesta sobre categoría no canónica del Choclo Marolio (`nombre_categoria: null` + nota)

### Preguntas prioritarias trasladadas a David

Tres nuevas preguntas se agregaron al HANDOFF a partir de este test:

1. **Pseudo-productos de voucher por categoría:** cómo tratar banners tipo "20% con MAXI VOUCHER en ACEITES, BEBIDAS, CERVEZAS..." — ¿filas separadas como hoy, o metadata del folder?
2. **Billeteras digitales vs tarjetas bancarias:** Mercado Pago, MODO, Ualá no son tarjetas tradicionales — ¿mismo campo o distinción?
3. **Doble precio (final + con billetera/tarjeta específica):** regla de cuándo usar `precio_oferta` vs `precio_tarjeta_banco`

### Lo que se mantuvo sin modificar

No se agregaron ejemplos específicos de productos a las skills. No se incorporaron listas de categorías faltantes para "conservas vegetales" (choclo enlatado). No se formalizaron reglas basadas solo en los 4 productos de un único folder. La filosofía de evitar overfitting desde v3.9 se mantuvo consistente en esta iteración.

---

## v3.10 — Códigos múltiples como señal de variedad (Abril 2026)

### Modificados

- Skill `handling-closed-brand-categories` — agregada señal complementaria para detección de variedades: cuando el folder lista múltiples códigos de producto bajo una misma imagen y precio, esto confirma objetivamente que hay variantes agrupadas. La señal complementa (no reemplaza) la inspección visual de texto legible en los envases.

### Comportamiento esperado

- Códigos múltiples + texto legible de variante → registrar como variedad con `tipo_variedad` apropiado y elegir variante concreta para `descripcion`.
- Códigos múltiples + sin texto diferenciador → registrar como variedad con `tipo_variedad: null` + nota en `comentarios`. La multiplicidad de códigos sirve como confirmación de que hay variantes aunque no se identifiquen visualmente.

### Motivación

Durante el test ciego de YAGUAR el agente detectó que en varios productos (obleas, fideos semolados) el folder lista explícitamente múltiples códigos asociados a la misma imagen y precio. Esto es un indicador más objetivo que la inspección visual: si el emisor del folder asoció múltiples SKUs a una imagen es porque hay múltiples variantes. Incorporar esto como señal refuerza la detección de variedades sin introducir overfitting (es una heurística estructural, no específica de ningún producto o marca).

### No modificado

Se evaluó también agregar un principio sobre "discrepancia folder vs packaging" (cuando el texto inferior del folder dice algo distinto al packaging del producto, ej: "1KG" sin mencionar "Clásico" cuando el envase dice "Clásico"). Se decidió no incorporarlo por ahora para evitar sumar complejidad mientras no haya suficiente evidencia.

---

## v3.9 — Refinamiento de skills tras test ciego BECERRA (Abril 2026)

### Contexto

Se corrió un test ciego del agente (instancia nueva de Claude aplicando las skills v3.8 sobre la imagen de BECERRA sin ver el manual de David). El resultado reveló que los 6 productos se identifican bien (precios, marcas, medidas correctas en ambos runs), pero hay puntos de ambigüedad en las skills que generaron divergencias consistentes entre runs.

### Modificados (principios generales, sin overfitting)

- Skill `classifying-ad-type` — agregado principio sobre **agrupadores no-marca**: cuando un banner agrupa productos de marcas distintas (fabricantes, eventos, campañas) cada uno con su precio individual, los productos se clasifican según su propio tratamiento visual. `publicacion` se reserva para agrupadores que son una marca comercial específica.
- Skill `reading-promotions` — agregada clarificación sobre **banners decorativos sin estructura promocional**: el campo `tipo_promocion` requiere una mecánica identificable (porcentaje, NxM, segunda unidad a X%, beneficio con tarjeta). Texto de marketing genérico que destaca el precio pero no comunica estructura promocional → `null`. Principio de "ante la duda, null" explícito.

### Trasladado a preguntas pendientes con David (no son cambios de skills)

Varios puntos que el test ciego reveló se identificaron como decisiones del cliente, no parches de skills:

- Convención de unidad de medida (ML/GR/CC/L/KG) — el manual es inconsistente
- Caso "caja + recarga del mismo SKU" — ambigüedad estructural
- Solapamiento de categorías COCINA / LIMPIADORES Y MULTIUSOS / BAÑO en el archivo
- Convención ortográfica BIOACTIVE vs BIO ACTIVE

### Lo que NO se modificó (decisión explícita)

El test ciego sugirió varios cambios tentadores (listas de ejemplos específicos de productos, reglas tipo "para shampoo usar ML, para crema usar GR", ejemplos por marca) que se descartaron por riesgo de overfitting. Las skills deben expresar **principios generalizables** — un ejemplo útil hoy puede quedar obsoleto apenas aparezca un producto nuevo.

### Resultado medible del test

Comparación 3 vías (Manual de David / V4 nuestro / Test ciego instancia nueva):

- Matches exactos descripción vs Manual: V4 = 3/6, Test ciego = 0/6
- Matches exactos categoría vs Manual: V4 = 4/6, Test ciego = 5/6
- Convergencia V4 vs Test ciego en estructura general: alta (6/6 productos, 6/6 marcas, 6/6 precios, 6/6 medidas numéricas)

Las 3 diferencias principales del Test ciego vs Manual se deben a ambigüedades de convención (ML vs CC en medidas, no a errores de extracción). El test confirmó que las skills funcionan para una instancia fresca y detectó ambigüedades reales que ahora están documentadas.

---

## v3.8 — Regla estricta de nombre literal para `nombre_categoria` (Abril 2026)

### Modificados

- Skill `extracting-products` — la sección del campo `nombre_categoria` ahora tiene una regla crítica explícita: el valor del campo **siempre** debe ser literalmente idéntico al valor de la columna `CATEGORIAS` del archivo `references/categorias-contratadas.md`, sin modificaciones de ningún tipo.
- La regla prohíbe explícitamente: "corregir" singular/plural, "normalizar" mayúsculas/minúsculas, "arreglar" typos, o interpretar el nombre de otra forma.

### Motivación

Durante el test de BECERRA, el agente asignó `DESODORANTES DE AMBIENTE` (plural, forma canónica del archivo) mientras que el manual cargó `DESODORANTE DE AMBIENTES` (singular, invertido). Esta diferencia de formato rompe cualquier intento de match exacto entre el output del agente y la base maestra de GDSnet.

La skill ya mencionaba usar el valor "exacto" del archivo, pero no era suficientemente enfática para evitar que el agente aplique normalizaciones de sentido común (como uniformar singular/plural). Al hacer la regla crítica y darle ejemplos explícitos del caso DESODORANTES, se reduce la probabilidad de desviaciones.

Caso paradigmático: **el propio manual de carga histórica tiene errores** respecto al archivo canónico de categorías. El agente, al seguir estrictamente el archivo canónico, puede incluso estar "más correcto" que las cargas manuales — pero lo importante es que sea **consistente** con el archivo, que es el único criterio que garantiza el match con la base maestra.

---

## v3.7 — Skill dedicada para construcción de SKUs (Abril 2026)

### Agregados

- Nueva skill `skills/core/building-sku-description/SKILL.md` dedicada exclusivamente a la construcción del campo `descripcion` siguiendo las convenciones de SKU de GDSnet.
- Definición de los 3 patrones canónicos identificados en los 596 SKUs del Excel de David:
  - **Patrón A** (36% de los casos): `[MARCA] [LÍNEA] [TIPO_SI_AMBIGUO] [VARIANTE] [MEDIDA][U_MEDIDA]` — ej: `NESCAFE GOLD 95G`, `COCA COLA ZERO 2.5L`, `DOVE SH RECON COMPLETA 400ML`
  - **Patrón B** (46%): `[MARCA] [TIPO DE PRODUCTO]` — ej: `CIF BAÑOS`, `AMANDA YERBAS`, `ARCOR CARAMELOS`
  - **Patrón C** (18%): `[MARCA] [TIPO DE PRODUCTO] TODOS|TODAS` — ej: `OREO TODAS`, `KNORR CALDOS TODOS`
- **Jerarquía de componentes** dentro del Patrón A con distinción entre imprescindibles (marca, línea, medida), condicionales (tipo de producto si la línea sola es ambigua) y opcionales (variante cuando es legible).
- Árbol de decisión para elegir qué patrón usar en cada caso.
- Criterio visual para distinguir "línea" vs "variante": la línea es la palabra destacada en el envase (banner, fuente grande); la variante es texto menor que especifica algo dentro de la línea.
- Diccionario de abreviaciones confirmadas (Opción C — híbrido): términos frecuentes con abreviación establecida (`SH`, `CR`, `DP`, `LIQ`, `TBK`, `S/AZ`, `C/DOSIF`, `V/M`, etc.) + criterio para que el agente abrevie ad-hoc cuando corresponda, marcándolo en `comentarios`.
- Reglas de formato generales: mayúsculas, sin acentos, coma decimal, medida pegada a unidad.

### Nota importante — pregunta abierta con David

Los sufijos `1-2`, `2-2` y similares aparecen al final de algunos SKUs (`FERNET BRANCA 750ML 1-2`, `OREO 118G 2-2`, `KNORR GALLINA 6U 2-2`). Su significado se desconoce. Hasta que David confirme qué representan (lote, combo, agrupación, etc.), el agente **no** agrega estos sufijos a sus descripciones. Pregunta registrada en la skill y en la lista de pendientes del HANDOFF.

### Motivación

Durante el test de BECERRA, Felipe detectó que la descripción es el campo más crítico para el match con la base maestra de GDSnet, y que GDSnet tiene una convención estructurada para formar los SKUs que el agente no estaba aplicando. La descripción genérica que producía el agente ("Limpiador Cif Crema Multiuso Original") diverge del formato canónico esperado ("CIF BIO ACTIVE CREMOSO 750G").

Al probar el primer output del agente con la skill nueva, salió otro insight clave: al omitir el modelo/línea del producto (`SKIP LIQ CICLOS CORTOS 800ML` vs el correcto `SKIP EXPERT CICLOS CORTOS 800ML`), el SKU pierde información crítica para el match. Esto llevó a formalizar la jerarquía de componentes: la línea es tan imprescindible como la marca, y la variante es opcional.

Separar esta lógica en una skill dedicada tiene 3 ventajas:
1. La complejidad de los 3 patrones + la jerarquía + el diccionario de abreviaciones no cabe cómodamente en `extracting-products`.
2. Una skill única para SKUs facilita iteración: cada vez que se descubra un nuevo patrón o abreviación, se actualiza un solo archivo.
3. El agente puede invocar esta skill explícitamente cada vez que tiene que armar un `descripcion`, sin duplicar reglas en otras skills.

### Modificados

- Skill `extracting-products` — la sección del campo `descripcion` ahora referencia explícitamente `building-sku-description` como la fuente autoritativa para construir el SKU.

---

## v3.6 — Refuerzo de la regla "no inventar" para variedades no legibles (Abril 2026)

### Modificados

- Skill `handling-closed-brand-categories` reforzada con regla estricta sobre variedades no legibles: cuando se ven múltiples envases del mismo producto sin texto diferenciador visible, el agente NO debe inventar nombres de variedad basándose en colores de packaging.
- Agregada subsección "Regla para variedades no legibles" con criterio estricto: `tipo_variedad: null`, descripción genérica y nota `"variedades visibles sin texto legible"` en `comentarios`.
- Criterio claro de "legible" vs "no legible": legible = texto impreso diferenciador en la etiqueta (ej: "Frescura Cítrica", "Original"); no legible = envases con colores distintos pero sin texto de variedad visible.
- Agregado al "Qué NO debe hacer": explícitamente prohibido inventar variedades desde colores de packaging.

### Motivación

Durante el test sobre el catálogo BECERRA, el agente (el redactor de estas skills actuando como agente) generó output que incluía `tipo_variedad: "Varias fragancias"` para un producto Lavavajilla Cif con 3 envases de colores distintos sin texto de fragancia visible. Esto es un caso textbook de alucinación visual: el agente infirió fragancias desde los colores cuando no había información real para hacerlo.

Felipe detectó el problema y propuso la "Opción A" (conservadora): si no se puede leer el texto de variedad, `tipo_variedad: null`. La skill actualizada formaliza esta regla con ejemplo explícito y refuerzo en "Qué NO debe hacer".

Este tipo de regla es especialmente importante porque el principio "no inventar" es fácil de respetar cuando el dato está completamente ausente (precio no visible → null) pero más difícil cuando hay *alguna* información visible que invita a especular (colores de envase → fragancias inferidas).

---

## v3.5 — Incorporación del listado de publicadores (Abril 2026)

### Agregados

- Archivo `references/publicadores.md` con los 40 publicadores (cadenas, mayoristas, farmacias y diarios) cuyos folders procesa o planea procesar GDSnet.
- Marca 🎯 sobre los 7 publicadores prioritarios para la próxima ronda de extracción (antes resaltados en amarillo en el Excel original): DIARCO, MAXICONSUMO, YAGUAR, BECERRA, COTO, JUMBO y DIARIO CLARÍN.
- Sección con observaciones operativas: publicadores que publican solo por Facebook o con flyers físicos, tratamiento especial de los diarios como agregadores multi-cadena, convenciones del campo CANAL.

### Notas importantes

- **Credenciales de diarios:** el Excel original incluye usuario y contraseña para Clarín y La Nación. Se omiten en el archivo del repo por seguridad; el equipo de GDSnet las mantiene aparte.
- **Skills de cadena pendientes:** de los 40 publicadores, solo COTO tiene skill específica hoy. El resto se procesa con las skills core. A medida que se procesen catálogos de más publicadores, se irán creando las skills correspondientes cuando se detecten patrones únicos.

### Motivación

David envió el archivo `PUBLICADORES__Y_LINKS.xlsx` como parte del paquete de referencia inicial. El listado documenta el alcance operativo del proyecto y sirve para planificar qué skills de cadena crear a futuro. No es una skill y no modifica el comportamiento del agente en el procesamiento de páginas.

---

## v3.4 — Asignación de categorías canónicas en todos los ejemplos (Abril 2026)

### Modificados

- Skill `extracting-products` — reformulada la regla de `nombre_categoria`. Antes: "solo si está escrita explícitamente en el folder". Ahora: el agente matchea el producto contra la lista canónica de `references/categorias-contratadas.md` y asigna el valor exacto. Si no hay match claro: `null` + nota en `comentarios`.
- Skill `extracting-products` — agregada sección "Excepción controlada: matching contra listas canónicas del cliente" dentro de la regla absoluta "no inventar datos", aclarando que matchear contra listas canónicas provistas por el cliente no viola el principio de no inventar.
- 16 ejemplos JSON en las skills actualizados con categorías canónicas reales:
  - Cervezas (Miller, Heineken, Imperial Golden, Blue Moon) → `CERVEZA`
  - Yerbas (Nobleza Gaucha, Cruz Malta, Taraguí) → `YERBA MATE`
  - Vermouth Federal Rosato/Rosso → `APERITIVOS C/ALCOHOL`
  - Jugo Manzana Tutti → `RTD` (Ready To Drink — bebidas listas para tomar, distinto de `JUGOS EN POLVO`)
  - Fanta regular/Zero → `GASEOSAS`
  - Amaro Ramazzotti → `APERITIVOS C/ALCOHOL`
  - Champagne Mumm → `CHAMPAGNE`
  - Mostaza y Ketchup Natura → `ADEREZOS`
- 1 ejemplo mantiene `null` intencional: "Productos Espadol" (genérico, múltiples categorías posibles como `ALCOHOL EN GEL`, `JABONES DE TOCADOR`, etc. sin poder decidir sin más contexto).

### Motivación

Antes, los ejemplos JSON mostraban `"nombre_categoria": null` porque la regla anterior solo aceptaba categoría si estaba escrita en el folder. Al cambiar la regla (usar la lista canónica de GDSnet), los ejemplos tenían que actualizarse para enseñar al agente el comportamiento correcto. Dejar los ejemplos con `null` transmitiría la regla vieja.

---

## v3.3 — Incorporación de categorías contratadas de GDSnet (Abril 2026)

### Agregados

- Nueva carpeta `references/` en la raíz del proyecto para datos de referencia del cliente.
- Archivo `references/categorias-contratadas.md` con las 74 categorías que GDSnet procesa actualmente por contrato. Cada categoría incluye el detalle de qué productos abarca (`INCLUYE`) y cuáles están explícitamente excluidos (`NO INCLUYE`).
- 16 categorías tienen exclusiones explícitas documentadas (ej: Chocolates NO incluye chocolate para taza; Vinos NO incluye vino Patero; Tomates solo incluye salsas/puré/pulpa, no trituradas ni latas).

### Modificados

- Skill `extracting-products` — la sección del campo `nombre_categoria` ahora referencia el archivo de categorías contratadas. **El agente sigue sin filtrar** por estas categorías (extrae todo lo visible); el filtrado es una decisión de pipeline posterior.
- README actualizado con la nueva carpeta `references/` y el estado del proyecto.

### Decisión de diseño

El agente extrae **todos los productos visibles** del catálogo sin importar si su categoría está contratada o no. El filtrado por categorías contratadas ocurre en una capa posterior al output del agente. Razones:

1. Cuando GDSnet contrate categorías nuevas, los datos ya están capturados — no hay que re-procesar catálogos anteriores.
2. Separa extracción (responsabilidad del agente) de filtrado comercial (responsabilidad del pipeline).
3. Simplifica la lógica del agente: una regla menos que aplicar.

### Motivación

David Feinmann (PM de GDSnet) envió el archivo `CATEGORIAS_FOLDERS.xlsx` con las categorías contratadas, destacando que es importante que el agente reconozca qué categorías bajar para no procesar productos de categorías no contratadas. La decisión de hacer el filtrado en una capa posterior (en vez de en el agente) balancea el pedido del cliente con flexibilidad futura.

### Nota sobre typos en las categorías

El archivo original contiene algunos typos (`LIUSTRAMUEBLES`, `TODOAS`, `PREMEZCALAS`, `PREMEZCALS`). Se preservaron tal cual para garantizar match exacto contra la base maestra de GDSnet. Si GDSnet corrige la fuente, actualizar el archivo en este repo.

---

## v3.2 — Distinción entre variedades y líneas distintas + campo comentarios (Abril 2026)

### Agregados

- Campo `comentarios` (texto libre) agregado al esquema de salida. Usos principales:
  - `"varios sabores"` para bloques de variedades (siguiendo la convención de GDSnet)
  - Información adicional visible no cubierta por otros campos (ej: "edición limitada")
  - Notas de incertidumbre para el revisor humano (ej: "precio poco legible")
- Regla en `formatting-output` para el campo `comentarios` (se preserva tal cual, sin transformaciones)

### Modificados

- Skill `handling-closed-brand-categories` refactorizada en el Caso D para distinguir explícitamente entre:
  - **Variedades** (fragancias, sabores, tipos del mismo producto base): generan UN solo registro con una variedad visible concreta elegida en la descripción y el texto `"varios sabores"` en el campo `comentarios`
  - **Líneas distintas** (fórmulas, composiciones o tipos estructuralmente distintos, aunque compartan marca): generan N registros, uno por línea
  - **Marcas distintas**: N registros, uno por marca
- Agregada subsección "Cómo distinguir en la práctica" con 4 preguntas prácticas para resolver casos ambiguos
- Agregados Ejemplos 3 (Jugos Tutti con una variedad concreta elegida + comentario "varios sabores") y 4 (Fanta regular/Zero → 2 registros)
- Skill `extracting-products` — agregado campo 13 (`comentarios`) con su descripción, y actualizado el JSON schema de respuesta
- Todos los ejemplos JSON en las skills actualizados para incluir el campo `comentarios`

### Notas de implementación pendiente

- El nombre `comentarios` es provisional; el esquema final del Excel de GDSnet puede renombrarlo a `observaciones` u otro término. Cuando David confirme el esquema final, el renombre es un find/replace en todas las skills.

### Motivación

El Caso D original mezclaba en una misma categoría cosas que David (PM del cliente) aclaró son distintas: "Las variedades, que son fragancias, sabores o tipos van en un solo registro. Los productos que son distintos en marca o distinta línea de producto va cada uno en registros diferentes aunque se presenten juntos."

Además, para el caso de variedades la convención de carga de GDSnet es elegir una variedad concreta visible en la imagen para el registro, y aclarar "varios sabores" en comentarios (no usar una descripción genérica tipo "varios sabores" sin aclaración).

El caso de Federal Rosato/Rosso confirma la regla: son líneas distintas (vermouth rosado vs rojo), no variedades, por eso van en dos registros separados. El caso de Jugos Tutti es el opuesto: son variedades del mismo producto, van en un solo registro con una variedad concreta elegida y el comentario "varios sabores".

---

## v3.1 — Skill de formato de output y Caso D en marcas cerradas (Abril 2026)

### Agregados

- Skill `formatting-output` con las reglas de formato del Excel de carga de GDSnet (unidades compactas en mayúsculas, promociones con sufijo DTO, SKU concatenado, etc.)
- Actualización del system prompt del agente con el orden correcto de aplicación: extracción pura → skills core → skill de cadena → formatting-output

### Modificados

- Skill `handling-closed-brand-categories` extendida con el Caso D: múltiples marcas o variantes bajo una promoción compartida (ej: "2x1" con 4 marcas de cerveza, Federal Rosato/Rosso con mismo precio). Regla: una entrada por marca o variante visible.

### Motivación

El test sobre la página 10 y la página 8 del catálogo de COTO reveló dos mejoras necesarias: 1) el agente estaba consolidando bloques multi-marca/multi-variante en una sola entrada cuando el manual hace una por variante, 2) el formato del output no coincidía con las convenciones del Excel de GDSnet. Se resuelven ambos con skills en vez de código.

---

## v3.0 — Rearquitectura a agente con skills (Abril 2026)

Cambio completo de arquitectura: de pipeline procedural en Python a agente autónomo con skills modulares.

### Motivación

La v2 tenía toda la lógica de negocio y el conocimiento específico por cadena hardcodeado en código Python (CHAIN_CONFIGS, reglas en constantes, clasificaciones en funciones). Agregar una cadena nueva requería tocar código. El scoring de confianza y las reglas de casos especiales estaban dispersos y eran difíciles de iterar.

### Cambios principales

- Eliminado todo el código Python del agente anterior
- Eliminado el pipeline procedural
- Creada estructura de skills en formato estándar Claude Skills con YAML frontmatter
- Skills core que aplican a todas las cadenas
- Skills específicas por cadena (empezando con COTO)
- Agente diseñado para correr en Claude Managed Agents
- System prompt que orquesta el uso de skills

### Estado de las skills

- ✅ 7 skills core creadas: extracting-products, reading-prices, reading-promotions, classifying-ad-type, detecting-combos, handling-closed-brand-categories, extracting-multiple-products-per-image
- ✅ Skill de COTO creada con toda la información que antes estaba en CHAIN_CONFIGS

---

## v2.1 — Fix del bug de unidad duplicada (Abril 2026)

Archivos modificados: `rules.py`

Fix de la duplicación de unidad en formato SKU. 18 de 70 SKUs tenían la unidad repetida (ej: "MARCUS MALBEC 750CC 750CC"). Se agregó un helper para detectar si la unidad ya estaba en la descripción antes de concatenarla.

---

## v2.0 — Versión usada para la PoC con GDSnet

Primera versión funcional del agente. Pipeline procedural en Python con vision API.

Resultados sobre COTO Almacén y Bebidas:
- 70/70 productos identificados correctamente
- 100% de coincidencia en precios
- 100% de identificación de marcas

Esta versión quedó archivada en la rama `v2-legacy`.

---

## v1 — Versión inicial experimental

Primeros intentos de extracción. No productiva.
