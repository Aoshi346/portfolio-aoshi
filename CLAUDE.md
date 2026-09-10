# Project Standards — portfolio-aoshi (Aoshi Blanco Sanz)

## Commands
- Install: `npm install`
- Dev: `npm run dev` (Vite, http://localhost:5173)
- Build: `npm run build` (`tsc && vite build`)
- Preview prod build: `npm run preview`
- Lint: `npm run lint`

## Never Do
- Use `any` type (use `unknown` with guards) — `strict` is on
- Put secrets in `import.meta.env.VITE_*` (embedded in the public bundle)
- Inject external/untrusted data via `innerHTML` (XSS) — use `textContent`
- Leak WebGL/GSAP resources — always delete program/buffers + cancel RAF + kill timelines on teardown
- Use `gsap.from` — it infers one end by reading the DOM and has caused three real regressions. Use `fromTo` with both ends written by hand, and `Array.from(...)` for live collections
- Give a GSAP-animated element a CSS `transform` hover — the inline transform always wins. Animate a child or the wrapper
- Add a ScrollTrigger pin to Vice without placing it in the `refreshPriority` ladder (hero 2, obra rail 1, rest 0 — descending by document order)
- Change `OBRA_TRANSIT` / `OBRA_REST` in `vice.choreography.ts` without changing the same constants in `scripts/measure-obra-rail.py` — the harness reimplements the obra rail's master timeline to know where the track *should* be. Out of sync it does not fail, it lies. Same trap one level up: the rail's pin reserves less scroll than the lateral travel (5040 vs 5760), so anything measuring the pin window against `distance` is measuring the wrong thing
- Put `data-scene` on anything that is not a scene. It is how the site marks its five sections, so `:root[data-theme="vice"] [data-scene]` hands the element `padding: calc(9rem + 6.5vh)` — 202.5px top and bottom, measured — and Vice's choreography walks `[data-scene]` to know where it is. The index rows carried it once: rows grew to 405px, the five stopped fitting in a 900px viewport, and the first one landed at `top: -545` — off screen and unclickable
- Size type with a continuous function over scale tokens. `clamp(var(--t-2), 6.2cqi, var(--t-3))` has no `px` literal and still returns any real number between its stops: 46 of 65 measured combinations landed on 17.09 / 18.39 / 20.51px. It hides at 390 and 1440, which is exactly where a clamp lands on its clean stops. Step discretely — a `@container` or `@media` that swaps one token for another
- Reuse an opacity across themes. A percentage is calibrated against a surface, not a token: 55% of `--color-paper` reads 5.74:1 over Vice's dark scrim and 3.72:1 over Caelestia's light one, which fails AA. Carry the number and you carry nothing — say in the comment which scrim it was measured against, and give each theme its own value (`--nav-dim`)
- Set a numeric threshold that is tighter than its instrument's noise. 480ms for a 460ms animation is under two frames of slack, so it measures machine load, not the animation. Prefer the declared value (deterministic) and keep the stopwatch as a sanity check with explicit margin
- Write a theme's choreography without destructuring `gsap` from the context it is handed. `hyprChoreography` took only `ScrollTrigger` and `root` and used a bare `gsap`: `tsc` and `eslint` both passed — the identifier exists in the type space — and the built chunk threw `gsap is not defined` the moment `reveal.ts` called it, so Hyprland's choreography ran *nothing*, background treatment included. Only the browser console catches this
- Trust a contrast measurement without opening the console first. Every number for the Hyprland cursor was measured for weeks against a page whose choreography was crashing, so the shader read far brighter than it really is. No assertion could detect it: they all compared the page against itself. `.hero-mail` went from 4.29:1 to 6.38:1 *without touching the cursor* once the crash was fixed
- Ship animations without a `prefers-reduced-motion` fallback
- `console.log` in production code
- `git push --force` / `git push origin main` without approval
- Declare DONE without a build + a real browser screenshot

## Theme Status
- **Vice: DONE.** Closed with the `2026-08-04-vice-fondo-tinta` plan (background `viceInk.ts`, a
  two-ink halftone poster; the scene-nav trigger lost its box, gained a register mark). Reviewed
  live by Aoshi, `lidia-naive-tester` gate green, `vera-art-director` gate BLOCK explicitly
  accepted (7.12/10 against a 7.5 gate — the residual is a known, accepted product finding, not a
  defect). **Do not touch Vice** (background, nav trigger, choreography, typography) unless Aoshi
  asks for it explicitly. Full record in `docs/superpowers/specs/2026-08-04-vice-fondo-tinta-design.md`.
- **Caelestia: all six phases (A, B1-B5) are MERGED.** The theme's design is closed; two things
  keep it from being DONE, and neither is design work: **B3 needs the nine real project captures**
  (today they are "CAPTURA PENDIENTE" markers painted in *Vice's* palette) and **B4 has two open
  product P1s**. Also open: `measure-caelestia-obra.py` fails three contrast assertions — **it failed
  the same way before B5 merged** (verified in a separate worktree against `1f61752`), and the shape
  of the failure (`bg=rgba(0, 0, 0, 0)`) points at its own instrument, not at the CSS. Read each
  phase's block below before touching anything.
- **Caelestia's interface review with Aoshi (2026-09-05/06) is MERGED into `main`** (`1c246eb`,
  branch `fix/repaso-interfaces`, not pushed). Nine dictated faults fixed one by one, each with
  its gate seen red first: the hero no longer paints before the choreography arrives
  (`js-cae-entrada`), the shell toast no longer fires on load, the terminal leaves before the
  name is traced, bar and dock enter (CSS, `no-preference`), the Obra drawer fills the window as
  an elevated sheet with layered text relay, C and Zustand icons from Devicon Plain, scenes 4/5
  renamed **Stack** and **Contacto**, the "Disponible" chip left the bar. Two design changes came
  out of it: the **"Ahora mismo" card** was redesigned (`2026-09-05-caelestia-ahora-mismo`, order
  who/what/status, no box, live 240-vertex figure, entrance blooming from its light; Vera 6.6
  BLOCK residual, Lidia 6.4) and the **Contacto dino is a toy** (jump, eye follow, and dragging is
  a *glance* at another hour that undoes itself on release; the troquel spins with a spring and
  **the generative background follows the glance** via `caelestia:hora`). Full record, including
  the ten mistakes paid during the session (measuring at 1412x748, a commit claiming
  `verify.py` green while it was red, subagents stalling on background monitors, OOM with
  parallel harnesses, the hour hook not reaching the background), in
  `docs/superpowers/specs/2026-09-05-caelestia-repaso-interfaces.md`. **Do not re-measure the
  card at 1412x748**: that is the inner window with a 1440x900 page.
- **Hyprland and Caelestia: IN PROGRESS.** Current focus. They share `shaderBackground.ts` with
  Vice (don't touch that module without confirming Vice still renders) but each has its own
  background (`hyprGradient.ts` / `caelestiaBlobs.ts`), palette, and typography — see `src/themes/themes.css`.
  The obra section in Hyprland has a new device (the cartel, `2026-08-10-hyprland-obra-cartel`
  plan and spec): five titles always on screen, captured screenshot travels with GSAP Flip into a
  large viewer on click. Contrast against the real shader background measured per-glyph (not
  viewport-wide, which overstated it): only the resting title dips below AA, and only in the
  shader's brightest 0.5% of frames (3.88:1) — a shader brightness ceiling, pending a product
  decision, not an illegibility problem (see the spec's `Registro de implementación` /
  `Color y contraste`). The "Con qué construyo" section (the Stack scene) was redesigned and
  merged on 2026-09-10 — see its own block below. Hyprland overall stays IN PROGRESS.
- **Hyprland's cursor is DONE and merged** (`2026-08-19-hyprland-cursor-luz`): "the adaptive
  hollow". Pointing at something pressable opens a pool clipped to the element — it **darkens
  where the background is bright and lights up where it is already dark**, with the edge lit and a
  dot marking the hand; over running text it goes out and the system cursor takes over. The sign is
  decided by the luminance of the background occluding the `z-index: -4` canvas, read once per
  target. Two mechanisms: the canvas for targets with nothing opaque above it, an inline
  `background-image` for the rest (it paints above the element's own background and below its
  text). `scripts/measure-cursor-luz.py` gates it, and its **assertions are split by family** —
  the darkening one must improve contrast, the lighting one must hold an AAA floor *and be
  perceptible*. One gate for both could only demand what holds for both, which is nothing, and that
  already slipped through once. Read the spec's epilogue before re-tuning anything: the whole
  calibration predates the `gsap` fix.

- **Hyprland's Stack scene is MERGED** (`2026-09-09-hyprland-stack-cimientos`, spec state
  `en ejecucion` until Aoshi reviews it on the real site): the catastro is retired and
  `[data-scene="credits"]` is now **"los cimientos"** — three area columns from `skillGroups`
  (Interfaz 8, Backend y datos 5, Herramientas 5, widths 550/344/344 at 1440, ratio 1.6/1/1) over a
  2px `--l1` floor line carrying the five base languages one type step **above** the names. The
  composition is the sentence: three things he builds, resting on five things he knows. **There is
  no hierarchy between the 23 names** — the old device sized them by how many projects used them,
  and that data does not stretch (seven technologies appear in no public project, the four
  transversal ones appear in all five). The hierarchy is between strata.
  New module `src/components/hyprStackCimientos.ts`, **no GSAP**: an `IntersectionObserver` decides
  when, CSS marks the times. **`credits.ts` is NOT touched** — its generic DOM is hidden whole,
  the pattern Caelestia's B3/B4 proved. Retiring the catastro removed 1,662 lines (797 CSS, 526
  harness, 339 choreography) with Vice and Caelestia byte-identical, verified by `git worktree`.
  Gated by `scripts/measure-cimientos.py` (14 families; gate 10, the contrast one, sits behind
  `--contraste`). Contrast per glyph against the live shader: name 9.66:1, area label 5.79:1,
  language 15.65:1, icon 6.53:1 against a 3:1 decorative floor, hovered 9.66:1, phrase 9.35:1.
  - **The entrance is commanded by the floor**: the ember line traces left to right, lights the
    five languages in its wake (each delay derived from its own x, not written by hand), and only
    then do the columns grow from it by clipping. One lighting in the scene, not twenty-three.
    Its trigger is anchored to the **device's own box**, never the section's — the same fix this
    branch made to the placa, where an entrance ran to completion 119px below the fold for a month
    with the harness green.
  - **The phrase lives in the air, not under the floor's label.** Hovering, focusing or tapping a
    name lights it `--l3` and writes that technology's literal `detail` in Instrument Serif italic
    inside the 48px of air between the columns and the floor. It first sat beside "LENGUAJES BASE",
    and **both critique gates independently called that a defect**: for the 18 names that are not
    base languages it read as a template bug. Moving it up costs zero pixels — the air was already
    there — and the 48px gap the gate measures is unchanged.
  - **What the harness had to learn the hard way, twice.** A mouse click used to extinguish the
    name under the cursor: `blur` on the previously focused button fired `apagar()` without
    checking who was active. And **gate 4 never clicked with a mouse anywhere** — it hovered,
    tapped and used the keyboard — so a gate titled "the hover extinguishes on leaving" was green
    while ordinary clicking blanked the device. Separately, `gate 6` compared the painted phrase
    against the DOM's own copy of the string, both written by the same line: it now parses the 23
    `detail` values out of `content.ts` and fails loudly if the parse comes back empty.
  - **Two rulings worth keeping.** The reduced-motion guard is written selector by selector on
    purpose (`*` does not reach pseudo-elements) and the apuntado rule is scoped with
    `[data-cimientos]` so it beats the entrance rule **structurally**, not because it appears later
    in the sheet. Below 1024px the device stacks: between 821 and 1023 the 8/5/5 proportion
    collapses to equal columns and "Claude Code" wraps, so the stacked band runs to 1023 and gate
    8 only measures three columns from 1024 up.
  - **`measure-cursor-luz.py` now exits with exactly 1 expected failure**, and that is written in
    its own docstring. Retiring the catastro removed `.credit`, its **only occluded target** — the
    one exercising the `background-image` mechanism instead of the canvas. `.cim-nombre` is not a
    replacement (the cimientos have no opaque background), so the harness says what is missing and
    since when instead of substituting a softer target. **Giving that family a new occluded target
    is an open commission.**
  - Open, and recorded in the spec: the cursor's orange edge around the 23 new buttons (that is the
    separate cursor commission), the scene selector's stale silhouettes, retiring the dead nodes
    `credits.ts` still builds (`.credits-rail`, `.credits-glow`, `.credits-spark` and
    `STRIP_REPAINT_EVENT`, which now has no listener), that `8fr 5fr 5fr` is hand-written and
    mirrors counts that live in `content.ts` with no gate comparing them, and that
    `measure-cimientos.py` is hooked nowhere — it is launched by hand, by decision.
  - Gates: `lidia-naive-tester` 6.3/10 red on the phrase's old placement, **fixed**;
    `vera-art-director` **BLOCK residual 6.22→7.42/10**, 0.08 under the gate, **zero actionable
    P0s**, and she certifies that the two findings which blocked the catastro are closed by
    construction. Residual accepted: the 1px `--rule` dividers are indistinguishable from the
    shader in the lower third of each column (measured pixel by pixel; it is the token's luminance
    sitting inside the shader's range, the same brightness ceiling the theme already carries), and
    GSAP's icon is a wordmark that does not scale like the rest of the set at 20px.

- **Caelestia's cursor is BUILT and gated, pending merge** (`2026-09-04-caelestia-cursor`, branch
  `design/caelestia-cursor` in the `portfolio-aoshi-cursor` worktree): **"la gota"** — a drop of the
  hour's pigment. It is a theme-wide device, not one of the B1-B5 phases. Over pressables it tenses
  into a pearl and waits; **on click it spills and floods the target to its edges**; over
  hover-select targets (`button[aria-pressed]`, the Credits pieces) it spills on entry instead. Over
  running text it goes out and the system I-beam takes over. The two states are not two symbols —
  they are **one gesture fired at two moments**, which is how it satisfies "a cursor cannot have a
  manual". DOM, not canvas (it needs `backdrop-filter` and `mix-blend-mode`), and **no GSAP**: CSS
  transitions only, so the mount stays synchronous. No trail, no positional inertia.
  `src/components/caelestiaCursor.ts`, gated by `scripts/measure-caelestia-cursor.py` (8 gates, 53
  assertions, every one seen red against the failure it claims to catch).
  - **The night spill's opacity is 0,20 and the day's is 0,22 — do not unify them.** They are
    different mixes: `multiply` over light paper darkens the text's background, `screen` over dark
    surface lightens it, and that is what eats contrast. At 0,30 the Obra caption fell to 4,06:1 at
    06:30, below AA; at 0,20 the worst of the 24-hour sweep is **4,92:1**. The margin is 0,43, not
    an order of magnitude — re-run gate 6 whole before touching it.
  - **The spec's fallback (paint the spill under the text as an inline `background-image`, the
    Hyprland pattern) is worse here, not a safety net**: a `background-image` paints below the
    element's children, and the Obra card has an `<img>` filling its box, so the spill would vanish
    in the scene where it shows most. That open question is closed.
  - `destroy()` retires live rings **through `retirarCerco`**, never a raw `remove()`: it is the
    only path that also cancels their 1200ms backstop timer.

- **Caelestia's shell is DONE and merged** (`2026-08-20-caelestia-escritorio`, phase A of six): the
  theme stopped being a set of tokens and became **a Material You 3 desktop shell whose colour and
  scheme are governed by the visitor's clock**. The hue walks the full 360-degree wheel over 24
  hours; lightness never moves, so **contrast is invariant by construction** — measured once, valid
  for all 1440 clock positions. Scheme is light 07:00-20:00, dark outside, and **never interpolated**:
  surface and text swap lightness order, so any continuous path between schemes crosses 1:1 contrast.
  Proven in motion, not just by arithmetic: sampling every ~15ms across the threshold, `L` jumps
  0.245 to 0.925 in one step with no intermediate value in 90+ samples.
  The five scenes are a **horizontal workspace rail** — a workspace is not scrolled, it is switched —
  so the theme has no page scroll and inactive workspaces are `inert`. `sceneNav` is hidden here
  (`display: none`): the bar already carries the five scenes as always-visible pills, and its panel
  changed the hash without moving anything. Fraunces (`opsz 9 wght 900 SOFT 0 WONK 1`) over Hanken
  Grotesk and Martian Mono. `scripts/measure-caelestia-hora.py` gates it with 16 assertions.
  **Phases B1-B5 (the five sections inside the window) are NOT done** — *true when phase A closed;
  all five are merged today, see their blocks below.* Their layout still assumed a page that
  scrolls, so cramped content inside a workspace was expected, not a defect.
  `vera-art-director` gate BLOCK explicitly accepted (6.55/10 against a 7.5 gate), same as Vice: its
  P0 was fixed, its three P1s are open product decisions recorded in the spec.
  **Read the spec's `Registro de implementación` before re-tuning anything.** It records the lesson
  that cost this phase most: **eight times the failure was in the instrument, not the design** — a
  regex reading `oklch()` as RGB bytes (1.00:1 everywhere), a frozen clock that made the
  threshold-crossing branch unreachable *by construction*, a PNG-size proxy that passed against the
  very shader it existed to catch, a focus assertion titled "and uses the anchor" that only read
  `outlineStyle`, contrast `PARES` watching roles that are never painted, and an A/B that triggered
  the warning it was measuring (`page.screenshot()` forces its own `ReadPixels`). The spec's numbers
  all held. **Never accept a gate you have not seen go red against the failure it claims to catch.**

- **Caelestia's phase B1 (Título) is DONE** (`2026-08-26-caelestia-titulo`, first of the five
  inside-window phases): the `#hero` scene stopped being cramped shell leftovers and became **the
  desktop presenting itself** — a justified three-line headline at `opsz 144` (the shell stays at
  `opsz 9`; two separate tokens, `--cae-display-axes-cartel` vs `--cae-display-axes`, never one
  reused), a signature and a right-edge stat column, an "Ahora mismo" widget built entirely from
  `content.ts` literals (no derived field invented — `10.º semestre` is parsed out of
  `education[0].period`'s parenthetical, not a new field), and a `whoami`-typed terminal entrance
  whose signature lands as 15 traced Fraunces glyph paths. The background is new too:
  **`src/backgrounds/caelestiaBlobs.ts` no longer exists** — it's `src/backgrounds/caelestiaFiguras.ts`
  now, five Material 3 Expressive figures (puffy/sunny/cookie/clover/burst) that morph with the
  visitor's hour and share `shaderBackground.ts` (float-uniform-only, so a `vec3`/`vec2` in the
  approved prototype got split into loose floats and rebuilt inside the shader). Hovering the
  widget or a stat nudges the whole background aside via a CSS transform, reduced-motion skips the
  entrance straight to the landed state, and the ink-sweep/number-flip closing gestures run off the
  same timeline. `scripts/measure-caelestia-titulo.py` gates it with the eight assertion families in
  its own docstrings — all eight were seen red against the exact failure they claim to catch before
  being accepted (see the spec's implementation notes for what broke each one). **Mobile is
  explicitly out of scope for B1**: the headline's justification target is a fixed 1080px measure
  with no narrow-viewport fallback, so at 390px the titles overflow and the stat column overlaps
  them — known, not a regression to chase. **B2-B5 (Quién soy, Obra, Créditos, Fundido, still
  inside the same window) remain pending** — *true when B1 closed; all four are merged today.*
  B1 only closes `#hero`.
  `lidia-naive-tester` gate green (7.1/10, zero P0). `vera-art-director` gate came back **BLOCK**
  initially (6.36/10 against the 7.5 gate) on a real P0, not a polish issue: the phase-A generic
  workspace-panel rule gave Título the same opaque `background` as the other four scenes (which
  ARE application windows), covering 78% of the generative background — fixed before accepting the
  gate (a scoped CSS exception for `[data-scene="hero"]`, reviewed, no leak to the other scenes or
  to Vice/Hyprland). Three polish findings remain accepted as known debt (a typography-scale gap
  recurring for the 5th time project-wide, widget spacing off the 4/8px grid, one repeated font-axis
  literal) — full detail in the B1 spec's implementation record and "Gates de crítica" section.
- **Caelestia's phase B2 (Quién soy) is DONE and merged** (`2026-09-02-caelestia-quien-soy`, second
  of the five inside-window phases). The `#about` scene stops being a cramped card and becomes **the desktop's
  own `neofetch` output**: a typed `~ $ neofetch` entry, a name/email/status header with a filete
  measured by `Range` (not the `<span>`'s block box, which reports the container's width), a
  `key: value` field list sourced entirely from `content.ts`, and a portrait clipped to a
  `clip-path: polygon(...)` that morphs between two Material 3 figures on hover.
  `scripts/measure-caelestia-quien-soy.py` gates it with 8 assertion families (38 checks); the shell
  harness `scripts/measure-caelestia-hora.py` (16 assertions) stays green, confirming phase A is
  untouched. **The trap not to repeat:** a `clip-path: polygon()` only interpolates against another
  polygon with the **same vertex count** — mismatched point counts (240 vs a lower count) silently
  fall back to a hard cut, no error, no warning. And `*` in a `prefers-reduced-motion` CSS guard does
  **not** reach pseudo-elements — `.ficha-k::before` needed its own explicit rule to stop animating
  under reduced motion; the generic wildcard guard missed it.
- **Caelestia's phase B3 (Obra) is MERGED but still `en ejecucion`** (`2026-09-03-caelestia-obra`,
  third of the five inside-window phases). The `#obra` scene stops being a 4964px rail inside a
  748px window (4 of 5 projects unreachable, plus internal scroll — exactly what phase A's law
  forbids) and becomes **the Editorial**: five always-visible cards (16:10 capture + Fraunces
  italic caption, alternating ±3-5° tilt that straightens on hover) in a fixed row, with a
  **drawer** opening below carrying the full project sheet. New module
  `src/components/caelestiaObraEditorial.ts`. **`src/sections/obra/projectScene.ts` was NOT
  touched** — better than the plan foresaw: that DOM stays as-is for Vice/Hyprland and under
  Caelestia `themes.css` hides it whole instead of rewriting it. Entrance gesture is **Caída**
  (cards fall with a per-card rotation and `bounce.out`; the drawer enters in four separate layers,
  never as a flat block) — no typed terminal, that would have been the third one. Gated by
  `scripts/measure-caelestia-obra.py`.
  **Why it is not DONE:** the nine real captures in `public/media/obra/*.webp` do not exist — they
  are "CAPTURA PENDIENTE" markers painted in **Vice's** palette (purple/amber), which inside
  Caelestia read as a theme error. That is a commission for Aoshi, not design debt; the visual gate
  stays blocked until they exist. Mobile out of scope, same as B1/B2.

- **Caelestia's phase B4 (Créditos) is MERGED and `en ejecucion`** (`2026-09-03-caelestia-creditos`,
  fourth of the five inside-window phases). The `#credits` scene stops being a plot-share layout
  with 10px of internal scroll, 424 dead px at the right edge and **four group labels that existed
  in the DOM and painted none**, and becomes **the package tray**: if each Caelestia scene is an
  application, Credits is the package manager — what is installed on this machine. Four equal-height
  bands (one per territory, label right-aligned in a 158px gutter), 23 fixed 142px modules, all 23
  technologies always on screen. New module `src/components/caelestiaCreditosBandeja.ts`;
  **`src/components/credits.ts` is NOT touched and NOT branched by theme** — its generic DOM is
  hidden whole from `themes.css`, the same pattern B3 proved with `projectScene.ts`.
  - **Size encodes nothing.** All 23 pieces are one size (88px, a single value in the whole DOM).
    Both possible yardsticks lie: a global one inflates Herramientas because `tooling` is in all
    five projects; a per-territory one makes JavaScript (one work) as big as Git (five).
  - **23 unique Material 3 figures**, one harmonic family, **240 vertices each** — two `polygon()`s
    only interpolate with the same vertex count. They are rebuilt at runtime from a 23-row table in
    `src/utils/figurasM3.ts` (the generator emits 167KB of literals and they are not needed:
    dividing by `rmax` is redundant once you box-fit by each axis' *span*, measured at 4.4e-16).
  - **Hover selects without clicking**; focus reaches the same. Entrance is **"la instalación"**:
    the 23 arrive as identical circles — unopened packages — and morph to their figure, in a wave by
    territory. No typed terminal: that would have been the third after B1 and B2.
  - Gated by `scripts/measure-caelestia-creditos.py` (9 assertion families). **It takes over two
    minutes** because of the 24-hour sweep: launch it with `nohup` and wait on the PID.
  **Why it is not DONE:** `vera-art-director` came back **BLOCK (5.3/10 against a 7.5 gate)`, accepted
  as residual like Vice/shell/B1 — but its two product P0s were fixed first (`2b8db2c`).
  `lidia-naive-tester` green (7.1/10, zero P0), with two open product P1s: the hover gesture is not
  discoverable, and "Aparece en" does not link to the Obra scene, breaking the *"knows X → used it
  in Y"* chain that is this scene's whole contribution. Mobile out of scope, same as B1/B2 — today
  at 390px the scene already carries 154px of internal scroll, which B4 neither fixes nor worsens.
  **The lesson that cost this phase most is about instruments, again:** the entrance ran *on mount*,
  finishing 2803ms in with the scene **4334px outside the viewport** — the signature gesture of the
  phase was never once seen. It was a regression against a pattern the same theme had documented one
  phase earlier (`caelestiaObraEditorial.ts` listens for `caelestia:workspace`). And **its gate had
  two assertions, both on the reduced-motion path**: titled "the entrance", it never checked that the
  entrance happened. It is the ninth tautological instrument in this track and the only one not
  caught by sabotage — it was caught by looking at the scene. **A gate that only measures the
  degraded branch does not watch the path the visitor sees.**
- **Caelestia's phase B5 (Fundido) is DONE** (`2026-09-04-caelestia-fundido`, last of the five
  inside-window phases). The `#contacto` scene stops being the shared carta-de-ajuste layout and
  becomes **the desktop's own contraportada**: the only one of the five scenes that inverts to a
  flooded `--cae-primary` field instead of an application window. A Material 3 figure (the
  "troquel", 240 points, bleeding 10px past the right edge, Ruling S) recorta el fondo generativo del
  escritorio; inside it, the Chrome offline dino stands on a horizon with two clouds (BSD-3-Clause
  code, but the sprite is a Google-identifiable asset — a branding risk Aoshi accepted explicitly,
  twice, recorded in the spec). A fourth type voice, `--cae-display-axes-cierre` (italic, `opsz 144`,
  `wght 300`, `SOFT 100`, `WONK 1`), used in exactly one place on the whole site: the closing line,
  set at `--t-10` (159.66px), softening from the B1 cartel voice (`wght 900`) as it lands. The
  fundido plays once per session (the first arrival at the workspace, ~1900ms: the field floods, the
  troquel opens, the line traces and softens, the dino runs in and stops); every return plays only a
  440ms entrance (content settles, the troquel breathes, the dino glances toward wherever you came
  from) — same "you don't reopen the app you're already in" rule B2 established for the ficha. Four
  contact channels split into two *acts* (`mailto:`/`tel:`, work offline, 85px tall) and two
  *destinations* (external links, need network, 42px) — deliberately unequal weight, not four equal
  columns. **390px is explicitly in scope for this phase** (B1-B3 left it out on purpose; a
  contact scene that only works on desktop contradicts the one thing it exists to do): the troquel
  stops bleeding and becomes a whole 196px seal (the figure drops to 8 lobes, matching Material 3's
  own rule that lobe complexity must shrink with size), the headline steps down to `--t-7` (67.4px,
  not the `--t-8` an earlier spec draft assumed — verified against the actual build with `Range`,
  word by word, per this project's "the build is the source of truth" rule), and the four channels
  regroup into full-width acts plus half-width destinations, all touch targets well above the
  48×48 Material floor. `scripts/measure-caelestia-fundido.py` gates it with **fourteen** assertion
  families (95 checks) from the spec's `## Los gates`, each seen red against its own sabotage before
  being accepted. Two pairs are deliberately NOT contrast-checked: the decorative
  clouds (WCAG exempts decoration) and "the day eye" — a pair that never gets painted, since by day
  the eye is the sprite's own cutout in `--cae-surface`, not `--cae-anchor`. **A real environment
  trap paid while building this harness:** this sandbox's `requestAnimationFrame`/`setTimeout`
  fire every 200-400ms under `--use-gl=swiftshader` instead of every ~16ms, so a duration-based
  "how long did it keep animating" measurement is worthless here — it measures the sandbox's frame
  starvation, not the choreography. The fix was reading GSAP's synchronously-rendered first-frame
  value (a timeline renders its tweens' start state the instant it's built and played, no frame
  needed) in the same `evaluate()` call as the click: the fundido's troquel tween starts from
  `scale(0)`, the entrance's from `scale(0.965)`, and "nothing fired" leaves it unchanged — three
  states, one synchronous read, no timing assumptions.
  **The closing round is where the real defect was, and no gate was watching it:** leaving the scene
  *mid-fundido* and coming back left the seal broken for the rest of the visit — the dino frozen half
  outside it, the cloud invisible, the horizon at 0.91 of its stroke, and the run cycle looping
  forever. Cause: `aterrizado()` kept the list of what-to-restore **by hand** and had drifted from
  the score, and `pararZancada()` was the bicho tween's `onComplete` — which `kill()` never fires.
  There is no list any more: `anotar()` reads the score's own targets as it builds. **A list kept in
  two places desyncs the moment someone adds a tween.** Gate 13 covers that path (cuts anchored to
  *state*, never to a stopwatch: with a `setTimeout` the same gate came out red under load and green
  when idle). Gate 14 covers the hover Caelestia was missing — it was the only one of the three skins
  whose primary CTA did not react to the mouse; hovering now paints the actionable box the padding
  already created, `currentColor` at 10%, so the state layer walks with the visitor's clock.
  **Thirteen broken instruments across phase A, B2 and B5.** Two of them were caught by gate 14
  itself: `CONTRASTE_JS` stopped at the first ancestor that painted *anything*, so a translucent
  state layer got composited over **white** and read 1.03:1 for text that reads fine (it now stops at
  the first **opaque** one and stacks the translucent layers); and reading a style in the same tick as
  the `Tab` returned the transition's *first* frame. **The stopwatch has lied three times in this
  phase alone.**

- **Caelestia's phase B6 (mobile and tablet) is DONE** (`2026-09-07-caelestia-movil`, branch
  `design/caelestia-movil`). B1-B4 left narrow viewports out of scope on purpose; Aoshi opened his
  phone at the end of the interface review and four of the five scenes did not fit (Título
  justifies to a fixed 1080px measure, Quién soy overflowed 847 over 362, Obra 1316, Stack 1364).
  **The law he chose is option A: each workspace scrolls inside itself**; the document still never
  scrolls, and the inner scroll returns to zero when you switch scenes. Two bands: **compacta**
  (`max-width: 900px`, phone and tablet portrait) and **media** (`901-1365px`, tablet landscape).
  Título becomes **"Silencioso"** — no "Ahora mismo" card, no stat column, no live figure: three
  lines of prose, four numbers and a footer, and the short branch is decided by
  `widget.getClientRects().length === 0`, what actually paints, never a width read in TS. Quién soy
  goes to one column, Obra becomes a snap carousel where the centred card is the selected one (the
  centre is resolved with `getBoundingClientRect()` against the track — `offsetLeft` measures
  against the workspace rail and only card 1 ever centred), Stack stacks its four bands. One
  gesture per scene, all under 900ms.
  Gated by `scripts/measure-caelestia-movil.py` (10 families, 143 checks).
  **Two instrument lessons worth more than the CSS:**
  1. **`scrollWidth`/`scrollHeight` lie in both axes.** Contacto's flooded field is a `<span>` with
     `transform: scale(5.7)` inside an `overflow: clip`: it inflates them to 1835 and 1629 over a
     scene that is fully visible. Gates 1 and 2 now measure **content** — nodes with their own text
     or focusable — against the workspace's `getBoundingClientRect()`.
  2. **The excuse for "reachable by scrolling" must not apply upwards.** A container at `scrollTop`
     0 cannot scroll backwards, so anything above its edge is unreachable. With the generic excuse
     the gate went **green against the real fault**: Stack's header inherited `height: 96px` from
     desktop (`min-height: 0` does not cancel it) and, centred over 135px of content, pushed the
     piece's name 24px above the panel, cut by its rounded edge.
  `lidia-naive-tester` 7/10, zero P0. `vera-art-director` **BLOCK 6.22/10**, residual accepted as in
  Vice/shell/B1/B4 — but **its P0 was real and fixed first**: at 1024x768 Quién soy's name sat 12px
  under the fixed bar. The cause was in B2, not B6: `[data-ficha="neofetch"]` centres with
  `justify-content: center` at `height: 100%`, so in a box shorter than its content the overflow
  splits both ways and the top half is unreachable. It is `safe center` now (a no-op wherever it
  already fit), and in the media band the box grows. **The same fault was on `main`** at 1366x768
  and 1280x720 — ordinary laptops — with 11 and 35px of the `~ $ neofetch` command under the bar.
  Open and recorded, not fixed here: the typographic-scale debt (Vera's 7th sighting) — **closed on
  2026-09-07, see the type-scale block below**. **Two other open items were closed by Aoshi on his own phone** (2026-09-07, against the
  merged `main` over Tailscale): the headline still typing at 1.5s and a 27px black band under the
  panel. Neither exists on a real device — both were the instrument (the `swiftshader` stopwatch and
  the headless compositor under device emulation; the band showed identically on `main` without B6
  and never at 1440x900). **Do not chase either again from a Playwright capture.** Full record in
  the spec.
  Two later faults Aoshi dictated after the merge, both fixed (`e4beed5`): the mobile Título block
  painted in its final state before the terminal (it was in neither the entrance-hiding CSS rule nor
  the choreography's initial states), and Stack broke on narrow phones — the tira used
  `repeat(4, 1fr)` (`1fr` is `minmax(auto, 1fr)`, so columns never shrink: 351 over 332 at 360px),
  the header figure was a flex child without `flex-shrink: 0`, and **the header changed height on
  selection (164 to 254px), so the tira moved under the finger between `pointerdown` and `click` —
  you tapped one piece and a different one was selected**. The header now has a fixed height, as
  desktop already did. The harness gained a 360x800 band and a walk over all 23 headers.

- **The type scale is closed and gated** (`2026-09-07-escala-tipografica`, branch
  `design/escala-tipografica`). Vera had flagged "no type scale" **seven times** across phase A, B1,
  the "Ahora mismo" card, B4 and B6, and each time it was accepted as known debt. The scale existed
  — a perfect fourth, ratio 1.333, ten steps from 12 to 159.66px — but **nothing obliged anyone to
  use it**: 69 of 177 `font-size` declarations carried a literal, 39 distinct values, and 57 of
  those literals were Caelestia's.
  **What changed:** one step below the floor, `--t-0` (10.67px), at ratio **1.125 instead of
  1.333** — deliberate, because at 10px the eye resolves a 1px step and at 120px it does not
  resolve fifteen, so one ratio across the whole range leaves you either with no small sizes or
  with fifteen large ones nobody uses. (It shipped as **two** steps below the floor, `--t-00` at
  9.5px and `--t-0` at 10.67px — see "The steps that merged" below for why there is only one now.)
  The scale is declared **once, on bare `:root`**,
  where it lived three times over — once per theme, identical — while `style.css` consumed it with
  **17 fallbacks** (`var(--t-1, 0.53rem)`), a second scale in the shadows: the number that would
  paint if the token were missing. All 57 literals moved to their nearest step, median shift
  **0.50px**, max 3.90px.
  **The one exception is named by selector** (`#hero .cae-ln`): B1's headline justifies by measuring
  the text and stretching it to the measure, so its size is decided by the box's width and cannot be
  on the scale by construction. A second element with an inline size turns the gate red.
  Gated by `scripts/measure-escala-tipografica.py`, **two families that watch each other**. The
  static one reads the source; the live one reads the **computed** `font-size` of everything that
  paints text, and it is not redundant — it caught three sizes no regex could see: a `0.92em` that
  computed to 14.72px, a `font-size: 0` used as a hiding trick (now a proper visually-hidden span,
  better than before: the name stays in the accessibility tree), and a `<small>` the browser shrank
  to 7.60px with its own `smaller`.
  **Two lessons this cost:**
  1. **`--t-0` already existed at 9px**, declared by B5 for Fundido's mono labels, with a comment
     making this spec's own argument — *the sixth time that defect appeared*. This repair had been
     started once already, in miniature, and stopped at three selectors. Worse: after moving the
     scale to `:root`, that old declaration **survived and won on specificity**, so inside Caelestia
     the token still read 9px — and **the gate was blind to it**, because it checked that `--t-1`
     was declared once, not all twelve.
  2. **A tie is decided by the accessibility floor, not by list order.** `.cae-obra-caption` sat at
     14px, exactly 2px from both `--t-1` and `--t-2`; the script that built the plan's table broke
     the tie downwards for no reason. At 12px the glyph thins and contrast under the cursor's spill
     falls to **4.21:1 in Obra at 04:30**, below AA. It is `--t-2` now.
  Hyprland's literals are deliberately out of scope until its redesign closes; Vice only lost the
  duplicated declaration — the same numbers.
  **The steps that merged (2026-09-08):** `vera-art-director` measured the two steps below the
  floor at triple density and found `--t-00` (9.5px) and `--t-0` (10.67px) — 1.17px apart — read as
  a single size wherever they actually sit in the same frame: the bar (`.cae-mark` at 10.67 next to
  `.cae-ws-n` at 9.5) and the Obra drawer (`.cae-obra-drawer-kick` at 10.67 next to
  `.cae-obra-drawer-meta dt` and `.cae-obra-prose h4` at 9.5). If two steps read as one, they are
  one: they merged into a single `--t-0` at 10.67px, so the scale has **eleven** tokens, not twelve,
  and the 18 declarations that read `var(--t-00)` now read `var(--t-0)` (the 6 that already read
  `var(--t-0)` are unchanged). Growing 1.17px moved Stack's worst-case header (`.cae-cred-cab`)
  from 248 to **251px**, so its phone `min-height` moved from `15.5rem` to `15.6875rem` — gate 5b of
  `measure-caelestia-movil.py` confirms `[251]` uniform across all 23 pieces.


## Architecture Notes
- Stack: Vite + TypeScript (strict) + Tailwind + GSAP + Lenis — no backend, no framework, **no Three.js**
- Three themes over one DOM, switched by `data-theme` (vice / hyprland / caelestia). The skin is decided by CSS, never by the markup. The theme is picked at random per visit: to verify, always use `?theme=vice`
- Entry point: `src/main.ts` mounts into `#app` (`index.html`)
- Layout: `src/sections/*` (one per scene, each tagged `data-scene`), `src/components/*`, `src/utils/*`. **Read the directory — don't trust a list here**, it drifts
- Backgrounds: `src/backgrounds/*` — raw WebGL fragment shaders (`shaderBackground.ts` + one per theme), not a 3D engine
- Themes: `src/themes/*` — tokens in `themes.css`; Vice's motion is centralised in `vice.choreography.ts` as numbered gestures, not scattered per section
- Content (single source of truth): `src/data/content.ts`
- Theme modules (cursor, scroll rail, choreography, backgrounds) load via deferred `import()` and return a handle with `destroy()`, called on `pagehide`

## What NOT to Change
- WebGL/GSAP cleanup (delete program/buffers, `cancelAnimationFrame`) — prevents context-lost
- The `refreshPriority` ladder on Vice's pins — without it the obra rail pins on top of the about section
- `prefers-reduced-motion` guards
- Defensive null checks (real edge cases)
- `rel="noopener noreferrer"` on external links
