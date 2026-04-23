# Contexto de continuidad — Proyecto GDS Folders

Documento para próximas iteraciones del proyecto con otra instancia de Claude u otra sesión de trabajo.

---

## Qué es este proyecto

Agente de IA que extrae productos de catálogos promocionales de supermercados argentinos para GDSnet. GDSnet es una empresa que vende información estructurada sobre precios y promociones a fabricantes y marcas. Hoy el proceso es 100% manual (equipo humano mirando imágenes y cargando planillas). El agente automatiza eso.

**Cliente:** GDSnet (Argentina). Stakeholders principales: Andrés Hernandez (COO), Javier (CEO), David Feinmann (Project Manager, punto de contacto principal), Juan Vidal Pich (contacto técnico).

**Volumen del cliente:** 30.000 filas por mes (~3000 imágenes/mes).

**Consultor:** Felipe Maliar (junto con Amadeo Tanoira).

---

## Dónde está el proyecto ahora

### Lo que está hecho

1. **PoC completada** sobre COTO Almacén y Bebidas — 70/70 productos, 100% precios, 100% marcas. Cliente aprobó avanzar con implementación.
2. **Arquitectura rearquitecturada (v3)** — se descartó el código Python previo y se rearmó como agente con skills modulares siguiendo el estándar de Claude Skills (YAML frontmatter + markdown). Todo el conocimiento vive en skills, no en código.
3. **8 skills core creadas:**
   - `extracting-products` (skill principal)
   - `reading-prices`
   - `reading-promotions`
   - `classifying-ad-type`
   - `detecting-combos`
   - `handling-closed-brand-categories` (con Caso D: múltiples marcas/variantes bajo promo compartida)
   - `extracting-multiple-products-per-image`
   - `formatting-output` (aplica convenciones de formato de GDSnet al final del proceso)
4. **1 skill de cadena:** `coto`
5. **Testing:** corridas sobre páginas 8 y 10 del catálogo de COTO. El agente funciona bien. Descubrimos que el manual del cliente carga MENOS productos que el agente (hipótesis: GDSnet filtra por categorías contratadas por clientes).

### Repo

GitHub: https://github.com/fmaliarbot/GDS-Folders (privado). La versión v2 ya está en main (con fix de unidad duplicada mergeado). La v3 todavía no se subió — está local.

### Próximos pasos esperados

**Material recibido de David (Abril 23):**
- ✅ Lista de categorías contratadas por GDSnet → incorporada en `references/categorias-contratadas.md` (74 categorías)
- ✅ Lista de sitios de cadenas y diarios a procesar → incorporada en `references/publicadores.md` (40 publicadores, 7 marcados como próximos)
- ✅ Campos actualizados del Excel → identificados vía `PLANILLA_DATOS_FOLDERS_PARA_IA.xlsx` (33 campos oficiales)
- ✅ Cargas manuales de los 7 catálogos → tenemos los Excels de JUMBO, COTO FINDE, YAGUAR, DIARCO, CLARIN COTO, MAXICONSUMO, BECERRA (596 SKUs totales)
- ✅ Aclaración sobre variedades vs líneas distintas → incorporada en skill `handling-closed-brand-categories`

**Todavía pendiente de David:**
- Casos especiales (David los está replanteando con Comercial — advirtió que hay inconsistencias históricas en la metodología de carga)
- Definiciones finales de los campos nuevos del Excel (solapa "Campos" que David dijo que puede cambiar)
- **Convención para el `ID FOLDER`** — actualmente se completa automáticamente en su sistema según la descripción
- **Significado de sufijos `1-2`, `2-2` en SKUs** (aparece en `FERNET BRANCA 750ML 1-2`, `OREO 118G 2-2`, `KNORR GALLINA 6U 2-2`) — se desconoce si son lote, combo, agrupación u otra cosa. Hasta que David confirme, el agente no los agrega.
- **Convención de unidad de medida (ML/GR/CC/L/KG):** el manual mezcla formatos para el mismo tipo de producto. ¿Qué criterio usan? ¿Se sigue la indicación del envase físico, el texto del folder, o hay una convención interna?
- **Caso caja + recarga del mismo SKU:** cuando el folder muestra dos presentaciones del mismo producto (ej: botella + doypack) bajo un único precio y medida, ¿corresponde 1 registro o 2?
- **Ambigüedad de categorías:** `COCINA`, `LIMPIADORES Y MULTIUSOS` y `BAÑO` tienen descripciones idénticas en el archivo de categorías contratadas ("pequeñas superficies: gatillos, repuestos, cremosos, geles"). ¿Cómo desambiguar?
- **Convención ortográfica:** en el manual aparece `BIOACTIVE` (junto) y `BIO ACTIVE` (separado) para la misma línea de producto. ¿Cuál es el canon?
- **Banners de voucher/promo que aplican a categorías enteras (no a productos):** en MAXICONSUMO el manual genera filas "pseudo-producto" (sin SKU, sin precio, sin marca) por cada categoría afectada por un voucher de devolución (ej: MAXI VOUCHER 20% en ACEITES, AGUAS SABORIZADAS, CERVEZAS, etc. generó 16 filas separadas). Esto parece mezclar dos entidades conceptualmente distintas: productos con promoción vs categorías con promoción. **Pregunta prioritaria para David:** ¿deberían estos banners de voucher por categoría registrarse como filas separadas en el mismo esquema de producto, o como metadata aparte del folder? Esto también conecta con el comentario de David sobre "inconsistencias históricas que hay que replantear con Comercial".
- **Billeteras digitales vs tarjetas bancarias:** el esquema tiene `tarjeta_bancos` pero aparecen billeteras digitales (Mercado Pago) que no son tarjetas de banco tradicionales. ¿Se registran en el mismo campo o hay que distinguir? Mismo tema aplica a MODO, Ualá, etc.
- **Doble precio (final + con billetera/tarjeta específica):** algunos folders muestran dos precios simultáneamente (precio final y precio pagando con X billetera/tarjeta). El esquema actual tiene `precio_oferta` + `precio_tarjeta_banco` pero no tiene regla explícita de cuándo usar cada uno.

**Decisiones técnicas pendientes con Juan Vidal Pich (call técnica por agendar):**
- Dónde se almacenan los catálogos descargados (S3/GCS/otro)
- Cómo se expone la base maestra de productos al agente
- Quién dispara el proceso (GDSnet/sistema propio) y con qué frecuencia
- Formato de intercambio de datos
- Permisos y autenticación

**Pendiente futuro:**
- Construir el Agente 1 (descarga de catálogos) — por ahora el foco fue el Agente 2 (extracción)
- Migración a Claude Managed Agents cuando esté todo validado localmente
- Push del proyecto v3 a GitHub (repo privado todavía no creado)

---

## Arquitectura actual del agente

```
gds-folders/
├── agent/
│   ├── system_prompt.md      Instrucciones base del agente
│   └── config.yaml           Modelo (Opus 4.6), skills cargadas, beta flags
│
└── skills/
    ├── core/                 Skills transversales
    │   ├── extracting-products/SKILL.md
    │   ├── reading-prices/SKILL.md
    │   ├── reading-promotions/SKILL.md
    │   ├── classifying-ad-type/SKILL.md
    │   ├── detecting-combos/SKILL.md
    │   ├── handling-closed-brand-categories/SKILL.md
    │   ├── extracting-multiple-products-per-image/SKILL.md
    │   └── formatting-output/SKILL.md
    └── chains/               Skills por cadena
        └── coto/SKILL.md
```

**Nota sobre testing:** no se guardan outputs de pruebas previas en el repo. La convención es correr tests nuevos en cada iteración con imágenes frescas para evitar sesgos. Si se quieren preservar hallazgos, ir al CHANGELOG y documentarlos como nota, no como artefacto persistente.

---

## Decisiones clave que guiaron el diseño

### 1. Filosofía: todo en skills, nada en código

El usuario (Felipe) rechazó explícitamente tener lógica hardcodeada o configuraciones en código Python. El principio es: el agente LLM es el que "decide" qué hacer, las skills son su conocimiento. El código queda reducido a infraestructura y ejecución, no lógica de negocio.

### 2. Separación clara de responsabilidades en skills

- **Skills core:** conocimiento transversal a todas las cadenas (cómo extraer, cómo leer precios, cómo clasificar avisos, etc.)
- **Skills de cadena:** particularidades por cadena (tarjetas de fidelidad con nombres específicos, convenciones de cada retailer)
- **Inicialmente había una capa de "clients"** pero se descartó por sobre-abstracción: este agente es específicamente para GDSnet, así que la skill de formato va en core.

### 3. Principio de "no inventar"

El agente solo registra lo que ve en la imagen. Si un dato no está visible → `null`. No se infiere por conocimiento general. Esto es crítico para la calidad: un `null` es siempre mejor que un dato inventado.

### 4. Filosofía del output

El agente produce output "puro" durante la extracción (preservando formato original). La skill `formatting-output` aplica las convenciones de GDSnet al final. Esto permite debuggear más fácilmente y separa dos responsabilidades: "qué vi" vs "cómo lo entrego".

### 5. Dos agentes en la arquitectura final

- **Agente 1:** descarga y almacenamiento de catálogos (recibe URLs, busca folders, descarga imágenes, organiza con metadata)
- **Agente 2:** extracción (recibe catálogo ya almacenado, extrae productos). El foco actual está acá.

Los detalles del Agente 1 se definen con Juan en la call técnica.

### 6. Hallazgo importante del testing

El manual carga MENOS productos que el agente. En la página 8: agente 8 productos, manual 3 productos. Hipótesis (a confirmar con David): GDSnet solo carga las categorías que tiene contratadas por clientes activos. Esto se resolverá cuando llegue la base de categorías contratadas.

**Implicación:** el agente extrae todo, el filtrado por categorías contratadas es un paso posterior (puede ser otra skill, o un post-procesamiento basado en la base maestra).

---

## Estado de comunicación con el cliente

### Emails recientes relevantes

1. **Entrega PoC** — Felipe envió resultados a Andrés/Javier/David. Aprobado.
2. **Feedback de David** sobre la PoC con 5 puntos (categorías desde base maestra, scoring a reformular, 2 agentes, skills por cadena, costo). Felipe respondió punto por punto.
3. **Javier confirmó avance** con David como PM de ambos proyectos (Folders + Web Scraping).
4. **Felipe preguntó a David** por casos especiales — David respondió que el miércoles manda el material.
5. **Felipe consultó sobre duplicado Federal y convención del Id_Folder** — pendiente respuesta de David.

### Web Scraping (segundo proyecto, menos activo)

GDSnet tiene otro proyecto para incorporar agentes al proceso de web scraping de precios de ecommerce. PoC definida, enviada al cliente. Tres áreas: limpieza/normalización, match EAN↔URL, análisis/insights. Esperando definiciones de David post-reunión del lunes con el equipo actual.

---

## Si empezás una sesión nueva

**Para retomar el trabajo:**

1. Leé el README y CHANGELOG del proyecto (están en el zip)
2. Revisá las skills existentes en `skills/core/` y `skills/chains/coto/`
3. Mirá el system prompt en `agent/system_prompt.md`
4. Si hay material nuevo de David (categorías, reglas, 7 catálogos), ese es el próximo trabajo:
   - Incorporar lista de categorías contratadas al contexto del agente
   - Agregar reglas de casos especiales como skills nuevas o expandir existentes
   - Actualizar skill `coto` o crear nuevas de otras cadenas
   - Ajustar `formatting-output` con campos nuevos del Excel
   - Correr el agente sobre los 7 catálogos y comparar contra los Excel manuales
5. Si no hay material nuevo todavía:
   - Preparar doc de agenda para call técnica con Juan
   - Actualizar el PRD (v0.2 hasta ahora, ir por v0.3)
   - Familiarizarse con Claude Managed Agents (https://platform.claude.com/docs/en/managed-agents/overview)

**Convenciones a mantener:**
- Skills siempre con YAML frontmatter (`name` + `description`)
- `name` en gerundio inglés minúsculas con guiones (ej: `detecting-combos`)
- Contenido de las skills en español
- Nunca meter lógica de negocio en código — siempre en skills
- Testing siempre ciego cuando se validan cambios (no conocer el resultado esperado antes de correr)
- No persistir outputs de pruebas anteriores en el repo — cada test es nuevo y fresco

**Archivos importantes de referencia que NO están en el zip:**
- Excel de carga manual de COTO (`Carga_manual_de_COTO_Almacenes_y_Bebidas.xlsx`) — lo tiene Felipe
- Imágenes del catálogo de COTO — las tiene Felipe en `C:\Users\PC User\Downloads\coto_extracted\coto`
- Informe de Resultados de la PoC (docx entregado al cliente)
- PRD v0.2 (en redacción)
