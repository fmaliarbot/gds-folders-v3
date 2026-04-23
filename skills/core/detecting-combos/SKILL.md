---
name: detecting-combos
description: Detecta productos vendidos en combo (dos o más productos con un único precio compartido) en catálogos promocionales de supermercados. Usar siempre que se encuentren productos con la palabra "Combo", el símbolo "+" entre productos, o un único precio para múltiples productos. Identifica cuál es el producto principal y cuál el secundario, asigna el precio correctamente y vincula ambos productos mediante el campo carrier.
---

# Detección de Combos

## Problema que resuelve esta skill

Algunos productos en los catálogos se venden juntos como un combo con un único precio compartido. El agente necesita identificar esta situación, separar cada producto como una entrada individual en el output, y vincularlos correctamente sin duplicar ni inventar precios.

## Cuándo aplica esta skill

Se debe activar cuando la imagen del catálogo muestra:

- La palabra "Combo" de forma explícita
- El símbolo "+" entre dos o más productos
- Dos o más productos con un único precio compartido
- Frases del tipo "Llevando X + Y"
- Promociones cruzadas como "X con Y"

## Qué debe hacer el modelo

1. Detectar que se trata de un combo analizando los indicadores visuales
2. Identificar cada producto individual dentro del combo
3. Marcar el producto que aparece más destacado o primero como "Principal"
4. Marcar los productos restantes como "Secundario"
5. Asignar el precio total del combo al producto principal
6. Asignar `precio_oferta = 0` a los productos secundarios
7. Referenciar cada producto en el campo `carrier` del otro

## Qué NO debe hacer

- Dividir el precio del combo entre los productos (el precio es del combo completo, no de cada producto individual)
- Inventar precios individuales que no están visibles en el catálogo
- Asumir cuál es el principal cuando no es claro (en ese caso, marcar ambos como "Principal" y registrar en observaciones para revisión manual)
- Crear una única entrada para el combo completo (cada producto debe tener su fila)

## Regla de asignación de precio

- **Producto principal:** lleva el precio completo del combo en `precio_oferta`
- **Producto secundario:** `precio_oferta = 0`, `precio_regular = null`
- **Indeterminado (no se sabe cuál es principal):** ambos como "Principal", ambos con el precio completo, registrar en observaciones que requiere revisión manual

## Ejemplo de output correcto

Imagen en el catálogo: "Ramazzotti 750ml + Mumm 750ml — $10.500"

```json
{
  "productos": [
    {
      "descripcion": "Amaro Ramazzotti",
      "unidad_medida": "x 750 ml",
      "marca": "Ramazzotti",
      "precio_regular": null,
      "precio_oferta": 10500,
      "porcentaje_descuento": null,
      "tipo_promocion": null,
      "tipo_imagen": "regular",
      "nombre_categoria": "APERITIVOS C/ALCOHOL",
      "combo": "Principal",
      "carrier": "Champagne Mumm x 750 ml",
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Champagne Mumm",
      "unidad_medida": "x 750 ml",
      "marca": "Mumm",
      "precio_regular": null,
      "precio_oferta": 0,
      "porcentaje_descuento": null,
      "tipo_promocion": null,
      "tipo_imagen": "regular",
      "nombre_categoria": "CHAMPAGNE",
      "combo": "Secundario",
      "carrier": "Amaro Ramazzotti x 750 ml",
      "tarjeta_fidelidad": null,

      "comentarios": null
    }
  ]
}
```

**Notar:** `precio_regular` queda en `null` en ambos porque no se ve. `tipo_promocion` queda en `null` porque no se menciona un porcentaje o descuento específico — simplemente es un combo a precio fijo.
