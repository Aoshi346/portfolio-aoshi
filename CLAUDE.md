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
- Leak WebGL/GSAP resources — always `dispose()` + cancel RAF + kill timelines on teardown
- Ship animations without a `prefers-reduced-motion` fallback
- `console.log` in production code
- `git push --force` / `git push origin main` without approval
- Declare DONE without a build + a real browser screenshot

## Architecture Notes
- Stack: Vite + TypeScript (strict) + Tailwind + Three.js + GSAP — no backend, no framework
- Entry point: `src/main.ts` mounts into `#app` (`index.html`)
- Sections: `src/sections/*` (hero, about, experience, caseStudies, skills, contact)
- Components: `src/components/*` (nav, footer, caseStudyPanel)
- 3D: `src/three/*` (heroScene). Utils: `src/utils/*` (dom, reveal, icons)
- Content (single source of truth): `src/data/content.ts`

## What NOT to Change
- WebGL/GSAP cleanup (`dispose`, `cancelAnimationFrame`) — prevents context-lost
- `prefers-reduced-motion` guards
- Defensive null checks (real edge cases)
- `rel="noopener noreferrer"` on external links
