# Traspaso — remodelacion de "Quien es" (tema Vice)

> Escrito el 2026-07-29 para que **otra sesion** ejecute el trabajo. Esta sesion
> no toco la seccion: solo levanto los hechos y las restricciones. Todo lo que
> hay aqui esta medido contra el codigo, no deducido.

## Que hay que hacer

Rediseñar `[data-scene="about"]` **en el tema Vice**, siguiendo el mismo metodo
que se uso para el cursor y para el cartel de reparto de creditos:

1. `superpowers:brainstorming` con el **companion visual** — mockups vivos,
   servidos, no capturas ni artifacts.
2. Convocar a `especialista-animaciones` y `especialista-ux-ui`, y proponer
   **opciones que los dos firmen**. El usuario ya rechazo dos veces el formato
   "ranking con descartes": quiere alternativas de consenso, no un podio.
3. Iterar sobre la elegida hasta ver los estados/variantes antes de tocar `src/`.

**No empieces a implementar hasta que el usuario elija.** El patron de las dos
sesiones anteriores fue: mockups -> "me gusta la B" -> iteracion sobre B ->
aprobacion explicita -> codigo.

## Estado del repo al escribir esto

Branch `design/creditos-cartel`, con **~16 ficheros modificados sin commitear**
(el cursor de Vice y el arreglo de la escalera de `refreshPriority`, mas la
puesta al dia de la documentacion). **Commitea o haz rama nueva antes de tocar
nada**, no trabajes encima de un arbol sucio ajeno.

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"   # Node del sistema es 18; Vite 8 exige >=20
npm run dev        # http://localhost:5173/?theme=vice
npm run build      # tsc + vite build
npm run lint
python3 scripts/verify.py
```

El tema se sortea por visita: **siempre `?theme=vice`**.

## Donde vive la seccion

| Fichero | Que hace |
|---|---|
| `src/sections/about.ts` (111 lineas) | Construye TODO el DOM. Compartido por los tres temas |
| `src/data/content.ts` | `identity`, `stats`, `aboutCopy`, `education`, `experience`, `focusAreas` |
| `src/style.css` | Base compartida: `.about-grid`, `.about-card`, `.about-facts`, `.about-stats`, `.about-track`, `.about-item`, `.about-line` |
| `src/themes/themes.css` (~lineas 118-215) | Bloque Vice: **solo escala y ritmo**, ni un color ni una estructura nueva |
| `src/themes/vice.choreography.ts` (~380-480) | `scene2Card` — gesto 2 "Subtitulado" |

## Que hay hoy en pantalla (no lo re-deduzcas)

Titulo `h2.hero-kick` = **"Quien es"** (tercera persona, no "Quien soy"), y
debajo `.about-grid` a dos columnas desde 860px:

**Columna izquierda — ficha (`[data-card]`)**: avatar de GitHub 76px, nombre en
display, estado ("Disponible para proyectos") con punto, y un `<dl>` de cuatro
pares: Rol / Base / Ahora / Estudia.

**Columna derecha (`.about-body`)**, en este orden:
1. Dos lineas de `aboutCopy`, cada una envuelta en su mascara `.about-line`.
2. Franja `[data-stats]` de cuatro cifras: **2021 Desde · 10 Semestre ·
   5 Proyectos · 1 En produccion**.
3. `[data-track]` a dos columnas:
   - **Trayectoria** — 1 experiencia (Pasante B2C, Telefonica Venezuela,
     Ago 2025 — May 2026) + 2 estudios (Ingenieria de Sistemas USM;
     100 Days of Code, Udemy).
   - **En que me enfoco** — 2 areas: "Datos a gran escala" e "Interfaces que
     aguantan".

**Densidad real: 1 experiencia, 2 estudios, 2 focos, 4 cifras.** Es poco
contenido para dos columnas — el hueco es probablemente el problema de diseno
de verdad, y conviene atacarlo en el brainstorm en vez de re-maquetar lo mismo.

## El gesto que existe hoy (gesto 2 — "Subtitulado")

`scene2Card`, cinco ScrollTrigger con id fijo (`vice-about-card`, `-lines`,
`-stats`, `-track`, `-parallax`), todos con
`start: "top 78%"`, `toggleActions: "play none none reverse"`:

- La ficha lleva **parallax con scrub** (`yPercent` -5 -> 5, `start: top bottom`,
  `end: bottom top`) **y a la vez** una entrada de `x`/`scale`/`clipPath`. No se
  pisan porque son propiedades distintas sobre el mismo nodo — patron ya
  validado. Si reorganizas, mantenlo separado asi.
- Lineas: `yPercent 105` con mascara, stagger 0.12.
- Cifras y items de trayectoria entran **por elemento, no por bloque**
  (stagger 0.09 / 0.06, delay 0.35 / 0.5). El comentario del codigo explica por
  que: mover la masa entera de golpe deja al ojo sin saber donde mirar.

## Restricciones duras — verificadas

1. **`about.ts` lo comparten los tres temas.** Hyprland y Caelestia visten el
   mismo DOM como widgets de interfaz. Cualquier cambio de estructura tiene que
   ser **aditivo**: nodos que los otros dos temas puedan ignorar por CSS, no una
   reorganizacion que les rompa la rejilla.
2. **`scene-surface` no es decorativo.** Esta en `.about-card`, `.about-stats` y
   las dos `.about-track-col` porque en Caelestia el fondo es un shader animado
   (`caelestiaBlobs`) y sin superficie el texto cae por debajo de 3:1 / 4.5:1
   — medido con el arnes de contraste. **No lo quites de esos tres sitios.**
3. **`scripts/verify.py` mide contraste WCAG sobre esta escena.** Si el rediseno
   quita una superficie o cambia el peso del texto sobre el fondo de Vice
   (`viceHaze.ts` en el momento de este handoff; hoy es `viceInk.ts`, la
   serigrafia de tinta — ver `2026-08-04-vice-fondo-tinta-design.md`), vuelve a
   correr `check_contrast_wcag`. No lo des por hecho.
4. **`gsap.from` esta prohibido en este repo** — deduce un extremo leyendo el DOM
   y ha causado tres regresiones reales. **`scene2Card` lo usa hoy CUATRO veces**
   (card, lines, stats, track): es deuda preexistente en la seccion exacta que
   vas a tocar. Si reescribes el gesto, pasalo a `fromTo` con los dos extremos
   escritos a mano, y `Array.from(...)` para colecciones vivas.
5. **Un `transform` inline de GSAP gana siempre a una regla CSS.** Todo lo que
   reciba entrada con GSAP no puede tener hover con `transform` en CSS: anima un
   hijo o el envoltorio.
6. **Si anades un pin de ScrollTrigger, entra en la escalera de
   `refreshPriority`** (descendente por orden de documento: hero 2, carril de
   obra 1, resto 0). Saltarse esto es exactamente lo que rompio el scroll
   horizontal el 29-jul-2026: el carril refrescaba antes que el hero, no veia
   sus 1665px de pin y colocaba su inicio 1605px antes de tiempo.
7. **`prefers-reduced-motion`**: `initScrollReveal` hace early-return con
   reduced-motion, asi que cualquier motion que muevas a CSS necesita su propia
   media query.
8. **Los dos temas restantes usan `data-reveal="fade-up"`** en la seccion porque
   no definen coreografia propia. Si lo quitas, entran sin animar.

## Preguntas abiertas para el brainstorm

1. **El desequilibrio de densidad.** La ficha es corta y la columna de texto
   larga; hoy se compensa con `align-self: center` y quedan ~150px de aire
   muerto repartidos. Un rediseno serio decide si la ficha crece, si el texto
   se reparte, o si la rejilla deja de ser 2x1.
2. **"Trayectoria" con una sola experiencia.** Dos columnas para 3 items y 2
   items respectivamente es mucho contenedor para poco contenido. ¿Se funden?
   ¿Se convierte en una linea de tiempo horizontal? ¿Se integra en la ficha?
3. **Movil (390x844).** Hoy todo se apila. Verificar antes de dar nada por hecho.
4. **Coherencia con lo ya elegido.** El cursor es la "marca de sincronismo" y
   creditos va hacia "cartel de reparto". La ficha de about tiene lenguaje de
   **ficha tecnica de rodaje** — vale la pena explorar si esa es la metafora que
   la unifica, o si compite con el cartel de creditos.

## Metodo de medicion — trampas ya pagadas

- **Verifica en el build de produccion, no en dev**, cuando el fallo sea de
  layout o ScrollTrigger: el HMR de Vite corrompe sus medidas y miente en los
  dos sentidos.
- **A/B antes que hipotesis**: si sospechas de un modulo, bloquealo con
  `page.route("**/<modulo>*", r => r.abort())` y vuelve a medir. Un minuto,
  sin tocar codigo. Esto descarto el cursor como causa de la regresion del pin.
- **`git worktree add` para comparar contra HEAD, NUNCA `git stash`**: un
  `stash --include-untracked` ya se llevo por delante una sesion entera.
- **Lenis sigue desplazando despues de `scrollTo`**: espera ~2,5s o ancla la
  comprobacion a `document.elementFromPoint`.
- **`page.screenshot()` en headless perturba GSAP**: para medir ritmo, muestrea
  `tl.progress()` desde dentro de la pagina.
- Bloquea el shader mientras depuras layout:
  `page.route("**/viceInk*", r => r.abort())` (era `viceHaze` en el momento de
  este handoff; el fondo de Vice cambio de modulo en `2026-08-04-vice-fondo-tinta`).

## Arnes

`python3 scripts/verify.py` deja **12 fallos preexistentes**, todos ajenos a esta
seccion (9 rellenos de galeria en `public/media/obra/`, 3 ficheros
`public/media/vice-*` del video que ya no carga nadie). **Cualquier fallo
distinto de esos 12 lo has introducido tu.** `npm run build` y `npm run lint` en
verde: mantenlos.

## Estilo

TypeScript strict, cero `any`, cero emojis. Comentarios en espanol **sin
tildes**, densos, que expliquen POR QUE y no QUE — y que suelan incluir la
medicion que motivo la decision. Es el estilo del repo.

## Companion visual

```bash
~/.claude/plugins/cache/claude-plugins-official/superpowers/6.2.0/skills/brainstorming/scripts/start-server.sh \
  --project-dir /home/aoshi/proyectos/portfolio-aoshi --open
```

Sirve el fichero mas reciente de `content/`. Los mockups anteriores viven en
`.superpowers/brainstorm/2975344-1785280534/content/` (cursor, estados del
cursor, alternativas de creditos) y se pueden abrir directamente del disco.
**Los mockups son interactivos y vivos, nunca capturas ni artifacts** — es una
preferencia explicita del usuario.
