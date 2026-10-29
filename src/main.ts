import "./style.css";
import type { BackgroundHandle } from "./backgrounds/shaderBackground";
import { caseStudies } from "./data/content";
import { createAbout } from "./sections/about";
import { createContacto } from "./sections/contacto";
import { createHero } from "./sections/hero";
import { createSkills } from "./sections/skills";
import { applyTheme } from "./themes";
import { caelestiaTheme as theme } from "./themes/caelestia";
import { el } from "./utils/dom";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) {
  throw new Error("Missing #app root element");
}

// La descarga de reveal.ts (y con ella la de GSAP) arranca en el instante en
// que se ejecuta este `import()`, no cuando se consume la promesa. Dispararlo
// aqui, antes de construir el DOM de las secciones, adelanta esa peticion
// varios milisegundos sin cambiar el orden de ejecucion de nada.
const revealModule = import("./utils/reveal");

const prefersReducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;

/*
 * Entrada de Titulo. Las piezas de `#hero` (terminal, trazo, firma, cifras,
 * widget) necesitan quedar ocultas ANTES del primer pintado -- si no, se ven
 * en su estado FINAL durante los ~2,9 s que tardan en llegar los tres
 * `import()` encadenados de la coreografia (reveal.ts -> gsap -> ScrollTrigger
 * -> caelestia.titulo.ts) y luego saltan de golpe a su estado inicial cuando
 * `montarEntrada` por fin corre. La via normal es esa misma funcion, que
 * retira la clase en cuanto ha escrito los estados iniciales con `gsap.set`
 * (sincrono, antes de construir la timeline); este timeout es solo el seguro
 * por si el chunk no llega nunca.
 */
if (!prefersReducedMotion) {
  document.documentElement.classList.add("js-cae-entrada");
  window.setTimeout(
    () => document.documentElement.classList.remove("js-cae-entrada"),
    3000,
  );
}

const backgroundHost = el("div", "bg-theme", []);
backgroundHost.setAttribute("aria-hidden", "true");
const noise = el("div", "bg-noise", []);
noise.setAttribute("aria-hidden", "true");

/*
 * El carril de obra va vacio: la coreografia lo localiza por
 * `data-obra-rail` para montarlo como un workspace mas del shell, y la
 * Editorial (`caelestiaObraEditorial.ts`) le añade su fila de tarjetas y su
 * cajon desde `caseStudies`.
 */
const obraRail = el("div", "obra-rail", []);
obraRail.setAttribute("data-obra-rail", "");

const main = el("main", "relative", [
  createHero(),
  createAbout(),
  obraRail,
  createSkills(),
  createContacto(),
]);

/*
 * Ids de escena para las anclas. Se ponen aqui y no en cada factoria porque
 * el carril de obra no es una escena sino un envoltorio de cinco, y su ancla
 * tiene que apuntar al carril.
 */
const ANCHOR_IDS: Record<string, string> = {
  hero: "hero",
  about: "quien-es",
  credits: "creditos",
  contacto: "contacto",
};
for (const [scene, id] of Object.entries(ANCHOR_IDS)) {
  main
    .querySelector<HTMLElement>(`[data-scene="${scene}"]`)
    ?.setAttribute("id", id);
}
obraRail.id = "obra";

app.append(backgroundHost, noise, main);

// La Editorial de Obra: fila de cinco tarjetas + cajon. Import diferido, igual
// que el resto de modulos del tema.
let caeObraHandle: { destroy: () => void } | null = null;
void import("./components/caelestiaObraEditorial").then(
  async ({ mountCaelestiaObraEditorial }) => {
    caeObraHandle = await mountCaelestiaObraEditorial(app);
  },
);

// La bandeja de Creditos: cuatro bandas y 23 piezas siempre en pantalla.
let caeCreditosHandle: { destroy: () => void } | null = null;
void import("./components/caelestiaCreditosBandeja").then(
  async ({ mountCaelestiaCreditosBandeja }) => {
    caeCreditosHandle = await mountCaelestiaCreditosBandeja(app);
  },
);

// El motor de color: la hora decide matiz y esquema. Va antes de
// `applyTheme` para que los tokens esten puestos en el primer pintado.
let caeColorHandle: { destroy: () => void } | null = null;
void import("./themes/caelestia.color").then(({ mountCaelestiaColor }) => {
  caeColorHandle = mountCaelestiaColor(document.documentElement);
});

// El shell: barra, dock y notificaciones.
let caeShellHandle: {
  destroy: () => void;
  setScene: (index: number) => void;
} | null = null;
void import("./components/caelestiaShell").then(({ mountCaelestiaShell }) => {
  caeShellHandle = mountCaelestiaShell(app);
});

// La pastilla activa la marca quien escucha, no quien pulsa: asi tambien
// queda sincronizada si el cambio de workspace llega de otro origen.
app.addEventListener("caelestia:workspace", (evento) => {
  if (!(evento instanceof CustomEvent)) return;
  const detalle: unknown = evento.detail;
  if (typeof detalle !== "object" || detalle === null || !("index" in detalle))
    return;
  const indice = Number((detalle as { index: unknown }).index);
  if (Number.isFinite(indice)) caeShellHandle?.setScene(indice);
});

/*
 * Cursor propio: la gota. Dos puertas antes de descargar siquiera el modulo:
 * el perfil de motion y que el puntero sea fino con hover real. En tactil no
 * hay hover que disparar ningun estado, asi que el coste correcto ahi es
 * cero, no "cero animacion": la puerta esta ANTES del `import()`, no dentro
 * del modulo.
 */
let caeCursorHandle: { destroy: () => void } | null = null;
if (
  !prefersReducedMotion &&
  window.matchMedia("(hover: hover) and (pointer: fine)").matches
) {
  void import("./components/caelestiaCursor").then(
    ({ mountCaelestiaCursor }) => {
      caeCursorHandle = mountCaelestiaCursor(app);
    },
  );
}

let backgroundHandle: BackgroundHandle | null = null;
void applyTheme(theme, backgroundHost).then((handle) => {
  backgroundHandle = handle;
});

// Libera el contexto WebGL al salir: el shader corre durante toda la visita.
// `pagehide`, no `beforeunload`: en movil (Safari/Chrome) y al entrar en
// bfcache, `beforeunload` no dispara de forma fiable, asi que el contexto
// WebGL se quedaba sin liberar en esas rutas de salida. `pagehide` cubre
// ambas — navegacion normal y bfcache — y es el evento recomendado para
// limpieza al abandonar la pagina.
window.addEventListener(
  "pagehide",
  () => {
    backgroundHandle?.destroy();
    caeColorHandle?.destroy();
    caeShellHandle?.destroy();
    caeObraHandle?.destroy();
    caeCreditosHandle?.destroy();
    caeCursorHandle?.destroy();
  },
  { once: true },
);

void revealModule.then(({ initScrollReveal }) => initScrollReveal(main, theme));

// Sonda de verificacion: la consume scripts/verify.py. No afecta al render.
Object.defineProperty(window, "__CONTENT_SHAPE__", {
  value: {
    galleries: caseStudies.filter((project) => project.gallery.length > 0)
      .length,
  },
  writable: false,
});
