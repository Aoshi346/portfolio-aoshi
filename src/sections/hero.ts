import { education, experience, identity, stats } from "../data/content";
import { FIRMA } from "../themes/caelestia.firma";
import { el, elFromMarkup } from "../utils/dom";

/**
 * Apertura. Suelo de conversion garantizado: nombre, rol y contacto legibles
 * al instante, sin depender de que el video o las animaciones hayan cargado.
 * El layout concreto lo decide el tema (themes.css).
 */
export function createHero(): HTMLElement {
  /*
   * El titular de Caelestia. Las tres lineas van escritas a mano y no salen de partir
   * `identity.headline` por espacios: el corte es una decision de diseno
   * (el spec explica por que "que" no puede quedar colgando al final de la
   * primera linea) y el texto sigue siendo literal de `content.ts`.
   */
  const CORTE = ["Construyo sistemas", "que aguantan producción,", "no demos."] as const;
  const lineas = CORTE.map((texto) => el("span", "cae-ln", [texto]));
  // Es el unico `<h1>` de la escena: nombre, rol y contacto del suelo de
  // conversion viven en el widget, la prosa movil y el kicker.
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

  const luz = el("i", "cae-wluz", []);
  luz.setAttribute("aria-hidden", "true");
  const disponible = el("span", "cae-pilla", [luz, identity.availability]);
  const figura = el("span", "cae-wfig", []);
  figura.setAttribute("aria-hidden", "true");
  const wnow = el("p", "cae-wnow", [identity.now]);
  const wsub = el("p", "cae-wsub", [`${identity.location} · Desde ${identity.since}`]);

  /*
   * Dos columnas fechadas, no dos filas de tabla (spec 2026-09-05-caelestia-
   * ahora-mismo): la fecha va ENCIMA como etiqueta y el nombre debajo, asi
   * estudios y empresa se leen como dos cosas distintas (hallazgo de Lidia
   * en B1), no como dos filas iguales.
   */
  const wcol = (fecha: string, nombre: string): HTMLElement =>
    el("div", "cae-wcol", [el("small", "cae-wfecha", [fecha]), el("b", "cae-wnombre", [nombre])]);

  const widget = el("div", "cae-widget", [
    el("div", "cae-wcab", [el("p", "cae-whd", ["Ahora mismo"]), figura]),
    wnow,
    wsub,
    el("div", "cae-wdos", [
      wcol(semestre, education[0].degree),
      wcol(experience[0].period, experience[0].organization),
    ]),
    el("div", "cae-wpie", [disponible]),
  ]);

  /*
   * B6 (spec 2026-09-07-caelestia-movil, «Titulo: Silencioso»): por debajo de
   * 900px la tarjeta no se monta y lo que dice se lee en tres lineas de
   * prosa, mas las cuatro cifras como una linea de mono. Es OTRO DOM, oculto
   * en escritorio desde themes.css: no se reescala la tarjeta. Los literales
   * son los mismos de arriba (identity, education[0], experience[0], stats);
   * `semestre` es el parentesis de education[0].period, ya extraido.
   */
  const lineaProsa = (fuerte: string, resto: string): HTMLElement =>
    el("span", "cae-mv-linea", [el("b", "", [fuerte]), resto]);
  const prosa = el("p", "cae-mv-prosa", [
    lineaProsa(identity.now, ` en ${identity.location}.`),
    lineaProsa(education[0].degree, `, ${semestre}.`),
    lineaProsa(experience[0].organization, `, ${experience[0].period}.`),
  ]);
  const cifrasMovil = el(
    "p",
    "cae-mv-cifras",
    stats.map((s) => el("span", "cae-mv-cifra", [el("b", "", [s.value]), el("small", "", [s.label])])),
  );
  const luzMovil = el("i", "cae-wluz", []);
  luzMovil.setAttribute("aria-hidden", "true");
  const pillaMovil = el("span", "cae-pilla cae-pilla-mv", [luzMovil, identity.availability]);
  const bloqueMovil = el("div", "cae-movil", [prosa, cifrasMovil, el("div", "cae-mv-pie", [pillaMovil])]);

  /*
   * La entrada de escena de Caelestia (tarea 6): una terminal falsa que
   * teclea `whoami` y, al terminar, el nombre trazado con los contornos
   * reales de Fraunces aterriza sobre `.cae-firma`. `montarEntrada`
   * (caelestia.titulo.ts) hace el movimiento; aqui solo va el DOM que
   * necesita.
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
    [widget, caeHead, bloqueMovil, term, trazoStage],
  );
  section.setAttribute("data-scene", "hero");

  return section;
}
