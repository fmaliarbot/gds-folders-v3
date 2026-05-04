---
name: extracting-multiple-products-per-image
description: Decide cuándo una imagen con varios productos debe registrarse como un solo SKU (variedades) o como múltiples SKUs (líneas distintas), siguiendo las convenciones de GDSnet. Resuelve la ambigüedad clave entre "el folder muestra Coca Original + Zero + Light" (variedades, 1 registro) y "el folder muestra Zucaritas + Froot Loops + Müsli" (líneas distintas, N registros). Esencial para evitar inflar o subreportar productos al cargar al sistema.
---

# Múltiples Productos en una Imagen

## Rol

Cuando una imagen muestra más de un producto, tu trabajo es decidir cuántos registros se generan: **uno con `tipo_variedad`** o **varios separados**. La distinción es crítica porque afecta directamente el conteo final y el matching contra la base maestra de GDSnet.

## La regla fundamental: variedades vs líneas distintas

David lo definió textualmente en el comentario del campo TIPO DE VARIEDAD:

> "Es cuando en la imagen se presenta más de un sku de distinto tipo, sabor o fragancia. **No se registran todas las variedades sino la descripción del sku que los contiene a todos.**"

Y en el documento de ajustes complementó:

> "Las fotos que presentan más de un producto y con sus variables descriptas, deben ser consideradas grabando un producto por línea y cada una con las variables publicadas."

Estas dos reglas parecen contradictorias pero NO lo son. La diferencia depende de si los productos mostrados son:

- **Variedades del mismo producto base** (mismo nombre comercial, distinto sabor/fragancia/tipo) → 1 registro.
- **Líneas distintas del mismo fabricante** (nombres comerciales distintos) → N registros.

## Cómo decidir: 4 preguntas en orden

### Pregunta 1: ¿Los productos comparten nombre comercial base?

- **Coca Cola Original / Coca Cola Zero / Coca Cola Light** → **mismo nombre base** ("Coca Cola"), distintas variantes. → Variedades.
- **Coca Cola / Fanta / Sprite** → **nombres distintos**. → Líneas distintas.
- **Mentos Mint / Mentos Fruit / Mentos Strawberry** → **mismo nombre base** ("Mentos"), distintos sabores. → Variedades.
- **Kellogg's Zucaritas / Froot Loops / Müsli / Choco Krispis** → **nombres distintos** (cada cereal tiene su propio nombre comercial). → Líneas distintas.

### Pregunta 2: ¿Tienen el mismo precio/promoción común o cada uno tiene su precio?

- **Mismo precio único para todas las variantes** (típico de variedades): "Mentos $1100, todos los sabores". → Confirma variedades.
- **Cada producto tiene su precio individual** (típico de líneas distintas): "Zucaritas $5000, Froot Loops $5500". → Confirma líneas distintas.

### Pregunta 3: ¿La imagen los presenta como una unidad o como ítems separados?

- **Mismo packaging visual, solo cambia la etiqueta del sabor** (ej: 4 latas Mentos idénticas con sabor distinto): unidad → variedades.
- **Packagings claramente diferentes** (cada cereal tiene su caja propia): ítems separados → líneas distintas.

### Pregunta 4: ¿Hay códigos de SKU compartidos o distintos?

Si el folder publica códigos de SKU (caso COTO con sus "Cod: 470498-470499"):

- **Códigos distintos para cada variante visible** → líneas distintas (cada SKU se registra).
- **Un solo código (o pocos) para muchas variantes visibles** → variedades.

## Aplicación práctica

### Caso típico de variedades (1 registro)

**Folder muestra:** Mentos Caramelos x29,5g, en 3 sabores distintos (Mint, Strawberry, Fruit) con precio único y código compartido.

**Registro:**

```json
{
  "categoria": "GOLOSINAS",
  "marca": "MENTOS",
  "descripcion": "MENTOS CARAMELOS 29,5G",
  "medida": 29.5,
  "u_medida": "GR",
  "tipo_promocion_oferta": "3X2",
  "tipo_variedad": "Varios sabores",
  "descripcion_variedad": null,
  ...
}
```

Solo 1 registro. La descripción cubre todas las variedades. El campo `tipo_variedad` indica que hay variantes.

### Caso típico de líneas distintas (N registros)

**Folder muestra:** Bloque Kellogg's con Zucaritas (190g), Froot Loops (195g), Müsli (255g), Choco Krispis (265g). Promoción común "35%DTO LLEVANDO 2 IGUALES".

**Registro: 4 entradas separadas.**

```json
[
  {
    "marca": "KELLOGGS",
    "descripcion": "KELLOGGS ZUCARITAS 190G",
    "medida": 190,
    "u_medida": "GR",
    "tipo_promocion_oferta": "35%DTO LLEVANDO 2 IGUALES",
    "tipo_oferta": "Publicación",
    ...
  },
  {
    "marca": "KELLOGGS",
    "descripcion": "KELLOGGS FROOT LOOPS 195G",
    "medida": 195,
    "u_medida": "GR",
    "tipo_promocion_oferta": "35%DTO LLEVANDO 2 IGUALES",
    "tipo_oferta": "Publicación",
    ...
  },
  ...
]
```

Cada cereal tiene su propio registro. Comparten promoción y `tipo_oferta: "Publicación"` pero son SKUs distintos.

### Caso ambiguo común: gaseosas grandes en línea

**Folder muestra:** Coca Cola Zero 2,25L, Coca Cola Sabor Liviano 2,25L. Mismo precio "25% DTO LLEVANDO 2".

**Análisis:**
- Pregunta 1: ¿Mismo nombre base? "Coca Cola" sí, pero "Zero" y "Sabor Liviano" son **variantes nombradas** del producto base.
- Pregunta 2: ¿Mismo precio? Sí.
- Pregunta 3: ¿Packaging distinto? Sí, las botellas son visualmente distintas (una negra, una blanca).
- Pregunta 4: Probablemente códigos distintos.

**Resolución:** **Líneas distintas** (2 registros), porque la pregunta 1 muestra que son variantes con nombre propio que se publicitan individualmente. Si fueran variedades del mismo (ej: 4 sabores de la misma Coca Cola Light) sería 1 registro.

**Caso borderline:** la decisión final depende del nivel de detalle del catálogo. Si tenés dudas, **registrá como líneas distintas** y agregá `LOW_CONFIDENCE` a `review_reasons` para que un humano confirme.

### Caso "Combiná 8X6" de Coca Cola (4 latas)

**Folder muestra:** Coca Cola 220ml, Coca Cola Sin Azúcar 220ml, Fanta Naranja 220ml, Sprite 220ml. Promoción común "8X6".

**Análisis:**
- Pregunta 1: Nombres comerciales DISTINTOS (Coca Cola, Fanta, Sprite son marcas distintas dentro del grupo Coca Cola Co.).
- Pregunta 2: Precio único compartido.
- Pregunta 3: Packagings distintos (colores propios de cada marca).
- Pregunta 4: Códigos compartidos (típicamente 2 códigos para 4 productos).

**Resolución:** **Líneas distintas** (4 registros), aunque haya código compartido. Los nombres comerciales mandan. El código compartido se documenta en algún campo de revisión si es ambiguo (`MULTIPLE_SKUS_SHARED_CODE` en review_reasons).

## Casos especiales

### Una marca con muchas presentaciones del mismo producto

Si el folder muestra Cif Limón 500ml + Cif Limón 1L + Cif Limón 5L con un solo precio "Aceptable", **NO son variedades** (no cambia sabor/fragancia, cambia tamaño). Son SKUs distintos por **medida**. Líneas distintas → 3 registros.

### Categorías cerradas

Si la imagen muestra varios productos pero la promoción aplica a "todos los X" sin SKU específico, NO es variedad ni líneas distintas: es **categoría cerrada**. Ver `handling-closed-brand-categories`.

### Combos

Si los productos están vendidos juntos con un solo precio, NO son variedades ni líneas distintas: es **combo**. Ver `detecting-combos`.

## Cómo describir variedades en el campo descripcion

Cuando registramos como **variedad** (1 registro), la descripción debe ser el **nombre común** que cubre todas las variantes:

| Variantes en la imagen | Descripción canónica |
|---|---|
| Mentos Mint, Strawberry, Fruit | `"MENTOS CARAMELOS 29,5G"` |
| Coca Cola, Coca Light, Coca Zero (mismo formato) | depende — ver caso ambiguo arriba |
| Sedal Ceramidas + Sedal Restauración + Sedal Liso (mismo gramaje) | `"SEDAL SHAMPOOS 350ML"` |

La descripción NO debe enumerar las variantes (`"MENTOS MINT/STRAWBERRY/FRUIT"` no es válido). Esa info va en `tipo_variedad`.

## Notas de diseño

### Por qué la regla de variedades pierde detalle a propósito

David explicitó que para variedades NO se registra cada sabor — se registra la descripción que las contiene a todas. La razón es de carga: GDSnet trackea ofertas a nivel línea-producto, no variedad. Si Mentos tiene 3 sabores en oferta con el mismo precio, GDSnet quiere ver "Mentos en oferta" no 3 registros que duplican datos.

### Por qué las líneas distintas SÍ se desagregan

Líneas distintas son productos individuales para GDSnet. Cada uno tiene su match en la base maestra. Inflar un solo registro genérico haría imposible el match SKU-por-SKU.

### Por qué los casos borderline van a revisión

El criterio "es variedad o línea distinta" depende parcialmente de cómo GDSnet trackea internamente cada producto. Cuando el folder no es claro, el revisor humano (que conoce la base maestra) decide. El agente no debe forzar una respuesta cuando la imagen es ambigua.
