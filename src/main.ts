import "./style.css";
import type { BackgroundHandle } from "./backgrounds/shaderBackground";
import { createCinemaChrome } from "./components/cinemaChrome";
import { createThemeSignature } from "./components/themeSignature";
import { caseStudies } from "./data/content";
import { createAbout } from "./sections/about";
import { createContacto } from "./sections/contacto";
import { createHero } from "./sections/hero";
import { createProjectScene } from "./sections/obra/projectScene";
import { createSkills } from "./sections/skills";
import { applyTheme, pickTheme } from "./themes";
import { el } from "./utils/dom";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) {
  throw new Error("Missing #app root element");
}

// El tema se resuelve antes de componer: de el cuelgan tokens, tipografia,
// fondo generativo y el perfil de motion que consume el scroll reveal.
const theme = pickTheme();

// La secuencia de entrada cinematografica necesita el hero oculto antes del
// primer pintado. La via normal es reveal.ts, que retira la clase de forma
// sincrona en cuanto GSAP carga (decenas de ms). Este timeout es solo el
// seguro para el caso raro de que ese modulo no llegue a cargar: sin el, el
// contenido se quedaria invisible para siempre en vez de solo unos segundos.
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!prefersReducedMotion && theme.motion.style === "cinematic") {
  document.documentElement.classList.add("js-intro");
  window.setTimeout(() => document.documentElement.classList.remove("js-intro"), 3000);
}

const backgroundHost = el("div", "bg-theme", []);
backgroundHost.setAttribute("aria-hidden", "true");
const noise = el("div", "bg-noise", []);
noise.setAttribute("aria-hidden", "true");

const main = el("main", "relative", [
  createHero(),
  createAbout(),
  ...caseStudies.map((project, index) => createProjectScene(project, index)),
  createSkills(),
  createContacto(),
]);

app.append(
  backgroundHost,
  noise,
  main,
  createCinemaChrome(),
  createThemeSignature(theme.label),
);

let backgroundHandle: BackgroundHandle | null = null;
void applyTheme(theme, backgroundHost).then((handle) => {
  backgroundHandle = handle;
});

// Libera el contexto WebGL al salir: el shader corre durante toda la visita.
window.addEventListener("beforeunload", () => backgroundHandle?.destroy(), { once: true });

void import("./utils/reveal").then(({ initScrollReveal }) => initScrollReveal(main, theme));

// Sonda de verificacion: la consume scripts/verify.py. No afecta al render.
Object.defineProperty(window, "__CONTENT_SHAPE__", {
  value: { galleries: caseStudies.filter((project) => project.gallery.length > 0).length },
  writable: false,
});
