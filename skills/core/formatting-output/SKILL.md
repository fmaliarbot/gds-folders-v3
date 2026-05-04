---
name: formatting-output
description: Aplica las convenciones finales de formato al output del agente y produce el JSON estructurado con todos los productos extraídos. Es la última skill que se aplica antes de devolver la respuesta. Convierte valores al formato canónico de GDSnet (mayúsculas para texto, códigos canónicos para unidades, formato uniforme de promociones) sin cambiar la información extraída. Garantiza que el output sea JSON válido y parseable, con todos los campos del schema.
---

# Formato de Output del Agente

## Problema que resuelve esta skill

El agente extrae información preservando lo que ve en el folder. Las convenciones internas de GDSnet exigen un formato estandarizado (mayúsculas, códigos canónicos, sin acentos en marcas, etc.). Esta skill aplica esas convenciones como paso final y produce el JSON con todos los productos.

## Cuándo usar esta skill

Activar al final del proceso, cuando se generó la lista de productos aplicando las skills de extracción. El orden correcto es:

1. Extraer productos aplicando `extracting-products` y skills auxiliares
2. Aplicar particularidades de la cadena (`coto`, etc.) si corresponde
3. Aplicar `flagging-for-review` para asignar `needs_review` y `review_reasons`
4. **Aplicar esta skill para formatear y emitir el JSON final**

## Principio fundamental

Esta skill es **solamente de formato**. No cambia la información, no infiere datos nuevos, no rellena campos faltantes. Solo reescribe los valores existentes según las convenciones canónicas.

Si un campo está en `null` antes del formato, sigue en `null` después. Si un precio es `500`, sigue siendo `500` después.

## Reglas de formato por campo

### Texto en general

Todos los campos de texto van en **mayúsculas**, sin acentos, salvo `descripcion_literal` que preserva el formato original del folder.

Reemplazos canónicos:
- Acentos: "MÜLLER" → "MULLER", "RIOJA" se queda igual (sin acento), "CAFÉ" → "CAFE".
- La letra `Ñ` se preserva.
- Diéresis se reemplazan: "ü" → "u".

### marca

Mayúsculas, sin acentos.

| Entrada | Salida |
|---|---|
| `"Aquarius"` | `"AQUARIUS"` |
| `"Coca Cola"` | `"COCA COLA"` |
| `"Müller"` | `"MULLER"` |
| `"Cif"` | `"CIF"` |

### descripcion (SKU canónico)

Construida por `building-sku-description`. Esta skill solo verifica:
- Está en mayúsculas.
- No tiene acentos.
- Usa coma decimal en medidas (`"2,25L"`, no `"2.25L"`).
- La medida va pegada a la unidad (`"750ML"`, no `"750 ML"`).

Si llega algo fuera de norma, normalizarlo.

### descripcion_literal

**No transformar.** Preservar exactamente como aparece en el folder.

### medida

Número (entero o decimal). Sin string, sin unidad pegada. Coma o punto decimal según convención del lenguaje (en JSON: punto).

| Entrada | Salida |
|---|---|
| `"2,25"` | `2.25` |
| `"190"` | `190` |
| `"750"` | `750` |

### u_medida

Códigos canónicos en mayúsculas:

| Entrada | Salida |
|---|---|
| `"gr"`, `"g"`, `"gramos"` | `"GR"` |
| `"kg"`, `"kilo"` | `"KG"` |
| `"cc"` | `"CC"` |
| `"ml"`, `"mililitros"` | `"ML"` |
| `"l"`, `"lt"`, `"litros"` | `"L"` |
| `"un"`, `"u"`, `"unidades"` | `"UNI"` |

**Nota sobre CC vs ML:** David usa CC indistintamente con ML para bebidas envasadas. Mantener CC cuando se trate de bebidas con líquido envasado, salvo que el folder diga ML explícito en el packaging.

### tipo_oferta

Primera letra mayúscula, resto minúscula:

| Entrada | Salida |
|---|---|
| `"regular"`, `"Regular"`, `"REGULAR"` | `"Regular"` |
| `"destacada"`, `"destacado"` | `"Destacado"` |
| `"publicidad"` | `"Publicidad"` |
| `"publicacion"`, `"publicación"` | `"Publicación"` |

### Precios (precio_oferta, precio_anterior, precio_tarjeta_banco, precio_tarjeta_fidelidad)

Numéricos, sin símbolo `$`, sin separadores de miles. Decimales con punto.

| Entrada | Salida |
|---|---|
| `"$4.085"` | `4085` |
| `"4.085,50"` | `4085.50` |
| `"189,99"` | `189.99` |
| `null` | `null` |

**Importante:** los precios faltantes quedan en `null`. **No reemplazar `null` por `0`** — eso lo hace la capa de exportación a Excel/CSV si GDSnet lo pide después.

### Tipos de promoción (3 campos)

Mayúsculas. Formato canónico:

| Entrada | Salida |
|---|---|
| `"25%"`, `"25% off"` | `"25%DTO"` |
| `"35%dto"` | `"35%DTO"` |
| `"3x2"`, `"3X2"` | `"3X2"` |
| `"2x1"` | `"2X1"` |
| `"70% en la 2da unidad"` | `"70% DTO 2DA U"` |
| `"2do al 50%"` | `"2DO AL 50%"` |
| `"25% llevando 2"` | `"25%DTO LLEVANDO 2"` |
| `"oferta"` | `"OFERTA"` |

**Reglas:**
- Todo en mayúsculas
- Porcentajes simples llevan sufijo `DTO` (ej: `"25%"` → `"25%DTO"`)
- Promociones multi-unidad (`2X1`, `3X2`, `8X6`) NO llevan `DTO`
- "EN LA 2DA UNIDAD" se abrevia como `"2DA U"`
- Si el valor era `null`, queda `null`

### combo

Valores canónicos:

| Entrada | Salida |
|---|---|
| `"principal"` | `"Principal"` |
| `"secundario"` | `"Secundario"` |
| `null` | `null` |

### tarjeta_fidelidad y tarjeta_bancos

Mayúsculas. Nombres canónicos según skill de cadena:

| Entrada | Salida |
|---|---|
| `"Comunidad COTO"`, `"comunidad coto"` | `"COMUNIDAD COTO"` |
| `"Mi Carrefour"` | `"MI CARREFOUR"` |
| `"cencopay"`, `"Cencopay"` | `"CENCOPAY"` |
| `"mercado pago"` | `"MERCADO PAGO"` |
| `null` | `null` |

### tipo_variedad

Mantener formato sentence-case (primera letra mayúscula):

| Entrada | Salida |
|---|---|
| `"varios sabores"`, `"VARIOS SABORES"` | `"Varios sabores"` |
| `"varias fragancias"` | `"Varias fragancias"` |
| `"varios tipos"` | `"Varios tipos"` |
| `null` | `null` |

### needs_review y review_reasons

- `needs_review`: booleano (`true` / `false`).
- `review_reasons`: array. Si está vacío: `[]` (no `null`). Códigos en SCREAMING_SNAKE_CASE (`"PRODUCT_NOT_RECOGNIZED"`, no `"product not recognized"`).

## Estructura del JSON final

El agente devuelve **exactamente** este formato. Sin texto antes, sin texto después, sin backticks, sin explicaciones.

```json
{
  "productos": [
    {
      "categoria": "GASEOSAS",
      "marca": "COCA COLA",
      "descripcion": "COCA COLA ZERO 2,25L",
      "descripcion_literal": "Coca Cola Zero 2,25 lts",
      "id_sku_interno_spm": null,
      "ean": null,
      "medida": 2.25,
      "u_medida": "L",
      "pagina": 8,
      "tipo_oferta": "Destacado",
      "precio_oferta": 4085,
      "precio_anterior": 5450,
      "precio_tarjeta_banco": null,
      "precio_tarjeta_fidelidad": null,
      "tipo_promocion_oferta": "25%DTO LLEVANDO 2",
      "tipo_promocion_tarjeta_fidelidad": null,
      "tipo_promocion_tarjeta_bancos": null,
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,
      "tarjeta_bancos": null,
      "tipo_variedad": null,
      "descripcion_variedad": null,
      "maximo_unidades": null,
      "needs_review": false,
      "review_reasons": []
    }
  ]
}
```

## Reglas de validación antes de emitir

Antes de devolver el JSON, verificar:

1. **Es JSON válido y parseable.** Sin trailing commas, sin comentarios.
2. **Todos los productos tienen los 26 campos del schema.** Aunque sean `null` o `[]`, los campos deben estar presentes.
3. **`needs_review` es coherente con `review_reasons`:** si el array tiene elementos, `needs_review = true`. Si está vacío, `needs_review = false`.
4. **`combo` y `carrier` son coherentes:** si `combo = "Secundario"`, `carrier` no debe ser `null`. Si `combo = null`, `carrier` debe ser `null`.
5. **Los precios son numéricos o `null`,** nunca strings.
6. **Los códigos de unidad son canónicos** (`GR`, `KG`, `CC`, `ML`, `L`, `UNI`).
7. **Los códigos de `review_reasons` son canónicos.** Ver `flagging-for-review` para la lista válida.

## Notas de diseño

### Por qué el output es JSON y no Excel/CSV

El agente devuelve JSON estructurado para que el pipeline downstream lo consuma sin parsing de spreadsheets. La conversión a Excel/CSV es responsabilidad de la capa de integración con GDSnet, no del agente.

### Por qué `null` se preserva en lugar de convertirse a `0`

Cuando el agente no ve un dato, `null` es semánticamente correcto: "este dato no existe en la fuente". `0` significa "este dato existe y vale cero". Mezclarlos pierde información para auditoría. La capa de integración decide después cómo serializarlo a Excel.

### Por qué `descripcion_literal` no se transforma

El propósito de `descripcion_literal` es ser un campo de auditoría: muestra qué leyó el agente en el folder, sin manipular. Si lo transformamos pierde su utilidad. La descripción canónica vive en `descripcion`.

### Por qué los códigos de `review_reasons` son SCREAMING_SNAKE_CASE

Convención común para enums en sistemas de software. Permite agrupar productos a revisar por código sin ambigüedad de mayúsculas/minúsculas.
