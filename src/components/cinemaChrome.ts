import { identity } from "../data/content";
import { el } from "../utils/dom";

/**
 * Recursos globales de lenguaje de cine: barras de letterbox (entran solo en
 * la obra), barra de orientacion (evita perderse en un recorrido largo) y el
 * atenuador de fondo (solo hero y contacto van a plena luz).
 *
 * Un solo DOM para los tres temas: la coreografia que cablea estos recursos
 * (`cinemaChrome` en `vice.choreography.ts`) solo corre en Vice, asi que en
 * Hyprland/Caelestia quedan en su estado de reposo (letterbox a 0, atenuador
 * a 0). El propio CSS (`.cinema-chrome`, ver `style.css`) los mantiene
 * ocultos fuera de Vice para no dejar un rotulo estatico y sin sentido en los
 * otros dos temas.
 */
export function createCinemaChrome(): HTMLElement {
  const top = el("div", "letterbox letterbox-top", []);
  top.setAttribute("data-letterbox", "");
  const bottom = el("div", "letterbox letterbox-bottom", []);
  bottom.setAttribute("data-letterbox", "");

  const rail = el("div", "rail", [
    el("span", "", [identity.name]),
    el("span", "rail-now", ["01 · Título"]),
  ]);
  rail.setAttribute("data-rail", "");
  rail.setAttribute("aria-hidden", "true");

  // Atenuador del fondo: solo hero y contacto van a plena luz. Con todas las
  // secciones a imagen brillante, el texto largo pierde legibilidad y el
  // recorrido cansa.
  const dim = el("div", "backdrop-dim", []);
  dim.setAttribute("data-dim", "");

  const chrome = el("div", "cinema-chrome", [dim, top, bottom, rail]);
  chrome.setAttribute("aria-hidden", "true");
  return chrome;
}
