---
name: reading-promotions
description: Identifica y normaliza el tipo de promoción de un producto, separándolo en tres dimensiones según el schema canónico de GDSnet — promoción base, promoción adicional con tarjeta de fidelidad, y promoción adicional con tarjeta de banco. Aplica formato canónico (mayúsculas, sufijo DTO, etc.) y respeta la regla de no inventar promociones que no estén escritas en la imagen.
---

# Lectura de Promociones

## Problema que resuelve esta skill

Las promociones argentinas pueden tener hasta **3 capas simultáneas**:
1. La promoción **base** que aplica a todos los compradores (ej: "3X2", "35% DTO").
2. Un descuento **adicional** con tarjeta de fidelidad de la cadena (ej: "10% DTO Comunidad COTO").
3. Un descuento **adicional** con tarjeta de banco (ej: "5% DTO con Modo").

Antes mezclábamos todo en un solo campo. Ahora cada capa va a su propio campo: `tipo_promocion_oferta`, `tipo_promocion_tarjeta_fidelidad`, `tipo_promocion_tarjeta_bancos`.

Las **reglas globales** del agente (no inventar, ante la duda `null` con flag) están en `extracting-products`. Esta skill las extiende con detalle específico de los campos de promoción.

## Identificación de cada dimensión

### Promoción base (tipo_promocion_oferta)

Es la promoción "principal" que aparece más prominente en el folder. Generalmente es lo primero que ves al mirar el producto.

**Cómo aparece:**
- Texto grande, color destacado.
- Sin asociación a un logo de tarjeta.
- Aplica a todos los compradores que adquieran el producto.

**Ejemplos típicos:**
- `"3X2"`
- `"35%DTO"`
- `"70% DTO 2DA U"` (70% de descuento en la segunda unidad)
- `"25%DTO LLEVANDO 2"`
- `"8X6"` (combiná 8, pagá 6)
- `"2DO AL 50%"`
- `"OFERTA"` (cuando solo dice "oferta" sin porcentaje específico)

### Promoción con tarjeta de fidelidad (tipo_promocion_tarjeta_fidelidad)

Descuento adicional que el comprador obtiene presentando la tarjeta de fidelidad de la cadena.

**Cómo aparece:**
- Junto al nombre o logo de la tarjeta de fidelidad (Comunidad COTO, Mi Carrefour, Cencopay, etc.).
- Leyenda: "X% DTO con [nombre tarjeta]".
- Suele ser un descuento adicional al base (no reemplaza a la promoción base).

**Ejemplos típicos:**
- `"5% DTO"` (con Comunidad COTO)
- `"10%DTO"` (con Cencopay)
- `"4X2"` (con tarjeta fidelidad cuando la base es 3X2)
- `"20%DTO"`

**Importante:** registrar SOLO si la promoción está visible junto a la tarjeta de fidelidad. NO asumir que existe por el nombre de la cadena.

### Promoción con tarjeta de banco (tipo_promocion_tarjeta_bancos)

Descuento adicional con tarjeta de banco específica.

**Cómo aparece:**
- Junto al nombre o logo de un banco/tarjeta (MODO, Mercado Pago, Banco Provincia, Visa, etc.).
- Leyenda: "X% DTO con [tarjeta/banco]".

**Ejemplos típicos:**
- `"10%DTO"` (con MODO)
- `"OFERTA"` (algunos folders tipo Maxiconsumo usan "OFERTA" como mecánica de tarjeta de banco para ciertos productos)
- `"LLEV 4U"` (llevando 4 unidades, en Maxiconsumo con Mercado Pago)

## Formato canónico

Después de leer la promoción, **formatearla** según las convenciones de GDSnet:

| Texto en la imagen | Formato canónico |
|---|---|
| `"25%"` | `"25%DTO"` |
| `"35% off"` | `"35%DTO"` |
| `"3x2"` | `"3X2"` |
| `"70% en la 2da unidad"` | `"70% DTO 2DA U"` |
| `"2do al 50%"` | `"2DO AL 50%"` |
| `"25% llevando 2"` | `"25%DTO LLEVANDO 2"` |
| `"oferta"` | `"OFERTA"` |
| `"llevá 4"` | `"LLEV 4U"` |

**Reglas:**
- Todo en mayúsculas.
- Porcentajes simples llevan sufijo `DTO` (`"25%"` → `"25%DTO"`).
- Promociones multi-unidad (`2X1`, `3X2`, `8X6`) NO llevan `DTO`.
- "EN LA 2DA UNIDAD" se abrevia como `"2DA U"`.
- "LLEVANDO X" se preserva. "LLEVÁ X" se abrevia como `"LLEV XU"`.

## Reglas de asignación

### Caso 1: solo hay promoción base

```json
{
  "tipo_promocion_oferta": "35%DTO",
  "tipo_promocion_tarjeta_fidelidad": null,
  "tipo_promocion_tarjeta_bancos": null
}
```

### Caso 2: promoción base + tarjeta de fidelidad

Folder muestra "25% DTO + 5% adicional con Comunidad COTO".

```json
{
  "tipo_promocion_oferta": "25%DTO",
  "tipo_promocion_tarjeta_fidelidad": "5% DTO",
  "tipo_promocion_tarjeta_bancos": null
}
```

### Caso 3: promoción solo con tarjeta de fidelidad (sin base)

Folder muestra solo "10% DTO con Comunidad COTO" sin descuento base.

```json
{
  "tipo_promocion_oferta": null,
  "tipo_promocion_tarjeta_fidelidad": "10%DTO",
  "tipo_promocion_tarjeta_bancos": null
}
```

**Importante:** en este caso el `precio_oferta` puede ser igual al `precio_anterior` (sin descuento base) o ser el precio aplicando solo la tarjeta de fidelidad. Mirar la imagen para decidir.

### Caso 4: las 3 dimensiones presentes

Folder muestra "20% DTO base, 5% adicional con Comunidad COTO, 10% adicional con MODO".

```json
{
  "tipo_promocion_oferta": "20%DTO",
  "tipo_promocion_tarjeta_fidelidad": "5% DTO",
  "tipo_promocion_tarjeta_bancos": "10%DTO"
}
```

### Caso 5: no hay promoción visible

```json
{
  "tipo_promocion_oferta": null,
  "tipo_promocion_tarjeta_fidelidad": null,
  "tipo_promocion_tarjeta_bancos": null
}
```

Esto es válido: hay productos publicados sin descuento (precio "lleno").

## Casos especiales

### Promoción aplicada a categoría cerrada

Cuando la promoción aplica a una categoría cerrada (ej: "70% DTO 2DA U en Shampoos y Acondicionadores"), el campo `descripcion_variedad` debe completarse con las categorías afectadas. Ver `handling-closed-brand-categories`.

### Promoción del tipo Publicidad (sin precios)

Si el producto es `tipo_oferta: "Publicidad"` (sin precios visibles) pero hay un texto de promoción visible (ej: solo dice "2X1"), **registrar igual** la promoción en `tipo_promocion_oferta`. La promoción es independiente del precio.

### Promoción "OFERTA" sin más detalle

Algunos folders (especialmente mayoristas tipo Yaguar) usan solo el texto "OFERTA" sin especificar mecánica. Registrar `tipo_promocion_oferta: "OFERTA"`.

### Múltiples promociones base

Si hay dos promociones base distintas para un mismo producto (ej: "3X2" y "70% DTO 2DA U"), eso es raro pero ocurre. Generalmente son alternativas mutuamente excluyentes. **Concatenar** con " / " si conviven en la imagen:

```json
{ "tipo_promocion_oferta": "3X2 / 70% DTO 2DA U" }
```

Pero antes verificar: ¿son alternativas o una es base + otra con tarjeta? Si una está asociada a tarjeta, separarlas.

## Cuándo dejar null

- No hay texto de promoción visible.
- El texto está borroso / no legible.
- Hay un porcentaje pero no se puede determinar a qué dimensión corresponde (sin tarjeta asociada y sin contexto base) — agregar `PRICE_AMBIGUOUS` a `review_reasons`.

## Notas de diseño

### Por qué pasamos de 1 campo a 3

Es el schema canónico de GDSnet. Antes mezclábamos todo en `tipo_promocion` y se perdía la dimensión de qué descuento aplicaba con qué condición. David lo separó explícito en su última iteración.

### Por qué los 3 campos pueden ser todos null

Hay productos sin promoción de ningún tipo (precio normal, sin descuento, sin tarjeta). Todos los campos en null es un caso válido y frecuente.

### Por qué la promoción se registra incluso sin precio

Una promoción visible tipo "2X1" es información útil aunque el folder no muestre precio. El revisor humano puede usarla para entender la oferta. Regla: lo que está escrito se registra.
