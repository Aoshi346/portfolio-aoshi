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
- Put `data-scene` on anything that is not a scene. It is how the site marks its five sections, the Créditos tray finds its scene through it and `themes.css` styles scenes by it. In the retired Vice theme it once landed on the index rows: they inherited the scene padding, grew to 405px and the first one ended at `top: -545`, off screen and unclickable
- Size type with a continuous function over scale tokens. `clamp(var(--t-2), 6.2cqi, var(--t-3))` has no `px` literal and still returns any real number between its stops: 46 of 65 measured combinations landed on 17.09 / 18.39 / 20.51px. It hides at 390 and 1440, which is exactly where a clamp lands on its clean stops. Step discretely — a `@container` or `@media` that swaps one token for another
- Reuse an opacity across surfaces. A percentage is calibrated against a surface, not a token: 55% of `--color-paper` read 5.74:1 over a dark scrim and 3.72:1 over a light one, which fails AA. Caelestia has a light and a dark scheme by time of day, so this still bites. Say in the comment which surface it was measured against, and give each scheme its own value
- Set a numeric threshold that is tighter than its instrument's noise. 480ms for a 460ms animation is under two frames of slack, so it measures machine load, not the animation. Prefer the declared value (deterministic) and keep the stopwatch as a sanity check with explicit margin
- Write the choreography without destructuring `gsap` from the context it is handed. The retired Hyprland choreography took only `ScrollTrigger` and `root` and used a bare `gsap`: `tsc` and `eslint` both passed — the identifier exists in the type space — and the built chunk threw `gsap is not defined`, so the choreography ran *nothing*. Only the browser console catches this
- Trust a contrast measurement without opening the console first. A cursor's contrast numbers were measured for weeks against a page whose choreography was crashing, so the shader read far brighter than it really is. No assertion could detect it: they all compared the page against itself. `.hero-mail` went from 4.29:1 to 6.38:1 *without touching the cursor* once the crash was fixed
- Ship animations without a `prefers-reduced-motion` fallback
- `console.log` in production code
- `git push --force` / `git push origin main` without approval
- Declare DONE without a build + a real browser screenshot

## Theme Status
**One theme: Caelestia.** Vice and Hyprland were retired on 2026-10-29. Their code, harnesses and
captures are whole in the git tag `tres-temas`; their history stays in `docs/estado-de-los-temas.md`.
**Before touching Caelestia, read its block there**: it says what is closed, what was measured, and
what must not be re-done.
- **Caelestia: design closed, not DONE.** Phases A, B1-B6, cursor and interface review merged.
  Open: B3 needs the nine real project captures, B4 has two product P1s, and
  `measure-caelestia-obra.py` fails three contrast assertions (its own instrument, not the CSS).
- **Type scale: closed and gated** (`2026-09-07-escala-tipografica`).

## Architecture Notes
- Stack: Vite + TypeScript (strict) + Tailwind + GSAP — no backend, no framework, **no Three.js**
- One theme, Caelestia: `index.html` hardcodes `data-theme="caelestia"` on `<html>` and every theme rule hangs from it. Its colour scheme (light/dark and hue) is set by the visitor's clock in `caelestia.color.ts`, so verify both day and night (Playwright `page.clock.set_fixed_time`)
- Entry point: `src/main.ts` mounts into `#app` (`index.html`)
- Layout: `src/sections/*` (one per scene, each tagged `data-scene`), `src/components/*`, `src/utils/*`. **Read the directory — don't trust a list here**, it drifts
- Background: `src/backgrounds/*` — raw WebGL fragment shader (`shaderBackground.ts` + `caelestiaFiguras.ts`), not a 3D engine
- Theme: `src/themes/*` — tokens in `themes.css`; the choreography (`caelestia.choreography.ts`) also BUILDS the layout (workspaces shell), so it runs under reduced motion too
- Content (single source of truth): `src/data/content.ts`
- Theme modules (cursor, shell, colour engine, choreography, background) load via deferred `import()` and return a handle with `destroy()`, called on `pagehide`

## What NOT to Change
- WebGL/GSAP cleanup (delete program/buffers, `cancelAnimationFrame`) — prevents context-lost
- `prefers-reduced-motion` guards
- Defensive null checks (real edge cases)
- `rel="noopener noreferrer"` on external links
