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
- Ship animations without a `prefers-reduced-motion` fallback
- `console.log` in production code
- `git push --force` / `git push origin main` without approval
- Declare DONE without a build + a real browser screenshot

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
