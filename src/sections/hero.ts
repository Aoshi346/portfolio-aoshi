import { identity } from "../data/content";
import { FIRMA, type Glifo } from "../themes/caelestia.firma";
import { el, elFromMarkup } from "../utils/dom";

/**
 * Apertura de Caelestia: el nombre, grande y en el centro, y debajo el rol.
 * Nada mas (spec 2026-10-29-caelestia-titulo-nombre). El nombre visible es un
 * SVG con los contornos reales de Fraunces; para lectores de pantalla el `<h1>`
 * lleva el texto en `.cae-nombre-txt`, visualmente oculto, y el SVG va
 * `aria-hidden`. El layout y la entrada los deciden themes.css y
 * caelestia.titulo.ts.
 */

/** Cuantos glifos tiene la primera palabra ("Aoshi"): corta el nombre en dos lineas. */
const GLIFOS_PRIMERA_LINEA = 5;

/**
 * Un SVG con los glifos dados. Cada `path` lleva `pathLength="1"` (el trazo se
 * dibuja entero midan lo que midan sus contornos) y `--i`, su posicion de
 * corrido por los 15 glifos del nombre (escalonado, tambien en movil).
 */
function svgDeGlifos(glifos: readonly Glifo[], desde: number): string {
  const paths = glifos
    .map((g, k) => `<path d="${g.d}" pathLength="1" style="--i:${desde + k}"></path>`)
    .join("");
  // Sin `viewBox` hasta que `ajustarSvgsNombre` mida la caja real (getBBox).
  return `<svg class="cae-nombre-svg" focusable="false">${paths}</svg>`;
}

export function createHero(): HTMLElement {
  // Contornos generados por `scripts/gen-firma-paths.py`: dato propio,
  // controlado y bundleado, no entrada externa. `elFromMarkup` es seguro aqui
  // (ver src/utils/dom.ts).
  const primera = FIRMA.glifos.slice(0, GLIFOS_PRIMERA_LINEA);
  const segunda = FIRMA.glifos.slice(GLIFOS_PRIMERA_LINEA);
  const lineaUna = elFromMarkup("cae-linea-una", svgDeGlifos(FIRMA.glifos, 0));
  const linea1 = elFromMarkup("cae-linea", svgDeGlifos(primera, 0));
  const linea2 = elFromMarkup("cae-linea", svgDeGlifos(segunda, GLIFOS_PRIMERA_LINEA));
  // `span` y no `div`: viven dentro de un `<h1>`.
  const comoSpan = (nodo: HTMLDivElement, clase: string): HTMLElement => {
    const span = el("span", clase);
    span.append(...Array.from(nodo.childNodes));
    return span;
  };

  const dibujo = el("span", "cae-nombre-dib", [
    comoSpan(lineaUna, "cae-linea-una"),
    comoSpan(linea1, "cae-linea"),
    comoSpan(linea2, "cae-linea"),
  ]);
  dibujo.setAttribute("aria-hidden", "true");

  const nombre = el("h1", "cae-nombre", [el("span", "cae-nombre-txt", [identity.name]), dibujo]);
  const rol = el("p", "cae-rol", [identity.intro]);
  const presenta = el("div", "cae-presenta", [nombre, rol]);

  const section = el(
    "section",
    "hero relative flex min-h-screen flex-col justify-center overflow-hidden px-6 py-24 md:px-12",
    [presenta],
  );
  section.setAttribute("data-scene", "hero");

  // `getBBox` mide 0 sobre un SVG fuera del documento: solo se agenda si la
  // seccion ya esta montada. Si no, la llama la coreografia tras el montaje.
  requestAnimationFrame(() => {
    if (section.isConnected) ajustarSvgsNombre(section);
  });

  return section;
}

/**
 * Pone a cada SVG del nombre un `viewBox` con la caja real de sus glifos
 * (`getBBox`) y su ancho/alto en `em` (valor/100: los contornos estan a tamano
 * 100), con la misma `y` y el mismo alto para todos, para que las dos lineas
 * de movil midan igual. Medir exige que el SVG este en el documento.
 */
export function ajustarSvgsNombre(hero: HTMLElement): void {
  const svgs = Array.from(hero.querySelectorAll<SVGSVGElement>(".cae-nombre-svg"));
  const cajas = svgs.map((svg) =>
    Array.from(svg.querySelectorAll<SVGPathElement>("path")).map((p) => p.getBBox()),
  );
  const todas = cajas.flat();
  if (todas.length === 0) return;
  const y0 = Math.min(...todas.map((b) => b.y));
  const y1 = Math.max(...todas.map((b) => b.y + b.height));
  if (!(y1 > y0)) return;

  svgs.forEach((svg, i) => {
    const propias = cajas[i];
    if (propias.length === 0) return;
    const x0 = Math.min(...propias.map((b) => b.x));
    const x1 = Math.max(...propias.map((b) => b.x + b.width));
    svg.setAttribute("viewBox", `${x0} ${y0} ${x1 - x0} ${y1 - y0}`);
    svg.style.width = `${(x1 - x0) / 100}em`;
    svg.style.height = `${(y1 - y0) / 100}em`;
  });
}
