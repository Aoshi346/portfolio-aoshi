import { contactChannels, identity, type ContactChannel } from "../data/content";
import { el } from "../utils/dom";

/**
 * Cierre del portfolio: carta de ajuste. Termino la emision y lo que queda en
 * pantalla es como localizar a quien emite — cuatro barras a sangre, una por
 * via, sobre una banda de titulo.
 *
 * Un solo DOM para los tres temas. Vice pinta las barras como gelatinas
 * translucidas para que el fondo generativo siga vivo debajo; Hyprland y
 * Caelestia las apilan en vertical con el estilo base de style.css.
 */
function createBar(channel: ContactChannel): HTMLAnchorElement {
  const bar = el("a", `contacto-bar contacto-bar--${channel.key}`, [
    el("span", "contacto-bar-label", [channel.label]),
    el("span", "contacto-bar-mark", []),
    // El dato se lee SIEMPRE, sin hover: en tactil no hay hover y el correo no
    // puede depender de el.
    el("span", "contacto-bar-value", [channel.value]),
  ]) as HTMLAnchorElement;

  bar.href = channel.href;
  if (channel.external) {
    bar.target = "_blank";
    bar.rel = "noopener noreferrer";
  }

  /*
   * Acto o destino. NO es una etiqueta nueva en `content.ts`: se deriva del
   * esquema del `href` que ya existe. `mailto:` y `tel:` disparan una
   * aplicacion del aparato y siguen sirviendo sin red; los externos abren una
   * pestana y la necesitan. Caelestia dimensiona cada grupo distinto con esto
   * (fase B5); Vice y Hyprland lo ignoran.
   */
  const esquema = channel.href.split(":")[0];
  bar.dataset.canal = esquema === "mailto" || esquema === "tel" ? "acto" : "destino";
  return bar;
}

export function createContacto(): HTMLElement {
  const estado = el("p", "contacto-estado", [
    el("span", "contacto-estado-label", ["Estado"]),
    // El mismo separador con el que el sitio ya escribe un estado en el chrome
    // de cine ("05 · Fundido"), no una chapa con punto latiendo.
    el("span", "contacto-estado-sep", ["·"]),
    el("span", "contacto-estado-value", [identity.availability]),
  ]);

  // El titular de cierre de Caelestia (B5) se parte en lineas para trazarlas
  // una a una, y eso lo hace `caelestia.fundido.ts` en el navegador. Aqui solo
  // queda el gancho: el texto sigue siendo el mismo literal de `content.ts`.
  const lead = el("p", "contacto-lead", [identity.invitation]);
  lead.setAttribute("data-fundido-lead", "");

  const band = el("div", "contacto-band", [
    el("p", "hero-kick", ["Contacto"]),
    el("h2", "contacto-title display-xl", ["Hablemos"]),
    lead,
    estado,
  ]);

  const bars = el("div", "contacto-bars", contactChannels.map(createBar));

  const section = el("section", "contacto relative flex min-h-screen flex-col", [band, bars]);
  section.setAttribute("data-scene", "contacto");
  return section;
}
