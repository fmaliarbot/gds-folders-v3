---
name: handling-closed-brand-categories
description: Maneja bloques de catálogo dedicados a una única marca bajo una promoción conjunta, o bloques con múltiples marcas/líneas compartiendo una promoción. Usar siempre que se vea un banner agrupando productos bajo una misma oferta (ej: "Espadol", "Arcor", "2x1 cervezas multi-marca", "Federal Rosato/Rosso", "Fanta regular/Zero"). Cubre cuatro casos, incluyendo la distinción crítica entre variedades (fragancias/sabores/tipos → 1 registro) y líneas distintas (fórmulas/composiciones distintas → N registros).
---

# Marca Cerrada y Publicaciones por Marca

## Problema que resuelve esta skill

Una zona de la página del catálogo muestra un grupo de productos de una sola marca bajo una promoción conjunta. A veces hay productos individuales visibles, a veces solo la marca y la promoción. El agente debe registrar correctamente cada variante sin inventar productos ni categorías que no estén visibles.

## Cuándo aplica esta skill

Se activa cuando la imagen muestra:

- Un bloque dedicado a una marca (ej: banner "Espadol", "Arcor", "Unilever", "Nobleza Gaucha")
- Una promoción que aplica a la marca completa, no a un SKU específico
- Productos individuales visibles o no dentro del bloque de marca

## Los tres casos posibles

### Caso A: Marca cerrada con productos visibles

La imagen muestra el banner de marca y varios productos o sub-grupos identificables de esa marca.

**Ejemplo:** Bloque "70% en la 2da unidad" con yerbas Nobleza Gaucha, Cruz Malta y Taraguí visibles.

**Qué hacer:** Crear una entrada por cada producto o sub-grupo distinguible.

```json
{
  "productos": [
    {
      "descripcion": "Yerbas y mate cocido",
      "unidad_medida": null,
      "marca": "Nobleza Gaucha",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": null,
      "tipo_promocion": "70% en la 2da unidad",
      "tipo_imagen": "publicacion",
      "nombre_categoria": "YERBA MATE",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Yerbas y mate cocido",
      "unidad_medida": null,
      "marca": "Cruz Malta",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": null,
      "tipo_promocion": "70% en la 2da unidad",
      "tipo_imagen": "publicacion",
      "nombre_categoria": "YERBA MATE",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Yerbas y mate cocido",
      "unidad_medida": null,
      "marca": "Taraguí",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": null,
      "tipo_promocion": "70% en la 2da unidad",
      "tipo_imagen": "publicacion",
      "nombre_categoria": "YERBA MATE",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    }
  ]
}
```

**Notar:**

- La descripción refleja lo que se VE como grupo ("yerbas y mate cocido"), no una categoría inventada
- Cada marca visible tiene su propia línea
- Precios en `null` porque no se ven individualmente
- `tipo_imagen` es `publicacion` porque es un grupo de marca

### Caso B: Marca cerrada sin productos visibles

La imagen muestra solo la marca y la promoción, sin productos individuales identificables.

**Ejemplo:** Solo se ve "Espadol — 20% de descuento" con una imagen genérica de la marca.

**Qué hacer:** Una sola entrada con lo que se ve. No inventar productos ni categorías.

```json
{
  "productos": [
    {
      "descripcion": "Productos Espadol",
      "unidad_medida": null,
      "marca": "Espadol",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": 0.20,
      "tipo_promocion": "20%",
      "tipo_imagen": "publicacion",
      "nombre_categoria": null,
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    }
  ]
}
```

**Notar:**

- No se generan líneas por categoría de Espadol (jabón, alcohol en gel, etc.) — eso lo sabe GDSnet por su base maestra, no el modelo
- La descripción es genérica porque no hay productos específicos visibles
- Esto probablemente vaya a "Para Revisión" por los campos faltantes

### Caso C: Publicación con productos individuales y precios

La imagen muestra el bloque de marca y cada producto tiene su propio precio visible.

**Ejemplo:** Bloque Milka + Cadbury con "tabletas de chocolate y galletitas", cada producto con su precio individual.

**Qué hacer:** Una línea por cada producto visible con sus datos individuales, incluyendo el precio de cada uno.

### Caso D: Múltiples productos bajo una promoción compartida

La imagen muestra un bloque donde varias marcas distintas, o variantes/líneas de una misma marca, comparten una única promoción. Todos son visibles pero no tienen precio individual: todos están bajo la misma oferta.

Este caso requiere distinguir entre **variedades** y **líneas distintas**, porque la regla de carga es diferente para cada uno.

#### Distinción clave: variedades vs líneas distintas

**Variedades:** son fragancias, sabores o tipos del mismo producto base. Ejemplos:
- Sabores de fideos (al huevo, común, integral)
- Fragancias de shampoo (manzanilla, bebé, cítrico)
- Sabores de jugo (naranja, manzana, multifruta)
- Tipos de yerba (tradicional, suave, con palo)

**Regla para variedades:** **UN SOLO registro** que representa al producto, eligiendo una de las variedades visibles en la imagen para usar en la descripción. Agregar el texto `"varios sabores"` en el campo `comentarios` para señalar que la promoción aplica a más variedades además de la elegida. No usar "varios sabores" genérico en la descripción.

**Regla para variedades no legibles — aplicación estricta del principio "no inventar":**

Cuando se ven múltiples envases o variantes del producto en la imagen pero **no hay texto legible** que permita identificar qué variedad específica es cada una (ej: 3 envases del mismo producto con distinto color de packaging pero sin etiquetas con nombres de fragancia/tipo visibles):

1. **`descripcion`:** usar una descripción genérica del producto sin inventar un nombre de variedad. No asumir "limón", "menta", "cítrico" u otros nombres basándose solo en colores del envase. El color del envase NO es texto legible.
2. **`tipo_variedad`:** dejar en `null`.
3. **`descripcion_variedad`:** dejar en `null`.
4. **`comentarios`:** agregar la nota `"variedades visibles sin texto legible"` para señalar al revisor humano que el producto tiene variantes pero no se pudieron identificar.

**Cómo distinguir "variedad legible" vs "variedad no legible":**

- ✅ **Legible:** un envase dice claramente "Frescura Cítrica", "Original", "Floral" como texto impreso en la etiqueta visible → elegir una concreta y marcar `tipo_variedad` con `"Varias fragancias"` / `"Varios tipos"` / `"Varios sabores"` según corresponda.
- ❌ **No legible:** tres envases con colores distintos (azul, amarillo, verde) sin texto diferenciador visible → variedad no se identifica, `tipo_variedad: null` + nota en `comentarios`.

**Señal adicional — códigos múltiples bajo un mismo precio:**

Cuando el folder lista múltiples códigos de producto asociados a una misma imagen y precio (ej: "Cód. 4815, 15317, 15318, 75380"), esto es evidencia objetiva de que hay múltiples SKUs agrupados bajo ese precio. El folder los trata como un bloque con precio único precisamente porque son variantes o formatos de un mismo producto base.

Esta señal complementa la inspección visual:

- Si hay códigos múltiples **y** texto de variante legible en los envases → tratar como variedades con `tipo_variedad` apropiado y elegir una variante concreta para la descripción.
- Si hay códigos múltiples **pero** no hay texto diferenciador legible en los envases → tratar como variedades con `tipo_variedad: null` y nota explicativa en `comentarios`. La existencia de múltiples códigos confirma que hay variantes aunque no se puedan identificar visualmente.
- Si no hay códigos múltiples **y** no hay texto diferenciador → evaluar si son realmente variantes del mismo producto o si son presentaciones distintas del mismo SKU único (ver Caso D y otras reglas).

Los códigos múltiples son una pista útil pero no son obligatorios en todos los folders — no todos los catálogos los publican. Su ausencia no prueba que no hay variedades.

**Ejemplo — variedades no legibles:**

Imagen: 3 envases de Lavavajilla Cif con colores distintos (azul, amarillo, verde), sin texto visible que diga qué variedad es cada uno. Todos a $3.490, x 500 cc.

**Qué hacer:** un registro con descripción genérica. NO inventar fragancias basándose en colores.

```json
{
  "descripcion": "Lavavajilla Cif Active Gel",
  "marca": "Cif",
  "medida": 500,
  "u_medida": "cc",
  "precio_oferta": 3490,
  "tipo_variedad": null,
  "descripcion_variedad": null,
  "comentarios": "variedades visibles sin texto legible"
}
```

**Por qué esta regla es estricta:**

El principio "no inventar datos" aplica con fuerza acá. Un color de envase no es información sobre la fragancia — es solo un color. Inventar que "el azul es cítrico" o "el amarillo es limón" es exactamente el tipo de alucinación que degrada la calidad del dataset. Es mejor registrar el producto con `tipo_variedad: null` y que un revisor humano complete, que registrar una fragancia inventada que parece cierta.

**Líneas distintas:** son productos que difieren en su composición, formulación o posicionamiento comercial, aunque compartan marca. Ejemplos:
- Coca Cola regular, Coca Cola Zero, Coca Cola Light (distintas fórmulas)
- Fanta regular, Fanta Zero (distintas fórmulas)
- Vermouth Rosato, Vermouth Rosso (distinto tipo de vermouth)
- Cerveza clara, cerveza negra, cerveza IPA (distintos estilos)
- Desodorante roll-on, aerosol, barra (distintas presentaciones)

**Regla para líneas distintas:** **UN REGISTRO POR CADA LÍNEA** visible, repitiendo precio y promoción en todas.

#### Cómo distinguir en la práctica

Si tenés dudas sobre si un bloque son "variedades" o "líneas distintas", preguntate:

1. **¿Son simplemente sabores/fragancias del mismo producto?** → variedades → 1 registro
2. **¿Son fórmulas distintas (zero, light, regular, etc.)?** → líneas distintas → N registros
3. **¿Son tipos estructuralmente distintos del producto (rosato vs rosso, clara vs negra)?** → líneas distintas → N registros
4. **¿Son marcas distintas?** → productos distintos → N registros (caso obvio)

Si no podés decidir claramente después de estas preguntas, la duda se resuelve marcando el caso para revisión humana, no inventando una regla.

#### Diferencia con Caso A

En el Caso A hay un banner de UNA sola marca con productos de esa marca. En el Caso D hay múltiples marcas o múltiples líneas bajo una promo conjunta.

#### Diferencia con combos

En un combo, los productos se venden JUNTOS por un único precio. En el Caso D, cada producto se vende por separado pero la promoción aplica a todos.

#### Ejemplo 1: Multi-marca con promo compartida (líneas distintas → N registros)

Imagen: bloque "2x1" con cervezas de 4 marcas distintas visibles (Miller, Heineken, Imperial Golden, Blue Moon), en porrón, sin precios individuales.

**Qué hacer:** crear una entrada por cada marca visible, repitiendo la promoción en todas.

```json
{
  "productos": [
    {
      "descripcion": "Cerveza",
      "unidad_medida": "porrón",
      "marca": "Miller",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": null,
      "tipo_promocion": "2x1",
      "tipo_imagen": "destacada",
      "nombre_categoria": "CERVEZA",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Cerveza",
      "unidad_medida": "porrón",
      "marca": "Heineken",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": null,
      "tipo_promocion": "2x1",
      "tipo_imagen": "destacada",
      "nombre_categoria": "CERVEZA",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Cerveza",
      "unidad_medida": "porrón",
      "marca": "Imperial Golden",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": null,
      "tipo_promocion": "2x1",
      "tipo_imagen": "destacada",
      "nombre_categoria": "CERVEZA",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Cerveza",
      "unidad_medida": "porrón",
      "marca": "Blue Moon",
      "precio_regular": null,
      "precio_oferta": null,
      "porcentaje_descuento": null,
      "tipo_promocion": "2x1",
      "tipo_imagen": "destacada",
      "nombre_categoria": "CERVEZA",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    }
  ]
}
```

#### Ejemplo 2: Líneas distintas de la misma marca (→ N registros)

Imagen: bloque de Federal Vermouth con dos líneas visibles (Rosato y Rosso), x 750 ml, $11.610, antes $19.350, 40%.

Rosato y Rosso son **líneas distintas** (vermouth rosado vs rojo, tipos estructuralmente distintos), no variedades.

**Qué hacer:** una entrada por cada línea visible. Precio y promo se repiten.

```json
{
  "productos": [
    {
      "descripcion": "Vermouth Rosato",
      "unidad_medida": "x 750 ml",
      "marca": "Federal",
      "precio_regular": 19350,
      "precio_oferta": 11610,
      "porcentaje_descuento": 0.40,
      "tipo_promocion": "40%",
      "tipo_imagen": "destacada",
      "nombre_categoria": "APERITIVOS C/ALCOHOL",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Vermouth Rosso",
      "unidad_medida": "x 750 ml",
      "marca": "Federal",
      "precio_regular": 19350,
      "precio_oferta": 11610,
      "porcentaje_descuento": 0.40,
      "tipo_promocion": "40%",
      "tipo_imagen": "destacada",
      "nombre_categoria": "APERITIVOS C/ALCOHOL",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    }
  ]
}
```

#### Ejemplo 3: Variedades del mismo producto (→ 1 registro con variedad específica + comentario)

Imagen: bloque de Jugos Tutti con varias variedades visibles (multifruta, naranja, manzana, xtreme ácido, chicle), x 200 ml, $480, antes $723, 3x2.

Los distintos sabores son **variedades** del mismo producto base (Jugo Tutti), no líneas distintas. La fórmula y el producto son el mismo; solo cambia el sabor.

**Qué hacer:** UN registro con una de las variedades visibles concretas (elegir una) en la descripción, y agregar el texto "varios sabores" en el campo `comentarios`. No usar "varios sabores" genérico en la descripción; la descripción debe reflejar una variedad real que está visible en la imagen.

```json
{
  "productos": [
    {
      "descripcion": "Jugo Manzana",
      "unidad_medida": "x 200 ml",
      "marca": "Tutti",
      "precio_regular": 723,
      "precio_oferta": 480,
      "porcentaje_descuento": null,
      "tipo_promocion": "3x2",
      "tipo_imagen": "destacada",
      "nombre_categoria": "RTD",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,
      "comentarios": "varios sabores"
    }
  ]
}
```

**Notas sobre la elección de la variedad:**
- Elegir cualquiera de las variedades visibles en la imagen. No hay preferencia entre ellas.
- La variedad elegida debe ser una que efectivamente se vea en la imagen (no inventar sabores que no están).
- El comentario "varios sabores" en `comentarios` es lo que señala al revisor humano que la promoción aplica a más variedades además de la elegida.

#### Ejemplo 4: Líneas distintas de la misma marca (fórmula distinta → N registros)

Imagen: bloque con Fanta regular y Fanta Zero, x 1,75 Lt, $3.335 (antes $4.450), 25% llevando 2.

Fanta regular y Fanta Zero son **líneas distintas** (fórmulas distintas — una con azúcar, otra sin), aunque compartan marca y presentación.

**Qué hacer:** dos entradas, una por cada línea.

```json
{
  "productos": [
    {
      "descripcion": "Gaseosa Naranja",
      "unidad_medida": "x 1,75 Lt",
      "marca": "Fanta",
      "precio_regular": 4450,
      "precio_oferta": 3335,
      "porcentaje_descuento": 0.25,
      "tipo_promocion": "25% llevando 2",
      "tipo_imagen": "destacada",
      "nombre_categoria": "GASEOSAS",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    },
    {
      "descripcion": "Gaseosa Naranja",
      "unidad_medida": "x 1,75 Lt",
      "marca": "Fanta Zero",
      "precio_regular": 4450,
      "precio_oferta": 3335,
      "porcentaje_descuento": 0.25,
      "tipo_promocion": "25% llevando 2",
      "tipo_imagen": "destacada",
      "nombre_categoria": "GASEOSAS",
      "combo": null,
      "carrier": null,
      "tarjeta_fidelidad": null,

      "comentarios": null
    }
  ]
}
```

#### Regla general del Caso D

- Si son **variedades** (fragancias/sabores/tipos del mismo producto base): **1 registro**
- Si son **líneas distintas** (fórmulas/composiciones/tipos estructuralmente distintos): **N registros, uno por línea**
- Si son **marcas distintas**: **N registros, uno por marca**

El precio, la unidad y la promoción se repiten en cada entrada cuando hay N registros. La descripción y/o la marca diferencian cada entrada.

## Qué NO debe hacer el modelo

- Inventar categorías de productos para una marca
- Generar múltiples líneas cuando solo se ve una marca sin productos
- Asumir qué productos vende una marca basándose en conocimiento general
- Completar precios que no se ven
- Usar `combo` para marca cerrada (combo es cuando hay un precio compartido entre dos productos que se venden juntos obligatoriamente)
- Fusionar múltiples marcas en una sola entrada con la marca concatenada (ej: "Miller/Heineken/Imperial/Blue Moon" en el campo marca). Cada marca visible debe tener su propia entrada.
- Generar un registro por cada variedad (sabor, fragancia, tipo) de un mismo producto base. Las variedades van en UN registro con una variedad concreta visible elegida, y "varios sabores" en comentarios.
- Usar frases genéricas como "varios sabores" o "multi sabor" en el campo descripción. La descripción debe ser una variedad concreta; la nota "varios sabores" va en `comentarios`.
- **Inventar nombres de variedad basándose en colores de packaging.** Un envase azul no significa "menta" ni "cítrico"; un envase rojo no significa "frutilla" ni "picante". El color no es información sobre el tipo/fragancia/sabor. Si el producto tiene variedades visibles pero no hay texto legible que las identifique, marcar `tipo_variedad: null` + nota en `comentarios` ("variedades visibles sin texto legible").
- Confundir líneas distintas con variedades. Si hay duda, aplicar las preguntas de la subsección "Cómo distinguir en la práctica".

