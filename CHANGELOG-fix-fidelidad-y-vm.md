# CHANGELOG — Update Fix Fidelidad y V/M (5-mayo-2026)

Tercer update, consolidando los dos bugs detectados en la corrida del 4 de mayo (página 8 COTO Super Finde):

1. **Tarjeta de fidelidad alucinada** — el agente puso `COMUNIDAD COTO` a Antares aunque el badge no era visible para ese SKU.
2. **Prefijo `V/M` en descripción** — el agente generaba `V/M ALFAJORES`, `V/M CARAMELOS`, etc., cuando lo correcto es `ALFAJORES`, `CARAMELOS`.

## Archivos modificados

```
gds-folders-update-fix-fidelidad-y-vm/
├── CHANGELOG-fix-fidelidad-y-vm.md
└── skills/
    ├── core/
    │   ├── extracting-products/SKILL.md              ← reforzar regla tarjeta_fidelidad y tarjeta_bancos
    │   └── handling-closed-brand-categories/SKILL.md ← convención de descripción para VARIAS MARCAS
    └── chains/
        └── coto/SKILL.md                              ← regla crítica Comunidad COTO por SKU
```

3 archivos. Mergea sobre la rama del segundo update.

## 1. Fix tarjeta de fidelidad alucinada

### Problema observado

En la corrida con la página 8 de COTO Super Finde, el bloque promocional de cervezas mostraba el badge "10% adicional Comunidad COTO" sobre **4 marcas específicas** (Grolsch, Blue Moon, Warsteiner, Kunstmann), pero **NO sobre Antares ni Salta Cautiva**.

El agente correctamente puso `tarjeta_fidelidad: "COMUNIDAD COTO"` en las 4 marcas con badge visible, pero también lo asignó incorrectamente a Antares — alucinando el dato. Salta Cautiva quedó bien (sin tarjeta).

### Cambios realizados

**`skills/core/extracting-products/SKILL.md`** — sección 20 (`tarjeta_fidelidad`) y 21 (`tarjeta_bancos`):

- Regla reforzada: "Completar SOLO si la imagen muestra el badge/logo **directamente sobre o junto al SKU concreto**".
- Lista explícita de comportamientos a evitar: NO asumir por bloque, NO asumir por cadena, NO asumir por proximidad visual.
- Aplica la misma regla a `tarjeta_bancos`.

**`skills/chains/coto/SKILL.md`** — sección "Tarjeta de fidelidad: COMUNIDAD COTO":

- Sección nueva titulada "Regla crítica: Comunidad COTO es por SKU, no por bloque".
- Ejemplo concreto del bloque de cervezas (Antares y Salta Cautiva → null; Grolsch/Blue Moon/Warsteiner/Kunstmann → COMUNIDAD COTO).
- Refuerzo en la sección "Cómo registrar" para que sea redundante y claro.

## 2. Fix convención `V/M` en descripción

### Problema observado

En la misma corrida, los registros con `marca: "VARIAS MARCAS"` tenían el campo `descripcion` con prefijo `V/M`:

- `"V/M ALFAJORES"` → debería ser `"ALFAJORES"`
- `"V/M CARAMELOS"` → debería ser `"CARAMELOS"`
- `"V/M SHAMPOO"` → debería ser `"SHAMPOO"`
- `"V/M CHAMPAGNE"` → debería ser `"CHAMPAGNE"`
- ...etc.

El prefijo `V/M` era invención del agente. La manual no lo usa nunca. La descripción debería ser literalmente el nombre de la categoría canónica.

### Cambios realizados

**`skills/core/handling-closed-brand-categories/SKILL.md`**:

- **Caso C** (categoría cerrada sin marca específica) — ejemplo JSON actualizado: `"descripcion": "CHOCOLATES"` en lugar de `"CHOCOLATES TODOS"`. Sección nueva "Convención de descripción para registros con `marca: 'VARIAS MARCAS'`" con regla explícita y lista de prefijos prohibidos (`V/M`, `VARIAS MARCAS`, `MULTI`).

- **Caso E** (bloque promocional con footer macro-categoría) — template del paso 2 actualizado: `"descripcion": "<CATEGORIA CANONICA>"` en lugar de `"<CATEGORIA CANONICA> TODOS"`. Nota agregada explicando que la decisión de cuándo agregar `TODOS`/`TODAS` es de la capa de exportación, no del agente.

- **Ejemplo completo** del Caso E actualizado: los 4 registros V/M de "EN GOLOSINAS" muestran `descripcion: "ALFAJORES"`, `"CARAMELOS"`, `"CHICLES"`, `"CHOCOLATES"` sin prefijo ni sufijo.

## Comportamiento esperado en la próxima corrida

Tomando como referencia la página 8 de COTO Super Finde:

| Marca | Antes (bug) | Ahora (esperado) |
|---|---|---|
| ANTARES | `tarjeta_fidelidad: "COMUNIDAD COTO"` | `tarjeta_fidelidad: null` ✓ |
| GROLSCH | `tarjeta_fidelidad: "COMUNIDAD COTO"` | `tarjeta_fidelidad: "COMUNIDAD COTO"` ✓ |
| SALTA CAUTIVA | `tarjeta_fidelidad: null` | `tarjeta_fidelidad: null` ✓ |
| `descripcion` de V/M ALFAJORES | `"V/M ALFAJORES"` | `"ALFAJORES"` ✓ |
| `descripcion` de V/M VINOS | `"V/M VINOS"` | `"VINOS"` ✓ |

## Lo que no cambia

- Ningún campo del schema cambia.
- Las otras 8 skills no se tocan.
- El system prompt no se modifica.
- Las references no cambian.

## Lo que queda pendiente

Mismo lote pendiente que en updates anteriores, esperando reunión del martes con David:

1. **Convención `OREO TODAS` vs `OREO GALLETITAS`** — pendiente de confirmar con David qué quiere GDS para SKUs con descripción individual de marca.

2. **Caso PASO DE LOS TOROS** — el agente lo clasificó como `APERITIVOS S/ALCOHOL` pero debería ser `GASEOSAS`. Esto requiere enriquecer la columna `INCLUYE` del archivo de categorías con ejemplos canónicos para desambiguar entre las dos categorías.

3. **`publicadores.md` con frecuencias** — sigue pendiente.

4. **Marcas cerradas sin categoría (caso ESPADOL)** — sigue pendiente.

5. **Lista canónica de categorías incompleta** — el archivo `CATEGORIAS_FOLDERS.xlsx` no incluye CHUPETINES, OBLEAS, VINOS ESPUMANTES, CREMAS DE TRATAMIENTO, CREMAS PEINAR. Confirmar con David si hay que agregarlas.

## Próximos pasos

### Inmediato

1. Mergear este zip sobre la rama del último update (o crear nueva rama).
2. Re-subir las 3 skills modificadas (`extracting-products`, `handling-closed-brand-categories`, `coto`) al workspace de Anthropic con `upload_skills.py`.
3. Re-correr el test contra la misma página 8 de COTO Super Finde y validar:
   - Antares y Salta Cautiva → `tarjeta_fidelidad: null` ✓
   - Grolsch/Blue Moon/Warsteiner/Kunstmann → `tarjeta_fidelidad: "COMUNIDAD COTO"` ✓
   - Knorr → `tarjeta_fidelidad: "COMUNIDAD COTO"` (badge visible) ✓
   - Registros V/M con descripción sin prefijo (ej: `"ALFAJORES"`, `"CARAMELOS"`, `"CHAMPAGNE"`)

### Post-reunión del martes

Aplicar lo que David confirme sobre los pendientes.
