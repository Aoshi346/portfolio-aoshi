import "./style.css";
import type { BackgroundHandle } from "./backgrounds/shaderBackground";
import { createThemeSignature } from "./components/themeSignature";
import { caseStudies } from "./data/content";
import { createHero } from "./sections/hero";
import { createProjectScene } from "./sections/obra/projectScene";
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
// primer pintado. El timeout es el seguro: si GSAP no cargara, el contenido
// reaparece igualmente en lugar de quedarse invisible.
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!prefersReducedMotion && theme.motion.style === "cinematic") {
  document.documentElement.classList.add("js-intro");
  window.setTimeout(() => document.documentElement.classList.remove("js-intro"), 3000);
}

const backgroundHost = el("div", "bg-theme", []);
backgroundHost.setAttribute("aria-hidden", "true");
const noise = el("div", "bg-noise", []);
noise.setAttribute("aria-hidden", "true");

// M1 (prototipo de direccion visual): apertura + dos escenas de obra, una con
// repositorio publico y otra privada, para ver ambas variantes de cierre.
const main = el("main", "relative min-h-screen", [
  createHero(),
  ...caseStudies.slice(0, 2).map((project, index) => createProjectScene(project, index)),
]);

app.append(backgroundHost, noise, main, createThemeSignature(theme.label));

let backgroundHandle: BackgroundHandle | null = null;
void applyTheme(theme, backgroundHost).then((handle) => {
  backgroundHandle = handle;
});

// Libera el contexto WebGL al salir: el shader corre durante toda la visita.
window.addEventListener("beforeunload", () => backgroundHandle?.destroy(), { once: true });

void import("./utils/reveal").then(({ initScrollReveal }) => initScrollReveal(main, theme.motion));
