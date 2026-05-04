---
name: building-sku-description
description: Construye la descripción canónica del SKU para el campo `descripcion` del schema, siguiendo uno de los tres patrones estándar (específico con medida, genérico por marca, o "TODOS/TODAS") y aplicando abreviaciones sistemáticas. Genera valores como "ALMA MORA MALBEC 750CC" o "MENTOS CARAMELOS 29,5G". Usar siempre que el agente genere el campo `descripcion` de un producto extraído. La consistencia del SKU es clave para que el pipeline de integración pueda matchear contra la base maestra de GDSnet.
---

# Construcción del SKU (campo `descripcion`)

## Problema que resuelve esta skill

El campo `descripcion` del output del agente debe coincidir con las convenciones de GDSnet para poder matchear contra su base maestra de productos. Una descripción fiel al folder pero que no siga la estructura esperada (ej: "Cerveza Lager Classic Hermann Müller x 500 ml") rompe el match aunque el producto sea el correcto.

Esta skill define los tres patrones de SKU que GDSnet usa históricamente y cuándo aplicar cada uno.

## Cuándo aplica esta skill

Se aplica al construir el valor del campo `descripcion` en la extracción de cada producto, sin excepción. Ninguna otra skill construye descripciones — todas delegan en esta.

## Los 3 patrones canónicos de SKU

### Patrón A: SKU específico con medida

**Estructura completa:** `[MARCA] [LÍNEA] [TIPO_SI_AMBIGUO] [VARIANTE] [MEDIDA][U_MEDIDA]`

**Cuándo usarlo:** cuando el producto en la imagen tiene una medida claramente visible.

#### Jerarquía de componentes — qué es imprescindible y qué es opcional

No todos los componentes de la estructura son igual de importantes. Esta jerarquía es la regla principal del Patrón A:

| Componente | Obligatoriedad | Descripción |
| :---- | :---- | :---- |
| **Marca** | Imprescindible | La marca comercial del producto (`SKIP`, `CIF`, `COCA COLA`, `COMFORT`) |
| **Línea** | Imprescindible | El modelo o línea comercial dentro de la marca (`EXPERT`, `ACTIVE GEL`, `SEGREDOS`, `BIOACTIVE`, `ZERO`). Es lo que suele aparecer destacado en fuente grande o banner del envase. |
| **Tipo de producto** | Condicional | Obligatorio solo si la línea sola no distingue al producto (ej: "BIOACTIVE" es la línea tanto de crema como de desinfectante de CIF, entonces hay que agregar `CREMOSO` o `DESINF` para distinguir). |
| **Variante** | Deseable pero opcional | Detalle adicional dentro de la línea (`CICLOS CORTOS`, `LIMON`, `SEGREDOS 36`, `ORIGINAL`). Se incluye si es visible y legible. Su ausencia no invalida el SKU. |
| **Medida + Unidad** | Imprescindible si visible | La cantidad del producto. Si no es visible, el producto queda en Patrón B, no A. |

**SKU mínimo válido:** `[MARCA] [LÍNEA] [MEDIDA][U_MEDIDA]` — ej: `SKIP EXPERT 800ML`

**SKU óptimo:** `[MARCA] [LÍNEA] [TIPO] [VARIANTE] [MEDIDA][U_MEDIDA]` — ej: `CIF DESINF BIOACTIVE ORIGINAL 360CC`

#### Cómo identificar línea vs variante

La distinción entre "línea" y "variante" es visual:

- **Línea:** suele aparecer destacada en el envase (fuente grande, banner central, parte superior del packaging). Es el nombre comercial de la familia/modelo del producto.
- **Variante:** aparece en texto menor, generalmente abajo o al costado. Especifica algo dentro de esa línea (sabor, fragancia, tamaño, intensidad, etc.).

Ejemplos visuales:
- En un envase Skip Expert con "Ciclos Cortos" abajo: **línea** = EXPERT, **variante** = CICLOS CORTOS
- En un envase Cif "Active Gel" con "x10 Más Espuma" y un color: **línea** = ACTIVE GEL, **variante** = (la que indique el color/texto — ej LIMON si está escrito)
- En un envase Comfort "Segredos" con un número "36": **línea** = SEGREDOS, **variante** = 36

Si no podés distinguir visualmente cuál es línea y cuál variante, lo más seguro es incluir ambas como parte de la descripción principal y marcar en `comentarios` que hubo duda.

#### Cuándo es obligatorio agregar "tipo de producto"

Hay marcas donde la misma línea se usa para productos distintos. En esos casos la línea sola no distingue y hay que incluir el tipo:

- **CIF BIOACTIVE** existe como crema multiuso Y como desinfectante → hay que distinguir: `CIF BIOACTIVE CREMOSO` vs `CIF DESINF BIOACTIVE`
- **SAN REMO** tiene harina, galletas, pastas, olivas → `SAN REMO CRACKERS`, `SAN REMO 000` (harina), `SAN REMO SPAGHETTI`
- **DOVE** tiene shampoo, acondicionador, crema → `DOVE SH RECON COMPLETA` (shampoo), `DOVE CR TRATAMIENTO` (crema)

Si conocés el producto y la línea sola es suficiente (ej: `NESCAFE GOLD` se entiende que es café), podés omitir el tipo. Si hay duda, incluilo.

#### Ejemplos reales del manual con descomposición

| Descripción GDSnet | Marca | Línea | Tipo | Variante | Medida |
| :---- | :---- | :---- | :---- | :---- | :---- |
| `SKIP EXPERT LIMP ACT DP 800ML` | SKIP | EXPERT | — | LIMP ACT DP | 800ML |
| `CIF BIO ACTIVE CREMOSO 750G` | CIF | BIO ACTIVE | CREMOSO | — | 750G |
| `CIF DESINF BIO ORIGINAL 360CC` | CIF | BIO | DESINF | ORIGINAL | 360CC |
| `CIF ACTIVE GEL X10 LIMON 500ML` | CIF | ACTIVE GEL X10 | — | LIMON | 500ML |
| `7UP FREE 1,5L` | 7UP | FREE | — | — | 1,5L |
| `ALMA MORA MALBEC 750CC` | ALMA MORA | — | — | MALBEC | 750CC |
| `DOVE SH RECON COMPLETA 400ML` | DOVE | — | SH | RECON COMPLETA | 400ML |
| `NESCAFE GOLD 95G` | NESCAFE | GOLD | — | — | 95G |
| `SAN REMO CRACKERS 303GR` | SAN REMO | — | CRACKERS | — | 303GR |
| `COCA COLA ZERO 2.5L` | COCA COLA | ZERO | — | — | 2.5L |
| `COMFORT SEGREDOS 36 500ML` | COMFORT | SEGREDOS | — | 36 | 500ML |

#### Regla práctica para decidir qué incluir

1. **Siempre:** marca + medida (si medida visible)
2. **Si la marca tiene varias líneas visibles en el folder o varias en la base de productos:** agregar línea
3. **Si la línea sola no distingue el producto** (porque la marca usa esa línea para varios tipos): agregar tipo de producto
4. **Si la variante es legible en el envase y es útil:** agregar variante
5. **Si la variante no es legible** (ej: 3 envases de colores distintos sin texto): omitir variante — ver regla "no inventar" en `handling-closed-brand-categories`

**Reglas de formato:**
- Todo en mayúsculas
- Medida y unidad SIN espacio entre ellas (`1,5L`, no `1,5 L`)
- Decimales con coma (`1,5L` no `1.5L`) — aunque hay inconsistencias en el manual (a veces punto)
- La unidad se abrevia: `L`, `ML`, `CC`, `G`, `GR`, `KG`

### Patrón B: Producto genérico de una marca (sin medida, sin variante)

**Estructura:** `[MARCA] [TIPO DE PRODUCTO]`

**Cuándo usarlo:** cuando el folder muestra un banner de marca sin especificar medida ni una variante concreta. Típico de bloques de "marca cerrada" (ver skill `handling-closed-brand-categories` Caso A/B).

**Ejemplos reales:**

| Descripción GDSnet |
| :---- |
| `AMANDA YERBAS` |
| `ARCOR CARAMELOS` |
| `CIF BAÑOS` |
| `CIF COCINA` |
| `COCINERO ACETOS` |
| `STARBUCKS CAPSULAS` |
| `SENSODYNE CREMAS DENTALES` |
| `DOVE DESODORANTES MUJER` |

**Reglas:**
- Todo en mayúsculas
- Sin medida ni unidad
- El "tipo de producto" es una descripción genérica del rubro que la marca representa en este bloque

### Patrón C: "TODOS" / "TODAS" al final

**Estructura:** `[MARCA] [TIPO DE PRODUCTO] TODOS` o `... TODAS`

**Cuándo usarlo:** cuando el folder explícitamente muestra que la promo aplica a todos los productos de esa línea/tipo de la marca. Variante del Patrón B cuando hay énfasis en "todos".

**Ejemplos reales:**

| Descripción GDSnet |
| :---- |
| `ACE DILUIR TODOS` |
| `DOWNY SUAVIZANTES TODOS` |
| `HELLMANNS ADEREZOS TODOS` |
| `OREO TODAS` |
| `KNORR CALDOS TODOS` |
| `KNORR SOPAS TODAS` |
| `BLANCAFLOR PREMEZCLAS TODAS` |

**Reglas:**
- `TODOS` o `TODAS` según concordancia de género con el tipo de producto (masculino/femenino)
- Todo en mayúsculas
- No agregar medida aunque alguna variedad individual pueda tenerla

## Cómo elegir el patrón correcto

Decisión en orden:

1. **¿El folder muestra una medida específica del producto (ej: "x 750 cc", "x 500 g")?**
   - **Sí** → Patrón A (específico con medida)
   - **No** → paso 2

2. **¿El folder muestra el texto "Todos", "Todas", "Todos los X" explícito?**
   - **Sí** → Patrón C (con TODOS/TODAS)
   - **No** → Patrón B (genérico)

3. Si hay múltiples envases visibles sin medida y sin "todos" explícito, usar Patrón B con un tipo de producto genérico (ej: "SHAMPOO", "YERBAS", "GALLETAS").

## Diccionario de abreviaciones confirmadas

Las siguientes abreviaciones están evidenciadas en las cargas manuales de GDSnet. Usar cuando la palabra completa aparece en el folder:

### Palabras comunes

| Palabra completa | Abreviación |
| :---- | :---- |
| Shampoo | `SH` |
| Crema | `CR` |
| Líquido | `LIQ` |
| Jabón | `JAB` |
| Desinfectante | `DESINF` |
| Desodorante | `DESOD` |
| Antitranspirante | `ANTITRANS` |
| Aceite | `AC` o `ACT` (ver contexto) |
| Premezcla | `PREMEZ` |
| Sémola | `SEMOL` |
| Infusión | `INFUS` |

### Packaging y presentación

| Palabra completa | Abreviación |
| :---- | :---- |
| Doypack | `DP` |
| Tetra Brik | `TBK` |
| Polietilén tereftalato (botella plástica) | `PET` |

### Modificadores del producto

| Palabra completa | Abreviación |
| :---- | :---- |
| Limpieza | `LIMP` |
| Activa | `ACT` (cuidado con ambigüedad con "aceite") |
| Reconstitución | `RECON` |
| Tratamiento | `TRAT` |
| Peinar | `PEINAR` (no se abrevia) |
| Clásico / Clásica | `CLAS` |
| Bioactive | `BIO` |

### Expresiones con barra

| Expresión | Abreviación |
| :---- | :---- |
| Sin alcohol | `S/ALCOHOL` |
| Sin azúcar | `S/AZ` |
| Sin sal | `S/SAL` |
| Con dosificador | `C/DOSIF` |
| Con aroma | `C/AROMA` |

### Casos especiales

| Caso | Convención |
| :---- | :---- |
| Múltiples marcas en un bloque | `V/M` (de "varias marcas") |
| Producto con varios formatos | usar Patrón B con el tipo (ej: `PEPSI` si la marca es toda) |

## Criterio general para abreviaciones no listadas

Si el folder tiene una palabra común para la que no hay abreviación en el diccionario, el agente puede abreviar con criterio siempre que:

1. La palabra sea **larga** (más de 6 letras) y haga el SKU innecesariamente largo
2. La abreviación sea **obvia e inequívoca** (ej: "Reforzado" → "REF", "Protección" → "PROT")
3. La abreviación sea consistente con el estilo del diccionario (prefijos de 3-5 letras, sin vocales al final cuando se puede evitar)

Cuando el agente abrevie algo no listado, agregar `LOW_CONFIDENCE` a `review_reasons` del producto para que el revisor humano pueda validar o corregir.

## Reglas de formato generales

Independientemente del patrón:

- **Todo en mayúsculas.** No hay excepciones para nombres propios o marcas registradas.
- **Sin puntuación** salvo la coma decimal en medidas (`1,5L`) y las barras en expresiones `S/AZ`, `C/DOSIF`.
- **Espacios simples** entre componentes. Nunca dobles.
- **Sin acentos** en las descripciones. `CAFÉ` se escribe `CAFE`, `ACEITE PARA FREÍR` se escribe `ACEITE PARA FREIR`.
- **Sin caracteres Unicode especiales.** `Müller` → `MULLER`, `Frías` → `FRIAS`.

## Qué NO hacer

- **No copiar literal** la descripción del folder si tiene mayúsculas/minúsculas mezcladas, puntuación extra, o palabras no abreviadas.
- **No inventar información** que no esté en el folder — si no hay variante visible, no agregarla.
- **No mezclar patrones** — un SKU es A, B o C. No hay híbridos tipo "marca + tipo + TODOS + medida".
- **No traducir** nombres de productos al español si el nombre original es en inglés (ej: "Corn Flakes" no se traduce a "Hojuelas de Maíz").
- **No agregar la cadena al SKU** (ej: no escribir "COTO ALMA MORA MALBEC 750CC" — la cadena es un campo aparte).

## Campos pendientes de definir con el cliente

- **Sufijos `1-2`, `2-2`, `3-3`:** aparecen al final de algunos SKUs (ej: `FERNET BRANCA 750ML 1-2`, `OREO 118G 2-2`, `KNORR GALLINA 6U 2-2`). Se desconoce su significado. Pregunta abierta con David: ¿qué convención usan? ¿Lote, combo, agrupación? Hasta que se confirme, el agente **no** agrega estos sufijos.

## Relación con otros campos

Esta skill afecta solo el campo `descripcion`. Los campos relacionados siguen sus propias reglas:

- **`marca`:** en mayúsculas, sin acentos. Se mantiene separada aunque aparezca al inicio de `descripcion`.
- **`medida` y `u_medida`:** campos separados en el output (ej: `500` y `ML`). La combinación `500ML` aparece al final de `descripcion` cuando aplica Patrón A.
- **`descripcion_literal`:** este campo guarda el texto del folder sin transformar. `descripcion` (este campo) es la versión canónica formateada.
- **`tipo_variedad`:** si el producto tiene variedades visibles, ver `extracting-multiple-products-per-image` para decidir si va 1 registro con `tipo_variedad` o N registros separados.
