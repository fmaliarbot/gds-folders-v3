---
name: reading-prices
description: Lee e interpreta precios en formato argentino desde catálogos y los asigna correctamente a uno de los 4 campos de precio del schema canónico (precio_oferta, precio_anterior, precio_tarjeta_banco, precio_tarjeta_fidelidad). Distingue por leyendas, posición visual y contexto. Aplica la regla de no inventar precios no visibles. Esencial para que las ofertas se carguen con precisión en GDSnet.
---

# Lectura de Precios

## Problema que resuelve esta skill

Los catálogos argentinos pueden mostrar hasta **4 precios distintos** para un mismo producto: precio anterior (regular), precio oferta (vigente), precio con tarjeta de banco, precio con tarjeta de fidelidad. Esta skill enseña cómo identificar cuál es cuál, leerlos correctamente en formato argentino, y cuándo dejar `null`.

Las **reglas globales** del agente (no inventar, ante la duda `null` con flag) están en `extracting-products`. Esta skill las extiende con detalle específico de los campos de precio.

## Formato de precios argentinos

- Separador de miles: punto (`.`)
- Separador decimal: coma (`,`)
- Símbolo: `$` (a veces omitido)

Ejemplos: `"$3.299"`, `"$2.143,90"`, `"$14.567,90"`, `"$700,90"`.

## Cómo convertir al output JSON

1. Quitar el símbolo `$`.
2. Quitar el punto de miles.
3. Reemplazar la coma decimal por punto.
4. Resultado: número (sin comillas).

| En la imagen | En el JSON |
|---|---|
| $3.299 | `3299` |
| $2.143,90 | `2143.9` |
| $14.567,90 | `14567.9` |
| $700,90 | `700.9` |
| $10.500 | `10500` |

## Los 4 campos de precio

### precio_oferta

El precio vigente con descuento. Generalmente el más prominente en la imagen.

**Cómo aparece:**
- Número grande, llamativo.
- Color destacado (rojo, amarillo, blanco sobre fondo de color).
- Leyenda: "Ahora", "Oferta", "Precio especial", o sin leyenda específica.
- A veces dentro de un sticker o badge.

### precio_anterior

El precio sin descuento (precio regular o "antes").

**Cómo aparece:**
- Tachado con una línea diagonal o horizontal.
- En letra más chica que el precio de oferta.
- Leyenda: "Antes", "P. Lista", "Precio regular".
- Color más claro o gris.

### precio_tarjeta_banco

El precio aplicando una tarjeta de banco específica.

**Cómo aparece:**
- Junto a un logo de tarjeta bancaria (Visa, Mastercard, Mercado Pago, etc.) o de un banco (Banco Provincia, Galicia, etc.).
- Leyenda: "Con tarjeta X", "Pagando con Y".
- Suele ser un tercer precio adicional al oferta y al anterior.

**Importante:** este campo va con el monto numérico final, NO con el porcentaje. Si solo se ve "10% adicional con MODO" pero no hay precio explícito, este campo queda `null` y la promo va en `tipo_promocion_tarjeta_bancos`.

### precio_tarjeta_fidelidad

El precio aplicando una tarjeta de fidelidad de la cadena (Comunidad COTO, Mi Carrefour, Cencopay, etc.).

**Cómo aparece:**
- Junto al logo o nombre de la tarjeta de fidelidad.
- Leyenda: "Con Comunidad COTO", "Con Cencopay".
- Igual que con tarjeta_banco: este campo es para el monto numérico final, no para el porcentaje.

## Reglas de asignación

### Caso 1: solo se ve un precio

- Ese precio va en `precio_oferta`.
- Los otros 3 campos quedan en `null`.
- No calcular `precio_anterior` aplicando un porcentaje al revés.

### Caso 2: se ven dos precios (uno tachado y uno destacado)

- El tachado / chico → `precio_anterior`.
- El destacado → `precio_oferta`.
- `precio_tarjeta_banco` y `precio_tarjeta_fidelidad` quedan en `null` salvo que haya un tercer precio explícito junto a un logo de tarjeta.

### Caso 3: se ven tres o más precios

- Identificar cada uno por su leyenda y/o logo asociado.
- Asignar al campo correspondiente.
- Si hay un precio "huérfano" sin leyenda clara, no asignarlo y agregar `PRICE_AMBIGUOUS` a `review_reasons`.

### Caso 4: se ven porcentajes asociados a tarjeta pero no precios numéricos

- El precio numérico va en `precio_oferta` (precio base).
- El porcentaje adicional va en `tipo_promocion_tarjeta_fidelidad` o `tipo_promocion_tarjeta_bancos` según el tipo de tarjeta.
- Los campos `precio_tarjeta_banco` y `precio_tarjeta_fidelidad` quedan en `null`.

### Caso 5: no se ve ningún precio

- Los 4 campos van en `null`.
- Probablemente `tipo_oferta = "Publicidad"`.

## Qué NO hacer

| Situación | Incorrecto | Correcto |
|---|---|---|
| Se ve $2.143,90 y 35% | Calcular `precio_anterior = 2143.9 / 0.65 = 3298.3` | `precio_oferta: 2143.9, precio_anterior: null` |
| Precio borroso, parece $3.2?? | Poner `3200` (adivinando) | `null` + `PRICE_AMBIGUOUS` en review_reasons |
| Se ve un precio en una esquina lejana sin contexto | Asignar a un producto cercano | `null` (no está claro a cuál pertenece) |
| Precio decimal $2.143,90 | `2143.90` (string) | `2143.9` (número) |
| Producto con descuento "20% adicional con MODO" sin precio numérico | Calcular un precio_tarjeta_banco | `precio_tarjeta_banco: null`, registrar en `tipo_promocion_tarjeta_bancos` |

## Precios de combo

Ver la skill `detecting-combos` para la lógica completa. Resumen:

- Precio total del combo → `precio_oferta` del Principal.
- Secundario → `precio_oferta: 0` (no `null`).
- `precio_anterior`: `null` en ambos (no existe un "precio regular" de un combo).

## Notas de diseño

### Por qué tenemos 4 campos de precio y no 1

Es el schema canónico de GDSnet. Las cadenas argentinas (especialmente Jumbo, COTO, Carrefour) ofrecen tres dimensiones de precio simultáneas: base, con tarjeta de fidelidad, con tarjeta bancaria. Si lo metiéramos todo en un solo campo perderíamos visibilidad de qué precio aplica con qué condición.

### Por qué el precio numérico está separado del % de descuento de tarjeta

A veces el folder muestra el precio final con tarjeta (ej: $4.085 con MODO). Otras veces solo muestra "20% DTO con MODO" sin precio explícito. Separados, podemos representar los dos casos.

### Por qué siempre formato numérico, nunca string

Para que el JSON sea procesable por el pipeline downstream sin parsing adicional. Strings tipo `"$2.143,90"` requerirían conversión y son fuente de errores. Números puros (`2143.9`) son inequívocos.
