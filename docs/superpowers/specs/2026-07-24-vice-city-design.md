# Vice City — diseño del tema

Fecha: 2026-07-24 · Estado: **implementado** (el tema vive en `main`; ver la bitacora del rediseno)
Rama: `design/redesign-cinematic-themes`

## Contexto

El portfolio tiene un sistema de temas "rice" que sortea uno al azar en cada visita
(Vice City, Hyprland, Caelestia). Hyprland está **aprobado y no se toca**. Este spec
cubre solo **Vice City**, que se rechazó en tres iteraciones:

1. Degradado plano con sol → *"muy meh, no hay visual storytelling"*.
2. Shader synthwave (skyline en bandas, sol cortado, reflejo) → *"no me gusta"*.
3. Foto única teñida con progresión horaria → *"podemos hacerlo mejor"*.

Diagnóstico: un shader procedural **siempre se ve dibujado**. El look de GTA VI es
fotográfico. La materia prima estaba mal elegida, no la ejecución.

Resultado buscado: un hero cinematográfico real, que se sienta rodado y no ilustrado,
sin romper el suelo de conversión (nombre, rol y contacto legibles al instante).

## Decisiones (no re-litigar)

| Decisión | Elección |
|---|---|
| Materia prima del fondo | **Fotografía y vídeo reales**, no procedural |
| Hero | **Vídeo en bucle autónomo** (opción A), no scrubbing |
| Secciones interiores | Fotografía atenuada (~30% de brillo) como textura |
| Acento | Ámbar `#ffd166` |
| Texto | Crema cálido `#fff4e8` (no blanco frío) |
| Display | Passion One 900, mayúsculas |
| Subtítulo | Manrope **200** a 20–27 px — línea de cartel, no párrafo |
| Cuerpo | Manrope 400, 15 px, interlineado 1,7 |
| Etiquetas | Manrope 700 en mayúsculas con tracking — **sin mono** |
| Contenedor del stack | **Créditos de película** interactivos, sin cajas |
| Gesto de scroll | Se conserva el zoom del nombre tipo GTA |
| Motion | **Un gesto propio por sección**, todos en lenguaje de cine |
| Clip del hero | Mixkit `4999` — atardecer sobre la bahía desde el aire (3,1 MB en 720p) |
| Galería de obra | Tira **horizontal arrastrable** con capturas reales |

### Por qué bucle y no scrubbing

Se prototiparon ambos. El scrubbing mejorado (deriva en reposo, suavizado, metraje
direccional, puerta de carga) quedó defendible, pero pierde en lo que importa aquí:

- Exige **descargar el vídeo entero** antes de responder (~2,5–4 MB frente a ~1,2 MB).
- Decodifica en cada búsqueda: caro en CPU y batería, con tirones en móvil medio.
- **Falla de forma visible**: promete una interacción que no responde.
- **Compite con el zoom del nombre por el mismo scroll.** No caben los dos.

Con bucle, el scroll queda libre para que el protagonista sea el nombre — que es
además lo que hace la web real de GTA VI.

### Por qué no se incrusta Pricedown

GTA VI usa **Pricedown Black** + **GTAArtDeco** (custom de Rockstar, no licenciable).
La licencia gratuita de Typodermic para Pricedown dice literalmente:

> Allowed: `web page (not embedded)` · **Not allowed: `web page (embedded)`**

Incrustarla como webfont violaría su licencia. **Passion One 900** es la alternativa
libre más cercana (Google Fonts). Si en el futuro se compra una licencia web de
Typodermic, basta cambiar el token `--font-display`.

## Arquitectura

### Principio: un solo DOM semántico, presentación por tema

Los créditos no son un cambio de color: son otra estructura. Para no triplicar el JS,
el stack se renderiza **siempre** con la misma información (`rol`, `nombre`, `nota` —
datos que ya existen en `src/data/content.ts`), y cada tema decide con CSS cómo se ve:

- **Vice** → fila de créditos con las tres partes visibles.
- **Hyprland** → píldora: oculta la nota (mantiene su aspecto actual).
- **Caelestia** → contenedor tonal redondeado.

Se conserva así la propiedad clave del motor: cambiar `data-theme` re-skinea todo.
Solo se cae a variantes en JS cuando el CSS no dé.

### Fondo

`Theme.mountBackground(container) -> { destroy() }` ya soporta esto sin cambios de
interfaz: Vice montará capas de `<video>` + `<img>` en lugar de un canvas WebGL.

Capas del hero, de abajo arriba:
1. `<img>` póster (la foto), visible al instante.
2. `<video autoplay muted loop playsinline>`, que entra fundido al estar listo.
3. Gradación Vice (`soft-light`) + capa de color.
4. Scrim (degradado oscuro) — **garantiza contraste pase lo que pase en la imagen**.
5. Grano animado (`steps`), textura de película proyectada.

**Degradación sin culpa:** en móvil, con `save-data` o con `prefers-reduced-motion`,
el vídeo no se carga y se queda el póster. El vídeo es un lujo para quien puede.

### Tokens nuevos

`--font-lead` y `--lead-weight` (el subtítulo tiene familia y peso propios por tema),
además de los ya existentes `--display-weight`, `--display-transform`, `--display-tracking`.

### Assets

- **Foto base:** Unsplash `aT2JKn38cqw` (ciudad al atardecer con palmeras). Licencia
  libre, uso comercial, sin atribución obligatoria. Criterio de elección: **la zona
  donde va el nombre queda oscura**.
- **Vídeo del hero:** Mixkit `4999` — atardecer sobre la bahía desde el aire. Licencia
  libre, sin atribución. 3,1 MB en 720p sin optimizar; es el más ligero de los
  candidatos probados.
- **Capturas de proyecto:** las aporta el usuario (confirmado). Sustituyen a las
  maquetas de interfaz del prototipo sin cambiar el componente de galería. Pendiente
  de resolver si las del proyecto de Telefónica pueden publicarse tal cual o requieren
  ofuscar datos.
- **Iconos de tecnología:** `simple-icons`, ya instalado. Se importan como SVG crudo
  (`?raw`) igual que hoy en `src/utils/icons.ts`.
- **Optimización obligatoria:** recortar a 6–8 s con bucle limpio, re-codificar a
  WebM/AV1 con MP4 de respaldo a 1280×720 y bitrate bajo. El grano y la gradación van
  encima, así que aguanta más compresión de lo normal. Objetivo: **≈1,2 MB**.
  Sin optimizar, los originales pesan 40–89 MB (medido); es inaceptable.
- Fotos a WebP con tamaños responsive y `preload` del póster del hero.

## Sistema de motion: un gesto por sección

El fallo detectado en la primera versión del spec: todas las secciones usaban las
mismas recetas genéricas (`fade-up`, `stagger`, `chars`). Cambiaba el easing según el
tema, pero **el gesto era idéntico en todas partes**, y eso aplana el conjunto.

Cada sección tiene ahora su propio gesto, todos en lenguaje de cine:

| Sección | Gesto | Referencia |
|---|---|---|
| Hero | El nombre se monta letra a letra tras su máscara; al bajar, crece y te atraviesa | Título de apertura |
| Sobre mí | La ficha entra desde la izquierda; las líneas suben una a una desde su máscara | Subtitulado |
| Obra | El ordinal cae de golpe, el título aterriza seco, el texto se descubre con máscara que barre | Cartela de título |
| Stack | La lista rueda al entrar y **se asienta** para poder usarse | Créditos finales |
| Contacto | Fundido a negro; solo queda encendido el email | Fade out |

**Detalle crítico del hero:** el texto de acompañamiento (rol, frase, esquinas) debe
desvanecerse **antes** de que el nombre empiece a crecer. Si todo se arrastra a la vez,
el gesto se lee roto — fue el defecto que hubo que corregir en el prototipo.

**Detalle crítico de los créditos:** ruedan al entrar, pero **se detienen**. Un rodillo
en movimiento perpetuo sería imposible de usar, y la sección es interactiva.

### Recursos globales

- **Barras de letterbox**: entran solo durante las secciones de obra y se retiran al
  salir. Dicen "esto es la película" sin una palabra.
- **Barra de orientación** fija arriba: nombre a la izquierda, `03 / 06 · Cartela` a la
  derecha. El visitante nunca se pierde en un recorrido largo.
- **Corte vs. fundido**: corte seco entre proyectos, fundido entre el resto.

### Implicación de arquitectura

`utils/reveal.ts` aplica recetas por atributo (`data-reveal="fade-up"`). Sirve para
gestos genéricos, **no para coreografías por sección**. Hay que pasar a una
**coreografía por sección registrada por el tema activo**: más código GSAP, pero es
donde está el valor. Los temas sin coreografía propia siguen con las recetas genéricas.

## Estructura y composición por sección (Vice)

Cada sección se compone distinto. Antes todas eran "texto a la izquierda, centrado
vertical", y esa monotonía aplanaba el recorrido tanto como el motion repetido.

| Sección | Fondo | Composición |
|---|---|---|
| Hero | Vídeo en bucle | Centrado. Nombre grande y los datos en las **esquinas inferiores** (ubicación izq., email der.), como metadatos de un plano |
| Sobre mí | Foto atenuada | **Asimétrico**: ficha de reparto a la izquierda (avatar, estado de disponibilidad, datos) y a la derecha frase de entrada + cifras + trayectoria |
| Obra ×4 | Foto atenuada | Ordinal gigante arriba der., título, **fila de metadatos** (rol · periodo · stack · estado), problema/solución, y **galería horizontal** |
| Stack | Foto atenuada | **Dos columnas**: lista de créditos a la izquierda, panel de detalle a la derecha |
| Contacto | Foto a plena luz | Centrado, email grande, datos en las esquinas |

Solo hero y contacto van a plena luz. Si todas las secciones fueran imagen brillante,
se rompen la legibilidad del texto largo y la fatiga visual al scrollear.

### Sobre mí — contenido

Ficha: avatar de GitHub, nombre, **indicador de disponibilidad con pulso** ("Abierto a
oportunidades" — la señal más útil para una reclutadora), y datos duros (rol, base,
ahora, estudia).

Derecha: frase de entrada en Manrope 200, una línea sobre los repos privados, una
**fila de cifras** (`2021` desde · `9.º` semestre · `4` proyectos · `1` en producción)
y dos columnas de trayectoria y foco.

**No** llevar aquí una fila de tecnologías: duplica la sección de créditos. Cada
sección debe decir algo distinto.

### Obra — galería horizontal

Tira de capturas **arrastrable con el ratón** (`pointerdown`/`pointermove`, no solo
trackpad), con `scroll-snap` centrado, barra de avance y realce al pasar el cursor.
Cada captura lleva **cromo de ventana** (semáforo + título) para que se lea como
pantalla real. Anchos variables para que el conjunto se lea como collage.

### Stack — créditos interactivos

Lista a la izquierda (`rol` + `nombre`); al pasar el cursor o pulsar, el **panel
derecho** muestra el **icono real de la tecnología** (de `simple-icons`, ya instalado
en el proyecto), su rol y para qué se usa. El panel nunca queda vacío: arranca con el
primer elemento seleccionado.

## Alcance

**Dentro:** el tema Vice City completo.

**Fuera (diferido, no implementar ahora):**
- Metáfora estructural por tema (Hyprland como gestor de ventanas en mosaico,
  Caelestia como superficies Material You). **Aprobado como concepto**, se hará
  tema a tema después de Vice.
- Parallax 2.5D sobre las fotos.
- Secuencia de 4 fotos cruzándose por sección.
- Progresión horaria del color al scroll (dorada → noche). Gustó como idea; la maqueta
  no convenció. Reevaluar sobre el sitio real, donde hay mucho más recorrido de scroll.
- Segundo vídeo nocturno en secciones interiores.

**No se toca:** Hyprland (aprobado por el usuario).

## Verificación

1. `npm run build` (tsc + vite) sin errores y `npm run lint` limpio. Requiere **Node 22**
   (`.nvmrc`); con Node 18 el build de Vite 8 falla.
2. Screenshots con Playwright (`--use-gl=swiftshader`) en 1440×900 y 390×844 para
   `?theme=vice`, y de control para `?theme=hyprland` (no debe regresar).
3. Confirmar: vídeo reproduciéndose, póster visible antes de que cargue, nombre + rol +
   contacto legibles en el primer viewport, cero errores de consola.
4. Emular `prefers-reduced-motion: reduce` → sin vídeo, sin animación, sin letterbox,
   sin rodillo de créditos. La galería sigue siendo navegable y el panel de créditos
   sigue respondiendo: **son contenido, no decoración**.
5. Emular `save-data` y viewport móvil → no se descarga el vídeo.
6. Interacción: arrastrar la galería con ratón y con dedo; recorrer los créditos con
   `Tab` y confirmar que el panel cambia (accesible por teclado, no solo por hover).
7. Medir el peso real del vídeo servido; si supera ~1,5 MB, volver a codificar.
8. Anti-mock: `grep -rE "lorem|placeholder|mockData" src/` → vacío. Confirmar además
   que no queda ninguna maqueta de interfaz del prototipo en la galería.

## Riesgos

- **Peso del vídeo.** Es el riesgo principal. Mitigado por recorte, re-codificación y
  degradación en móvil. Si no se baja de ~1,5 MB, el hero se queda en foto.
- **Legibilidad sobre imagen variable.** Mitigada por el scrim, que es obligatorio.
- **Licencias.** Solo Unsplash y Mixkit (libres, comerciales, sin atribución).
  Pricedown queda descartada por licencia; ver arriba.
- **Coste de la metáfora por tema.** Multiplica el trabajo por tres. Por eso se difiere
  y se hace tema a tema.
