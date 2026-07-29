# portfolio-aoshi

Portfolio personal de **Aoshi Blanco Sanz** — desarrollador full stack, Caracas.
Una sola página, en español, sin backend.

## Lo que tiene de particular

No es un portfolio con un tema y un modo oscuro. Son **tres pieles completas sobre un
mismo DOM**, y la que te toca **se sortea en cada visita**. No hay selector: es una
decisión de diseño, no una funcionalidad pendiente.

Eso condiciona todo lo demás. El marcado no sabe de qué tema es —lo decide el CSS a
través de `data-theme` en `<html>`— así que cualquier cambio en una sección se juzga en
las tres pieles, no en la que tenías abierta.

| tema | id | carácter |
|---|---|---|
| Vice City | `vice` | cartel de cine ochentero: coreografía de scroll, letterbox, cursor propio |
| Hyprland | `hyprland` | piel de interfaz, estética de tiling window manager |
| Caelestia | `caelestia` | piel de interfaz clara, superficies Material You |

Para trabajar o verificar, **fija el tema por query string** o estarás depurando a ciegas:

```
http://localhost:5173/?theme=vice
```

El override existe para QA y capturas reproducibles (`pickTheme()` en `src/themes/index.ts`).

## Stack

Vite 8 · TypeScript 6 en modo `strict` · Tailwind 4 · GSAP 3 (con ScrollTrigger) · Lenis.

Sin framework, sin backend y **sin Three.js**: los fondos son *shaders* de fragmento
WebGL escritos a mano en `src/backgrounds/`, no una escena 3D. Es un detalle que conviene
tener claro antes de proponer soluciones.

## Arrancar

Requiere **Node 22** (está en `.nvmrc`). Vite 8 no arranca por debajo de 20, y en algunas
máquinas el Node del sistema es más antiguo:

```bash
nvm use                 # lee .nvmrc
npm install
npm run dev             # http://localhost:5173
```

| comando | qué hace |
|---|---|
| `npm run dev` | servidor de desarrollo |
| `npm run build` | `tsc && vite build` — si TypeScript se queja, el build falla |
| `npm run preview` | sirve el build de producción ya generado |
| `npm run lint` | ESLint |
| `python3 scripts/verify.py` | arnés de verificación en navegador real (ver abajo) |

## Cómo está organizado

```
index.html          script inline que sortea el tema antes del primer pintado
src/main.ts         punto de entrada: resuelve tema, compone escenas, monta en #app
src/sections/       una escena por archivo, cada una marcada con data-scene
src/components/     piezas reutilizables (cromo de cine, galería, cursor, carril)
src/backgrounds/    shaders WebGL crudos, uno por tema
src/themes/         tokens en themes.css; la coreografía de Vice en vice.choreography.ts
src/data/content.ts TODO el contenido, en un solo sitio
src/utils/          dom, iconos, scroll reveal
scripts/verify.py   arnés de verificación
docs/superpowers/   specs, planes y bitácora de las iteraciones de diseño
```

**Lee el directorio, no confíes en una lista.** Una enumeración de secciones en prosa se
desactualiza siempre: este proyecto ya arrastró documentación citando `experience` y
`caseStudies` como secciones mucho después de que dejaran de existir.

Dos cosas que cuesta descubrir solo:

- **`src/sections/skills.ts` produce `data-scene="credits"`.** El nombre del archivo y el
  id de la escena no coinciden: la sección se rediseñó como cartel de reparto y el id
  siguió al diseño, no al archivo.
- **Las cinco escenas de obra son la misma plantilla** (`src/sections/obra/projectScene.ts`)
  instanciada una vez por proyecto, dentro de un carril horizontal.

## Convenciones que no son negociables

Ninguna es preferencia estética. Cada una salió de una regresión real:

- **Nunca `gsap.from`.** Deduce un extremo leyendo el DOM y ya causó tres regresiones.
  Usa `fromTo` con los dos extremos escritos a mano, y `Array.from(...)` para colecciones
  vivas.
- **Un `transform` inline de GSAP gana siempre a una regla CSS.** Si un elemento recibe
  entrada con GSAP, su hover se anima en un hijo o en un envoltorio, nunca en el mismo
  nodo.
- **Todo módulo de tema devuelve un handle con `destroy()`**, y se llama en `pagehide`
  (no en `beforeunload`: en móvil y con bfcache no dispara de forma fiable). Hay que
  borrar programa y buffers de WebGL, cancelar `requestAnimationFrame` y matar las
  timelines. Fugas equivalen a *context lost*.
- **Todo pin de ScrollTrigger en Vice entra en la escalera de `refreshPriority`**
  (descendente según el orden del documento: hero 2, carril de obra 1, resto 0). Sin
  ella, el carril de obra se fija encima de la sección "Quién es".
- **Ningún trigger de entrada de Vice se ancla a `[data-scene]`.** En Vice esa caja lleva
  más de 200px de padding de tema y las escenas van centradas, así que el primer píxel
  útil puede caer por debajo del pliegue: los delays se gastan fuera de pantalla. Ánclalo
  al primer nodo de contenido.
- **`prefers-reduced-motion` siempre.** El scroll reveal hace early-return y ni siquiera
  importa GSAP, así que lo que deba morir con `reduce` va en GSAP; lo que deba sobrevivir
  (un hover, por ejemplo) va en CSS **con su propia media query**.
- **Cuidado con `display: contents`.** Borra la caja del elemento, así que ni una timeline
  ni un ScrollTrigger pueden anclarse a él: un rect a cero se mide en `top = 0` del
  documento y el trigger dispara al cargar, sin error ni aviso.
- Sin `any` (usa `unknown` con guards). Sin `console.log` en producción. Sin emojis.
  Comentarios en español, y que expliquen **por qué**, con la medida que motivó la
  decisión.

## Seguridad

Es un frontend estático: **todo lo que va al bundle es público**, incluido cualquier
`import.meta.env.VITE_*`. Nada secreto en el cliente. Los enlaces externos llevan
`rel="noopener noreferrer"`, y los datos que vengan de fuera (query params incluidos) se
escriben con `textContent`, nunca con `innerHTML`.

## Verificación

Este proyecto es shader y animación: que compile no demuestra nada. Antes de dar algo por
terminado:

```bash
npm run build && npm run lint
python3 scripts/verify.py
```

`scripts/verify.py` es el arnés. Tiene dos mitades:

- **Sin navegador, primero y en segundos:** comprueba que la documentación no cite rutas
  del repo, binarios del sistema o dependencias que ya no existen, y que el `Estado:` de
  cada spec no contradiga las casillas de su plan. Nació de fallos reales: cinco ficheros
  daban Three.js como stack, y un plan quedó con 47 casillas sin marcar mientras su spec
  se declaraba terminado. **Este README entra en esa comprobación**, así que si citas aquí
  una ruta que borras luego, el arnés lo caza.
- **Con navegador real:** tipografías, contraste WCAG por escena, galerías, cromo de cine
  y degradación con `prefers-reduced-motion`.

Los fallos conocidos y aceptados viven en `scripts/verify-baseline.json` (hoy 12, todos
rellenos de imagen pendientes en `public/media/`). **El arnés sale 0 mientras la ejecución
coincida con esa lista, y 1 en cuanto aparezca uno nuevo o se arregle uno sin quitarlo de
ahí.** Para regenerarla:

```bash
python3 scripts/verify.py --update-baseline
```

Para capturas usa Playwright con `--use-gl=swiftshader`, o el canvas WebGL sale en negro.

### Trampas de medición ya pagadas

Léelas antes de medir algo. Todas costaron tiempo:

- **Lenis sigue desplazando la página después de `scrollTo`/`scrollIntoView`.** Medir
  antes de que asiente da falsos positivos *y* falsos negativos. Replica
  `_scroll_to_and_settle()` de `scripts/verify.py`: rueda simulada y espera a que
  `window.scrollY` deje de cambiar. Un `scrollTo` mueve el scroll nativo pero **no** el
  target interno de Lenis.
- **`page.screenshot()` en headless perturba GSAP:** bloquea el compositor y la timeline
  salta hacia delante. Para medir ritmo, muestrea `tl.progress()` desde dentro de la
  página; para fotogramas concretos, `tl.pause()` más `tl.progress(x)`.
- **Verifica en el build de producción, no en `dev`,** cualquier fallo de layout o de
  ScrollTrigger: el HMR de Vite corrompe sus medidas y miente en ambos sentidos.
- **Para comparar contra `HEAD` usa `git worktree add`, nunca `git stash`.** Un
  `stash --include-untracked` ya se llevó por delante una sesión entera de trabajo.
- **A/B antes que hipótesis.** Si sospechas de un módulo, bloquéalo con
  `page.route("**/<modulo>*", r => r.abort())` y vuelve a medir.
- El arnés necesita memoria: con menos de ~3 GB libres, el navegador muere a mitad de la
  pasada con *execution context was destroyed*. Eso es presión de memoria, no una
  regresión.

## Contenido

Todo el texto, los proyectos, las tecnologías y los datos de contacto viven en
`src/data/content.ts`. Es la única fuente de verdad: las secciones no llevan texto
incrustado, y no debe quedar ni un placeholder en lo publicado.

## Estado

`main` es la rama de producción y la única publicada; la iteración de diseño va en ramas
`design/*`, que se quedan en local. **Sin deploy todavía**: el sitio no está en ninguna
URL, así que el repositorio es, por ahora, la única forma de verlo — clonar, `npm install`
y `npm run dev`.

Cuando haya deploy hay que actualizar este párrafo. Un README que sigue diciendo "sin
deploy" con el sitio en producción es exactamente el tipo de deriva que el arnés no puede
detectar: comprueba que las rutas existan, no que lo escrito siga siendo verdad.

## Licencia

Sin licencia pública. Todos los derechos reservados: el contenido, los textos y las
imágenes son personales.
