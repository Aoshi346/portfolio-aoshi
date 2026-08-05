import { identity } from "../data/content";
import { el } from "../utils/dom";

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
  // `.hero-corner` vive AHORA dentro de la superficie (antes era hermano):
  // en Vice/Caelestia sigue con `position: absolute` (style.css), asi que su
  // posicion visual no cambia pase lo que pase con su padre; en Hyprland pasa
  // a fluir en la columna de contenido del "lomo" (position: static en
  // themes.css, ver Task 2).
  const surface = el("div", "hero-surface", [nameWrap, lead, corner]);

  const section = el(
    "section",
    "hero relative flex min-h-screen flex-col justify-center overflow-hidden px-6 py-24 md:px-12",
    [eyebrow, divider, surface],
  );
  section.setAttribute("data-scene", "hero");

  return section;
}
