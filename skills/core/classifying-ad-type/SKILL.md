---
name: classifying-ad-type
description: Clasifica el tipo de aviso o imagen de cada producto del catálogo en uno de cuatro tipos (regular, destacada, publicidad, publicacion) según cómo se presenta visualmente. Usar siempre que se extraiga un producto, ya que esta clasificación afecta qué campos se esperan completos y si el producto irá a revisión. Incluye reglas de decisión, ejemplos y errores comunes a evitar.
---

# Clasificación de Tipo de Aviso

## Problema que resuelve esta skill

Cada producto extraído de un catálogo debe clasificarse según cómo se presenta visualmente en la página. Esta clasificación afecta qué datos se esperan completos y si el producto va a revisión humana.

## Los cuatro tipos

### regular

**Qué se ve:** Producto individual con tamaño estándar y uniforme. No se destaca visualmente del resto de la página. Tiene un espacio asignado similar al de los demás productos.

**Datos esperados:** Todos o la mayoría de los campos completos — precio regular, precio oferta, descuento, marca, descripción, unidad de medida.

**Ejemplo típico:** Una grilla de productos donde cada uno ocupa el mismo espacio rectangular, con su foto, nombre, marca, precio tachado y precio de oferta.

### destacada

**Qué se ve:** Producto que ocupa notablemente más espacio que los demás en la página. Imagen más grande, puede tener fondo de color diferente, borde especial, o estar en una posición prominente (centro, arriba, sección propia).

**Datos esperados:** Los mismos que `regular`, generalmente más completos porque hay más espacio para mostrarlos.

**Cómo distinguir de regular:** Si sacás ese producto de la página, quedaría un hueco grande. Los productos regulares son intercambiables en tamaño — los destacados no.

### publicidad

**Qué se ve:** Imagen del producto y/o marca, pero NO hay precios en pesos. Puede tener un tipo de promoción visible (ej: "2x1") pero sin valores monetarios. Puede tener un slogan o mensaje promocional genérico.

**Datos esperados:** Descripción, marca, y `tipo_promocion` si es visible. Los campos de precio quedan en `null`.

**Clave:** La ausencia de PRECIOS EN PESOS es lo que define este tipo. Si hay aunque sea un precio, no es publicidad. Pero si dice "2x1" sin precio, sigue siendo publicidad con `tipo_promocion: "2x1"`.

**Siempre va a revisión** por definición, porque no tiene datos de precio.

### publicacion

**Qué se ve:** Un grupo de productos del MISMO fabricante o marca, presentados juntos bajo un banner o bloque visual unificado. Los productos individuales dentro del bloque pueden tener sus propios datos.

**Datos esperados:** Variables. Algunos productos del grupo pueden tener precios, otros no. La promoción suele ser compartida (ej: "70% en la 2da unidad" para toda la marca).

**Cómo distinguir de regular:** Los regulares son productos independientes en una grilla. Las publicaciones son agrupaciones intencionales por marca o fabricante. Ver la skill `handling-closed-brand-categories` para el tratamiento completo.

## Árbol de decisión

```
¿Se ven precios en pesos ($)?
├── NO → ¿Se ve tipo de promoción (2x1, %, etc.)?
│   ├── SÍ → "publicidad" (con tipo_promocion registrado)
│   └── NO → "publicidad" (todo null excepto descripción/marca)
└── SÍ
    ├── ¿Es un grupo de productos de la misma marca?
    │   ├── SÍ → "publicacion"
    │   └── NO
    │       ├── ¿Ocupa más espacio que los demás?
    │       │   ├── SÍ → "destacada"
    │       │   └── NO → "regular"
```

## Errores comunes a evitar

### Confundir "publicidad" con "regular sin precio"

Si un producto regular simplemente no tiene precio visible (se borró, está tapado por otro elemento), sigue siendo `regular` con precio `null`. `publicidad` es cuando INTENCIONALMENTE no hay precio — es un espacio publicitario, no una oferta.

### Confundir "publicacion" con varios productos regulares

Si hay 5 marcas distintas en una grilla, son 5 regulares. Si hay 5 productos de la misma marca en un bloque dedicado con banner compartido, es una publicación.

### Marcar todo lo grande como "destacada"

Solo es destacada si es más grande que sus vecinos en la misma página. Si toda la página tiene productos grandes, son todos regulares. La clasificación de "destacada" es relativa al contexto de la página.

### Confundir un agrupador no-marca con "publicacion"

El tipo `publicacion` aplica cuando el agrupador es **una marca**. No todos los banners que agrupan productos son marca. Existen otros agrupadores que pueden aparecer en un catálogo:

- Un fabricante que comercializa múltiples marcas distintas
- Un evento o campaña (ej: aniversario, temporada, feria)
- Un proveedor o alianza comercial
- Una categoría temática (ej: "lo más pedido de la semana")

Cuando el agrupador **no es una marca** y los productos dentro tienen **precios individuales propios**, cada producto se clasifica según su propio tratamiento visual (generalmente `regular`, o `destacada` si ocupa más espacio que otros en la misma página). El agrupador actúa como contexto editorial, no como marca cerrada.

La distinción operativa:

- Si todos los productos del bloque pertenecen a la misma marca comercial → `publicacion`
- Si el bloque agrupa productos de marcas distintas (aunque compartan fabricante o campaña) → clasificar cada producto individualmente (`regular` o `destacada` según el caso)
