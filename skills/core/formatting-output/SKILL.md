---
name: formatting-output
description: Última skill que el agente aplica antes de devolver la respuesta. Define la estructura exacta del JSON final, las validaciones sintácticas (JSON parseable, todos los campos presentes, tipos correctos), y las reglas básicas de serialización (mayúsculas, números puros, arrays vacíos). NO contiene normalización semántica de valores — esa vive en `extracting-products` y skills auxiliares (reading-prices, reading-promotions, etc.).
---

# Formato del JSON Final

## Cuándo usar esta skill

Activar al final del proceso, después de extraer los productos y completar todos los campos. El orden es:

1. Aplicar `extracting-products` y skills auxiliares para extraer los datos.
2. Aplicar `flagging-for-review` para asignar `needs_review` y `review_reasons`.
3. **Aplicar esta skill para validar y emitir el JSON final.**

## Principio fundamental

Esta skill es **sintáctica**, no semántica. Verifica que el JSON sea válido y que todos los productos tengan los 26 campos en su tipo correcto. La normalización de valores (mayúsculas para texto, códigos canónicos para unidades, formato de promociones) ya se aplicó durante la extracción siguiendo las skills correspondientes.

Si algo llega mal formateado a este punto, este skill lo arregla — pero idealmente nunca debería pasar.

## Estructura del JSON final

El agente devuelve **exactamente** este formato. **Sin texto antes, sin texto después, sin backticks, sin explicaciones.**

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
      "tipo_oferta": "Publicación",
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

## Validaciones antes de emitir

Antes de devolver el JSON, el agente verifica:

### 1. Es JSON válido y parseable

- Sin trailing commas.
- Sin comentarios.
- Sin backticks ni texto fuera del objeto raíz.
- Strings con comillas dobles, no simples.

### 2. Todos los productos tienen los 26 campos

Aunque algunos campos sean `null` o `[]`, los campos deben estar presentes en el objeto. No omitir campos vacíos.

### 3. Tipos correctos por campo

| Campo | Tipo válido |
|---|---|
| Strings (categoria, marca, descripcion, etc.) | string o `null` |
| Precios (precio_oferta, precio_anterior, etc.) | number o `null` (nunca string) |
| medida | number o `null` (nunca string como `"190g"`) |
| u_medida | string canónico (`"GR"`, `"KG"`, `"CC"`, `"ML"`, `"L"`, `"UNI"`) o `null` |
| pagina | number entero |
| needs_review | boolean (`true` / `false`) |
| review_reasons | array (vacío `[]` cuando no hay nada, **no** `null`) |
| combo | `"Principal"`, `"Secundario"`, o `null` |

### 4. Coherencia entre campos relacionados

- **`needs_review` vs `review_reasons`:** si el array tiene elementos → `needs_review = true`. Si está vacío → `needs_review = false`.
- **`combo` vs `carrier`:** si `combo = "Secundario"` → `carrier` no debe ser `null`. Si `combo = null` → `carrier` debe ser `null`.

### 5. Códigos canónicos en `review_reasons`

Cada elemento del array es un código en SCREAMING_SNAKE_CASE. Ver `flagging-for-review` para la lista válida. No inventar códigos nuevos.

### 6. Códigos de `tipo_oferta` canónicos

Solo: `"Regular"`, `"Destacado"`, `"Publicidad"`, `"Publicación"` (con tilde). No otros.

## Reglas mínimas de formato (sintáctico)

Estas son las reglas finales que el agente revisa antes de emitir. La normalización semántica completa ya se hizo durante la extracción.

### Strings de texto

- Mayúsculas (excepto `descripcion_literal` y `tipo_oferta`/`combo`/`tipo_variedad` que tienen su propia convención).
- Sin acentos en `marca` y `descripcion`.
- La `Ñ` se preserva.
- `descripcion_literal` se preserva tal como aparece en el folder (ese es su propósito de auditoría).

### Números

- Sin símbolo `$`.
- Sin separador de miles.
- Decimales con punto, no coma.
- Formato canónico: `4085`, `2143.9`, `2.25`.

### Nulls preservados

- Nunca reemplazar `null` por `0`, `""`, `"N/A"` o cualquier otro placeholder.
- `null` significa "este dato no existe en la fuente". Es información válida.
- La capa de exportación a Excel/CSV decide después cómo serializarlos si hace falta.

### Arrays vacíos

- `review_reasons: []` cuando no hay nada que flagear (no `null`).

## Lo que NO hace esta skill

Para evitar duplicación con otras skills:

- **No define cómo construir descripciones** → `building-sku-description`.
- **No define el formato de precios argentinos** → `reading-prices`.
- **No define el formato de promociones** → `reading-promotions`.
- **No decide qué flagear** → `flagging-for-review` y `extracting-products`.
- **No decide qué categoría asignar** → `extracting-products` (regla 3).

Si llega algo mal formateado a este punto, esta skill lo arregla, pero la fuente de verdad de cada regla vive en su skill correspondiente.

## Notas de diseño

### Por qué el output es JSON y no Excel/CSV

El agente devuelve JSON estructurado para que el pipeline downstream lo consuma sin parsing. La conversión a Excel/CSV es responsabilidad de la integración con GDSnet, no del agente.

### Por qué `null` se preserva en lugar de convertirse a `0`

`null` es semánticamente distinto a `0`. `null` = "no existe el dato", `0` = "el dato existe y vale cero". Mezclarlos pierde información. Ver el caso del Secundario de un combo (`precio_oferta: 0` porque está absorbido por el Principal — eso sí es `0` real, no `null`).

### Por qué esta skill ahora es más corta que antes

En versiones anteriores duplicaba reglas de normalización con `extracting-products` y otras skills. La duplicación generaba contradicciones cuando hacíamos updates. Ahora cada regla vive en una sola skill (la que define el campo o concepto), y esta skill solo hace validación sintáctica final.
