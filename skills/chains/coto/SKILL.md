---
name: coto
description: Maneja las particularidades del catálogo de COTO, la cadena de supermercados e hipermercados argentina. Usar siempre que se procese un catálogo, folder o publicación de COTO. Incluye información sobre zona de cobertura, canal, tarjeta de fidelidad Comunidad COTO, convenciones de formato de SKU y reglas específicas de la cadena.
---

# Procesamiento de catálogos de COTO

## Cuándo usar esta skill

Activar esta skill cuando se está procesando cualquier catálogo, folder o publicación promocional de COTO. La skill provee el contexto específico de esta cadena para completar correctamente los campos fijos y resolver las particularidades de naming y formato.

## Datos fijos de la cadena

Al procesar un catálogo de COTO, los siguientes campos se completan con valores fijos:

| Campo | Valor |
| :---- | :---- |
| Nombre de la Cadena | COTO |
| Canal | Supermercado / Hipermercado |
| Zona de Cobertura | Nacional (Argentina) |
| Publicador | REGULAR (valor por defecto cuando no hay publicador específico) |

## Tarjeta de fidelidad: Comunidad COTO

COTO tiene una tarjeta de fidelidad propia llamada **Comunidad COTO**. Cuando se detecte que una promoción aplica con esta tarjeta, completar el campo `tarjeta_fidelidad` con el valor `Comunidad COTO`.

### Patrones de reconocimiento

La tarjeta puede aparecer en el catálogo con distintas variaciones textuales. Identificar como Comunidad COTO cualquiera de las siguientes:

- Comunidad COTO (forma canónica)
- comunidad coto (minúsculas)
- COMUNIDAD (aparece sola, típicamente en promociones "exclusivas")
- Logo o badge de Comunidad COTO
- Frases como "con Comunidad COTO", "exclusivo Comunidad", "precio Comunidad"

En todos estos casos, el valor canónico a registrar es **Comunidad COTO** (con esa capitalización exacta).

### Ejemplos de interpretación

- "40% OFF con Comunidad COTO" → `tarjeta_fidelidad: "Comunidad COTO"`, `tipo_promocion: "40% OFF"`
- "Exclusivo COMUNIDAD" → `tarjeta_fidelidad: "Comunidad COTO"`
- "Precio Comunidad $1.999" → `tarjeta_fidelidad: "Comunidad COTO"`, precio aplica solo con tarjeta

## URL del catálogo

La sección de catálogos semanales de COTO está disponible en:
`https://coto.com.ar/images/catalogos/revistas/semanal-alimentos/index_mobile.asp`

## Convención de formato de SKU

COTO sigue convenciones específicas en cómo el equipo de GDSnet abrevia las descripciones de productos. El agente debe generar la descripción completa (ver skill `formatting-sku`), y luego el cruce contra la base maestra de GDSnet resuelve la abreviación canónica.

### Ejemplos observados

| Descripción larga (agente) | Abreviación manual (GDSnet) |
| :---- | :---- |
| COCINERO ACEITE MEZCLA SOJA Y GIRASOL PET 900CC | COCINERO MEZCLA PET 900CC |
| MORIXE HARINA ESPECIAL PARA PIZZAS CASERAS 1KG | MORIXE PIZZAS 1KG |
| HEINEKEN CERVEZA PORRON 330ML | HEINEKEN 330ML |
| FORMIS GALLETITAS RELLENAS ANIMALES CHOCOLATE 72G | FORMIS ANIMAMES CHOC 72G |

La descripción larga del agente contiene más información y facilita el match contra la base maestra, incluso cuando la convención manual es más corta.

## Tipos de aviso en catálogos de COTO

Los catálogos de COTO usan estas categorías de tipo de aviso:

- **Regular:** producto con foto y precio individual, tamaño estándar
- **Destacado:** producto con foto más grande, generalmente con borde o fondo especial
- **Publicidad:** banner o imagen sin producto específico (ej: portada, publicidad de marca)
- **Publicación:** grupo de productos de la misma marca agrupados bajo un publicador común

## Tipos de promoción frecuentes

Las promociones más comunes en COTO incluyen:

- Descuentos porcentuales: `25%DTO`, `30%DTO`, `35%DTO`, `40%DTO`
- Promociones multi-unidad: `2X1`, `3X2`, `4X3`
- Descuentos en segunda unidad: `70% EN LA 2DA`, `2DO AL 50%`
- Combinaciones con tarjeta: típicamente con Comunidad COTO para descuento adicional

## Categorías frecuentes observadas

En los catálogos de Almacén y Bebidas, las categorías más comunes son: Aceites, Harinas y Premezclas, Condimentos, Galletitas, Golosinas, Gaseosas, Aguas, Vinos, Cervezas, Aperitivos c/Alcohol, Gin, Yerba y Mate, Café, Conservas, Pastas, Almacén.

Esta lista es orientativa y no exhaustiva. Los valores canónicos de categoría deben obtenerse de la base maestra de GDSnet cuando esté disponible.

## Casos especiales conocidos en COTO

### Categorías cerradas con banner

COTO frecuentemente presenta familias de productos (vinos, cervezas) como un banner de marca con varios SKUs agrupados sin precio individual por producto. En estos casos:

- Clasificar como `tipo_imagen: "publicacion"` si el publicador es identificable (ej: "Pajaro Azul", "Iguazu")
- Clasificar como `tipo_imagen: "Destacado"` si es un banner de categoría sin publicador específico
- No inventar precios para cada producto individual — dejar `precio_regular` y `precio_oferta` en `null`
- Marcar `is_closed_category = true` para que el scoring lo trate correctamente

### Publicidades de portada

La primera página suele ser publicidad con productos pero sin precios ni descuentos visibles. Estos se registran con `tipo_imagen: "Publicidad"` y campos de precio en `null`.
