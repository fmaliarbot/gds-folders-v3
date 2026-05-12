# GDS Folders — Agente Extractor de Productos

> ⚠️ **REPO ARCHIVADO — 2026-05-12**
>
> El código de este repo se mergeó a [`gds-folders-ingestion`](https://github.com/fmaliarbot/gds-folders-ingestion) bajo `resources/agent_v3/`.
> Continuar el desarrollo de skills, system prompt y references **acá NO va a tener efecto productivo** — el container del Dispatcher/Triage lee del bake-in del repo de ingestion.
>
> Para iterar:
> - **Cambios definitivos**: PR sobre `gds-folders-ingestion`, archivos bajo `resources/agent_v3/`.
> - **Dev local** sobre un checkout alternativo: setear `GDS_FOLDERS_V3_DIR=/path/to/folder` antes de invocar el Dispatcher/Triage.
>
> Este repo queda como **referencia histórica** de cómo evolucionó el agente — incluye CHANGELOGs detallados que no se replicaron en el merge para no inflar el repo de ingestion. Ver commits `f1bc835` y anteriores para el árbol completo.

---

Sistema de agentes de IA para automatizar la extracción de productos de catálogos promocionales de supermercados argentinos para GDSnet.

## Arquitectura

Este proyecto está diseñado como un **agente autónomo con skills modulares**, preparado para correr en Claude Managed Agents en producción.

### Componentes

```
gds-folders/
├── agent/                  Configuración del agente
│   ├── system_prompt.md    Instrucciones base del agente
│   └── config.yaml         Modelo, beta flags, metadata
│
├── skills/                 Skills que guían el trabajo del agente
│   ├── core/               Skills transversales a todas las cadenas
│   │   ├── extracting-products/
│   │   ├── building-sku-description/
│   │   ├── reading-prices/
│   │   ├── reading-promotions/
│   │   ├── classifying-ad-type/
│   │   ├── detecting-combos/
│   │   ├── handling-closed-brand-categories/
│   │   ├── extracting-multiple-products-per-image/
│   │   └── formatting-output/
│   └── chains/             Skills específicas por cadena
│       └── coto/
│
└── references/             Datos de referencia del cliente
    ├── categorias-contratadas.md   Categorías que GDSnet procesa por contrato
    └── publicadores.md             Listado de cadenas/mayoristas/farmacias cuyos folders se procesan
```

### Filosofía

- **Todo el conocimiento vive en skills**, no en código Python
- **Cada cadena tiene su propia skill** con sus particularidades (tarjetas de fidelidad, convenciones, etc.)
- **Las skills core son compartidas** entre todas las cadenas y cubren desde extracción hasta formato de output
- **Datos de referencia del cliente** (categorías contratadas, listas canónicas) viven en `references/`, separados de las skills
- **El agente decide** qué skills aplicar en cada momento
- **Agregar una cadena nueva** es crear un nuevo directorio en `skills/chains/` — sin tocar código

## Cómo funciona el agente

1. Recibe un catálogo: colección de imágenes + metadata (cadena, fecha, etc.)
2. Carga las skills core (siempre) + la skill de la cadena correspondiente
3. Procesa cada página siguiendo las skills:
   - Identifica productos visibles
   - Extrae datos estructurados
   - Marca casos ambiguos para revisión humana
4. Produce un output JSON con todos los productos del catálogo

## Estado del proyecto

- ✅ PoC completada sobre COTO Almacén y Bebidas (100% productos identificados, 100% precios)
- ✅ Skills core migradas a formato Claude Skills estándar
- ✅ Skill de COTO creada con particularidades de la cadena
- ✅ Categorías contratadas de GDSnet incorporadas como referencia
- 🚧 En construcción: skills específicas por otras cadenas (cuando lleguen los 7 catálogos)
- ⏳ Pendiente: deploy a Claude Managed Agents
- ⏳ Pendiente: expansión a otras cadenas (Carrefour, Disco, etc.)

## Migración futura a Claude Managed Agents

La estructura del proyecto está diseñada para migrar sin fricción a Claude Managed Agents:

- `agent/system_prompt.md` → system prompt del Agent
- `agent/config.yaml` → parámetros del Agent (model, beta flags)
- `skills/` → skills uploadeadas al Agent
- Tools → definidas al crear el Agent

## Historial

La versión anterior del proyecto (v2 — código Python con pipeline procedural) está archivada en la rama `v2-legacy` para referencia histórica.
