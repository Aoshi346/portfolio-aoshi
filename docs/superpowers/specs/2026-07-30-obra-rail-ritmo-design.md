# El ritmo del carril de obra — reposo, tránsito y cartelas acopladas

Estado: en ejecucion
Plan: `docs/superpowers/plans/2026-07-30-obra-rail-ritmo.md`
Fecha: 2026-07-30
Alcance: tema Vice, escritorio (>=901px). Por debajo de 901px no hay carril y no se toca.

## Por qué

El desplazamiento lateral de `[data-obra-rail]` funciona: no hay bug. Lo que falla es el
ritmo — "va bien, pero siento que el timing no es perfecto". El encargo empezó midiendo,
porque un afinado sin números previos acaba en tanteo.

Todo lo que sigue está medido en el build de producción con `?theme=vice` a 1440x900, con
`scripts/measure-obra-rail.py`, a tres velocidades de rueda. Nada es deducido.

### Los cuatro defectos, con su número

| | qué se midió | resultado |
|---|---|---|
| M2 | adelanto de la entrada de cartela sobre el encuadre, piezas 2-4 | 938-995 px (lento), 730-769 px (normal), 90-233 px (flick) |
| M3 | velocidad lateral en el instante exacto del encuadre | 96-107% de la velocidad de tránsito. Cero deceleración |
| M4 | permanencia encuadrada, acotada a la ventana del pin | pieza 1 al 62-69% de la media central; pieza 5 al 33-40%, y 0 ms en flick |
| M1 | parada en seco a mitad de carril | scroll se para en 602 ms, el carril en 956 ms; deriva lateral 187 px |

### Diagnóstico: tres causas raíz, no cuatro defectos

1. **Dos relojes.** El carril avanza en tiempo de scroll (`scrub`); las entradas de
   `buildSlate` en tiempo real (`duration` + `toggleActions`). `containerAnimation` decide
   cuándo dispara el trigger, no cómo avanza el tween. Por eso el adelanto es función pura
   de la velocidad de scroll. El defecto no es "va adelantada": es que **no está acoplada**.
   Alargar el disparo arregla el scroll lento y empeora el flick.
2. **Un solo tween lineal sobre los cinco paneles.** Con `ease: "none"` la velocidad en el
   encuadre es idéntica a la de tránsito por construcción. No hay nada que pueda parar.
3. **El rango es [pieza 1 encuadrada .. pieza 5 encuadrada].** Cero entrada y cero salida:
   el carril se fija ya encima de la 1 y se suelta encima de la 5.

**Dos correcciones a la primera lectura de los números**, ambas verificadas después:

- **M1 no es sobrepaso.** Con `ease: "none"` y sin snap el sobrepaso es imposible. Los
  187 px son 75 px de scroll pendiente más 112 px de retardo acumulado que el scrub
  devuelve — y 112 coincide con los 115 px de desfase sostenido medidos a esa velocidad.
  El defecto real es que **el carril no aterriza en ningún sitio**: es un problema de
  destino, no de inercia.
- **El dato de la pieza 1 en M4 es un artefacto de la medida.** Acotar la permanencia a la
  ventana del pin descarta el tiempo en que la pieza 1 está en pantalla antes de que el pin
  enganche. La asimetría real es de cola: la pieza 5.

### El hallazgo que decidió el dimensionado

Sobre el mockup vivo del banco de montaje se midió que **la meseta sola no compra quietud**:

| reposo/tránsito | meseta a 644 px/s | pieza que peor se posa |
|---|---|---|
| 0.25 | 373 ms | 205 px/s |
| 0.45 | 564 ms | 148 px/s |
| 0.95 | 849 ms | 92 px/s |

Ni con la meseta al máximo se para, porque `scrub: 1` tarda 956 ms en asentarse y la meseta
dura menos: el carril se pasa el reposo entero recuperando retardo. Bajando el scrub:

| scrub | asentamiento | pieza que peor se posa (meseta 564 ms) |
|---|---|---|
| 1.0 | 960 ms | 147 px/s |
| 0.7 | 672 ms | 58 px/s |
| 0.5 | 480 ms | 18 px/s |
| 0.3 | 288 ms | 1 px/s |

**Regla de diseño, con número: el reposo solo se siente como reposo si el asentamiento del
scrub es más corto que la meseta.** De ahí `scrub: 0.5`.

## Restricción técnica que fija la arquitectura

`containerAnimation` **exige que el contenedor sea lineal**. Verificado en el fuente de
ScrollTrigger: `_parsePosition` mide `_caScrollDist` entre `seek(0)` y `seek(max)` y hace un
mapeo **lineal** de posición de elemento a posición de scroll; además `start`/`end` pasan a
referirse al tiempo de la animación, no al scroll. Con un contenedor con ease o con mesetas
ese mapeo miente y los disparos caen en sitios arbitrarios.

Consecuencia directa: **no se puede segmentar el carril y dejar `buildSlate` como está.**
Las entradas de cartela tienen que vivir DENTRO de la timeline maestra, en posiciones
absolutas. Los dos especialistas llegaron a esta misma arquitectura por caminos distintos.

## Dimensionado

Todo en unidades de `innerWidth` (`iw`), para que escale y para que `end` y los destinos
sigan siendo funciones. A 1440 px de ancho, `iw = 1440`.

```
recorrido lateral   travel = 4 · iw                    = 5760 px
transito            T      = 0.56 · iw                 =  806 px de scroll por 1440 laterales
reposo              R      = 0.252 · iw  (= 0.45 · T)  =  363 px
presupuesto del pin end    = 4T + 5R = 3.5 · iw        = 5040 px
engranaje                  = 1440 / T                  = 1.79 : 1
scrub                                                  = 0.5  (asentamiento ~480 ms)
```

El documento pasa de 12307 a **11587 px** (−720). La sección fijada (viewport + reserva del
pin) baja del **54,1% al 51,3%** del documento: sigue siendo la sección dominante. Acortar el
carril alivia el recorrido hasta el contacto, no lo resuelve.

### Timeline maestra

Nueve segmentos alternos, empezando y acabando en reposo. Unidades: 1 = T.

| # | segmento | intervalo | x | ease |
|---|---|---|---|---|
| 1 | reposo 1 | 0.00 – 0.45 | 0 | — |
| 2 | tránsito | 0.45 – 1.45 | 0 → −1·iw | `power2.inOut` |
| 3 | reposo 2 | 1.45 – 1.90 | −1·iw | — |
| 4 | tránsito | 1.90 – 2.90 | −1·iw → −2·iw | `power2.inOut` |
| 5 | reposo 3 | 2.90 – 3.35 | −2·iw | — |
| 6 | tránsito | 3.35 – 4.35 | −2·iw → −3·iw | `power2.inOut` |
| 7 | reposo 4 | 4.35 – 4.80 | −3·iw | — |
| 8 | tránsito | 4.80 – 5.80 | −3·iw → −4·iw | `power2.inOut` |
| 9 | reposo 5 | 5.80 – 6.25 | −4·iw | — |

Duración total 6.25 unidades. El **último destino se clampa a `travel()` exacto**, no a
`4 · innerWidth`: con barra de scroll o redondeo subpíxel los dos valores difieren y quedaría
una franja de la pieza 5 fuera del encuadre.

`power2.inOut` hace pico a 2× la media: pico lateral ~2300 px/s a velocidad de lectura
normal, frente a los 644 px/s de hoy. **Ese es el cambio de carácter buscado** — de cinta
continua a pase de cartela — y es inherente a cualquier diseño con mesetas, porque hay que
cubrir los mismos 1440 px laterales en menos scroll.

### Entrada de cartela

Cada cartela entra dentro de la timeline maestra. Ventana de la pieza `i`:

```
i = 0:  [0.00 , 0.36]
i >= 1: base = 0.45 + (i-1)·1.45     ventana = [base + 0.35 , base + 1.045]
```

La ventana dura **0.695 unidades = 560 px de scroll**, arranca al 35% de su tránsito y cierra
**36 px después** de que la pieza quede encuadrada. Deja de haber adelanto: pase lo que pase
con la velocidad de scroll, la cartela se monta con la pieza.

Reparto interno, en fracciones de esa ventana. **Todo `fromTo` con los dos extremos escritos
a mano**; ni un `gsap.from`.

| elemento | pos | dur | px | de → a | ease |
|---|---|---|---|---|---|
| ordinal | 0.00 | 0.22 | 123 | `y −70 → 0`, `scale 1.35 → 1`, `opacity 0 → 1` | `expo.out` |
| título (chars) | 0.06 | 0.30 | 168 | `yPercent 118 → 0`, `opacity 0 → 1`, stagger 0.012 | `power3.out` |
| lead | 0.26 | 0.26 | 146 | `y 20 → 0`, `opacity 0 → 1` | `power2.out` |
| meta | 0.34 | 0.24 | 134 | `y 14 → 0`, `opacity 0 → 1` | `power2.out` |
| máscaras | 0.44 | 0.36 | 202 | `clipPath inset(0 100% 0 0) → inset(0 0% 0 0)`, stagger 0.05 | `power3.out` |
| galería | 0.56 | 0.34 | 190 | `x 46 → 0`, `opacity 0 → 1` | `power3.out` |

`pos`, `dur` y el stagger van todos en **fracciones de la ventana**, no en unidades de la
timeline maestra ni en segundos.

El último cierra en 0.90, es decir **20 px antes** del encuadre: la pieza aterriza ya montada,
sin los ~950 px de cartela quieta que se medían.

El stagger del título baja de 0.08 s a 0.012 porque cambia de unidad: 0.012 × ~14 caracteres
= 0.168 de la ventana ≈ 94 px de scroll.

### Parallax de la galería

Deja de tener `scrub` propio — hoy son **tres** suavizados anidados (Lenis 1.15, el scrub del
carril, y el `scrub: 1` del parallax), y el contenedor ya aporta el suyo. Pasa a la timeline
maestra, `xPercent −3.5 → 3.5`, `ease: "none"`, con ventana `[base + 0.35 , base + 1.45]`
(`[0, 0.45]` para la pieza 0): **cubre también el reposo**.

Eso es deliberado: mientras el track está quieto la captura sigue derivando unos píxeles con
el dedo, así que la meseta nunca se lee como que la página se ha colgado. Es el riesgo
principal de un carril con reposos y esta es su mitigación.

## Qué se toca

- `src/themes/vice.choreography.ts`
  - `scene3Slate()` — el `gsap.to` único pasa a timeline maestra. `scrub: 1 → 0.5`.
    `end` pasa de `+=travel()` a `+=3.5·innerWidth`, siempre como función.
  - `buildSlate()` — deja de crear ScrollTriggers propios. Recibe la timeline maestra y una
    posición, y devuelve su sub-timeline. Mueren los cinco `gsap.from`, los `delay` de reloj
    de pared y `toggleActions`.
  - `obraTriggerIds()` — ya no hacen falta siete ids por escena; queda el del carril.

## Lo que no se toca

- La escalera de `refreshPriority`: hero 2, carril 1, resto 0. Los valores son relativos y no
  cambian.
- `invalidateOnRefresh` y `end`/destinos como función.
- `gsap.matchMedia()` con `(min-width: 901px) and (prefers-reduced-motion: no-preference)`.
- El `destroy()` en `pagehide` y la limpieza de WebGL/GSAP.
- Nada anclado a `[data-scene]` ni a un nodo con `display: contents`.

## Re-verificación obligatoria por el cambio de distancia

El pin pasa de reservar 5760 px a 5040. Cuatro cosas miden contra eso:

1. `railBound("start"|"end")` (`vice.choreography.ts:1200`) lee `pin.start`/`pin.end`. La
   región del carril en la barra de orientación se estrecha del 54,1% al 51,3% del documento:
   comprobar que "03 · Obra" no se solapa con "04 · Créditos".
2. El trigger de créditos (`start: "top 80%"`, `:901`) no debe dispararse con el carril aún
   fijado.
3. El encendido y apagado del letterbox y del cromo en la frontera fin-de-carril /
   inicio-de-créditos. Fue una regresión real y está documentada en el comentario de
   `refreshPriority`.
4. `window.dispatchEvent(new Event("scrollrail:refresh"))` (`:846`) sigue publicando la
   altura correcta.

Y re-medir M1-M5 con `scripts/measure-obra-rail.py` sobre el build nuevo: el afinado está
hecho cuando los números se mueven en la dirección acordada, no cuando "se ve mejor".

Objetivos numéricos:

| | hoy | objetivo |
|---|---|---|
| adelanto de la **cartela entera** (M2) | 938-995 px | ≤ 40 px, y sin dispersión entre velocidades |
| adelanto del **`.lead`** (M2) | 938-995 px | ≤ 260 px |
| v lateral en el encuadre (M3) | 220-245 px/s | ≤ 20 px/s en las cinco piezas |
| permanencia pieza 5 vs central (M4) | 33-40% | paridad |
| documento | 12307 px | ~11587 px |

**Corrección posterior a la aprobación del spec.** La primera versión de esta tabla ponía un
solo objetivo de M2 (≤ 40 px) contra la métrica que el instrumento mide hoy, que es la
opacidad del `.lead`. Son cosas distintas: en el dimensionado de arriba el `.lead` cierra al
52% de la ventana y la galería al 90%, así que el lead termina 233 px antes del encuadre y la
cartela entera 20 px antes. Con un único objetivo de 40 px medido sobre el lead, el gate era
inalcanzable por construcción. Se separan las dos métricas y `measure-obra-rail.py` pasa a
medir también el cierre de la galería. Los dos números mejoran respecto a los 938-995 px de
hoy; el que describe "la pieza aterriza ya montada" es el de la cartela entera.

## Fuera de alcance, anotado

- **Orientación, índice y salida.** Durante el 54% del documento no hay barra de scroll (Vice
  la sustituye), `scrollRail` y `cinemaChrome` van `aria-hidden`, y no hay índice de piezas ni
  forma de saltar. El especialista de UX lo llama el defecto mayor de la sección. Es
  navegación, no ritmo: encargo aparte, junto con el hallazgo del naive test sobre los
  ~8600 px hasta el `mailto:`. Acortar el carril alivia ese hallazgo pero no lo cierra: eso lo
  cierra un CTA persistente.
- **Trampa de teclado, sin verificar.** Sospecha del especialista de UX: tabular a un enlace
  de una obra fuera de pantalla haría que el navegador ponga `scrollLeft` en `.obra-rail`, que
  GSAP no conoce, desalineando el carril de forma permanente. No se ha medido. Verificar con
  Tab real antes de darlo por cierto o por falso.
- **`will-change: transform` permanente** sobre un track de 7200x900 (`themes.css`). Capa de
  composición grande que nunca se retira, sumada al shader a pantalla completa. No es medible
  en swiftshader: el A/B en headless da 6 fps con shader y 25 sin él, pero eso es rasterizado
  por software, no señal de GPU real. Necesita navegador real.
- **Número de piezas.** Decisión de contenido, no de animación.

## Ya cerrado durante este encargo

`dcc7998` — con `prefers-reduced-motion: reduce` y ancho >=901px, las obras 2 a 5 eran
**inalcanzables**: la geometría horizontal colgaba solo del ancho, así que el CSS montaba un
track de 7200 px en un carril de 1440 px con `overflow: hidden` mientras `scene3Slate` nunca
llegaba a correr. Verificado antes (1 de 5 alcanzables) y después (5 de 5), sin regresión en
modo normal.

## Registro de implementación

_Pendiente. Al terminar, anotar aquí en qué se desvió la realidad del dimensionado de arriba
y por qué. Sin este registro el spec miente._
