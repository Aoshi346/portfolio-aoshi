# Ascua — Hyprland deja de ser una piel de color y pasa a ser luz con canto

Estado: en ejecucion
Plan: `docs/superpowers/plans/2026-08-05-hyprland-ascua.md`
Fecha: 2026-08-05
Alcance: solo el tema Hyprland — tokens, tipografía, dispositivos de escena, fondo,
navegación y coreografía propia. **Vice no se toca** (cerrado el 2026-08-05 en `0aee0af`).
**Caelestia no se toca**: se decoplan de él los selectores que hoy comparte con Hyprland,
dejando su render byte a byte idéntico. `shaderBackground.ts` es compartido y no se modifica.

## Por qué

Hyprland no es un tema a medio hacer: es un esqueleto. Medido antes de empezar:

- `src/themes/themes.css:1084-1107` define **12 tokens**, frente a los 31 de Vice. No tiene
  escala tipográfica propia — `--t-1..--t-10` sólo existe en Vice, y `style.css` compensa con
  literales en `rem` "medidos en Hyprland/Caelestia" repartidos por unos 19 sitios.
- `--font-display` y `--font-body` son **la misma fuente** (Space Grotesk): no hay pareja
  tipográfica ni jerarquía de familia.
- No tiene coreografía, ni cursor, ni carril de scroll, ni cortinilla. `src/main.ts` lo lleva
  por el camino genérico en todos los casos.
- Su única CSS propia son 43 líneas de píldoras de créditos **compartidas con Caelestia**.
- `--nav-dim: 55%` está copiado de Vice. Una opacidad se calibra contra un scrim concreto; no
  se hereda.

Y su paleta actual —`#05070a` con cian `#33ccff` y verde ácido `#00ff99`, Space Grotesk,
monoespaciada— es el resultado por defecto de "portfolio de desarrollador oscuro". El tema no
falla por estar poco pulido: **falla porque es la respuesta de plantilla.**

## Qué se construye

### La tesis

Vice y Hyprland comparten esqueleto editorial y se oponen en material. Vice es **tinta
impresa**: opaca, cálida, mate, táctil, versal condensada sobre trama de semitono. Hyprland es
**luz con canto**: emisiva, de bordes duros, negro neutro, caja baja ancha.

El error que costó tres iteraciones y queda escrito para no repetirlo: las tres primeras
propuestas resolvían **atmósfera** (degradados, cristal, manchas desenfocadas) en vez de
**dispositivos**. Vice se recuerda por objetos con forma —un carril horizontal, barras a
sangre con rótulos girados, un cartel de reparto, el cajetín de cine—, no por su fondo. Un
degradado bonito con texto encima no es un dispositivo por muy bien ejecutado que esté el
detalle. La dirección aprobada tiene **radio 0 en todo menos la navegación**.

### Paleta — Ascua

| Token | Valor | Trabajo |
|---|---|---|
| `--void` | `#0b0404` | El campo. Negro con sesgo rojo, no negro puro. |
| `--l1` | `#ff5a34` | Luz primaria, naranja de brasa. |
| `--l2` | `#e01d3c` | Luz secundaria, carmesí. |
| `--l3` | `#ffa03c` | Tercera luz, ámbar de rescoldo. Con cuentagotas. |
| `--text` | `#ffeae6` | Texto. |
| `--haze` | `#b18c86` | Secundario y rótulos. |
| `--rule` | `#3d1c1c` | Filetes. El tema se construye sobre filetes de 1px. |
| `--catch` | `#ffd9cc` | El tono que recoge el blanco del display. |

Elegida entre tres tonalidades montadas y vistas en el companion (Sodio ámbar, Ascua rojo,
Xenón frío). **Ascua por una razón concreta: es la única que no roza a Vice por ningún lado.**
Vice es ámbar miel `#ffd166` sobre tinta púrpura `#150726`; aquí no hay ni miel ni púrpura.
Sodio se sostenía pero por margen estrecho, y Xenón devolvía el tema al azul, que es de donde
vino el aviso de plantilla.

### Tipografía — tres caras, tres trabajos

Espeja la disciplina de Vice (display de impacto / texto / una cara reservada a un solo
trabajo), con caras que no comparte:

- **Display: Bricolage Grotesque** (variable, ejes `opsz` y `wght`), peso 600, **caja baja**,
  `letter-spacing: -.032em`, `line-height: .94`. Contra la versal negra condensada de Passion
  One con interlineado 0,84.
- **Texto: Instrument Sans** 400/500.
- **Reservada: Instrument Serif itálica**, y sólo para **lo hablado** — las frases en primera
  persona, una por escena. Es el equivalente de Pathway Gothic One en Vice, que sólo aparece en
  lo acreditado. Es además el único gesto de calidez conseguido por *forma* y no por color.
- **Sin monoespaciada, ninguna.** Es la señal más fuerte de "herramienta de desarrollador", y
  Vice hace exactamente lo mismo a propósito (sobrescribe su `--font-mono` a Manrope).
- Escala propia `--t-1..--t-10`, **los mismos diez pasos que Vice**: base 16, razón 1,333.
  Espejar el sistema numérico es parte de organizar como Vice.

### Los dispositivos

| Vice | Hyprland |
|---|---|
| Chrome de cine persistente (cajetín, letterbox, atenuador) | **El haz**: cuña de bordes nítidos con `clip-path`, montada fuera de toda escena, que cruza en diagonal y no se desmonta |
| Cortinilla de academia con iris | **El encendido**: la página arranca a oscuras y el haz entra con un barrido duro |
| Una sola gramática de revelado (desenfoque → nitidez) | **Corte de máscara** lateral para rótulos, crecimiento de regla vertical, subida lenta del display |
| Carril horizontal de obra (la bobina) | **La tira de exposición**: banda a sangre partida en cinco escalones de la misma luz, sin radio, filete de 1px entre ellos, exposición creciente; el apuntado se abre y los demás se comprimen |
| Cartel de reparto (créditos como prosa) | **El reparto**: rol una vez como rótulo a la izquierda, nombres fluyendo, encendido en cadena como lámparas |
| Carta de ajuste (cierre de emisión) | **Las bandas**: contacto a sangre, filete entre bandas, rótulo izquierda y valor grande derecha; al apuntar, la luz inunda la banda de izquierda a derecha con corte duro |
| Marcas de esquina de visor | **Filete inferior** que se pinta al apuntar una fila |

### Movimiento — contraste de tiempos

El defecto de fondo de las versiones descartadas era que **todo iba lento y suave**: un ajuste
global no es una coreografía. Se construye sobre dos curvas:

- Atmosférico: **900ms**, `cubic-bezier(.16,.84,.28,1)`.
- Cortes: **400–500ms**, `cubic-bezier(.7,0,.2,1)` — rápido y **sin rebote**.

Esa diferencia es lo que hace que el movimiento parezca decidido. Todo degrada con
`prefers-reduced-motion`.

## Restricciones

### `check_theme_identity`: el que rompe es el marcador 2, no el 3

Corregido tras cruzar el gate contra el diseño aprobado, no contra el de tiles que se descartó:

- **Marcador 3** (`scripts/verify.py:1146-1157`, `.hero-surface` con `boxShadow: none` y
  `borderWidth: 0px`) **sigue pasando**: el hero de Ascua es texto a sangre sin chrome, así que
  no hereda la tarjeta de Caelestia. No hay que tocarlo. Sí hay que **añadir** marcadores
  propios de Hyprland, porque hoy el gate no protege nada suyo: radio 0 y filete de 1px donde
  Caelestia lleva radio y sombra.
- **Marcador 2** (`scripts/verify.py:1159-1174`, `.credits-list` en `flex-direction: row` con
  `.credit-role` oculto) **se rompe por diseño**. El reparto de Ascua es rol a la izquierda como
  rótulo y nombres fluyendo a la derecha, en filas con filete: ni es fila de píldoras ni oculta
  el rol. Hay que partir la aserción en dos, una por tema, no relajarla para los dos.

### Caelestia sale del bloque compartido sin cambiar

Los selectores de `themes.css:2403-2445` hoy alcanzan a los dos temas. Se separan en dos
bloques: el de Caelestia queda **literalmente igual**, y Hyprland recibe el suyo. Se verifica
con una pasada de `verify.py --theme caelestia` antes y después.

### El tema es cálido y Vice también

Riesgo asumido y acotado por elección de tonalidad, no por casualidad. Si en la revisión sobre
el sitio real los dos se parecen más de lo aceptable, la salida es empujar Ascua hacia el
carmesí (`--l2` como luz primaria), no retocar Vice.

### Las dos copias de la hoja de fuentes cambian juntas

`index.html` duplica el mapa `fontHrefs` a propósito para evitar el FOUC, y `src/themes/hyprland.ts`
tiene el suyo. Una desincronización degrada a la vía lenta en silencio.

## Qué se descartó, y por qué

- **La mecánica del compositor** (tiles con gaps, barra de workspaces, barras de título por
  tile, etiquetas monoespaciadas, cursor de retícula, `dim_inactive`). Rechazada por Aoshi por
  demasiado técnica: producía una herramienta de desarrollador, no un portfolio que lee una
  reclutadora. Se conserva de ella **una sola cosa**, que fue su acierto: los nombres de
  sección en español llano y el contacto siempre alcanzable.
- **La atmósfera de cristal** (tarjetas `rgba(255,255,255,.07)` con `backdrop-blur` y borde
  blanco uniforme, fondo de manchas desenfocadas, degradado azul→violeta). Rechazada como "AI
  slop": son los tics del diseño generado, y el degradado azul→violeta es el peor de ellos.
- **La óptica calculada por lámina** (canto especular orientado a la fuente, medido y
  funcionando: 118,4° / 129,3° / 149,1° / 181,4° / 212,9°). Técnicamente correcta y bonita, pero
  seguía vistiendo una tarjeta redondeada: resolvía el acabado sin resolver la forma.
- **Sodio y Xenón** como tonalidades, por lo dicho arriba.
- **Scroll-snap en la tira.** Medido con A/B: con snap, fijar `scrollLeft=400` aterriza en 477,
  y como los anclajes caen cada ~477px cada incremento de rueda volvía al origen. El carril se
  quedaba clavado en 34 de 954 y bloqueaba la página en 1760 de 3600.

## Verificación

- `npm run build` y `npm run lint` en verde.
- `python3 scripts/verify.py` en verde para `--theme hyprland`, **y también** `--theme vice` y
  `--theme caelestia`: la prueba de que el rediseño no se llevó por delante a los otros dos.
  Más una pasada `--reduced`.
- Capturas reales a 1440×900 y 390×844 con `?theme=hyprland`. **En esta máquina el chromium de
  Playwright no está descargado**: hay que lanzar contra `/usr/bin/google-chrome`
  (`chromium-browser` no existe).
- Contraste medido sobre píxel compuesto y **con recorte ajustado al glifo**, no a la caja del
  bloque: medir una caja ancha y casi vacía devuelve la variación del fondo, no la del texto —
  dio 1,5:1 sobre un texto que estaba en 7,9:1. Cifras del prototipo aprobado en Ascua: display
  14,4:1 · hablada 11,6:1 · afirmación 14,4:1 · prueba 6,05:1 · rótulo 6,03:1.
- Ninguna escena puede quedar sin revelar tras un recorrido con rueda, ni siquiera a golpes.
  El observador de intersección pierde callbacks con scroll rápido, así que lleva red por
  posición.
- El carril no puede secuestrar la rueda: tiene que consumir su recorrido y **soltar**.
- Revisión de Aoshi **sobre el sitio real haciendo scroll**, no sobre capturas.
- Gates `lidia-naive-tester` y `vera-art-director` (umbral 7,5/10).

**Prototipo de referencia, aprobado y medido:**
`.superpowers/brainstorm/689488-1785939513/content/hyprland-v5-canto.html`, tonalidad `ascua`.
Las tres tonalidades quedan en el fichero, recuperables si alguna vez se quiere volver.

## Registro de implementación

Tareas 1-8 y tarea 9 (pasos 1-7) completadas el 2026-08-05. Pendiente: revisión de
Aoshi sobre el sitio real, gates `lidia-naive-tester`/`vera-art-director`, commit final.

### Números medidos (Tarea 9, paso 4 — recorte ajustado al glifo)

| Elemento | Ratio | Umbral |
|---|---|---|
| `.display-xl` | 17,5:1 | 4,5:1 |
| `.lead` | 8,71:1 | 4,5:1 |
| `.hero-kick` | 6,12:1 | 4,5:1 |
| `.hero-corner` | 6,86:1 | 4,5:1 |
| `.credit` | 17,1:1 | 4,5:1 |
| `.scene-index-title` (menú abierto, fondo sólido `--color-ink`) | 5,75:1 | 4,5:1 |
| `.scene-index-num`/`.scene-index-name` | 6,55:1 | 4,5:1 |
| `.scene-index-blurb` (el más ajustado) | 4,74:1 | 4,5:1 |

`--nav-dim: 58%` / `--nav-dim-soft: 52%` (estimación de la tarea 1) se midieron contra
el fondo real y pasan AA con margen — no hizo falta recalibrar.

### Divergencias respecto al plan

El plan traía la CSS/TS casi lista para copiar, pero cuatro huecos no cubiertos
aparecieron al verificar contra el sitio real (no al leer el plan):

1. **`.about-pairs` y `.credit-group-label` parten de `display: none`** en
   `style.css` (solo Vice los enciende). El plan no incluía el `display: block`
   necesario para Hyprland — sin él, el bloque de afirmación/prueba y el rótulo
   del reparto seguían invisibles pese a llevar CSS propia.
2. **`<button>.credit` con `appearance: auto`**: Chrome computa `display: inline`
   como `inline-block` en un botón salvo que se añada `appearance: none`
   (confirmado en Chrome real, no artefacto de swiftshader). Sin esto el marcador
   de identidad de la tarea 8 (`display === "inline"`) no podía pasar nunca.
3. **Títulos de obra cortados a media palabra**: en un panel comprimido a ~168px,
   una palabra larga sin espacios (p. ej. "HyprFinance") desborda el `display-lg`
   y `overflow: hidden` la chapa en seco. Arreglado con `clamp` + `nowrap` +
   `text-overflow: ellipsis` cuando el panel está cerrado, tamaño de firma al
   abrir. El fallo lo destapó el arnés de contraste (medía `fg == bg` exacto
   donde no había ningún glifo visible que muestrear).
4. **Scrims insuficientes contra el fondo animado**: los paneles de obra
   (0.2–0.65 de opacidad), `.about-pairs` (sin scrim) y `.scene-nav-trigger`
   (transparente) dejaban pasar el haz brillante bajo el texto secundario. Subidos
   a 0.82–0.94 (obra), 78% (about-pairs) y 82% (nav-trigger). El escalón de
   exposición (`--hypr-e`) también se bajó de intensidad (`*1%` → `*0.35%`): a
   máxima intensidad competía con la legibilidad del panel que anuncia.

Dos falsos positivos encontrados en el arnés mismo (`scripts/verify.py`), no
defectos del tema — confirmados visualmente y con un `git worktree` del commit
previo a esta rama:

- `background-clip: text` dejaba `color: transparent`, que el arnés componía
  literalmente sobre el fondo (dando `fg == bg`, 1,00:1) para texto que en
  realidad renderiza en alto contraste. Mismo defecto ya conocido del contorno
  `-webkit-text-stroke`; se excluye del gate igual que un fondo no sólido.
- `.scene-index` (menú de navegación) se oculta con `clip-path`, no con
  `display`/`visibility`, así que el filtro de candidatos del arnés lo media
  igualmente CERRADO contra lo que hay detrás. Afectaba a los tres temas por
  igual — confirmado en Caelestia con el commit `28eec96` (11 fallos antes del
  fix, 9 después, todos preexistentes y ajenos a esta rama).
