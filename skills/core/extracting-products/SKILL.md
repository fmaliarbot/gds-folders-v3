---
name: extracting-products
description: Extrae productos de imágenes de catálogos promocionales de supermercados argentinos, identificando todos los campos visibles (descripción, marca, precios, promociones, unidad de medida, categoría, tipo de imagen). Esta es la skill principal que se debe usar para procesar cada página de un catálogo. Aplica la regla fundamental de no inventar datos, respeta el formato original del texto, y produce un JSON estructurado con una entrada por producto visible.
---

# Extracción de Productos de Catálogos

## Rol

Actuás como un analista experto en lectura de catálogos promocionales de supermercados argentinos. Tu trabajo es mirar una imagen de una página del folder y extraer todos los productos visibles con sus datos estructurados.

## Regla absoluta: no inventar datos

Extraé solo lo que ves escrito o impreso en la imagen.

- Si un precio no se ve → `null`
- Si la unidad de medida no se ve → `null`
- Si el porcentaje de descuento no se ve → `null`
- Si la marca no se ve → `null`
- Si un dato está borroso y no lo podés leer con certeza → `null`

No uses conocimiento general sobre productos argentinos para completar campos. No calcules precios que no están visibles. No derivés porcentajes que no están escritos. Un `null` es siempre mejor que un dato inventado.

### Excepción controlada: matching contra listas canónicas del cliente

La regla de "no inventar" aplica a **datos observables en la imagen**. No aplica a decisiones de matching contra listas canónicas provistas por el cliente, que son reglas de negocio explícitas.

El único caso en esta skill donde esto aplica es el campo `nombre_categoria`: el agente matchea el producto contra la lista oficial de `references/categorias-contratadas.md` y asigna el valor canónico correspondiente, aunque la categoría no esté escrita literal en la imagen. Ver sección "9. nombre_categoria" para el detalle.

Si el match no es claro, el comportamiento sigue siendo el mismo que el resto: `null` + nota en `comentarios`.

## Campos a extraer por cada producto

### 1. descripcion

El SKU canónico del producto según las convenciones de GDSnet. Este es el campo más crítico para el cruce con la base maestra del cliente: una descripción fiel al folder pero que no siga la estructura esperada rompe el match aunque el producto sea correcto.

**Cómo construirlo:** Usar **siempre** la skill `building-sku-description`, que define:

- Los 3 patrones canónicos (específico con medida, genérico por marca, "TODOS/TODAS")
- Cómo decidir cuál patrón aplica según lo que muestra el folder
- Diccionario de abreviaciones frecuentes (`SH`, `CR`, `DP`, `LIQ`, `TBK`, `S/AZ`, `V/M`, etc.)
- Reglas de formato (mayúsculas, sin acentos, coma decimal, medida pegada a unidad)

**Nunca** construir una `descripcion` sin consultar esa skill. No copiar el texto tal como aparece en la imagen — GDSnet tiene una convención estructurada que hay que respetar.

**Regla clave:** La descripción es el SKU completo incluyendo marca, modelo/variante y medida cuando corresponda. El campo `marca` separado se mantiene igualmente.

Ejemplos correctos (para más, ver `building-sku-description`):

- Folder muestra "Nescafé Gold x 95g" → `descripcion: "NESCAFE GOLD 95G"`, `marca: "NESCAFE"`, `medida: 95`, `u_medida: "G"`
- Folder muestra "Cif Baños" como banner de marca sin medida → `descripcion: "CIF BAÑOS"`, `marca: "CIF"`, `medida: null`, `u_medida: null`
- Folder muestra "Todas las yerbas Amanda" → `descripcion: "AMANDA YERBAS TODAS"`, `marca: "AMANDA"`, `medida: null`, `u_medida: null`

### 2. unidad_medida

El gramaje, volumen, cantidad o presentación del producto.

**Cómo extraerlo:** Tomar la unidad tal como aparece escrita. Formato original del folder (ej: "x 820 g", "x 900 ml", "x 1.5 lt", "Pack x 6").

Incluir la presentación cuando está indicada: "porrón", "bot" (botella), "lata", etc.

Ejemplos:
- "Vino El Cazador, bot x 750 ml" → `unidad_medida: "bot x 750 ml"`
- "en porrón de cerveza" → `unidad_medida: "porrón"`

Si no se ve como texto en el folder: `null`.

### 3. marca

El nombre de marca tal como aparece escrito. Si dice "Copa de Oro", poner eso. Si dice "Inalpa Vida", poner la versión completa.

Cuando hay múltiples marcas en un mismo bloque (ej: "Miller/Heineken/Imperial Golden/Blue Moon"), listarlas separadas por "/".

Si no se ve: `null`.

### 4. precio_regular

El precio SIN descuento. A veces aparece tachado, en letra más chica, o con la leyenda "Antes", "Precio regular", "P. Lista".

**Cómo extraerlo:** El número tal como está, sin símbolo $. Ver la skill `reading-prices` para el formato.

Si no se ve un precio sin descuento: `null`. No calcularlo.

### 5. precio_oferta

El precio CON descuento. Generalmente es el número más grande y prominente.

**Cómo extraerlo:** Igual que precio_regular, solo el número.

Si no se ve: `null`.

### 6. porcentaje_descuento

El porcentaje de descuento tal como está escrito, convertido a decimal.

- "35%" → `0.35`
- "25% OFF" → `0.25`

Si no se ve un porcentaje escrito: `null`. No calcularlo a partir de los precios.

### 7. tipo_promocion

El texto de la promoción tal como aparece en la imagen. Copiar textual.

Ejemplos: "35%", "2x1", "70% en la 2da unidad", "2do al 50%", "3x2", "Llevá 3 pagá 2".

**Importante:** Si la imagen muestra un tipo de promoción (como "2x1"), registrarlo SIEMPRE, incluso si el producto es tipo "publicidad" (sin precios). La promoción es un dato visible independiente del precio.

Si no hay texto de promoción visible: `null`.

### 8. tipo_imagen

Cómo se presenta este producto en la página. Ver la skill `classifying-ad-type` para la clasificación detallada. Valores posibles: `regular`, `destacada`, `publicidad`, `publicacion`.

### 9. nombre_categoria

La categoría canónica del producto según el sistema de clasificación de GDSnet. Es una de las entradas del archivo `references/categorias-contratadas.md` (columna `CATEGORIAS`).

**Regla crítica — fuente de verdad absoluta:**

El valor del campo `nombre_categoria` **SIEMPRE** debe ser **literalmente idéntico** a uno de los valores de la columna `CATEGORIAS` del archivo `references/categorias-contratadas.md`. Sin excepciones.

Esto incluye:
- Respetar **exactamente** el uso de singular vs plural (ej: `DESODORANTES DE AMBIENTE` es el valor canónico, NO `DESODORANTE DE AMBIENTES`)
- Respetar **exactamente** los typos originales del archivo (ej: `LIUSTRAMUEBLES`, `PREMEZCALAS`, `PREMEZCALS`)
- Respetar **exactamente** las mayúsculas/minúsculas y acentos del archivo (ej: `CAFÉ` con tilde)
- Respetar **exactamente** los espacios y signos (ej: `APERITIVOS C/ALCOHOL` con la barra)

**El agente NUNCA debe "corregir", "normalizar" ni "interpretar" el nombre de la categoría.** Si el archivo dice `DESODORANTES DE AMBIENTE`, el agente escribe `DESODORANTES DE AMBIENTE`. Si el archivo tiene un typo, el agente preserva el typo. La razón es que cualquier desviación rompe el match exacto contra la base maestra de GDSnet, que es el único criterio que importa.

**Cómo asignarla:**

1. Mirar el producto (descripción, marca, presentación) y matchearlo contra la lista de categorías contratadas disponible en `references/categorias-contratadas.md`.
2. Copiar el valor **literal** de la columna `CATEGORIAS` del archivo. No reformular, no modificar.
3. Revisar la columna `NO INCLUYE` del archivo para descartar matches erróneos. Por ejemplo, un producto de chocolate para taza NO va a la categoría `CHOCOLATES`; un vino Patero NO va a `VINOS`.

**Cuándo dejar `null`:**

- Cuando el producto no matchea claramente con ninguna categoría de la lista
- Cuando el producto podría ir a dos o más categorías y no se puede elegir con certeza
- Cuando el producto cae en una exclusión explícita (NO INCLUYE) y no hay otra categoría clara

En cualquiera de estos casos, dejar `nombre_categoria` en `null` y agregar una nota en el campo `comentarios` explicando el motivo (ej: `"categoría no identificable con la lista contratada"`, `"posible match con VINOS pero podría ser APERITIVOS C/ALCOHOL"`).

**Importante — distinguir de la sección del folder:**

La categoría canónica de GDSnet NO es lo mismo que el título de sección que aparece escrito en la página del folder (ej: "Bebidas", "Almacén"). Esos títulos son segmentaciones visuales del folder; la categoría canónica es el valor interno de GDSnet que va en la columna del output.

Si la página tiene un título tipo "Bebidas" pero el producto es un vino, la categoría canónica es `VINOS` (según la lista), no `Bebidas`.

### 10. combo

Si el producto es parte de un combo. Ver la skill `detecting-combos` para la lógica completa.

Valores: `"Principal"`, `"Secundario"`, o `null`.

### 11. carrier

Si es combo, la descripción del otro producto del combo. Ver la skill `detecting-combos`.

### 12. tarjeta_fidelidad

Si la imagen muestra explícitamente que una tarjeta de fidelidad aplica a este producto.

**Cómo detectarlo:** Buscar menciones como "Comunidad Coto", "Club Dia", "Mi Carrefour", logos de tarjetas, o textos como "X% adicional con [tarjeta]" junto al producto.

**Importante:** Solo registrar si la imagen lo muestra explícitamente para ese producto. No asumir que aplica a todos los productos por ser de una cadena. La skill específica de cadena (ej: `coto`) provee los nombres canónicos de las tarjetas.

Si no se ve mención de tarjeta junto al producto: `null`.

### 13. comentarios

Campo libre para notas sobre el producto que no encajan en otros campos pero que el revisor humano necesita saber.

**Cuándo usarlo:**

- **"varios sabores"** cuando el bloque tiene variedades (sabores/fragancias/tipos) del mismo producto y se eligió una variedad concreta para la descripción. Ver `handling-closed-brand-categories` → Caso D.
- **"varias variedades"** o el término que corresponda cuando es un caso similar pero no son sabores (ej: distintos perfumes de un mismo shampoo).
- **Información adicional visible** sobre el producto que no entró en descripción ni marca (ej: "edición limitada", "nuevo").
- **Notas de incertidumbre** que ayuden al revisor humano (ej: "precio poco legible", "producto parcialmente cortado en la imagen").

**Cuándo NO usarlo:**

- No poner interpretaciones ni deducciones del modelo.
- No repetir información que ya está en otros campos.
- No usar para marcar productos "para revisión" — eso es parte del flujo de flag, no del campo `comentarios`.

Si no hay nada relevante que anotar: `null`.

**Nota sobre el nombre del campo:** el nombre `comentarios` es provisional. El esquema final del Excel de GDSnet puede usar otro nombre (`observaciones`, `nota`, etc.). Cuando David confirme el esquema final, se renombra en todas las skills.

## Situaciones especiales

### Varios productos en una misma imagen

Ver la skill `extracting-multiple-products-per-image`.

### Grupo de productos de una marca (tipo "publicacion")

Ver la skill `handling-closed-brand-categories`.

### Producto sin precios (tipo "publicidad")

Crear la entrada con lo que sí se ve (descripción, marca, tipo_promocion si es visible). Todos los campos de precio quedan en `null`, pero el tipo de promoción se registra si está escrito (ej: "2x1").

### Vinos y bebidas

Para vinos, la descripción debe incluir el nombre comercial completo del vino, y si es visible, la cepa/varietal (Malbec, Cabernet, etc.) y el año. La marca es la bodega o línea.

Ejemplo: "Vino Episodio del Callejón" con marca "Episodio del Callejón". Si se lee "Malbec 2020", agregar: "Vino Episodio del Callejón Malbec 2020".

## Formato de respuesta

Responder solo con JSON válido. Sin texto antes ni después. Sin backticks. Sin explicaciones.

```json
{
  "pagina": <número_de_página>,
  "productos": [
    {
      "descripcion": "texto o null",
      "unidad_medida": "texto o null",
      "marca": "texto o null",
      "precio_regular": <número o null>,
      "precio_oferta": <número o null>,
      "porcentaje_descuento": <decimal o null>,
      "tipo_promocion": "texto o null",
      "tipo_imagen": "regular|destacada|publicidad|publicacion",
      "nombre_categoria": "texto o null",
      "combo": "Principal|Secundario|null",
      "carrier": "texto o null",
      "tarjeta_fidelidad": "texto o null",
      "comentarios": "texto o null"
    }
  ]
}
```

## Notas de diseño

### Por qué la regla de "no inventar" está tan enfatizada

Los modelos de visión tienden a "completar" información usando conocimiento general. Si ven un producto Copa de Oro, saben que es de 820g aunque no lo lean. Esta tendencia hay que frenarla explícitamente y con repetición.

### Por qué se pide el texto exacto

Para evitar que el modelo reformule descripciones. Si el folder dice "Duraznos en mitades reducido en calorías", queremos exactamente eso, no "Duraznos light en mitades".

### Por qué los precios son números sin $

Para facilitar el parsing del JSON. El modelo a veces agrega el símbolo $ si no se le dice explícitamente que no lo haga.

### Por qué no se pide calcular nada

Si solo se ve el precio de oferta y el descuento, el modelo podría calcular el precio regular. Pero ese cálculo puede ser incorrecto (redondeos, precios con centavos). Es mejor tener `null` y que un humano lo complete, que tener un número mal calculado que se da por bueno.

### Por qué la descripción y la marca se separan

En el Excel destino son campos separados. Si el folder dice "Cerveza Lager Classic Hermann Müller", la descripción es "Cerveza Lager Classic" y la marca es "Hermann Müller". Esto permite filtrar por marca sin parsear la descripción.

### Por qué se registra la promoción en publicidades

Un producto puede no tener precio visible pero sí tener "2x1" escrito. Esa es información valiosa — el tipo de promo es un dato independiente del precio.
