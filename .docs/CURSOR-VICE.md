# Cursor propio de Vice — marca de sincronismo

> Estado: implementado y verificado (2026-07-29). Sin commitear.
> Codigo: `src/components/viceCursor.ts` · CSS al final de `src/themes/themes.css`
> · montaje en `src/main.ts`.

## Que es

La marca con que los montadores de cine alineaban cabeza y cola de bobina:
circulo fino con cruz, **fija — nunca gira**. Sustituye al cursor del sistema
solo donde toca, y deja al navegador lo que el navegador dice mejor.

El motivo se eligio sobre otros cuatro porque su anclaje esta VERIFICADO en el
codigo, no supuesto: el leader de apertura ya monta un `.leader-cross`
(`introLeader.ts:41`) y un `.leader-cue` (circulo de 13px con halo, la
"quemadura" de cambio de rollo). El cursor reutiliza dos elementos que el
visitante ya vio en los primeros 1,6 s.

## El contrato (esto es lo que no se toca)

Cerrado entre los especialistas de motion y de UX tras tres vueltas. Cualquier
cambio futuro del cursor tiene que seguir cumpliendolo entero.

1. **El punto de clic no lleva retardo.** Se escribe en el propio manejador de
   `pointermove`, sin tween ni transicion CSS. Un punto que va detras del raton
   hace que el usuario pulse donde ve el punto y falle el objetivo. Solo la
   marca (circulo y brazos) lleva suavizado.
2. **Nada se anima solo.** La cruz no gira. El destello es un disparo por
   entrada, no un bucle. Una animacion permanente e independiente del raton
   compite con "algo se mueve en la escena" para quien tenga temblor o baja
   atencion.
3. **Nunca se persigue la geometria de un elemento.** La marca escala sobre si
   misma; no encaja en el contorno de nada. En el carril de obra las cartelas
   se mueven con el scrub bajo un raton quieto: perseguirlas obligaria a leer
   `getBoundingClientRect` por fotograma.
4. **Si el JS falla, no se pierde ni una senal.** Ver "Lista blanca".
5. Solo `transform` y `opacity`. Sin `filter` ni `mix-blend-mode` animados: el
   fondo ya es un shader WebGL a pantalla completa.

## Reparto de senales

| Senal | Donde vive | Quien manda | Por que |
|---|---|---|---|
| `pointer` | botones, `.credit`, enlaces internos | **El cursor** | Es el glifo mas pobre y el unico cuyo mensaje la marca dice mejor |
| `grab` / `grabbing` | `.gallery-track` (`style.css:809`) | El navegador | Unica pista de que la galeria se arrastra: debe sobrevivir a un fallo del JS |
| I-beam | todo el texto corrido | El navegador | Ocultarlo quita la senal de que se selecciona y se copia |
| `pointer` de confianza | `a[target="_blank"]` (`projectScene.ts:112`, `contacto.ts`) | El navegador | Abren pestana nueva; la certeza de "esto es un enlace real" no se toca |

## Lista blanca — el truco que la hace segura

El CSS se apoya en que **`cursor` solo se hereda cuando el elemento no declara
el suyo**. `.gallery-track` declara `grab` y los `<a>` reciben `pointer` de la
hoja del navegador, asi que el `cursor: none` del lienzo NO les llega: hay que
apuntarlos uno a uno.

Eso da gratis la garantia que exigia el contrato: **un pulsable nuevo conserva
su glifo nativo mientras nadie lo opte explicitamente**. No hay forma de que
alguien anada una seccion y pierda una senal en silencio.

La clase `.vice-cursor-ready` la pone el JS SOLO tras montar con exito. Si el
modulo no carga o revienta antes, ninguna de esas reglas existe.

## Estados

| Estado | Aspecto | Cuando |
|---|---|---|
| Reposo | circulo 16px al 70%, cruz de 9px, punto 6px magenta | lienzo de escenografia |
| Pulsable | circulo a 30px, borde magenta, brazos al borde, mas un destello | sobre algo pulsable |
| Pulsado | se contrae a 23px con trazo de 2px, sin rebote | `pointerdown` |
| Ya activo | anillo interior y punto en ambar | `aria-pressed="true"` en `.credit` |
| Apagado | todo a `opacity: 0`, sin fundido | zona nativa |

El estado "ya activo" existe porque `credits.ts:109` pone `aria-pressed` y
ninguna otra senal visual del cursor lo reflejaba. Ojo: `credits.ts:130`
selecciona la fila en `mouseenter`, no en `click` — el estado "pulsable"
coincide con un cambio real de la pagina, asi que el cursor confirma algo que
ya ha pasado, no promete algo que pasara.

`aria-pressed` se relee **cada fotograma** a proposito: `credits.ts` lo cambia
en `mouseenter`, que puede llegar despues de nuestro `pointerover`.

## Puertas de montaje

El modulo **no se descarga siquiera** si falla alguna:

- `theme.id === "vice"`
- `!prefersReducedMotion`
- `matchMedia("(hover: hover) and (pointer: fine)")` — en tactil no hay hover
  que dispare ningun estado, asi que el coste correcto es cero, no "cero
  animacion"
- Ademas se monta **despues del leader**: montarlo antes solo lograria que la
  marca parpadease dentro de un gesto de 1,6 s

Limpieza en `pagehide`, junto al fondo y la barra de progreso.

## El bug del estado obsoleto (arreglado, no lo reintroduzcas)

Al desplazar la pagina, **el elemento bajo un raton quieto cambia sin que se
dispare ningun evento de puntero**. Sin nada mas, el estado se quedaba
congelado en el del elemento anterior. En Vice no es un caso raro: el carril de
obra mueve las cartelas por debajo del cursor mientras este no se mueve.

Se resuelve revalidando la zona con `document.elementFromPoint` en el
**siguiente fotograma** tras un scroll, no en el propio evento: `scroll` llega
en rafagas y hacerlo ahi seria un test de posicion por evento en lugar de uno
por fotograma pintado.

## Como medir esto sin enganarte

- **Lenis sigue desplazando la pagina despues de posicionar.** Dos medidas de
  esta sesion dieron falso positivo por leer antes de que asentara. Espera
  ~2,5 s tras cualquier `scrollIntoView`/`scrollTo`, o ancla la comprobacion a
  `document.elementFromPoint` en vez de a un selector.
- **En headless con `--use-gl=swiftshader` el rAF va tan lento** que la marca
  no alcanza al punto de clic y parece descentrada. No lo es: medido con el
  raton quieto, punto en (315.0, 416.1) y marca en (316.0, 416.0).
- Para depurar sin que el shader lo haga inviable:
  `page.route("**/viceInk*", r => r.abort())` (antes `viceHaze`, retirado).
