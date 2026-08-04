# Tinta de cartel — el fondo de Vice pasa a ser materia impresa

Estado: implementado
Plan: `docs/superpowers/plans/2026-08-04-vice-fondo-tinta.md`
Fecha: 2026-08-04
Alcance: el fondo del tema Vice. Hyprland y Caelestia no se tocan — comparten
`shaderBackground.ts` y hay que comprobar que siguen intactos. La tipografía, la coreografía y
las cinco escenas no se rediseñan.

## Por qué

El fondo de Vice es hoy `viceHaze`: bruma de fbm con warp de dominio teñida de magenta a cian y a
ámbar. Funciona, acota su brillo y pasa el gate de contraste. Su problema no es de calidad, es de
naturaleza: **es generativo, así que no se puede dirigir**. Deriva. La revisión visual del 3 de
agosto lo describe como "fondo generativo casi vacío" (F-011), y ese vacío no se arregla subiendo
la amplitud del ruido: un ruido más fuerte sigue sin decir nada.

El intento anterior de darle contenido fue un vídeo autorado en Remotion —la bahía de Miami del
atardecer al amanecer, desplazada por el scroll frame a frame. Pasó todos los gates: techo de
brillo verificado en los 600 fotogramas, retraso de scrub de 167 ms sobre un techo de 200, arnés
en verde, cero errores de consola. **Y se descartó igualmente**, al verlo en movimiento. Queda en
`design/vice-fondo-remotion` (commit `e94cbe8`).

De ese descarte sale la premisa de este spec, y conviene dejarla escrita porque explica las tres
direcciones caídas de golpe:

> El tema Vice no es "una página con estética ochentera". Es **una película**. `introLeader.ts`
> monta una cuenta atrás con brazo barredor e iris —una cola de arranque de bobina—,
> `cinemaChrome.ts` pone barras de formato, Passion One se eligió como la alternativa libre más
> cercana a Pricedown y Pathway Gothic One existe solo para el cartel de reparto. Ponerle detrás
> un paisaje es ponerle *aquello de lo que trata la película*. Pero el fondo de una película no
> es su argumento.

Así que el fondo deja de representar un lugar y pasa a ser **materia**: la superficie sobre la
que este cartel estaría impreso.

## Qué se construye

Una **serigrafía a dos tintas** —magenta `#ff2e88` y ámbar `#ffd166`, los dos acentos que el tema
ya tiene— tramada en semitono sobre la tinta profunda `#150726`, con el scroll moviendo el
balance entre las dos planchas.

Cinco decisiones lo sostienen, y las cinco salen de haberlo montado y medido en el companion, no
de la intención:

**1. La trama dibuja luz, no ruido.** Cada plancha trama un foco suave que cruza el encuadre con
el recorrido. La primera versión tramaba fbm y leía como una textura pegada encima: en un cartel
el semitono **siempre** describe una forma. La caída del foco es cerrada (gaussiana con factor
1.9); con una caída amplia el foco llenaba la pantalla y quedaba un único montículo centrado, que
es justo lo contrario de tener composición.

**2. Cada plancha lleva su propia imagen.** Magenta arriba a la izquierda, ámbar abajo a la
derecha, cruzándose solo en la franja de en medio. Es el hallazgo central: al poner el mismo
campo en las dos tintas, magenta y ámbar se suman en las mismas zonas y dan **marrón** — el
encuadre entero se embarra. Dos planchas con la misma imagen no son una duotonía, son una capa
teñida dos veces.

**3. El scroll mueve el balance de tintas.** Magenta manda en la apertura, ámbar en el cierre: el
mismo arco de color que el tema ya recorre. Sustituye a la primera idea —que el scroll abriera y
cerrara el desregistro—, que casi no se veía y no significaba nada. El desregistro se queda, pero
pequeño y constante: una máquina bien calibrada que aun así no es perfecta.

**4. Densidad de rasqueta.** Una variación de muy baja frecuencia en la cobertura, distinta por
tinta porque son dos pasadas distintas. Es lo que retira la última sensación de "capa de patrón
aplicada por software".

**5. Marcas de registro en las cuatro esquinas.** La cruz dentro de un anillo que el impresor pone
fuera del corte para alinear las planchas. Van en **una sola tinta**: si estuvieran en las dos no
servirían para registrar nada, que es exactamente el chiste. Es el elemento de firma — el detalle
que solo reconoce quien sabe y que nadie pone en una web.

Lo que **no** se hace, aunque tiente: ni una tercera tinta ni un punto más grande. Dos tintas es
una restricción real de la serigrafía y coincide con los dos acentos del tema. La disciplina es lo
que hace que lea como impresión y no como patrón decorativo.

## Restricciones

### El techo de brillo, y por qué cambia de forma

En Vice el texto se apoya **directamente sobre el fondo**, sin scrim opaco encima. Eso solo
funciona porque el fondo acota su brillo en la fuente. `viceHaze` lo hacía con
`col = min(col, vec3(0.30, 0.26, 0.36))`.

**Ese clamp por canal es incorrecto y hay que sustituirlo por uno de luminancia.** Se calibró
mirando magenta y ámbar, y con esos tonos funciona; pero un cian tocando ese mismo tope es mucho
más luminoso, porque el verde aporta el 71% de la luminancia percibida. Medido: la variante de
cáusticas salía a media pantalla de teal claro **sin pasarse de ningún canal**. El sustituto
escala el color entero cuando su luminancia supera el techo, así que vale para cualquier tono:

```glsl
const float LUMA_MAX = 0.235;
vec3 ceilingClamp(vec3 c) {
  float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
  return l > LUMA_MAX ? c * (LUMA_MAX / max(l, 1e-4)) : c;
}
```

El objetivo medible es el que ya usa el proyecto: **p99.5 de luminancia por debajo de 62** (sobre
255) en la franja vertical 0.06–0.74 del alto, que es por donde pasa la tipografía. Con estos
valores el fondo mide 62 en el companion.

### Muaré

Es el riesgo específico de esta dirección y no tiene versión suave: una rejilla de puntos regular
batiendo contra la rejilla de píxeles de la pantalla hormiguea al hacer scroll. La trama se ancla
a `gl_FragCoord`, **no a coordenadas de imagen**, para que la lineatura sea constante en píxeles
de pantalla igual que lo es en el papel.

Queda un cabo abierto que el plan tiene que cerrar midiendo: `shaderBackground.ts` acota el DPR a
`min(devicePixelRatio, 1.5)`. En una pantalla de 3x el búfer va a 1.5x, así que el punto se ve
físicamente el doble de grande que en una de 1.5x. Hay que decidir con capturas si el paso se fija
en píxeles de búfer (tamaño constante respecto al búfer) o se escala con el `devicePixelRatio`
real (tamaño físico constante).

### Heredadas del proyecto

- Cero `any`; `strict` está activo.
- El módulo devuelve un handle con `destroy()` que se llama en `pagehide`, y libera programa,
  búferes y RAF. Fuga = context lost.
- `prefers-reduced-motion`: `mountShaderBackground` ya pinta un solo fotograma y no arranca RAF.
  El fotograma estático tiene que ser **legible y representativo**, no un extremo del arco.
- El scroll se lee de `window`, no de Lenis ni de ScrollTrigger: el fondo no puede depender de un
  import diferido ni de que Lenis se monte.
- Verificar SIEMPRE con `?theme=vice`; el tema se sortea por visita.

## Qué se descartó, y por qué

**Emulsión de 35 mm** (grano que nada, halación, respiración de ventanilla, marca de cambio de
bobina). Era mi recomendación y es la más coherente con el leader y el letterbox. Descartada por
preferencia del usuario tras verla en movimiento junto a las otras dos.

**Cáusticas de agua.** Preciosa y muy Miami, pero podría ser el fondo de cualquier hotel de playa:
no es de este proyecto. Fue además la que destapó el fallo del clamp por canal, así que su paso
por aquí no fue en balde.

Las tres quedan montadas y funcionando en `.superpowers/brainstorm/3762734-1785873008/content/`,
recuperables si alguna vez se quiere volver.

## Verificación

- `npm run build` y `npm run lint` verdes.
- Luminancia del fondo **aislado** (con el contenido oculto) por debajo del techo en al menos 12
  puntos del recorrido, a 1440x900 y 390x844.
- `scripts/verify.py` en verde contra su línea base, sin fallos nuevos. Atención especial al gate
  de contraste: `--nav-dim` es un porcentaje calibrado **contra una superficie**, así que cambiar
  el fondo puede invalidarlo aunque nadie toque el token. Ya pasó con el vídeo: cayó de 5,74:1 a
  4,17:1 sin editar una línea.
- Sin muaré visible a DPR 1, 1.5 y 2, en reposo y durante el scroll.
- Capturas reales a 1440x900 y 390x844, cero errores de consola.
- Gate final: `lidia-naive-tester` y `vera-art-director`.

## Registro de implementación (Tarea 9, cierre del plan)

Las Tareas 1-8 quedaron cerradas y revisadas antes de esta tarea; lo que sigue son los números
finales que el propio plan pedía dejar por escrito, más las divergencias reales respecto a lo
previsto arriba.

### Luminancia del fondo aislado (Tarea 3)

Con el arnés `scripts/measure-bg-luma.py` corregido (ver más abajo), midiendo el fondo realmente
aislado en 12 puntos del recorrido de scroll:

| Viewport | peor banda | techo banda | peor fotograma | techo fotograma | peor pixel | techo pixel |
|---|---|---|---|---|---|---|
| 1440×900 | 53.75 | 62 (margen 8.25) | 53.54 | 82 (margen 28.46) | 55.75 | 150 (margen 94.25) |
| 390×844  | 54.01 | 62 (margen 7.99) | 53.82 | 82 (margen 28.18) | 55.25 | 150 (margen 94.75) |

Ambos viewports pasan sin tocar ninguna de las tres palancas previstas (mezcla de tintas /
`LUMA_MAX` / posición del foco ámbar) — el shader tal como quedó de la Tarea 2 ya cumplía. El
margen sobre el techo de banda (~8 puntos) no es enorme; queda documentado en el informe de la
Tarea 3 como riesgo residual no confirmado ni descartado (posible colapso de ruido `fbm` en
software rendering frente a GPU real), pendiente de una mirada en navegador real si algún día se
audita de nuevo el brillo.

### Bug de arnés descubierto y corregido en la Tarea 3

El arnés de brillo entregado en la Tarea 1 (`scripts/measure-bg-luma.py`) no aislaba el fondo:
usaba `#app { visibility: hidden }` para ocultar el contenido, pero el canvas del shader vive
**dentro** de `#app` (como hijo de `.bg-theme`, igual que el resto del contenido), así que esa
regla ocultaba también el fondo. El síntoma fue una lectura idéntica al 0.01 en las 12 posiciones
de scroll (12.21 exacto), que resultó ser la luminancia plana de `--color-ink` pintada por
`html { background-color }` cuando no hay nada más visible — es decir, el arnés daba un falso
verde para cualquier fondo, incluso uno roto, porque no estaba midiendo el shader en absoluto. Se
corrigió cambiando la regla de aislamiento a
`#app > *:not(.bg-theme):not(.bg-noise) { visibility: hidden !important; }`, que sí deja visible
el fondo y oculta solo el contenido real. El techo (62/82/150) no se movió — el fix hace que el
instrumento mida lo que ya decía medir. Cualquier medida de brillo de las Tareas 1/2 apoyada en la
versión vieja del arnés no midió el shader real y debe descartarse a favor de los números de la
Tarea 3 de arriba.

### Decisión de muaré (Tarea 5)

Se detectó, con evidencia medida (no a ojo), una discrepancia real en el tamaño físico del punto
de trama entre pantallas sin retina (DPR 1) y pantallas retina (DPR ≥ 1.5): a `pitch` fijo en
píxeles de búfer, el punto salía ~1.5x más grande en DPR 1 que en DPR ≥ 1.5 (7.0px CSS vs 4.7px
CSS), por el recorte que `shaderBackground.ts` ya aplica al ratio real (tope 1.5). No hubo
hormigueo ni bandas de interferencia en ningún caso (diff de píxeles entre fotogramas consecutivos
< 0.1/255 en todos los DPR probados).

**Decisión: (b) — escalar el paso de trama con el ratio buffer/CSS**, usando el ratio ya recortado
por `shaderBackground.ts` (`Math.min(devicePixelRatio, 1.5)`), no el `devicePixelRatio` crudo. La
razón de usar el ratio recortado y no el crudo: pedirle al shader más finura de trama de la que el
búfer real puede resolver (por ejemplo, escalar para un DPR 3 real cuando el búfer sigue capado a
1.5x) sería la receta de un muaré nuevo — exactamente el riesgo que la tarea vino a vigilar.
Implementado como un uniform aditivo `uPixelRatio` en `shaderBackground.ts` (no-op para Hyprland y
Caelestia, que no lo declaran en su fragment shader) y `pitch = 7.0 * (max(uPixelRatio, 1.0) / 1.5)`
en `viceInk.ts`, que deja el paso exactamente en 7.0 para el caso más común (cualquier pantalla
retina) y lo reduce a ~4.67 para DPR 1, igualando el tamaño físico en pantalla. Verificado tras el
fix: densidad de punto visualmente idéntica entre DPR 1, 1.5 y 2, sin parpadeo nuevo.

### Divergencias respecto al plan original

- Ninguna decisión de diseño (mezcla de tintas, `LUMA_MAX`, posición de foco, `--nav-dim`) tuvo
  que recalibrarse — el plan preveía la posibilidad de tocar esas palancas en las Tareas 3 y 4 y
  no hizo falta en ningún caso.
- El único hallazgo no previsto por el plan fue el bug del arnés de brillo (arriba), que es una
  corrección de instrumentación de la propia Tarea 1, no un cambio de dirección del shader.
- La Tarea 4 retiró `.bg-theme::before` (el lavado magenta-ámbar en `soft-light`) por quedar
  redundante con el color propio del nuevo fondo, decisión validada con diff de píxeles y
  `verify.py` en dos estados (con/sin la regla), no solo por intuición. El `::after` se mantuvo
  intacto porque sí aporta margen de contraste medible (4.28:1 → 3.67:1 en el chip de teléfono de
  contacto al retirarlo).

### Gates finales (Tarea 9)

- `npm run build` (Node 22, `tsc && vite build`) — verde.
- `npm run lint` — verde, sin salida.
- `python3 scripts/verify.py --url http://127.0.0.1:4173` (build de producción servido con
  `vite preview`) — `TODO OK — 12 fallos conocidos, 0 nuevos (verify-baseline.json)`. Los 12
  fallos son los ya documentados en tareas anteriores: 9 assets de galería pendientes (Tarea 11
  fuera de este plan) y 3 fixtures de vídeo SMPTE pendientes (Tarea 8 histórica de este plan,
  cierre fuera de alcance). Ninguno relacionado con el fondo de tinta.
- Capturas reales de las cinco escenas (hero, about, obra, credits, contacto) a 1440×900 y
  390×844 con `?theme=vice`: canvas WebGL activo con la trama de semitono magenta/ámbar en las
  diez, cero errores de consola en cada captura.

- `npm run build` y `npm run lint` verdes.
- Luminancia del fondo **aislado** (con el contenido oculto) por debajo del techo en al menos 12
  puntos del recorrido, a 1440x900 y 390x844.
- `scripts/verify.py` en verde contra su línea base, sin fallos nuevos. Atención especial al gate
  de contraste: `--nav-dim` es un porcentaje calibrado **contra una superficie**, así que cambiar
  el fondo puede invalidarlo aunque nadie toque el token. Ya pasó con el vídeo: cayó de 5,74:1 a
  4,17:1 sin editar una línea.
- Sin muaré visible a DPR 1, 1.5 y 2, en reposo y durante el scroll.
- Capturas reales a 1440x900 y 390x844, cero errores de consola.
- Gate final: `lidia-naive-tester` y `vera-art-director`.
