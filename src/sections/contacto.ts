import { contactChannels, identity, type ContactChannel } from "../data/content";
import { el } from "../utils/dom";

/**
 * Cierre del portfolio: carta de ajuste. Termino la emision y lo que queda en
 * pantalla es como localizar a quien emite — cuatro barras a sangre, una por
 * via, sobre una banda de titulo.
 *
 * Las barras se apilan en vertical con el estilo de style.css y themes.css.
 */
function createBar(channel: ContactChannel): HTMLAnchorElement {
  const bar = el("a", `contacto-bar contacto-bar--${channel.key}`, [
    el("span", "contacto-bar-label", [channel.label]),
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
   * (fase B5).
   */
  const esquema = channel.href.split(":")[0];
  bar.dataset.canal = esquema === "mailto" || esquema === "tel" ? "acto" : "destino";
  return bar;
}

export function createContacto(): HTMLElement {
  const estado = el("p", "contacto-estado", [
    el("span", "contacto-estado-value", [identity.availability]),
  ]);

  // El titular de cierre de Caelestia (B5) se parte en lineas para trazarlas
  // una a una, y eso lo hace `caelestia.fundido.ts` en el navegador. Aqui solo
  // queda el gancho: el texto sigue siendo el mismo literal de `content.ts`.
  const lead = el("p", "contacto-lead", [identity.invitation]);
  lead.setAttribute("data-fundido-lead", "");

  const band = el("div", "contacto-band", [
    el("h2", "contacto-title display-xl", ["Hablemos"]),
    lead,
    estado,
  ]);

  const bars = el("div", "contacto-bars", contactChannels.map(createBar));

  const section = el("section", "contacto relative flex min-h-screen flex-col", [band, bars]);
  section.setAttribute("data-scene", "contacto");
  return section;
}
