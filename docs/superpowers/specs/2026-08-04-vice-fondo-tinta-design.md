# Tinta de cartel — el fondo de Vice pasa a ser materia impresa

Estado: en ejecucion
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
