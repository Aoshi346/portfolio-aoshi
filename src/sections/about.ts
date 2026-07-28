import { aboutCopy, education, experience, focusAreas, identity, stats } from "../data/content";
import { el } from "../utils/dom";

function createCard(): HTMLElement {
  const avatar = el("img", "about-avatar");
  avatar.src = identity.githubAvatar;
  avatar.alt = identity.name;
  avatar.width = 50;
  avatar.height = 50;
  avatar.loading = "lazy";
  avatar.decoding = "async";

  const status = el("p", "about-status", [el("span", "about-dot", []), identity.availability]);

  const facts = el("dl", "about-facts", [
    el("dt", "", ["Rol"]),
    el("dd", "", [identity.role]),
    el("dt", "", ["Base"]),
    el("dd", "", [identity.location]),
    el("dt", "", ["Ahora"]),
    el("dd", "", [identity.now]),
    el("dt", "", ["Estudia"]),
    el("dd", "", [education[0]?.institution ?? ""]),
  ]);

  // `scene-surface` es el gancho compartido que Caelestia ya viste como
  // tarjeta Material You (ver themes.css); en Vice/Hyprland no aporta nada
  // por si sola, asi que el look cinematografico lo pone `.about-card`.
  const card = el("div", "about-card scene-surface", [
    avatar,
    el("p", "about-name display-lg text-2xl", [identity.name]),
    status,
    facts,
  ]);
  card.setAttribute("data-card", "");
  return card;
}

function createStats(): HTMLElement {
  // `scene-surface`: en Caelestia el fondo detras de esta franja es un shader
  // animado (`caelestiaBlobs`), no un color fijo — sin una superficie encima,
  // el numero en accent cae por debajo de 3:1 en los frames donde el blob
  // se corre debajo del texto (medido con el arnes de contraste).
  const group = el(
    "div",
    "about-stats scene-surface",
    stats.map((stat) => el("div", "", [el("b", "", [stat.value]), el("span", "", [stat.label])])),
  );
  group.setAttribute("data-stats", "");
  return group;
}

function createTrack(): HTMLElement {
  // `scene-surface` en las dos columnas: en Caelestia gana la superficie
  // Material You (necesaria ademas para que el titulo, sobre fondo claro sin
  // tarjeta, no caiga por debajo de 4.5:1 — medido con el arnes de contraste).
  const path = el("div", "about-track-col scene-surface", [
    el("h3", "about-h", ["Trayectoria"]),
    ...experience.map((item) =>
      el("div", "about-item", [
        el("b", "", [`${item.role} · ${item.organization}`]),
        el("span", "", [item.period]),
      ]),
    ),
    ...education.map((item) =>
      el("div", "about-item", [
        el("b", "", [item.degree]),
        el("span", "", [`${item.institution} · ${item.period}`]),
      ]),
    ),
  ]);

  const focus = el("div", "about-track-col scene-surface", [
    el("h3", "about-h", ["En qué me enfoco"]),
    ...focusAreas.map((area) =>
      el("div", "about-item", [el("b", "", [area.title]), el("span", "", [area.detail])]),
    ),
  ]);

  const track = el("div", "about-track", [path, focus]);
  track.setAttribute("data-track", "");
  return track;
}

/** Linea envuelta en su mascara: sube desde detras al entrar. */
function createLine(className: string, text: string): HTMLElement {
  const line = el("span", "about-line", [el("span", className, [text])]);
  line.setAttribute("data-line", "");
  return line;
}

export function createAbout(): HTMLElement {
  const body = el("div", "about-body", [
    createLine("lead text-paper/90", aboutCopy[0] ?? ""),
    createLine("block mt-3 text-sm leading-relaxed text-paper/85", aboutCopy[1] ?? ""),
    createStats(),
    createTrack(),
  ]);

  const section = el(
    "section",
    "about relative flex min-h-screen flex-col justify-center px-6 py-24 md:px-12",
    [el("h2", "hero-kick", ["Quién es"]), el("div", "about-grid", [createCard(), body])],
  );
  section.setAttribute("data-scene", "about");
  // Vice trae su propio gesto de subtitulado (vice.choreography.ts) y lo
  // aplica en exclusiva; Hyprland y Caelestia no definen coreografia propia,
  // asi que sin este atributo la seccion entraria sin animar en esos dos.
  section.setAttribute("data-reveal", "fade-up");
  return section;
}
