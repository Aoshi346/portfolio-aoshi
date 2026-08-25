import "./style.css";
import type { BackgroundHandle } from "./backgrounds/shaderBackground";
import { createCinemaChrome } from "./components/cinemaChrome";
import { createIntroLeader } from "./components/introLeader";
import { mountSceneNav } from "./components/sceneNav";
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

// La descarga de reveal.ts (y con ella la de GSAP) arranca en el instante en
// que se ejecuta este `import()`, no cuando se consume la promesa. Dispararlo
// aqui, antes de construir el DOM de las secciones, adelanta esa peticion
// varios milisegundos sin cambiar el orden de ejecucion de nada.
const revealModule = import("./utils/reveal");

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

/*
 * Leader de apertura (solo Vice). Clase y timeout PROPIOS, no los de
 * `.js-intro`: aquella solo oculta el nombre del hero, mientras que el leader
 * tapa la pantalla entera. Si compartieran mecanismo, un fallo pasaria de "el
 * nombre tarda en verse" a "la pagina se queda en negro". El seguro es ademas
 * mas corto (1,8s) que el de `.js-intro` (3s), acorde a lo que dura el gesto:
 * cuenta atras ~0,96s mas iris ~0,62s.
 */
let introLeader: HTMLElement | null = null;
if (!prefersReducedMotion && theme.id === "vice") {
  introLeader = createIntroLeader();
  document.documentElement.classList.add("js-leader");

  const dropLeader = (): void => {
    document.documentElement.classList.remove("js-leader");
    introLeader?.remove();
  };

  /*
   * DOS seguros encadenados, no uno. El primero cubre "GSAP no llego nunca" y
   * se cuenta desde la carga. El segundo se arma cuando la coreografia avisa
   * de que empieza el gesto (`leader:start`) y cubre "la timeline arranco pero
   * se quedo a medias".
   *
   * Un unico seguro anclado a la carga no vale, y es un fallo medido: la
   * timeline no arranca hasta que terminan de cargar GSAP, Lenis y el modulo
   * de coreografia — cerca de un segundo despues en desarrollo. El seguro de
   * 1,8 s saltaba a mitad de la cuenta atras y arrancaba el leader de la
   * pantalla en pleno gesto.
   */
  let leaderGuard = window.setTimeout(dropLeader, 2600);
  window.addEventListener(
    "leader:start",
    () => {
      window.clearTimeout(leaderGuard);
      // Duracion del gesto (~1,62 s) con margen holgado.
      leaderGuard = window.setTimeout(dropLeader, 3000);
    },
    { once: true },
  );
}

const backgroundHost = el("div", "bg-theme", []);
backgroundHost.setAttribute("aria-hidden", "true");
const noise = el("div", "bg-noise", []);
noise.setAttribute("aria-hidden", "true");

/*
 * Las obras van en un carril propio. En Vice ese carril se recorre en
 * HORIZONTAL (la coreografia lo fija y lo desplaza con el scroll, ver
 * `scene3Slate`); en los otros dos temas el carril no hace nada y las escenas
 * siguen apiladas en vertical. El DOM es el mismo para los tres: quien decide
 * la direccion es el CSS de cada tema, igual que con el resto de la piel.
 */
const obraTrack = el(
  "div",
  "obra-track",
  caseStudies.map((project, index) => createProjectScene(project, index)),
);
obraTrack.setAttribute("data-obra-track", "");
const obraRail = el("div", "obra-rail", [obraTrack]);
obraRail.setAttribute("data-obra-rail", "");

const main = el("main", "relative", [
  createHero(),
  createAbout(),
  obraRail,
  createSkills(),
  createContacto(),
]);

/*
 * Ids de escena para las anclas de la navegacion. Se ponen aqui y no en cada
 * factoria porque el carril de obra no es una escena sino un envoltorio de
 * cinco, y su ancla tiene que apuntar al carril.
 */
const ANCHOR_IDS: Record<string, string> = {
  hero: "hero",
  about: "quien-es",
  credits: "creditos",
  contacto: "contacto",
};
for (const [scene, id] of Object.entries(ANCHOR_IDS)) {
  main.querySelector<HTMLElement>(`[data-scene="${scene}"]`)?.setAttribute("id", id);
}
obraRail.id = "obra";

app.append(
  backgroundHost,
  noise,
  main,
  createCinemaChrome(),
  createThemeSignature(theme.label),
);

// El leader va el ultimo del arbol y con z-index propio: tapa todo lo demas
// mientras dura, cromo de cine incluido.
if (introLeader) app.append(introLeader);

// El encendido de Hyprland: equivalente de la cortinilla de Vice en el
// material de Ascua. Import diferido, igual que el resto de modulos de tema.
let ignitionHandle: { destroy: () => void } | null = null;
if (!prefersReducedMotion && theme.id === "hyprland") {
  void import("./components/hyprIgnition").then(({ mountHyprIgnition }) => {
    ignitionHandle = mountHyprIgnition(app);
  });
}

// El cartel de obra en Hyprland: entrada por barrido y relevo de letras al
// pasar el puntero. Import diferido, igual que el resto de modulos de tema.
let cartelHandle: { destroy: () => void } | null = null;
if (theme.id === "hyprland") {
  void import("./components/obraCartel").then(async ({ mountObraCartel }) => {
    cartelHandle = await mountObraCartel(app);
  });
}

// Navegacion de escenas, comun a los tres temas: vive fuera del cromo de
// cine (aria-hidden) para que quede en el arbol de accesibilidad.
const sceneNavHandle = mountSceneNav(app);

// Barra de progreso propia: solo Vice sustituye la del navegador. Los otros
// dos temas son "pieles de interfaz" y ahi la barra nativa es lo correcto.
let scrollRailHandle: { destroy: () => void } | null = null;
if (theme.id === "vice") {
  void import("./components/scrollRail").then(({ mountScrollRail }) => {
    scrollRailHandle = mountScrollRail(app);
  });
}

/*
 * Cursor propio de Vice. Tres puertas antes de descargar siquiera el modulo:
 * el tema, el perfil de motion y que el puntero sea fino con hover real. En
 * tactil no hay hover que disparar ningun estado, asi que el coste correcto
 * ahi es cero, no "cero animacion".
 *
 * Se monta tras el leader, no antes: el gesto de apertura tapa la pantalla
 * entera y no hay nada pulsable debajo, asi que montarlo antes solo lograria
 * que la marca parpadease dentro de un gesto de 1,6 s.
 */
let cursorHandle: { destroy: () => void } | null = null;
if (
  theme.id === "vice" &&
  !prefersReducedMotion &&
  window.matchMedia("(hover: hover) and (pointer: fine)").matches
) {
  const mountCursor = (): void => {
    void import("./components/viceCursor").then(({ mountViceCursor }) => {
      cursorHandle = mountViceCursor(app);
    });
  };
  if (introLeader) {
    // El leader se desmonta solo; esperamos a que suelte la pantalla.
    window.addEventListener("leader:start", () => window.setTimeout(mountCursor, 1800), {
      once: true,
    });
  } else {
    mountCursor();
  }
}

/*
 * Cursor propio de Hyprland: la luz de mano. Las mismas tres puertas que
 * Vice — el tema, el perfil de motion y que el puntero sea fino con hover
 * real. En tactil no hay hover que disparar ningun estado, asi que el coste
 * correcto ahi es cero, no "cero animacion".
 *
 * Se monta con retardo, no de inmediato: `hyprIgnition` tapa la pantalla al
 * abrir y debajo no hay nada pulsable. A diferencia del leader de Vice, hoy
 * no emite ningun evento al soltarla, asi que el retardo es fijo. Si algun
 * dia lo emite, esto pasa a escucharlo igual que hace Vice.
 */
let hyprCursorHandle: { destroy: () => void } | null = null;
if (
  theme.id === "hyprland" &&
  !prefersReducedMotion &&
  window.matchMedia("(hover: hover) and (pointer: fine)").matches
) {
  window.setTimeout(() => {
    void import("./components/hyprCursor").then(({ mountHyprCursor }) => {
      hyprCursorHandle = mountHyprCursor(app);
    });
  }, 1800);
}

// El motor de color de Caelestia: la hora decide matiz y esquema. Va antes de
// `applyTheme` para que los tokens esten puestos en el primer pintado.
let caeColorHandle: { destroy: () => void } | null = null;
if (theme.id === "caelestia") {
  void import("./themes/caelestia.color").then(({ mountCaelestiaColor }) => {
    caeColorHandle = mountCaelestiaColor(document.documentElement);
  });
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
    scrollRailHandle?.destroy();
    cursorHandle?.destroy();
    hyprCursorHandle?.destroy();
    ignitionHandle?.destroy();
    cartelHandle?.destroy();
    caeColorHandle?.destroy();
    sceneNavHandle.destroy();
  },
  { once: true },
);

void revealModule.then(({ initScrollReveal }) => initScrollReveal(main, theme));

// Sonda de verificacion: la consume scripts/verify.py. No afecta al render.
Object.defineProperty(window, "__CONTENT_SHAPE__", {
  value: { galleries: caseStudies.filter((project) => project.gallery.length > 0).length },
  writable: false,
});
