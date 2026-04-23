# Publicadores y links de folders

Listado de los publicadores (cadenas, mayoristas, farmacias, diarios) cuyos catálogos promocionales GDSnet procesa o planea procesar.

Este archivo documenta el **alcance operativo** del agente de extracción de folders. No es una skill (no altera el comportamiento del agente por página procesada). Es referencia para:

- Entender el scope del proyecto
- Planificar qué skills de cadena hay que crear (skills específicas en `skills/chains/`)
- Trazar la relación entre catálogo procesado y su fuente de descarga

Fuente: archivo `PUBLICADORES__Y_LINKS.xlsx` enviado por David Feinmann (GDSnet), Abril 2026.

## Próximos publicadores a procesar

Los siguientes publicadores están marcados como prioritarios para la próxima ronda de extracción (venían resaltados en amarillo en el Excel original):

- **DIARCO** (MAYORISTA) — https://www.diarco.com.ar/
- **MAXICONSUMO** (MAYORISTA) — https://maxiconsumo.com/
- **YAGUAR** (MAYORISTA) — https://yaguar.com.ar/
- **DIARIO CLARIN** (SUPERMERCADO/MAYORISTA) — https://www.kiosco.clarin.com/   Usuario Jbenites@gdsnet.com CLAVE gds569
- **BECERRA** (SUPERMERCADO) — https://www.supermercadobecerra.com.ar/  Y FLAYERS POR FACEBOOK
- **COTO** (SUPERMERCADO) — https://www.coto.com.ar/
- **JUMBO** (SUPERMERCADO) — https://www.jumbo.com.ar/

## Listado completo por canal

### MAYORISTA

| Nombre | Tipo | Link / Medio |
| :---- | :---- | :---- |
| **DIARCO** 🎯 | CADENA | https://www.diarco.com.ar/ |
| **MAKRO** | CADENA | https://makro.com.ar/ |
| **MAXICONSUMO** 🎯 | CADENA | https://maxiconsumo.com/ |
| **NINI** | CADENA | https://www.nini.com.ar/ |
| **VITAL** | CADENA | https://www.vital.com.ar/ |
| **YAGUAR** 🎯 | CADENA | https://yaguar.com.ar/ |
| **GRAN TORNADO** | CADENA | https://grantornado.com.ar/ |
| **CARREFOUR MAXI** | CADENA | https://www.carrefour.com.ar/ |
| **CAPO** | CADENA | PUBICA POR FACEBOOK |
| **TADICOR** | CADENA | https://www.tadicormendoza.com/ |

### SUPERMERCADO

| Nombre | Tipo | Link / Medio |
| :---- | :---- | :---- |
| **ATOMO** | CADENA | EL FOLDER LO PUBLICA POR FACEBOOK |
| **BECERRA** 🎯 | CADENA | https://www.supermercadobecerra.com.ar/  Y FLAYERS POR FACEBOOK |
| **BUENOS DIAS** | CADENA | https://novedades.superbuenosdias.com/ |
| **CARACOL** | CADENA | https://www.supercaracol.com.ar/    Y FLAYERS POR FACEBOOK |
| **CARREFOUR HIPER MARKET Y EXPRESS** | CADENA | https://www.carrefour.com.ar/ |
| **CHANGO MAS** | CADENA | https://www.masonline.com.ar/ |
| **COMODIN** | CADENA | https://www.comodinencasa.com.ar/ |
| **COOPERATIVA** | CADENA | https://www.cooperativaobrera.coop/ |
| **MARIANO MAX** | CADENA | https://www.marianomax.com.ar/  Y FLAYERS POR FACEBOOK |
| **DIARCO BARRIO** | CADENA | https://www.diarco.com.ar/ |
| **LA GALLEGA** | CADENA | https://www.lagallega.com.ar/ |
| **LIBERTAD** | CADENA | https://www.hiperlibertad.com.ar/ |
| **TOLEDO** | CADENA | publica por historias de redes sociales  facebook |
| **CORDIEZ** | CADENA | https://www.cordiez.com.ar/ |
| **COTO** 🎯 | CADENA | https://www.coto.com.ar/ |
| **DIA** | CADENA | https://diaonline.supermercadosdia.com.ar/ |
| **DINOSAURIO** | CADENA | https://www.dinoonline.com.ar/ |
| **DISCO** | CADENA | https://www.disco.com.ar/ |
| **JUMBO** 🎯 | CADENA | https://www.jumbo.com.ar/ |
| **LA ANONIMA** | CADENA | https://www.laanonima.com.ar/ |
| **SUPER IMPERIO** | CADENA | https://www.supertop.com.ar/  Y FLAYERS POR FACEBOOK |
| **VEA** | CADENA | https://www.vea.com.ar/      https://supermercadosvea.com.ar/ |

### FARMACIA Y PERFUMERIA

| Nombre | Tipo | Link / Medio |
| :---- | :---- | :---- |
| **PIGMENTO** | CADENA | https://promocionespigmento.com.ar/ |
| **FARMACITY** | CADENA | https://www.farmacity.com/ |
| **FARMAR** | CADENA | https://www.farmar.com.ar/ |
| **SOY TU FARMACIA** | CADENA | solo folleto físico |
| **SIMPLICITY** | CADENA | https://www.simplicity.com.ar/ |
| **CENTRAL OESTE** | CADENA | https://www.centraloeste.com.ar/ |

### SUPERMERCADO/MAYORISTA

| Nombre | Tipo | Link / Medio |
| :---- | :---- | :---- |
| **DIARIO CLARIN** 🎯 | DIARIO | https://www.kiosco.clarin.com/   Usuario Jbenites@gdsnet.com CLAVE gds569 |
| **DIARIO LA NACION** | DIARIO | https://edicionimpresa.lanacion.com.ar/   Usuario Jbenites@gdsnet.com CLAVE gdsnet01 |


## Observaciones importantes

### Publicadores sin web

Algunos publicadores no tienen sitio web público y publican sus promociones por otros canales:

- **CAPO** (mayorista): publica solo por Facebook
- **ATOMO**: folder publicado por Facebook
- **TOLEDO**: publica por historias de redes sociales (Facebook)
- **SOY TU FARMACIA**: solo folleto físico
- **BECERRA, CARACOL, MARIANO MAX, SUPER IMPERIO**: tienen web + flyers por Facebook

Para estos casos el pipeline de descarga de folders tiene que contemplar canales no-web (scraping de redes sociales, recepción de archivos físicos, etc.). No afecta al agente de extracción en sí, que sigue procesando imágenes.

### Diarios como publicadores agregados

Los diarios (Clarín y La Nación) publican ediciones digitales que incluyen folders promocionales de múltiples cadenas. Procesar un diario puede cubrir varios publicadores en una sola descarga. Las credenciales de acceso están en el Excel original; se manejan por el equipo de GDSnet, no se incluyen en este repo por seguridad.

### Canales en el campo CANAL

Los cuatro valores usados en el archivo son:

- `MAYORISTA`: cadenas mayoristas
- `SUPERMERCADO`: cadenas de supermercados retail
- `FARMACIA Y PERFUMERIA`: cadenas de farmacias y perfumería
- `SUPERMERCADO/MAYORISTA`: agregadores (diarios) que cubren ambos canales

## Cobertura actual del agente

De los 40 publicadores del listado, el agente tiene una skill específica (`skills/chains/<cadena>/`) solo para **COTO** por ahora. El resto se procesa con las skills `core` sin ajustes por cadena.

A medida que se procesen catálogos de más publicadores, se irán creando las skills de cadena correspondientes cuando se detecten patrones únicos que requieran tratamiento específico (nombres canónicos de tarjetas de fidelidad, convenciones de layout, etc.).

## Notas de mantenimiento

- Este archivo refleja el estado al mes de Abril 2026.
- Cuando GDSnet agregue/elimine publicadores, actualizar esta lista y marcar los nuevos "próximos a bajar" con 🎯.
- El archivo original (`PUBLICADORES__Y_LINKS.xlsx`) lo mantiene el equipo de GDSnet; pedir la versión actualizada cuando corresponda.
