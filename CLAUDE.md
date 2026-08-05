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
