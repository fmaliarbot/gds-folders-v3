# Categorías contratadas de GDSnet

Lista de las categorías de productos que GDSnet procesa actualmente por contrato con sus clientes. Esta lista define el alcance operativo del agente: **productos cuya categoría no esté en esta lista no se cargan al sistema de GDSnet**.

Fuente: archivo `CATEGORIAS_FOLDERS.xlsx` enviado por David Feinmann (GDSnet), Abril 2026.

## Cómo usar esta lista

El agente extrae todos los productos visibles en cada página del catálogo (eso sigue siendo responsabilidad de la skill `extracting-products`). El filtrado por categorías contratadas es una decisión de diseño del pipeline: el agente reporta todo, y una capa posterior filtra según las categorías contratadas.

Esto permite que cuando GDSnet contrate categorías nuevas, el output del agente ya tiene los datos capturados y solo hay que expandir el filtro, sin volver a correr el agente.

## Formato de las columnas

- **CATEGORÍAS**: el nombre canónico de la categoría tal como GDSnet lo registra. Se preservan exactamente como están, incluyendo typos (ej: `LIUSTRAMUEBLES`, `PREMEZCALAS`) para garantizar match exacto con la base maestra.
- **INCLUYE**: qué productos entran dentro de esa categoría. `TODAS LAS VARIEDADES` indica scope total; otros valores son enumeraciones específicas.
- **NO INCLUYE**: productos explícitamente excluidos aunque parezcan entrar en la categoría.

## Listado completo

| CATEGORÍAS | INCLUYE | NO INCLUYE |
| :---- | :---- | :---- |
| ACEITES | TODAS LAS VARIEDADES |  |
| ACONDICIONADOR | TODAS LAS VARIEDADES |  |
| ADEREZOS | KETCHUP-MOSTAZAS-SALSA GOLF |  |
| ADEREZOS PARA ENSALADAS | SALSAS, ACETOS, JUGOS DE LIMON | VINAGRE-SALSA DE SOJA |
| AGUAS SABORIZADAS | TODAS LAS VARIEDADES |  |
| ALCOHOL EN GEL | AEROSOL Y GEL |  |
| ALFAJORES | TODAS LAS VARIEDADES |  |
| APERITIVOS C/ALCOHOL | TODAS LAS VARIEDADES |  |
| APERITIVOS S/ALCOHOL | TODAS LAS VARIEDADES |  |
| ARROZ | TODAS LAS VARIEDADES |  |
| ARROZ PREPARADO | TODAS LAS VARIEDADES |  |
| BALSAMOS | CREMAS PEINAR, TRATAMIENTO, SERUM, AMPOLLAS |  |
| BAÑO | GATILLO,REPUESTOS, CREMA,  CANASTAS, BLOQUES, ADHESIVOS, GELES |  |
| CACAO EN POLVO | TODAS LAS VARIEDADES |  |
| CAFÉ | TODAS LAS VARIEDADES |  |
| CALDOS | TODAS LAS VARIEDADES: POLVOS, CUBOS, HORNO, GRANULADOS, SABORIZANTES |  |
| CARAMELOS | CARAMELOS Y CHUPETINES TODAS LAS VARIEDADES |  |
| CERVEZA | TODAS LAS VARIEDADES |  |
| CHAMPAGNE | TODAS LAS VARIEDADES |  |
| CHICLES | TODAS LAS VARIEDADES |  |
| CHOCOLATES | TODAS LAS VARIEDADES | CHOCOLATE PARA TAZA |
| COCINA | PEQUEÑAS SUPERFICIES: GATILLOS, REPUESTOS, CREMOSOS, GELES |  |
| COMIDAS CONGELADAS LISTAS | SOLO PIZZAS CONGELADAS |  |
| CREMAS CORPORALES | TODAS LAS VARIEDADES | SOLARES |
| CREMAS DENTALES | TODAS LAS VARIEDADES |  |
| CREMAS FACIALES | TODAS LAS VARIEDADES, TAMBIEN TOALLAS DESMAQUILLANTES TONICOS, SERUM | SOLARES |
| CUIDADO DE LA ROPA | POLVOS , LIQUIDOS, EN PAN, DILUIR | PRELAVADO Y QUITAMANCHAS. LAVANDINAS PARA ROPA |
| DESODORANTES DE AMBIENTE | SOLO DESINFECTANTES |  |
| DESODORANTES HOMBRE | TODAS LAS VARIEDADES |  |
| DESODORANTES MUJER | TODAS LAS VARIEDADES |  |
| DESODORANTES PEDICOS | SOLO PEDICOS |  |
| DETERGENTES | TODOAS LAS VARIEDADES TAMBIEN INCLUYE PARA MAQUINAS |  |
| FECULAS | TODA LAS VARIEDADES |  |
| FLANES Y POSTRES | SOLO PARA PREPARAR: FLANES, POSTRES, HELADOS, MOUSSE | REFRIGERADOS |
| GALLETAS ARROZ | TODAS LAS VARIEDADES |  |
| GALLETAS BOZCOCHOS | TODAS LAS VARIEDADES |  |
| GALLETAS DULCES | TODAS LAS VARIEDADES | MADALENAS |
| GALLETAS SALADAS | TODAS LAS VARIEDADES | GRISINES |
| GASEOSAS | TODAS LAS VARIEDADES |  |
| GELIFICABLES | GELATINAS PARA PREPARAR | REFRIGERADOS |
| GIN | TODAS LAS VARIEDADES |  |
| HARINAS DE TRIGO | TODAS LAS VARIEDADES |  |
| JABONES DE TOCADOR | TODAS LAS VARIEDADES- LIQUIDOS Y PASTILLAS |  |
| JUGOS EN POLVO | TODAS LAS VARIEDADES |  |
| LAVANDINAS | SOLO EN GEL | REGULARES |
| LIMPIADORES Y MULTIUSOS | PEQUEÑAS SUPERFICIES: GATILLOS, REPUESTOS, CREMOSOS, GELES | PISOS |
| LIUSTRAMUEBLES | TODAS LAS VARIEDADES |  |
| MAYONESAS | TODAS LAS VARIEDADES |  |
| MILANESAS Y REBOZADOS | SOJA-POLLO,MILANESAS  DE VEGETALES Y PESCADOS REBOZADOS |  |
| PASTAS FRESCAS | TODAS LAS VARIEDADES | ELABORACION PROPIA DE LOS SUPERMERCADOS |
| PASTAS PREPARADAS | TODAS LAS VARIEDADES PARA PREPARAR |  |
| PASTAS SECAS | TODAS LAS VARIEDADES |  |
| PASTAS SECAS RELLENAS | TODAS LAS VARIEDADES |  |
| PESCADOS CONGELADOS | TODAS LAS VARIEDADES |  |
| PREMEZCLAS CELIACOS | SALADAS/DULCES PARA PARA PREPARAR |  |
| PREMEZCALAS DULCES | TODAS LAS VARIEDADES PARA PREPARAR |  |
| PREMEZCALS SALADAS | TODAS LAS VARIEDADES PARA PREPARAR |  |
| PURE | TODAS LAS VARIEDADES PARA PREPARAR |  |
| REBOZADORES | REBOZADORS/PAN RALLADO |  |
| RTD | BEBIDAS LISTAS PARA TOMAR TODAS LAS VARIEDADES |  |
| SEMOLA | TODAS LAS VARIEDADES |  |
| SHAMPOO | TODAS LAS VARIEDADES |  |
| SNACKS OTROS | POCHOCLOS PREPARADOS/Y PARA PREPARAR |  |
| SOPAS | TODAS LAS VARIEDADES |  |
| SUAVIZANTES | TODAS LAS VARIEDADES |  |
| TALCOS | SOLO PEDICOS | TRADICIONALES/COMUNES |
| TAPAS DE EMPANADAS | TODAS LAS VARIEDADES |  |
| TAPAS DE TARTA | TODAS LAS VARIEDADES |  |
| TOMATES | SALSAS, PURE, PULPA | TRITURADO, LATAS DE TOMATES PERITA/CUBOS/EXTRACTO |
| TORTILLAS | FAJITAS, TORTILLAS MEJICANAS, MASA PARA TACOS |  |
| VEGETALES CONGELADOS | TODAS LAS VARIEDADES | PAPA- BATATAS |
| VINOS | TODAS LAS VARIEDADES | PATERO |
| VODKA | TODAS LAS VARIEDADES |  |
| YERBA MATE | TODAS LAS VARIEDADES: YERBA MATE/MATE COCIDO |  |

## Categorías con exclusiones (atención especial)

Las siguientes 16 categorías tienen exclusiones explícitas. Al asignar un producto a una de estas categorías, verificar que no caiga en la exclusión:

- **ADEREZOS PARA ENSALADAS**: NO incluye vinagre ni salsa de soja
- **CHOCOLATES**: NO incluye chocolate para taza
- **CREMAS CORPORALES**: NO incluye cremas solares
- **CREMAS FACIALES**: NO incluye cremas solares
- **CUIDADO DE LA ROPA**: NO incluye prelavado, quitamanchas ni lavandinas para ropa
- **FLANES Y POSTRES**: NO incluye refrigerados (solo los que son para preparar)
- **GALLETAS DULCES**: NO incluye madalenas
- **GALLETAS SALADAS**: NO incluye grisines
- **GELIFICABLES**: NO incluye refrigerados (solo gelatinas para preparar)
- **LAVANDINAS**: solo en gel, NO incluye regulares
- **LIMPIADORES Y MULTIUSOS**: NO incluye limpiadores de pisos
- **PASTAS FRESCAS**: NO incluye las de elaboración propia de los supermercados
- **TALCOS**: solo pédicos, NO incluye tradicionales/comunes
- **TOMATES**: NO incluye triturados ni latas de tomates perita/cubos/extracto (solo salsas, puré, pulpa)
- **VEGETALES CONGELADOS**: NO incluye papa ni batatas
- **VINOS**: NO incluye vino Patero

## Notas de mantenimiento

- Esta lista se actualiza cuando GDSnet agrega o quita categorías contratadas.
- Los typos (`LIUSTRAMUEBLES`, `TODOAS`, `PREMEZCALAS`, `PREMEZCALS`) se preservan tal cual para garantizar match exacto contra la base maestra de GDSnet. Si en algún momento GDSnet corrige el origen, actualizar acá también.
- Fuente de verdad: archivo `CATEGORIAS_FOLDERS.xlsx` en el repo (si se agrega como binario) o solicitar al equipo de GDSnet la versión actualizada.
