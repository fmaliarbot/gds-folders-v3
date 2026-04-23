---
name: formatting-output
description: Aplica las convenciones de formato del Excel de GDSnet al output del agente antes de entregarlo. Usar siempre como paso final, después de extraer los productos aplicando las skills de extracción. Convierte el formato "puro" del agente (preservando lo que ve la imagen) al formato estandarizado que GDSnet usa en su Excel de carga (unidades compactas en mayúsculas, promociones con sufijo DTO, SKU concatenado, etc.).
---

# Formato de Output para GDSnet

## Problema que resuelve esta skill

El agente extrae información de los catálogos preservando el formato original de lo que aparece en la imagen (ej: "x 237 ml", "25%", "2x1"). GDSnet tiene convenciones específicas para su Excel de carga que difieren del formato natural. Esta skill aplica esas convenciones como paso final, sin modificar la información real extraída.

## Cuándo usar esta skill

Activar esta skill al final del proceso de extracción, cuando se genera el output para GDSnet. El orden correcto es:

1. Extraer productos de las imágenes aplicando skills de extracción (`extracting-products`, `reading-prices`, etc.)
2. Aplicar particularidades de la cadena (`coto`, `carrefour`, etc.)
3. **Aplicar esta skill para formatear el output según las convenciones de GDSnet**
4. Entregar el resultado

## Principio fundamental

Esta skill es **solamente de formateo**. No cambia la información, no infiere datos nuevos, no rellena campos faltantes. Solo reescribe los valores existentes según las convenciones de GDSnet.

Si un campo está en `null` antes del formateo, sigue en `null` después. Si un precio es `500`, sigue siendo `500` después.

## Reglas de formato por campo

### Unidad de medida

Formato compacto, en mayúsculas, sin "x", sin espacios.

| Formato puro del agente | Formato GDSnet |
| :---- | :---- |
| `"x 237 ml"` | `"237ML"` |
| `"x 1,75 Lt"` | `"1,75L"` |
| `"x 750 ml"` | `"750ML"` |
| `"x 750 CC"` | `"750CC"` |
| `"x 330 ml"` | `"330ML"` |
| `"x 2 Lt"` | `"2L"` |
| `"x 1 kg"` | `"1KG"` |
| `"x 820 g"` | `"820G"` |
| `"bot x 750 ml"` | `"750ML"` (se quita "bot", la presentación va en el SKU si aplica) |
| `"porrón"` | `"PORRON"` |

**Regla general:** quitar "x ", quitar espacios internos, convertir a mayúsculas, quitar puntos si los hubiera. La coma decimal se preserva (ej: "1,75L").

**Presentaciones no numéricas** (porrón, lata, pack): se convierten a mayúsculas y se preservan como están.

### Tipo de promoción

Formato en mayúsculas. Para descuentos porcentuales, agregar sufijo `DTO`.

| Formato puro del agente | Formato GDSnet |
| :---- | :---- |
| `"25%"` | `"25%DTO"` |
| `"35%"` | `"35%DTO"` |
| `"40%"` | `"40%DTO"` |
| `"2x1"` | `"2X1"` |
| `"3x2"` | `"3X2"` |
| `"70% en la 2da unidad"` | `"70% EN LA 2DA"` |
| `"2do al 50%"` | `"2DO AL 50%"` |
| `"25% llevando 2"` | `"25%DTO LLEVANDO 2"` |

**Reglas:**
- Todo en mayúsculas
- Porcentajes simples agregan `DTO` al final (ej: `"25%"` → `"25%DTO"`)
- Las promociones multi-unidad (`2X1`, `3X2`) no llevan `DTO`
- Texto adicional (como "llevando 2") se mantiene pero en mayúsculas
- Si el valor era `null`, queda `null`

### Marca

En mayúsculas.

| Formato puro del agente | Formato GDSnet |
| :---- | :---- |
| `"Aquarius"` | `"AQUARIUS"` |
| `"Fanta"` | `"FANTA"` |
| `"Fanta Zero"` | `"FANTA"` (ver nota abajo) |
| `"Coto"` | `"COTO"` |
| `"Fond de Cave"` | `"FOND DE CAVE"` |
| `"Hermann Müller"` | `"HERMANN MULLER"` (sin acentos especiales) |

**Nota sobre variantes de marca:** cuando una marca tiene variantes que el catálogo presenta como sub-marcas (ej: Fanta / Fanta Zero), la marca canónica en GDSnet es la marca principal (`FANTA`), y la variante se refleja en el SKU y descripción. Confirmar con el mapeo de la base maestra.

**Caracteres especiales:** reemplazar acentos y diéresis por su equivalente sin acento (ej: "Müller" → "MULLER"). La letra `Ñ` se preserva.

### SKU (descripción del producto)

Concatenación de: `MARCA + DESCRIPCIÓN + UNIDAD DE MEDIDA`, todo en mayúsculas.

| Componentes | SKU GDSnet |
| :---- | :---- |
| Marca: Aquarius, Desc: "Agua saborizada uva verde", Unidad: "x 237 ml" | `"AQUARIUS UVA VERDE 237ML"` |
| Marca: Fanta, Desc: "Gaseosa sabor Naranja", Unidad: "x 1,75 Lt" | `"FANTA NARANJA 1,75L"` |
| Marca: Coto, Desc: "Soda", Unidad: "x 1,75 Lt" | `"COTO SODA 1,75L"` |
| Marca: Heineken, Desc: "Cerveza", Unidad: "x 330 ml" | `"HEINEKEN 330ML"` |
| Marca: Fond de Cave, Desc: "Vino Fond de Cave reserva", Unidad: "x 750 ml" | `"FOND DE CAVE RES MALBEC 750CC"` |

**Reglas:**
- Todo en mayúsculas
- La descripción se abrevia siguiendo convenciones del manual cuando es posible (ej: "reserva" → "RES", "reducido en calorías" → "REDUC CAL")
- La marca NO se repite en la descripción si ya aparece
- La unidad de medida va al final en formato GDSnet
- Quitar palabras redundantes ("sabor", "gaseosa") si la categoría ya lo implica

**Nota:** el SKU final canónico viene de la base maestra de GDSnet. Si no hay match, se usa la concatenación siguiendo estas reglas. El cruce contra la base maestra tiene prioridad sobre esta formación automática.

### Categoría

En mayúsculas, nombre canónico según la base de categorías contratadas de GDSnet.

| Formato puro del agente | Formato GDSnet |
| :---- | :---- |
| `"Aguas saborizadas"` | `"AGUAS SABORIZADAS"` |
| `"Gaseosas"` | `"GASEOSAS"` |
| `"Vinos"` | `"VINOS"` |
| `"Aperitivos con alcohol"` | `"APERITIVOS C/ALCOHOL"` |

**Nota:** la lista definitiva de categorías viene de la base de categorías contratadas de GDSnet. Esta skill asume que el valor ya es el canónico y solo lo convierte a mayúsculas.

### Tipo de aviso

Primera letra en mayúscula, resto en minúsculas. Los espacios de padding a la derecha son opcionales (el Excel del manual los incluye pero no son significativos).

| Formato puro del agente | Formato GDSnet |
| :---- | :---- |
| `"regular"` | `"Regular"` |
| `"destacada"` | `"Destacado"` (nota: el manual usa masculino) |
| `"publicacion"` | `"Publicacion"` |
| `"publicidad"` | `"Publicidad"` |

### Publicador

En mayúsculas. Valor por defecto: `"REGULAR"` si no hay publicador específico identificado.

### Precios

Formato numérico sin decimales si el precio es entero. Con decimales si los tiene.

| Formato puro | Formato GDSnet |
| :---- | :---- |
| `500` | `500.0` o `500` (ambos válidos) |
| `2143.9` | `2143.9` |
| `null` | Ver regla de campos vacíos abajo |

### Campos vacíos: null vs 0

GDSnet usa el valor `0` en algunos campos cuando el dato no existe, y el valor vacío/null en otros. La regla depende del campo:

- **Precio_Regular, Precio_Oferta:** si el producto no tiene precio visible → `0` (no `null`)
- **Descuento %, Porcentaje_Descuento:** si no hay porcentaje → `null` o campo vacío
- **Unidad de medida:** si no es visible → queda vacío (no `null` literal en el Excel, sino celda vacía)
- **Marca, SKU:** nunca deberían estar vacíos; si lo están, el registro va a revisión

**Principio:** el agente sigue usando `null` para "dato no visible" durante la extracción. Esta skill convierte a `0` los precios cuando el registro final se escribe al Excel.

### Combo

| Formato puro | Formato GDSnet |
| :---- | :---- |
| `"Principal"` | `"Principal"` |
| `"Secundario"` | `"Secundario"` |
| `null` | campo vacío |

### Tarjeta de fidelidad

En mayúsculas, nombre canónico de la skill de cadena.

| Formato puro | Formato GDSnet |
| :---- | :---- |
| `"Comunidad COTO"` | `"COMUNIDAD COTO"` |
| `null` | campo vacío |

### Comentarios

Campo de texto libre con notas del agente para el revisor humano. En el Excel se conserva el texto tal como lo generó el agente.

| Formato puro | Formato GDSnet |
| :---- | :---- |
| `"varios sabores"` | `"varios sabores"` (sin cambios) |
| `"edición limitada"` | `"edición limitada"` (sin cambios) |
| `null` | campo vacío |

**Nota:** el nombre de la columna en el Excel puede ser `Comentarios`, `Observaciones` u otro según el esquema final de GDSnet. El contenido no se transforma.

## Orden de aplicación

Esta skill se aplica al final, después de:

1. Extracción pura del agente
2. Aplicación de skills core (`extracting-products`, `reading-prices`, etc.)
3. Aplicación de skill de cadena (`coto`, `carrefour`, etc.)
4. Resolución de categoría contra base maestra (cuando esté disponible)

Y antes de:

5. Generación del Excel final para entregar a GDSnet

## Casos edge y decisiones pendientes

Esta skill tiene reglas inferidas del Excel manual de referencia. Algunas particularidades que aún requieren confirmación de GDSnet:

- Formato exacto de promociones compuestas (ej: tarjeta + %)
- Tratamiento de caracteres especiales en nombres de marca
- Criterio para abreviaciones en SKU cuando la descripción es larga
- Convenciones para categorías nuevas no presentes en el manual de referencia

Estos puntos se irán refinando a medida que procesemos más catálogos y recibamos feedback del cliente.
