# Spec de Caelestia — Obra: el gestor de archivos deja de tener scroll interno

Estado: en ejecucion
Fecha: 2026-09-03
Plan: `docs/superpowers/plans/2026-09-03-caelestia-obra.md`
Alcance: la **fase B3** de las seis del rediseño de Caelestia — la escena `#obra` dentro del
workspace. Toca `src/sections/obra/projectScene.ts` (comparte los tres temas — cualquier cambio se
verifica en Vice y Hyprland), el bloque `:root[data-theme="caelestia"]` de `src/themes/themes.css`
y un gesto nuevo en `src/themes/caelestia.choreography.ts`.

**Vice no se toca** (cerrado el 2026-08-05). **Hyprland no se toca**: su cartel de obra
(`2026-08-10-hyprland-obra-cartel-design.md`) es un dispositivo distinto y **su gesto queda vetado
aquí explícitamente** — ver `## Lo que NO es`. La fase A (el shell) y B1 (Título) están cerradas y
**tampoco se tocan**. El fondo es de B1 y B3 lo hereda sin tocarlo.

Maqueta viva, rescatada al repo: `2026-09-03-caelestia-obra-maqueta.html`.

---

## Por qué

Medido sobre el build de producción, en la ventana de **1412 × 748** que impone el carril de
workspaces (`npm run build && npx vite preview`, `?theme=caelestia`):

| | antes | después |
|---|---|---|
| alto del contenido del carril | **4964 px** | 747 px |
| `overflow` de `div#obra.obra-rail` | **`auto`** (scroll interno) | ninguno |
| proyectos alcanzables sin desplazar | **1 de 5** | 5 de 5 |
| desborde del primer proyecto bajo el dock | **139 px** cortados | 0 |
| ancho muerto a la derecha de la superficie | **~300 px** vacíos | 0 |
| paleta de las capturas | placeholders morado/ámbar de **Vice** | huecos neutros 16:10 en tokens de Caelestia |

Dos defectos, y el primero es estructural: **cuatro de los cinco proyectos no existían dentro del
workspace** (fuera de la caja, entre y=1051 y y=5032), y **el carril tenía scroll interno**, que es
justo lo que la ley de la fase A prohíbe — *un espacio de trabajo no se desplaza, se cambia*.

---

## La decisión de partida: cada escena es una aplicación

Viene de la fase A y no se reabre. Obra es **el gestor de archivos** del escritorio. La agenda de
maquetado (`docs/superpowers/plans/2026-09-02-caelestia-obra-maquetado.md`) proponía un punto de
partida de tipo **lista-detalle** (columna de proyectos a la izquierda, ficha a la derecha,
Material genérico). **Se construyó, se enseñó y Aoshi la rechazó explícitamente** ("no me gusta esa
composición") por leerse como un panel de administración gris sin firma tipográfica propia — cajas
grises, mono/sans sin jerarquía.

### Composiciones descartadas

Comparadas en vivo dentro de la ventana real, con el motor de color copiado y contenido literal de
`content.ts`:

| Composición | Por qué se descarta |
|---|---|
| **A · Lista-detalle** | Rechazada por Aoshi tras verla — Material genérico, sin identidad. |
| **B · Galería tipo Finder** | El dock se solapa con la tira de miniaturas adicionales; no se llevó más allá de M2. |
| **C · Rejilla de carpetas** | El panel de detalle se abre como overlay sobre la rejilla y tapa las últimas dos carpetas mientras está abierto; funcional pero sin firma. |
| **D · Ficha de propiedades** (Get Info de Finder) | Buena ejecución —iconos reales de `simple-icons`, líneas de puntos— pero perdió contra E en la comparación directa. |

### Composición elegida: E · Editorial

Una **galería tipo revista**: las cinco tarjetas —captura 16:10, leyenda en Fraunces itálica— viven
en una fila horizontal siempre visible arriba, con inclinación alterna sutil por tarjeta
(±3–5°, que se endereza al pasar el ratón). Al seleccionar una, un **cajón** se abre debajo con la
ficha completa. Es la primera vez que la escala grande de Fraunces —hasta ahora reservada a
titulares de sección— entra en un componente de contenido secundario, y es precisamente lo que la
distingue de un panel de admin genérico.

**Probada contra los dos extremos de contenido** (M3): EchoPlan (el más largo, `problem`+`solution`
~550 caracteres, 2 capturas) y TesisFar (el único caso real sin `period` — ver la corrección más
abajo). Los dos caben en la ventana con el mismo margen, ~1 px de sobra sobre 748.

**Corrección de contenido durante la sesión:** un borrador intermedio de esta maqueta usaba
«Editor de texto» como el caso «sin `period`» — es un error: `content.ts` no le falta el campo a
Editor de texto (`period: "2024"`), es a **TesisFar** al que le falta por completo. Se corrigió
antes de cerrar M3/M5, y el hallazgo queda anotado para no repetirlo al implementar.

---

## Composición

```
~/obra ▸ vista editorial                                              1 / 5
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ 16:10  │ │ 16:10  │ │ 16:10  │ │ 16:10  │ │ 16:10  │   <- fila fija, siempre visible
│captura │ │captura │ │captura │ │captura │ │captura │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
 EchoPlan   TesisFar  HyprFinance  WatchDog  Editor de..  <- Fraunces itálica + rótulo mono
┌──────────────────────────────────────────────────────┐
│ GESTIÓN DE CAMPAÑAS      ROL           PROBLEMA   SOLUCIÓN
│ EchoPlan                 Desarrollo…   ...texto...  ...texto...
│ Todas las campañas...   [captura]     PERIODO
│ Proyecto privado ...                   STACK [iconos]
│                                        ESTADO
└──────────────────────────────────────────────────────┘  <- cajón, entra por Y
```

- **La fila de tarjetas no se mueve nunca.** Es la «lista quieta» del eje compartido de Material 3.
- **El cajón cuelga debajo**, con: título (`kick` + `h2` Fraunces), vista previa de la captura,
  metadatos (`Rol`/`Periodo`*/`Stack`/`Estado`), y `problem`/`solution` a dos columnas.
  `*Periodo` **desaparece la fila entera** cuando el proyecto no lo tiene — nunca un valor
  inventado. Igual que ya hace `projectScene.ts` en producción hoy.
- **Las marcas del stack son iconos reales monocromos de `simple-icons`** (los mismos SVG que
  `src/utils/icons.ts` ya inlinea), coloreados con `currentColor` — nunca el color de marca. Es la
  misma regla que ya impuso el cartel de Obra en Hyprland, por el mismo motivo: un logo con su
  color propio metería paletas ajenas en un tema que solo tiene los tokens `--cae-*`. `Zustand` no
  tiene slug en `simple-icons`: se pinta como texto, no se inventa un logotipo.
- **El pie de la ficha tiene dos estados** (M7): el enlace «Ver repositorio» en
  `--cae-primary`, con foco visible real y siendo **el único punto de tabulador de la ficha**; y la
  nota de proyecto privado, con un testigo apagado en `--cae-outline` — nunca el color activo, para
  no leerse como algo pulsable.

---

## El tratamiento de la captura (M4)

Caja neutra **16:10**, radio **16px** (mismo valor que ya usan la tarjeta flotante de la composición
D y el propio cajón — Material 3, no un número suelto), filete de 1px en `--cae-outline`.

**En reposo**: `filter: saturate(.52)` + un velo de `--cae-surface-container-high` al 16% en
`mix-blend-mode: multiply`. El velo funde la captura —de colores necesariamente ajenos, es una
imagen de otra aplicación— con la superficie de esa hora exacta, sea cual sea su matiz.

**Al seleccionar**: el velo desaparece, la saturación vuelve a 1, y aparece un anillo de 2px en
`--cae-primary`. La imagen se lee tal cual es, y solo entonces.

Probado con un **simulacro sintético** de paleta deliberadamente ajena (azul/coral/menta) — **nunca
los `.webp` de Vice**, que ya se descartaron por chillar en Caelestia — a las 09:00 (esquema claro,
matiz 195°) y a las 03:00 (esquema oscuro, matiz 105°). La regla aguanta en los dos: el velo no
depende del matiz porque usa el token de superficie, que ya gira con la hora por construcción.

**Bloqueo que sigue en pie:** las nueve capturas reales de `public/media/obra/*.webp` no existen —
son marcadores «CAPTURA PENDIENTE» con la paleta de Vice. Ver `## Bloqueo de implementación`.

---

## La selección (M5): el eje compartido es Y, no X

La agenda de maquetado sugería el eje de la composición de partida (lista-detalle, entrada por X).
Con **E** ya elegida, el eje real es otro: la lista (la fila de tarjetas) no se mueve, y lo que
entra es el **cajón, que vive debajo** — así que el eje compartido de Material 3 aquí es
**vertical**. La ficha entra con `y: 14→0`, `opacity 0→1`, 0,3 s en `--hard`
(`cubic-bezier(0.7,0,0.2,1)`).

**Pasar el ratón sin pulsar** solo levanta la tarjeta (`translateY -6px`, sombra que crece,
inclinación a 0°) — no abre nada. El cajón solo cambia con un clic.

---

## La entrada de escena (M6): Caída

El shell (barra, dock, ventana) ya está montado antes de que pase nada — nada de terminal ni
prompt, sería el tercer tema en repetir el mismo tic (B1 teclea `whoami`, B2 es la salida entera de
`neofetch`).

Se probaron **siete mecanismos** en total, en dos tandas. Primera tanda —tres curvas del mismo
mecanismo (revelar tarjeta a tarjeta)—: Cascada, Barrido, Expansión. **Rechazadas en bloque**
("no me gustan, sugiere mas ideas"). Segunda tanda —mecanismos distintos de verdad—: Carga por
lotes (shimmer de miniatura generándose), Montaje (todo el bloque en una pieza), **Caída**,
Indexado (barra de luz escaneando). **Caída fue la elegida.**

### Caída

1. La ruta `~/obra` se descubre en la barra con un recorte de izquierda a derecha (0,28 s,
   `power2.out`) — el mismo dispositivo de barrido que ya firma B1/B2, aplicado aquí a una etiqueta
   de una línea, no a un titular.
2. Las cinco tarjetas **caen desde arriba con una rotación por tarjeta** (−5°, 4°, −3°, 5°, −4° —
   ni todas iguales ni un gradiente ordenado, como un archivo que se suelta de verdad) y se asientan
   con `ease: bounce.out`, escalonadas 0,08 s. `transformOrigin: 50% 0%` para que la rotación pivote
   desde arriba, no desde el centro.
3. **El cajón no entra como bloque plano.** Cuatro capas propias, cada una tras la anterior:
   - el título (`h2`) se descubre con el mismo recorte de tinta que el `~/obra` de la barra —
     recorte, nunca fundido, coherente con la ley de sección que ya fijó el cartel de Hyprland
     ("aquí nada se desvanece: las cosas se recortan o se relevan");
   - `kick` (el rótulo del área) y la vista previa de la captura, con un `power2.out` corto;
   - las cuatro filas de metadatos, en cascada de 0,06 s;
   - los dos bloques de prosa (`Problema`/`Solución`), en cascada de 0,08 s.

   Este orden en capas fue una corrección durante la sesión: la primera versión de Caída animaba
   las tarjetas y luego el cajón entero como un solo `fromTo` — funcional, pero exactamente el
   defecto de "bloque plano" que ya se había señalado en las tres primeras variantes. Se descompuso
   el cajón en las cuatro capas de arriba antes de aceptar el gesto.

Repetir y el deslizador de velocidad (×0,4 por defecto, hasta ×0,1) forman parte del instrumento de
juicio, no del producto — sirven para ver la coreografía cuadro a cuadro, tal como pide la agenda.

---

## Movimiento reducido y las 03:00 (M8)

Con `prefers-reduced-motion: reduce`, la escena aterriza ya montada: primer proyecto seleccionado,
ficha ya escrita, sin shimmer, sin caída, sin barrido. `animation-name: none` en todo lo que en
movimiento normal fue transición.

**El croma no es el mismo en los dos esquemas** (lección ya pagada en B1: croma alto con claridad
baja da barro en OkLCH) — pero aquí no hace falta una regla aparte: el motor de color
(`caelestia.color.ts`) ya escala el croma por matiz (`chromaScaleAt`) y por esquema (`OSCURO`/
`CLARO` llevan su propia `c` por rol), así que las tarjetas, el cajón y las marcas del stack lo
heredan sin tocar nada. Verificado a las 03:00 (esquema oscuro, matiz 105°): la composición
completa —incluida la barra con forma de píldora real y el dock con los iconos de contacto reales—
se lee igual de bien que a las 09:00.

---

## Fidelidad del shell — corrección durante la sesión

Un borrador intermedio de la maqueta aproximaba la barra y el dock a mano (radio 10px, fondo con
`color-mix`, cuatro cuadrados grises como iconos del dock). **Aoshi lo señaló explícitamente**
("usa los actuales, se fiel a lo que tenemos"). Se corrigió calcando el DOM real
(`document.querySelector('.cae-bar'/'.cae-dock').outerHTML` contra el build servido en `:4373`):

- la barra es **una píldora completa** (`border-radius: 999px`), no un rectángulo redondeado;
- la pestaña activa del workspace lleva fondo `--cae-primary` / texto `--cae-on-primary`, no un
  simple resaltado de superficie;
- el dock lleva los **cuatro iconos de contacto reales** (correo, LinkedIn, teléfono, GitHub — los
  mismos SVG y los mismos enlaces que `index.html`), no marcadores vacíos.

Regla para lo que sigue: **cualquier maqueta nueva de esta fase arranca copiando el `outerHTML` real
del shell**, no aproximándolo.

---

## Contenido: leído, no copiado

Todo texto visible sale de `caseStudies` en `src/data/content.ts`: `title`, `tag`, `lead`, `role`,
`period` (cuando existe), `status`, `stack`, `problem`, `solution`, `gallery.length`, `link` o
`privateProject`. **`tooling` no se pinta** — existe solo para el cruce «Aparece en» de Créditos.
Verificado carácter a carácter contra el fichero real durante la sesión (ver la corrección de
`period` más arriba).

---

## Bloqueo de implementación

**Las nueve capturas reales de `public/media/obra/*.webp` no existen.** Los ficheros actuales son
marcadores «CAPTURA PENDIENTE» pintados con la paleta de Vice (morado `#150726` / ámbar) — dentro
de Caelestia leen como un error de tema, no como contenido pendiente, y **el gate visual de esta
fase no se da por bueno con marcadores**.

Es un encargo a Aoshi, no deuda de diseño. El plan de implementación puede escribirse y ejecutarse
con el hueco neutro 16:10 documentado arriba, pero **el spec queda bloqueado para cerrar el gate
visual final hasta que las nueve capturas existan**.

---

## Los gates

El arnés nuevo, `scripts/measure-caelestia-obra.py`, hereda de B1/B2 y tiene que comprobar al menos:

1. **Cabe, y sin scroll interno.** `scrollHeight === clientHeight` en el contenedor de la escena (o
   el margen medido: ~1px). Esta es la aserción que cazaba el defecto original — verla dar rojo
   contra el estado actual (4964 contra 748) antes de fiarse de que da verde.
2. **Los cinco proyectos son alcanzables** con teclado y con ratón, y ninguno queda fuera de la
   ventana. Medido por caja, no por presencia en el DOM.
3. **Ninguna captura queda cortada** por el borde de la ventana ni por el dock.
4. **Anti-mock**: todo texto visible existe en `content.ts`; `tooling` no aparece; la fila
   `Periodo` está ausente exactamente en TesisFar y presente en las otras cuatro.
5. **Aguanta los dos extremos**: EchoPlan (texto más largo, 2 capturas) y TesisFar (sin `period`).
6. **Contraste** de los pares reales —título/cajón sobre `surface-container`, rótulos sobre
   `on-surface-variant`, enlace en `primary`— barriendo las 24 horas, ≥ 4,5:1.
7. **Movimiento reducido**: escena montada, primer proyecto seleccionado, sin recorrido,
   `animation-name: none`.
8. **El foco visible funciona**: el enlace del pie es alcanzable por teclado y es la única parada
   de tabulador de la ficha; la nota de privado no lo es.
9. **Los ejes del shell no se han movido**, y **Vice y Hyprland siguen intactos** —
   `projectScene.ts` es compartido por los tres temas.

**Ningún gate se da por bueno sin haberlo visto dar rojo contra el fallo que dice cazar.**

---

## Lo que NO es

- **No es el cartel de Hyprland.** Ese gesto (la captura viaja con GSAP Flip hasta un visor grande)
  queda vetado aquí explícitamente — repetirlo convertiría dos temas en el mismo tema con otra
  paleta. Aquí la selección se resuelve con el cajón vertical descrito arriba.
- **No es una tercera terminal.** Ninguna de las variantes de entrada probadas usa prompt, cursor
  parpadeante ni texto tecleado.
- **No hereda `.gallery-item`/`.gallery-caption` de `src/style.css`** (el tratamiento pensado para
  Vice) — el hueco de captura es un componente propio de esta fase.

---

## Trampas de medición pagadas en esta sesión — que no se repitan

- **`page.screenshot()` perturba el estado de GSAP, no solo el compositor.** Una medición en la
  propia página, tomada inmediatamente después de un `page.screenshot()` anterior, dio 18px de más
  de forma repetible — no una carrera de fuentes (se descartó con `document.fonts.ready` y doble
  `requestAnimationFrame`, sin efecto), sino la propia tween de entrada todavía en marcha. Solución:
  medir con un `setTimeout` que cubra la coreografía completa, nunca inmediatamente tras pintar.
- **Un bug de compositor de Chromium headless + swiftshader con `filter:blur()`** hizo que
  `page.screenshot()` de página completa mostrara un fondo claro incorrecto en esquema oscuro,
  mientras `getComputedStyle` y una captura aislada del elemento (`element.screenshot()`) mostraban
  el valor correcto los tres. Se evitó sustituyendo los `blob` decorativos por
  `radial-gradient` en vez de `filter:blur()` — no era necesario perseguir más el instrumento
  porque el valor real ya estaba verificado por dos vías independientes.
- **`Zustand` no tiene marca en `simple-icons`.** Confirmado contra `src/utils/stackIcons.ts`
  (`slugDeStack` ya devuelve `null` para él en producción) — la maqueta reproduce el mismo
  comportamiento, no lo inventa.

---

## Preguntas abiertas para el plan

1. **De dónde sale la vista previa del cajón y la captura de la fila.** `components/gallery.ts`
   construye un carril arrastrable pensado para Vice; esta fase necesita **una** imagen por
   proyecto en dos tamaños (miniatura 16:10 pequeña en la fila, la misma en el cajón). Hay que
   decidir si se reutiliza el primer `.gallery-item` vía CSS o si `projectScene.ts` expone un
   gancho propio — mismo tipo de decisión que ya resolvió el cartel de Hyprland para su miniatura.
2. **Reordenación de `projectScene.ts`.** La fila necesita título, rótulo y miniatura como hermanos
   directos; el resto pasa a ser el cajón. Cuánto se resuelve con CSS antes de tocar la estructura
   compartida por los tres temas.
3. **El ordinal gigante actual** (`clamp(7rem,26vw,22rem)` a `paper/[0.06]`) es un dispositivo de
   Vice — en Caelestia no tiene sitio en esta composición (no hay números de fila visibles); se
   oculta solo en Caelestia, igual que ya se ocultó en Hyprland.
4. **Las nueve capturas reales.** Bloquea el gate visual final, no el plan ni la implementación del
   resto de la escena — ver `## Bloqueo de implementación`.
