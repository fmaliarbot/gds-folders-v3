---
name: extracting-multiple-products-per-image
description: Maneja el caso en que una misma imagen o foto del catálogo muestra dos o más productos distintos, cada uno con sus propios datos. Usar siempre que se encuentren múltiples productos en la misma zona visual (ej: Mostaza y Ketchup Natura juntos, cada uno con su precio). Genera una entrada separada por cada producto individual, sin fusionarlos ni tratarlos como combo.
---

# Múltiples Productos en una Misma Imagen

## Problema que resuelve esta skill

Una sola imagen en el catálogo muestra más de un producto, cada uno con sus propios datos (marca, precio, unidad de medida). El agente debe generar una línea del output por cada producto individual, no una línea por imagen compartida.

## Cuándo aplica esta skill

Se activa cuando en la misma zona de la página del catálogo aparecen:

- Dos o más productos distintos con variables propias (precio, marca, unidad)
- Productos que comparten espacio visual pero son independientes comercialmente
- Ejemplo clásico: Mostaza y Ketchup Natura juntos en la misma foto

## Qué debe hacer el modelo

Crear una entrada JSON separada por cada producto individual visible. Cada uno lleva sus propios datos:

- Si cada producto tiene precio, marca o unidad diferentes, se reflejan individualmente
- Si comparten un dato (ej: misma marca, misma promoción), se repite en cada entrada
- El `tipo_imagen` se decide por cada producto según su prominencia visual

## Qué NO debe hacer

- Fusionar los productos en una sola línea
- Poner "Mostaza y Ketchup" como una descripción única
- Inventar precios individuales si solo hay un precio conjunto (en ese caso es un combo, no multi-producto)
- Meter la marca dentro de la descripción (la marca va en su campo aparte)

## Cómo distinguir multi-producto de combo

Esta es la diferencia más importante y fácil de confundir:

**Multi-producto:** Cada producto tiene su propio precio. Son productos independientes que comparten espacio visual por conveniencia del diseño del folder.

**Combo:** Los productos se venden JUNTOS con UN solo precio. Hay "+" o "Combo" explícito en la imagen. Ver la skill `detecting-combos` para el tratamiento específico.

## Ejemplo de output correcto

Imagen del catálogo: Mostaza Natura y Ketchup Natura, ambos al 35%, sin precios visibles.

```json
{
  "productos": [
    {
      "descripcion": "Mostaza",
      "unidad_medida": null,
      "marca": "Natura",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": 0.35,
      "tipo_promocion": "35%",
      "tipo_imagen": "regular",
      "nombre_categoria": "ADEREZOS",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Ketchup",
      "unidad_medida": null,
      "marca": "Natura",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": 0.35,
      "tipo_promocion": "35%",
      "tipo_imagen": "regular",
      "nombre_categoria": "ADEREZOS",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    }
  ]
}
```

**Notar:**

- Dos entradas separadas, una por cada producto
- Misma marca y misma promoción se repite en ambos
- Precios `null` porque no se ven en la imagen — no se inventan
- `combo` y `carrier` en `null` porque son productos independientes, no un combo
