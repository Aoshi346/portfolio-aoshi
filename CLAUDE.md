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
- **Hyprland and Caelestia: IN PROGRESS.** Current focus. They share `shaderBackground.ts` with
  Vice (don't touch that module without confirming Vice still renders) but each has its own
  background (`hyprGradient.ts` / `caelestiaBlobs.ts`), palette, and typography — see `src/themes/themes.css`.
  The obra section in Hyprland has a new device (the cartel, `2026-08-10-hyprland-obra-cartel`
  plan and spec): five titles always on screen, captured screenshot travels with GSAP Flip into a
  large viewer on click. Contrast against the real shader background measured per-glyph (not
  viewport-wide, which overstated it): only the resting title dips below AA, and only in the
  shader's brightest 0.5% of frames (3.88:1) — a shader brightness ceiling, pending a product
  decision, not an illegibility problem (see the spec's `Registro de implementación` /
  `Color y contraste`). The "Con qué construyo" section is still being redesigned on a separate
  branch — Hyprland overall stays IN PROGRESS.
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
  **Phases B1-B5 (the five sections inside the window) are NOT done** — their layout still assumes a
  page that scrolls, so cramped content inside a workspace is expected, not a defect.
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
  inside the same window) remain pending** — B1 only closes `#hero`.
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
