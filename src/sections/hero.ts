import { education, experience, identity, stats } from "../data/content";
import { FIRMA } from "../themes/caelestia.firma";
import { el, elFromMarkup } from "../utils/dom";

/**
 * Apertura. Suelo de conversion garantizado: nombre, rol y contacto legibles
 * al instante, sin depender de que el video o las animaciones hayan cargado.
 * El layout concreto lo decide el tema (themes.css).
 *
 * Hyprland ("Ascua") anade tres piezas que Vice/Caelestia no muestran nunca
 * (`display: none` en style.css, mismo patron que `.about-pairs`):
 * `.hero-divider` (el filete vertical del "lomo"), `.hero-name-ghost` (la
 * copia fantasma de la doble exposicion, aria-hidden) y el propio nombre
 * dividido en un `<span>` por palabra para el corte palabra-a-palabra.
 * Spec: docs/superpowers/specs/2026-08-05-hyprland-hero-lomo-design.md
 */
export function createHero(): HTMLElement {
  // El valor del atributo declara hacia donde sale cada bloque en el gesto de
  // salida de Vice (`vice.choreography.ts`): lo que esta sobre el nombre se va
  // hacia arriba y lo que esta debajo hacia abajo, de modo que el nombre queda
  // solo en el centro. El selector `[data-hero-fade]` que usan reveal.ts y
  // style.css no distingue valor, asi que los otros dos temas no se enteran.
  //
  // `.hero-kick` es HERMANO de `.hero-surface` (antes de este rediseno vivia
  // dentro, como su primer hijo). El movimiento es real y AFECTA a Vice y
  // Caelestia — no es inerte como se penso al principio — pero es el que se
  // queda: la rejilla de 3 columnas del "lomo" en Hyprland (columna 1 =
  // etiqueta rotada) solo puede colocar via CSS Grid a los HIJOS DIRECTOS
  // de `.hero`, y anidar `.hero-kick` en `.hero-surface` lo saca de alcance
  // de esa rejilla sin recurrir a trucos fragiles (`display: contents` con
  // spans de fila explicitos en cada hijo de la superficie). Vice y
  // Caelestia compensan con CSS propio en themes.css (buscar
  // "Important 4" en el historial) que reproduce exactamente el hueco y el
  // ancho que `.hero-kick` tenia estando dentro de la superficie — medido
  // contra el commit previo al rediseno (204998c) con Playwright, no a ojo.
  const eyebrow = el("p", "hero-kick", [identity.role]);
  eyebrow.setAttribute("data-hero-fade", "up");

  // Un <span> por palabra + el espacio literal entre ellos como nodo de texto
  // aparte: bajo Hyprland el espacio no se usa (el corte usa `gap` de flex),
  // pero para Vice/Caelestia (flujo normal, sin flex) es lo que mantiene el
  // espaciado visible entre palabras identico al de un h1 con texto plano.
  const words = identity.name.split(" ").flatMap((word, i, arr) => {
    const span = el("span", "hero-name-word", [word]);
    return i < arr.length - 1 ? [span, " "] : [span];
  });
  const name = el("h1", "display-xl mt-4 text-[clamp(2.8rem,11vw,9.5rem)]", words);
  name.setAttribute("data-hero-name", "");

  // Decorativo puro (duplica visualmente el nombre real): fuera del arbol de
  // accesibilidad para que un lector de pantalla no lo anuncie dos veces.
  const ghost = el("div", "hero-name-ghost", [identity.name]);
  ghost.setAttribute("aria-hidden", "true");

  const nameWrap = el("div", "hero-name-wrap", [ghost, name]);

  const lead = el("p", "lead mx-auto mt-5 max-w-[32ch] text-paper/85", [identity.subheadline]);
  lead.setAttribute("data-hero-fade", "down");

  const location = el("span", "", [identity.location]);

  const email = el("a", "hero-mail", [identity.email]);
  email.href = `mailto:${identity.email}`;

  const corner = el("div", "hero-corner", [location, email]);
  corner.setAttribute("data-hero-fade", "down");

  // Solo pinta bajo Hyprland (style.css lo oculta por defecto). La chispa y
  // el destello son hijos propios en vez de pseudo-elementos porque un
  // contenedor solo tiene `::before`/`::after` disponibles y el filete ya
  // necesita ambos para el trazo que crece y el corte de la palabra 1.
  const spark = el("span", "hero-divider-spark");
  const landing = el("span", "hero-divider-landing");
  const divider = el("div", "hero-divider", [spark, landing]);
  divider.setAttribute("aria-hidden", "true");

  // Envoltorio comun a los tres temas: Caelestia lo viste como tarjeta
  // Material You (themes.css), Vice y Hyprland lo neutralizan a sangre.
  // El DOM es unico; solo el CSS colgado de [data-theme] decide la piel.
  //
  // `.hero-corner` es HERMANO de `.hero-surface`, no hijo — igual que antes
  // de este rediseno. Un intento anterior lo anido dentro de la superficie
  // para que fluyera en la columna de contenido del "lomo" en Hyprland, y
  // eso rompio Caelestia: `.hero-surface` fija ahi `backdrop-filter:
  // blur(24px) saturate(1.25)`, y un `backdrop-filter` distinto de `none`
  // establece bloque contenedor para descendientes en `position: absolute`
  // (CSS estandar, no un bug de navegador) — con `.hero-corner` dentro,
  // `bottom`/`left`/`right` (style.css) resolvian contra la tarjeta en vez
  // de contra la seccion. Con `.hero-corner` fuera, en Vice/Caelestia
  // resuelve exactamente igual que siempre (contra `.hero`, que ya es
  // `position: relative`). En Hyprland entra en la misma columna que
  // `.hero-surface` via CSS Grid puro (`grid-column: 3` en themes.css, sin
  // tocar el DOM): fila 1 = surface, fila 2 = corner.
  const surface = el("div", "hero-surface", [nameWrap, lead]);

  /*
   * El titular de Caelestia. Vive en el DOM COMUN y `style.css` lo oculta en
   * Vice y Hyprland (`display: none`), que es el mismo patron que ya usan
   * `.hero-divider` y `.hero-name-ghost`.
   *
   * Las tres lineas van escritas a mano y no salen de partir
   * `identity.headline` por espacios: el corte es una decision de diseno
   * (el spec explica por que "que" no puede quedar colgando al final de la
   * primera linea) y el texto sigue siendo literal de `content.ts`.
   */
  const CORTE = ["Construyo sistemas", "que aguantan producción,", "no demos."] as const;
  const lineas = CORTE.map((texto) => el("span", "cae-ln", [texto]));
  // Revision final (Importante 1): con `.hero-surface` oculto bajo Caelestia
  // (themes.css), su `<h1>` (el `name` de arriba) queda sin pintar y un
  // tercio de las visitas (el tema se sortea) no renderizan ningun `<h1>` —
  // ni en el DOM, ni en el arbol de accesibilidad, ni para un crawler. Este
  // titular es el equivalente semantico correcto bajo Caelestia (el "Que
  // hago" de la escena), asi que pasa de `<p>` a `<h1>` sin condicionales:
  // vive dentro de `.cae-head`, que `style.css` ya oculta por defecto
  // (`display: none`) en Vice/Hyprland, asi que este segundo `<h1>` nunca
  // se pinta ahi — solo Caelestia lo enciende (themes.css lo pone en
  // `display: block` via `.cae-head`). El DOM compartido no distingue tag,
  // solo clase, asi que esto no rompe el patron de los tres temas.
  const titular = el("h1", "cae-tit", lineas);
  titular.setAttribute("data-cae-titular", "");

  const firma = el("span", "cae-firma", [identity.name]);
  const regla = el("span", "cae-regla");
  regla.setAttribute("aria-hidden", "true");
  const meta = el("span", "cae-meta", [identity.subheadline]);
  const kicker = el("p", "cae-kicker", [firma, regla, meta]);

  const statcol = el(
    "div",
    "cae-statcol",
    stats.map((s) => {
      const valor = el("span", "cae-v2", [s.value]);
      valor.setAttribute("data-n", s.value);
      return el("div", "", [valor, el("span", "cae-k", [s.label])]);
    }),
  );

  const caeHead = el("div", "cae-head", [kicker, titular, statcol]);

  /*
   * El widget "Ahora mismo" de Caelestia. `education[0].period` no tiene un
   * campo de semestre propio — es un solo string
   * ("2021 — presente (10.º semestre)") — así que se extrae el contenido
   * entre paréntesis en vez de inventar un campo nuevo en content.ts o
   * escribir el literal a mano (que quedaría desacoplado de la fuente en
   * cuanto cambie el semestre real).
   */
  const semestre = education[0].period.match(/\(([^)]+)\)/)?.[1] ?? education[0].period;

  const disponible = el("span", "cae-pilla", [identity.availability]);
  const wnow = el("p", "cae-wnow", [identity.now]);
  const wsub = el("p", "cae-wsub", [`${identity.location} · Desde ${identity.since}`]);

  const wfila = (izq: string, der: string): HTMLElement =>
    el("div", "cae-wfila", [el("span", "", [izq]), el("span", "cae-wn", [der])]);

  const widget = el("div", "cae-widget", [
    el("p", "cae-whd", ["Ahora mismo"]),
    disponible,
    wnow,
    wsub,
    wfila(education[0].degree, semestre),
    wfila(experience[0].organization, experience[0].period),
  ]);

  /*
   * La entrada de escena de Caelestia (tarea 6): una terminal falsa que
   * teclea `whoami` y, al terminar, el nombre trazado con los contornos
   * reales de Fraunces aterriza sobre `.cae-firma`. `montarEntrada`
   * (caelestia.titulo.ts) hace el movimiento; aqui solo va el DOM que
   * necesita. Vive en el DOM comun y `style.css` lo apaga en Vice/Hyprland,
   * mismo patron que `.cae-head`/`.cae-widget`.
   */
  const termTyped = el("span", "cae-term-typed");
  const termCursor = el("span", "cae-term-cursor", ["_"]);
  const termLine = el("p", "cae-term-line", ["$ ", termTyped, termCursor]);
  const term = el("div", "cae-term", [termLine]);
  term.setAttribute("aria-hidden", "true");

  // Contornos generados por `scripts/gen-firma-paths.py` — dato propio,
  // controlado y bundleado, no entrada externa: `elFromMarkup` es seguro aqui
  // (ver src/utils/dom.ts).
  const trazoMarkup = `<svg class="cae-trazo" viewBox="0 -80 ${FIRMA.ancho} 90">${FIRMA.glifos
    .map((g) => `<path d="${g.d}"></path>`)
    .join("")}</svg>`;
  const trazoStage = elFromMarkup("cae-trazo-stage", trazoMarkup);
  trazoStage.setAttribute("aria-hidden", "true");

  const section = el(
    "section",
    "hero relative flex min-h-screen flex-col justify-center overflow-hidden px-6 py-24 md:px-12",
    [eyebrow, divider, surface, widget, caeHead, corner, term, trazoStage],
  );
  section.setAttribute("data-scene", "hero");

  return section;
}
