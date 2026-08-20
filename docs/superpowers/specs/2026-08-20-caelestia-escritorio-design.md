# El escritorio — Caelestia deja de ser una piel y pasa a ser un shell gobernado por la hora

Estado: en diseno
Fecha: 2026-08-20
Alcance: la fase A (el shell) de un rediseño en seis fases. Toca `src/themes/caelestia.ts`,
el bloque `:root[data-theme="caelestia"]` de `src/themes/themes.css`,
`src/backgrounds/caelestiaBlobs.ts` (que se retira) y un módulo de coreografía nuevo para el tema.
**Vice no se toca** (cerrado el 2026-08-05). **Hyprland no se toca.** `shaderBackground.ts` es
compartido y no se modifica.

Hay **una excepción, y es la parte cara**: el cambio de workspace obliga a bifurcar el arranque en
`src/main.ts`, que comparten los tres temas. Ver `## El cambio de workspace` y el criterio de
aceptación que lo cubre.

---

## Por qué

Caelestia no falla por gusto. Falla porque no es un tema, es un juego de tokens.

**1. No tiene dispositivos ni coreografía propios.** Comparado con los otros dos, medido leyendo el
árbol:

| | Vice | Hyprland | Caelestia |
|---|---|---|---|
| Módulo de coreografía | `vice.choreography.ts` | `hypr.choreography.ts` | **ninguno** |
| Dispositivos de sección | carril, cartel de reparto, carta de ajuste | lomo, cartel, placa, catastro, cinta | **ninguno** |
| Líneas del módulo de tema | — | — | **15** |
| Líneas del fondo | — | — | **49** |

Los otros dos temas tienen un gesto que los define. Caelestia no tiene ninguno, y por eso se lee
como una piel puesta encima del mismo sitio.

**2. Una sola tipografía hace dos trabajos.** En `themes.css`:

```css
--font-display: "Outfit", system-ui, sans-serif;
--font-body:    "Outfit", system-ui, sans-serif;
```

Sin contraste de voz, la jerarquía tiene que salir entera del tamaño. El tamaño solo no construye
personalidad, y ese es el diagnóstico exacto de por qué el tema se lee plano.

**3. No hay escala tonal, que es lo único que Material You realmente aporta.** Las superficies son
siempre la misma:

```css
background: color-mix(in srgb, #ffffff 62%, transparent);
backdrop-filter: blur(24px) saturate(1.25);
```

Un único valor para todos los contenedores. Sin rampa de elevación, todo flota a la misma altura, y
un sistema cuya tesis es la elevación tonal se queda sin su tesis.

**4. El fondo son cuatro manchas difuminadas orbitando.** `caelestiaBlobs.ts` mezcla cuatro
`smoothstep` sobre una base. Es atmósfera sin estructura — el tic que este proyecto ya tiene
identificado como marca de diseño generado por IA.

**5. El tema declara "Material You" y no lo ejecuta.** El comentario de `caelestia.ts` dice
literalmente *"Material You: unico tema claro, muy redondeado, motion blando y amable"*. Material
You no es redondeo: es **color derivado de una fuente externa**. Un tema que lo cita sin derivar
nada está tomando prestado el nombre.

---

## Direcciones descartadas, y por qué

- **Material You bien ejecutado, sin más.** Aunque se hiciera perfecto, sigue siendo el sistema de
  otro. No da autoría.
- **Semilla fija violeta (`#6750A4`).** Es la baseline que Google publica, y también la del tema
  actual. La respuesta por defecto.
- **Índigo + jade.** Descartada por el autor: es el cluster número uno de paleta generada por IA.
  Propuesta y retirada el mismo día.
- **Arco de matiz corto (62°) y arco mineral de croma bajo.** Resuelven la colisión con los otros
  temas pero pierden el gesto: el color deja de leerse como algo que pasa.
- **Roboto / Roboto Flex.** Es la tipografía oficial de Material 3 y gana la discusión conceptual.
  Se descarta porque en su propia escala (Display Large en Regular) la jerarquía sale solo del
  tamaño — el mismo síntoma que tiene Outfit hoy. Cambiar Outfit por Roboto arregla el argumento y
  no arregla la página.
- **Ubuntu Sans, Gabarito, Unbounded, Anybody, Archivo, Gloock, Young Serif, Bodoni Moda,
  Piazzolla.** Evaluadas contra el contenido real. Ver `## Tipografía`.

---

## Dirección elegida — el escritorio

Caelestia es un **shell de escritorio Material You 3**, y su gesto firma es que **el color y el
esquema los gobierna el reloj del visitante**.

Eso no es decoración: es lo que hace un escritorio de verdad, y convierte el reloj de la barra —que
en cualquier otra propuesta sería adorno— en la pieza que manda sobre todas las demás. Es la
respuesta directa al diagnóstico 1: el tema pasa a tener un comportamiento, no solo una piel.

### Elemento firma

**El matiz recorre los 360° de la rueda a lo largo de 24 horas.** Un visitante a las 09:00 y otro a
las 21:00 no ven el mismo Caelestia. La claridad no se mueve nunca, así que el contraste tampoco.

---

## El motor de color

### Por qué OkLCH y no HSL

En OkLCH la claridad (`L`) es perceptual e independiente del matiz (`H`). Si se fijan `L` y `C` por
rol y solo gira `H`, **el contraste es invariante por construcción**: se mide una vez y vale para
las 1.440 posiciones del reloj. En HSL eso es falso y el color dinámico sería temerario.

`oklch()` es CSS nativo. El coste estimado es ~40 líneas de TypeScript y **cero dependencias**: no
hay que reimplementar HCT ni CAM16.

### Roles

`L` y `C` constantes por rol. `C` se multiplica además por la marea de croma (abajo). `H` es el
único valor que se mueve con la hora.

| rol | claro `L` | claro `C` | oscuro `L` | oscuro `C` |
|---|---|---|---|---|
| `surface` | 0.980 | 0.012 | 0.185 | 0.016 |
| `surface-container` | 0.955 | 0.020 | 0.235 | 0.022 |
| `surface-container-high` | 0.925 | 0.026 | 0.285 | 0.026 |
| `on-surface` | 0.245 | 0.035 | 0.925 | 0.016 |
| `on-surface-variant` | 0.470 | 0.032 | 0.795 | 0.024 |
| `outline` | 0.700 | 0.022 | 0.420 | 0.020 |
| `primary` | 0.505 | 0.130 | 0.815 | 0.115 |
| `on-primary` | 0.990 | 0.010 | 0.270 | 0.095 |
| `primary-container` | 0.895 | 0.062 | 0.395 | 0.105 |
| `on-primary-container` | 0.310 | 0.100 | 0.900 | 0.062 |

### El matiz

```
H(minutos) = (minutos / 1440 * 360 + 60) mod 360
```

El desfase 60 es el preajuste **mediodía frío**, elegido por el autor tras medir la alternativa. Con
el desfase 270 (*amanecer rojo*, la primera elección) la jornada laboral caía así:

| hora | matiz | croma efectivo | lectura |
|---|---|---|---|
| 09:00 | 45° | 32% | tostado |
| 11:00 | 75° | 32% | **crema** |
| 13:00 | 105° | 44% | oliva |
| 15:00 | 135° | 70% | verde |
| 17:00 | 165° | 96% | teal |

El crema a las 11:00 es exactamente el cliché de fondo que el proyecto rechaza, y caía justo en la
franja de más tráfico. Con desfase 60, las 11:00 miden `oklch(0.505 0.130 225)` — azul a croma
pleno, verificado en el navegador.

### La marea de croma

El matiz recorre la rueda entera, así que en algún momento entra en el naranja de Hyprland y en el
magenta de Vice. No se recorta el arco: se **baja la voz** en esos tramos.

```
d = distancia angular entre H y 240°
croma = 1                             si d <= 70
croma = max(0.32, 1 - (d - 70) / 115) si d > 70
```

Resultado: croma pleno entre ~170° y ~310° (la mitad fría), y un tercio de croma en el territorio
cálido. Cuando Caelestia pasa por donde vive Hyprland no es ascua, es piedra tostada.

### El ancla

Un color que **no gira**, para que el tema tenga algo constante que recordar.

```
azufre = oklch(0.855 0.152 96)      /* claro */
azufre = oklch(0.905 0.152 96)      /* oscuro: +0.05 de L, tope 0.92 */
sobre azufre = oklch(0.215 0.050 96)
```

Amarillo verdoso mineral, no dorado. No está en la paleta por defecto de Material, ni en la de
Tailwind. **Tiene un solo trabajo: marcar lo accionable** — el botón de contacto, la marca de
disponibilidad y el anillo de foco de teclado. Ningún otro uso.

---

## El esquema, y la regla dura que salió de una medida

**Claro de 07:00 a 20:00 locales. Oscuro fuera.** El claro es el canónico: es la franja en la que se
abre un portfolio, y mantiene la sacudida de los tres mundos frente a Vice y Hyprland, que son
oscuros.

### El esquema no se interpola nunca

Detectado por el autor a las 19:43 en la maqueta, con una banda de transición de 45 minutos a cada
lado. La superficie viaja de `L` 0.980 a 0.185 y el texto de 0.245 a 0.925: **intercambian el
orden**. Cualquier recorrido continuo entre los dos esquemas pasa obligatoriamente por el punto en
que ambos tienen la misma claridad.

| hora | `L` superficie | `L` texto | contraste |
|---|---|---|---|
| 19:15 | 0.980 | 0.245 | 15.32:1 |
| 19:35 | 0.803 | 0.396 | 5.07:1 |
| 19:45 | 0.715 | 0.472 | 2.68:1 |
| **19:55** | **0.627** | **0.547** | **1.38:1** |
| 20:15 | 0.450 | 0.698 | 2.77:1 |
| 20:45 | 0.185 | 0.925 | 14.94:1 |

> Los ratios de esta tabla se calculan con una aproximación de luminancia a partir de `L`
> (`Y ≈ L³`), suficiente para mostrar el cruce. **Los valores exactos WCAG los mide el arnés**, no
> esta tabla. Lo que no depende de la aproximación es la conclusión: si dos claridades intercambian
> el orden por un camino continuo, se cruzan, y en el cruce el contraste es 1:1. No hay easing ni
> banda más corta que lo evite.

**Regla:**

1. El esquema se decide **una sola vez, al cargar**, con el reloj del visitante.
2. No se interpola jamás. Ni con `transition` de CSS sobre los colores, que interpola igual.
3. Si el visitante deja la pestaña abierta y cruza el umbral, el cambio es **instantáneo** y lo
   anuncia el shell con una notificación ("El escritorio ha cambiado a modo noche"). Es lo que hace
   un escritorio.
4. Lo continuo es **solo el matiz**, y eso sí es seguro porque la claridad no se mueve.

En la implementación, el corte instantáneo se consigue desactivando las transiciones durante el
fotograma del cambio, no confiando en que no haya ninguna declarada.

---

## Tipografía

| rol | familia | ajuste |
|---|---|---|
| display | **Fraunces** | `opsz 9 · wght 900 · SOFT 0 · WONK 1` |
| cuerpo | **Hanken Grotesk** | 400 / 600 |
| utilidad | **Martian Mono** | `wdth 87.5` · 400 |

Las tres están en Google Fonts con esos ejes (verificado: HTTP 200 en la API de `css2`).

**Fraunces** es variable y tiene dos ejes que casi nadie toca: `SOFT` redondea los ángulos y `WONK`
activa formas alternativas deliberadamente torcidas. Con `opsz` a 9 los remates se afilan y el
contraste sube. Es una serifa, pero no la serifa elegante de catálogo.

Por qué una serifa aquí no repite a Hyprland: en `themes.css`, `--font-said: "Instrument Serif"`
aparece en **una sola regla de todo el fichero** (línea 1364) y está reservada a las frases en
primera persona. El display de Hyprland es Bricolage Grotesque. Aquí la serifa es la voz de cartel,
que es un papel distinto.

Al ser Fraunces variable, los cuatro ejes pueden afinarse durante la implementación sin reabrir la
decisión de tipografía.

---

## El shell

### La barra

Persistente, arriba, flotante con `border-radius` completo. De izquierda a derecha:

- **Marca** `caelestia`, en Martian Mono, color `primary`.
- **Pastillas de workspace**: las cinco escenas, numeradas 1–5, con su nombre. La activa toma
  `primary` de fondo y `on-primary` de texto, y ensancha su padding.
- **Bandeja**: marca de disponibilidad (punto en azufre + "Disponible") y **el reloj**, en Martian
  Mono y color `primary`. El reloj no es adorno: es lo que gobierna el tema, y tiene que verse.

### El dock

Centrado, **dimensionado a su contenido** — no estirado a todo el ancho, que es lo que hace que un
dock parezca un pie de página. Contiene:

- GitHub, LinkedIn, correo y teléfono, como iconos de 21px en celdas de 46px con radio 15px.
- Punto de "abierto" bajo GitHub y LinkedIn, como marca un dock lo que está corriendo.
- Separador, currículum en PDF, separador, y bandeja con la marca de disponibilidad.
- **Etiqueta al pasar** (tooltip encima), no etiqueta permanente.
- Al pasar: elevación de 7px y fondo en azufre.

### La ventana

Cada escena vive en una ventana con radio 20px sobre `surface-container`. **La ventana desplaza su
propio contenido**; lo que cambia entre escenas es el workspace, no el scroll.

### La notificación

Abajo a la derecha, contenedor tonal con punto en azufre. Dos disparos previstos:

1. **Al entrar**: "Disponible para proyectos".
2. **Al cruzar el umbral de esquema**: "El escritorio ha cambiado a modo noche".

---

## La ley de la sección

> **Cada escena tiene que resolverse en su primera pantalla.** Lo que quede bajo el pliegue es
> ampliación, nunca lo que hacía falta para entender la escena.

Con scroll de página esto era una recomendación. Con workspaces es un requisito, porque un visitante
puede cambiar de pastilla sin haber desplazado nada.

Medido en la maqueta a 1400×1150, con el contenido real y una ventana de 724px de alto:

| escena | alto de contenido | ¿desplaza? |
|---|---|---|
| Título | cabe | no |
| Quién soy | 724 | justo, no desplaza |
| Obra | 749 | sí |
| Créditos | muy por encima | sí |
| Fundido | muy por debajo | no — **deja media ventana vacía** |

Dos encargos que salen de aquí y van a la fase B: **Créditos** no puede ser una lista de 23 nombres
que empieza y sigue —necesita un resumen que valga por sí solo—, y **Fundido** llega corta. Con
scroll eso no se notaba porque la sección simplemente terminaba; con ventana de workspace, el vacío
es visible.

---

## El cambio de workspace

Al pulsar una pastilla, la escena sale por un lado y entra la siguiente. **No hay scroll de
página.** La dirección la marca el orden de las escenas. Duración de referencia: 520 ms con
`cubic-bezier(.2, 0, 0, 1)` (la curva `emphasized` de MD3).

Un workspace no se desplaza, se cambia. Es el gesto que sostiene la metáfora; con desplazamiento
suave, la barra sería un menú con reloj.

### El riesgo, dicho por delante

El sitio usa Lenis y coreografía de scroll. En Caelestia hay que desactivar ambas y montar la escena
por índice, y eso **bifurca el arranque en `src/main.ts`**, que comparten los tres temas. No es un
módulo nuevo aislado como `viceInk` o `hyprEmber`: es una rama en el punto común.

Es el único lugar del plan con riesgo real de rozar a Vice, que está cerrado. La mitigación es una
tarea de verificación explícita, no una promesa. Ver criterios de aceptación.

### Qué está prohibido

- Tocar `shaderBackground.ts`.
- Cambiar el orden o la estructura de las secciones en el DOM compartido.
- Que la rama de Caelestia en `main.ts` altere ninguna ruta de código que recorran Vice o Hyprland.

---

## Movimiento

- Curva base: `cubic-bezier(.2, 0, 0, 1)` (`emphasized` de MD3) en todo lo que se abre, entra o
  cambia de estado.
- Cambio de workspace: 520 ms.
- Recolor del matiz: 700 ms. Es continuo y no cruza nada, así que puede ser lento.
- Cambio de esquema: **0 ms**, por la regla de arriba.
- Dock y pastillas: 280 ms.
- `prefers-reduced-motion: reduce` anula toda transición y deja el cambio de workspace instantáneo.

---

## Accesibilidad

- **Contraste**: se mide una vez por rol y por esquema. Es válido para todas las horas por
  construcción, pero **hay que demostrarlo con el arnés**, no darlo por bueno.
- El azufre es también el color del anillo de foco (`:focus-visible`, 2px, offset 3px). Como no
  gira, el foco es el único elemento cuyo contraste no depende de la hora.
- Las pastillas de workspace son `<button>` reales dentro de un `<nav>` con `aria-label`.
- Los iconos del dock llevan `aria-label`; la etiqueta visual es un tooltip decorativo.
- La notificación no roba el foco.

---

## Criterios de aceptación

1. `npm run build` y `npm run lint` en verde.
2. **Vice y Hyprland renderizan idénticos antes y después**, con captura comparada contra `HEAD` en
   desktop y móvil. Es el criterio que cubre la bifurcación de `main.ts` y es bloqueante.
3. Un arnés nuevo, `scripts/measure-caelestia-hora.py`, que inyecta la hora y comprueba:
   - el contraste de `on-surface` sobre `surface` y de `on-surface-variant` sobre
     `surface-container`, muestreando las 24 horas, en los dos esquemas;
   - que **no existe ninguna hora** con un ratio por debajo de 4.5:1;
   - que en el minuto anterior y el posterior al umbral (06:59/07:00 y 19:59/20:00) el contraste no
     baja en ningún fotograma intermedio;
   - que el matiz a las 11:00 es 225° ±1.
4. El cambio de workspace no dispara ScrollTrigger ni deja Lenis vivo en Caelestia.
5. Cero errores de consola y cero avisos de contexto WebGL perdido.
6. `python3 scripts/verify.py` sale con código 0.
7. Captura en navegador real, no solo headless, en día y en noche.

---

## Preguntas abiertas para el plan

1. **El wallpaper generativo.** `caelestiaBlobs.ts` se retira, pero su sustituto no está diseñado —
   es un paso propio. Lo único fijado: **el color lo pone el motor de la hora**, no el shader.
   Mientras tanto, `--bg-fallback` cubre el hueco.
2. **Móvil.** La barra con cinco pastillas y el dock con seis celdas no caben a 390px. Hay que
   decidir si las pastillas se reducen a números, si el dock se colapsa, o ambas.
3. **El currículum en PDF** del dock: no existe el fichero. O se produce o se quita la celda.
4. **Qué pasa con el scroll del navegador** cuando el sitio deja de desplazarse en Caelestia:
   la altura del documento, el comportamiento del botón atrás y el enlace directo a `#obra`.

---

## Las fases siguientes

Esta spec cubre **solo la fase A**. Cada una de las siguientes lleva su propio spec y su propio
plan, igual que se hizo con Hyprland:

| fase | qué decide |
|---|---|
| B1 · Título | el hero: qué se ve en los primeros dos segundos |
| B2 · Quién soy | trayectoria, cifras y los dos focos, resueltos en una pantalla |
| B3 · Obra | los cinco proyectos con sus capturas — la que más dispositivo necesita |
| B4 · Créditos | los 23 nombres, con un resumen que valga solo |
| B5 · Fundido | contacto, que hoy llega corta y deja media ventana vacía |

Las cinco dependen del shell y no al revés: hasta que no esté fijado cuánto alto deja la barra,
cuánto come el dock y cómo se cambia de escena, diseñar una sección es diseñar a ciegas.

---

## Procedencia

Las decisiones de este documento se tomaron sobre maquetas vivas e interactivas, no sobre
descripciones. Viven bajo `.superpowers/brainstorm/` y **no están versionadas** (el directorio está
en `.gitignore`): son material de trabajo, no entregable. Lo que se conserva de ellas son los
números que aparecen en este spec.
