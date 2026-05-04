# Categorías Contratadas — GDSnet

Lista canónica de las **74 categorías de productos** que GDSnet procesa actualmente por contrato con sus clientes. Esta lista define el alcance operativo del agente.

**Fuente:** archivo `CATEGORIAS_FOLDERS.xlsx` enviado por David Feinmann (GDSnet), abril 2026.

## Reglas de uso

- El campo `categoria` de cualquier producto extraído **debe** ser literalmente uno de los valores de la columna `CATEGORIA` de esta tabla. Sin excepciones.
- Respetar **exactamente** las mayúsculas, acentos y typos del archivo. Por ejemplo `LIUSTRAMUEBLES` (con typo), `PREMEZCALAS DULCES` (con typo), `CAFÉ` (con tilde).
- La columna `INCLUYE` describe qué tipo de productos caen en la categoría.
- La columna `NO INCLUYE` describe productos que parecen pertenecer pero están explícitamente excluidos.
- Si un producto no matchea claramente con ninguna categoría, dejar `categoria: null` y agregar `CATEGORY_NOT_DEFINED` a `review_reasons`.
- Si un producto cae en una exclusión explícita (columna `NO INCLUYE`), también va a `null` + flag.

## Tabla canónica

| # | CATEGORIA | INCLUYE | NO INCLUYE |
|---|---|---|---|
| 1 | `ACEITES` | TODAS LAS VARIEDADES |  |
| 2 | `ACONDICIONADOR` | TODAS LAS VARIEDADES |  |
| 3 | `ADEREZOS` | KETCHUP-MOSTAZAS-SALSA GOLF |  |
| 4 | `ADEREZOS PARA ENSALADAS` | SALSAS, ACETOS, JUGOS DE LIMON | VINAGRE-SALSA DE SOJA |
| 5 | `AGUAS SABORIZADAS` | TODAS LAS VARIEDADES |  |
| 6 | `ALCOHOL EN GEL` | AEROSOL Y GEL |  |
| 7 | `ALFAJORES` | TODAS LAS VARIEDADES |  |
| 8 | `APERITIVOS C/ALCOHOL` | TODAS LAS VARIEDADES |  |
| 9 | `APERITIVOS S/ALCOHOL` | TODAS LAS VARIEDADES |  |
| 10 | `ARROZ` | TODAS LAS VARIEDADES |  |
| 11 | `ARROZ PREPARADO` | TODAS LAS VARIEDADES |  |
| 12 | `BALSAMOS` | CREMAS PEINAR, TRATAMIENTO, SERUM, AMPOLLAS |  |
| 13 | `BAÑO` | GATILLO,REPUESTOS, CREMA,  CANASTAS, BLOQUES, ADHESIVOS, GELES |  |
| 14 | `CACAO EN POLVO` | TODAS LAS VARIEDADES |  |
| 15 | `CAFÉ` | TODAS LAS VARIEDADES |  |
| 16 | `CALDOS` | TODAS LAS VARIEDADES: POLVOS, CUBOS, HORNO, GRANULADOS, SABORIZANTES |  |
| 17 | `CARAMELOS` | CARAMELOS Y CHUPETINES TODAS LAS VARIEDADES |  |
| 18 | `CERVEZA` | TODAS LAS VARIEDADES |  |
| 19 | `CHAMPAGNE` | TODAS LAS VARIEDADES |  |
| 20 | `CHICLES` | TODAS LAS VARIEDADES |  |
| 21 | `CHOCOLATES` | TODAS LAS VARIEDADES | CHOCOLATE PARA TAZA |
| 22 | `COCINA` | PEQUEÑAS SUPERFICIES: GATILLOS, REPUESTOS, CREMOSOS, GELES |  |
| 23 | `COMIDAS CONGELADAS LISTAS` | SOLO PIZZAS CONGELADAS |  |
| 24 | `CREMAS CORPORALES` | TODAS LAS VARIEDADES | SOLARES |
| 25 | `CREMAS DENTALES` | TODAS LAS VARIEDADES |  |
| 26 | `CREMAS FACIALES` | TODAS LAS VARIEDADES, TAMBIEN TOALLAS DESMAQUILLANTES TONICOS, SERUM | SOLARES |
| 27 | `CUIDADO DE LA ROPA` | POLVOS , LIQUIDOS, EN PAN, DILUIR | PRELAVADO Y QUITAMANCHAS. LAVANDINAS PARA ROPA |
| 28 | `DESODORANTES DE AMBIENTE` | SOLO DESINFECTANTES |  |
| 29 | `DESODORANTES HOMBRE` | TODAS LAS VARIEDADES |  |
| 30 | `DESODORANTES MUJER` | TODAS LAS VARIEDADES |  |
| 31 | `DESODORANTES PEDICOS` | SOLO PEDICOS |  |
| 32 | `DETERGENTES` | TODOAS LAS VARIEDADES TAMBIEN INCLUYE PARA MAQUINAS |  |
| 33 | `FECULAS` | TODA LAS VARIEDADES |  |
| 34 | `FLANES Y POSTRES` | SOLO PARA PREPARAR: FLANES, POSTRES, HELADOS, MOUSSE | REFRIGERADOS |
| 35 | `GALLETAS ARROZ` | TODAS LAS VARIEDADES |  |
| 36 | `GALLETAS BOZCOCHOS` | TODAS LAS VARIEDADES |  |
| 37 | `GALLETAS DULCES` | TODAS LAS VARIEDADES | MADALENAS |
| 38 | `GALLETAS SALADAS` | TODAS LAS VARIEDADES | GRISINES |
| 39 | `GASEOSAS` | TODAS LAS VARIEDADES |  |
| 40 | `GELIFICABLES` | GELATINAS PARA PREPARAR | REFRIGERADOS |
| 41 | `GIN` | TODAS LAS VARIEDADES |  |
| 42 | `HARINAS DE TRIGO` | TODAS LAS VARIEDADES |  |
| 43 | `JABONES DE TOCADOR` | TODAS LAS VARIEDADES- LIQUIDOS Y PASTILLAS |  |
| 44 | `JUGOS EN POLVO` | TODAS LAS VARIEDADES |  |
| 45 | `LAVANDINAS` | SOLO EN GEL | REGULARES |
| 46 | `LIMPIADORES Y MULTIUSOS` | PEQUEÑAS SUPERFICIES: GATILLOS, REPUESTOS, CREMOSOS, GELES | PISOS |
| 47 | `LIUSTRAMUEBLES` | TODAS LAS VARIEDADES |  |
| 48 | `MAYONESAS` | TODAS LAS VARIEDADES |  |
| 49 | `MILANESAS Y REBOZADOS` | SOJA-POLLO,MILANESAS  DE VEGETALES Y PESCADOS REBOZADOS |  |
| 50 | `PASTAS FRESCAS` | TODAS LAS VARIEDADES | ELABORACION PROPIA DE LOS SUPERMERCADOS |
| 51 | `PASTAS PREPARADAS` | TODAS LAS VARIEDADES PARA PREPARAR |  |
| 52 | `PASTAS SECAS ` | TODAS LAS VARIEDADES |  |
| 53 | `PASTAS SECAS RELLENAS` | TODAS LAS VARIEDADES |  |
| 54 | `PESCADOS CONGELADOS` | TODAS LAS VARIEDADES |  |
| 55 | `PREMEZCLAS CELIACOS` | SALADAS/DULCES PARA PARA PREPARAR |  |
| 56 | `PREMEZCALAS DULCES` | TODAS LAS VARIEDADES PARA PREPARAR |  |
| 57 | `PREMEZCALS SALADAS` | TODAS LAS VARIEDADES PARA PREPARAR |  |
| 58 | `PURE` | TODAS LAS VARIEDADES PARA PREPARAR |  |
| 59 | `REBOZADORES` | REBOZADORS/PAN RALLADO |  |
| 60 | `RTD` | BEBIDAS LISTAS PARA TOMAR TODAS LAS VARIEDADES |  |
| 61 | `SEMOLA` | TODAS LAS VARIEDADES |  |
| 62 | `SHAMPOO` | TODAS LAS VARIEDADES |  |
| 63 | `SNACKS OTROS` | POCHOCLOS PREPARADOS/Y PARA PREPARAR |  |
| 64 | `SOPAS` | TODAS LAS VARIEDADES |  |
| 65 | `SUAVIZANTES ` | TODAS LAS VARIEDADES |  |
| 66 | `TALCOS` | SOLO PEDICOS | TRADICIONALES/COMUNES |
| 67 | `TAPAS DE EMPANADAS` | TODAS LAS VARIEDADES |  |
| 68 | `TAPAS DE TARTA` | TODAS LAS VARIEDADES |  |
| 69 | `TOMATES` | SALSAS, PURE, PULPA | TRITURADO, LATAS DE TOMATES PERITA/CUBOS/EXTRACTO |
| 70 | `TORTILLAS` | FAJITAS, TORTILLAS MEJICANAS, MASA PARA TACOS |  |
| 71 | `VEGETALES CONGELADOS` | TODAS LAS VARIEDADES | PAPA- BATATAS |
| 72 | `VINOS` | TODAS LAS VARIEDADES | PATERO |
| 73 | `VODKA` | TODAS LAS VARIEDADES |  |
| 74 | `YERBA MATE` | TODAS LAS VARIEDADES: YERBA MATE/MATE COCIDO |  |

## Notas importantes

### Typos preservados intencionalmente

Algunos nombres tienen typos en el archivo original. **No corregirlos** — la base maestra de GDSnet usa estos valores literales:

- `LIUSTRAMUEBLES` (debería ser LUSTRAMUEBLES)
- `PREMEZCALAS DULCES` (debería ser PREMEZCLAS)
- `PREMEZCALS SALADAS` (debería ser PREMEZCLAS)
- `GALLETAS BOZCOCHOS` (debería ser BIZCOCHOS)
- `TODOAS LAS VARIEDADES` (en columna INCLUYE de DETERGENTES)

### Categorías que no están en la lista

Categorías que **no figuran** en este archivo y que el agente puede ver ocasionalmente en folders:

- `BARRAS DE CEREAL` — no contratada
- `LECHE LARGA VIDA` — no contratada
- `AGUA MINERAL` — no contratada (existe `AGUAS SABORIZADAS` solamente)
- `CHOCOLATE PARA TAZA` — explícitamente excluido de CHOCOLATES
- `VINO PATERO` — explícitamente excluido de VINOS
- `ENCURTIDOS`, `ESPECIAS` — no contratadas
- `LECHE EN POLVO`, `CACAO EN POLVO` (cuidado: existe `CACAO EN POLVO` como categoría propia)

Cuando aparezcan productos de categorías no contratadas, el agente puede:
- Extraer el producto si la marca y otros datos son visibles, dejar `categoria: null`, agregar `CATEGORY_NOT_DEFINED` a `review_reasons`.
- O omitir el producto si claramente cae fuera del alcance contratado. Decisión de procesamiento downstream.

### Macro-categorías de folder

Algunos folders usan **macro-categorías** descriptivas en sus footers promocionales (ej: "EN GOLOSINAS", "EN VINOS FINOS, CHAMPAÑAS Y ESPUMANTES", "EN SHAMPOO, ACONDICIONADOR Y TRATAMIENTOS CAPILARES").

Estas macro-categorías **no son** categorías canónicas. El agente debe matchear cada macro contra las 74 categorías de esta tabla y generar un registro por cada match razonable. Ver `handling-closed-brand-categories` para la lógica.