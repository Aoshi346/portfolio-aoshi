import { education, experience, focusAreas, identity } from "../data/content";
import { el } from "../utils/dom";

/** Una fila clave/valor de la salida, con su detalle opcional debajo. */
function fichaFila(clave: string, valor: string, detalle?: string): HTMLElement {
  const dd = el("dd", "ficha-v", [valor]);
  if (detalle) dd.append(el("small", "ficha-s", [detalle]));
  const fila = el("div", "ficha-fila", [el("dt", "ficha-k", [clave]), dd]);
  fila.setAttribute("data-ficha-fila", "");
  return el("div", "", [fila]);
}

/**
 * La escena «Quien soy» de Caelestia: la salida de `neofetch`.
 *
 * Cero datos nuevos. La cabecera del comando es `identity.email` — no un
 * `usuario@host` inventado — y ademas es la unica parada de tabulador de la
 * escena: el resto no navega a ninguna parte y esta entero a la vista.
 */
function createFicha(): HTMLElement {
  const foto = el("img", "ficha-foto");
  foto.src = identity.photo;
  foto.alt = identity.name;
  foto.width = 288;
  foto.height = 288;
  foto.loading = "lazy";
  foto.decoding = "async";
  /*
   * El anillo del roce es un ENVOLTORIO con el mismo `clip-path`, no un
   * `outline`: un contorno no sigue un recorte, se dibujaria rectangular.
   */
  const anillo = el("span", "ficha-anillo", [foto]);
  anillo.setAttribute("data-ficha-retrato", "");
  const retrato = el("div", "ficha-arte", [anillo]);
  retrato.setAttribute("data-ficha-grupo", "");

  const cursor = el("i", "ficha-cursor", ["▌"]);
  cursor.setAttribute("data-ficha-cursor", "");
  const comando = el("b", "ficha-cmd", []);
  comando.setAttribute("data-ficha-cmd", "");
  const linea = el("p", "ficha-cmd-linea", [el("span", "ficha-prompt", ["~ $"]), " ", comando, cursor]);

  const nombre = el("p", "ficha-nombre", [identity.name]);
  nombre.setAttribute("data-ficha-nombre", "");
  const grupoNombre = el("div", "", [nombre]);
  grupoNombre.setAttribute("data-ficha-grupo", "");

  const host = el("a", "ficha-host", [identity.email]);
  host.href = `mailto:${identity.email}`;
  host.setAttribute("data-ficha-host", "");

  const punto = el("i", "ficha-punto", []);
  const estado = el("span", "ficha-estado", [punto, identity.availability]);

  const identidad = el("div", "ficha-id", [host, estado]);
  identidad.setAttribute("data-ficha-grupo", "");

  const regla = el("div", "ficha-regla", []);
  regla.setAttribute("data-ficha-regla", "");

  const titulos = focusAreas.map((area) => area.title).join("  ·  ");
  const primerEnfoque = focusAreas[0];
  const segundoEnfoque = focusAreas[1];
  const filaEnfoque = fichaFila("Enfoque", titulos, primerEnfoque?.detail ?? "");
  if (segundoEnfoque) {
    filaEnfoque.querySelector(".ficha-v")?.append(el("small", "ficha-s", [segundoEnfoque.detail]));
  }

  const trabajo = experience[0];
  const carrera = education[0];
  const filas = el("dl", "ficha-filas", [
    fichaFila("Rol", identity.role),
    fichaFila("Base", identity.location),
    fichaFila("Ahora", identity.now),
    filaEnfoque,
    fichaFila(
      "Último puesto",
      `${trabajo?.role ?? ""} · ${trabajo?.organization ?? ""}`,
      trabajo?.period ?? "",
    ),
    fichaFila(
      "Estudia",
      carrera?.degree ?? "",
      `${carrera?.institution ?? ""} · ${carrera?.period ?? ""}`,
    ),
  ]);

  // La tira de color con la que `neofetch` cierra siempre. Los nueve tonos son
  // los tokens de la hora: el color lo pone el CSS, no este modulo.
  const tira = el(
    "div",
    "ficha-tira",
    [
      "--cae-surface",
      "--cae-surface-container",
      "--cae-surface-container-high",
      "--cae-primary",
      "--cae-primary-container",
      "--cae-anchor",
      "--cae-wall-1",
      "--cae-wall-2",
      "--cae-wall-3",
    ].map((token) => {
      const tono = el("i", "ficha-tono", []);
      tono.setAttribute("data-ficha-tono", token);
      return tono;
    }),
  );
  tira.append(el("span", "ficha-rotulo", []));
  tira.setAttribute("data-ficha-tira", "");
  const grupoTira = el("div", "", [tira]);
  grupoTira.setAttribute("data-ficha-grupo", "");

  const cursorFinal = el("i", "ficha-cursor", ["▌"]);
  cursorFinal.setAttribute("data-ficha-prompt", "");
  const promptFinal = el("p", "ficha-cmd-linea ficha-cmd-fin", [
    el("span", "ficha-prompt", ["~ $"]),
    " ",
    cursorFinal,
  ]);

  const columna = el("div", "ficha-col", [
    grupoNombre,
    identidad,
    regla,
    filas,
    grupoTira,
  ]);
  const cuerpo = el("div", "ficha-cuerpo", [retrato, columna]);
  const ficha = el("div", "ficha", [linea, cuerpo, promptFinal]);
  ficha.setAttribute("data-ficha", "neofetch");
  return ficha;
}

export function createAbout(): HTMLElement {
  const body = el("div", "about-body", [createFicha()]);

  const section = el(
    "section",
    "about relative flex min-h-screen flex-col justify-center px-6 py-24 md:px-12",
    [el("h2", "hero-kick", ["Quién soy"]), el("div", "about-grid", [body])],
  );
  section.setAttribute("data-scene", "about");
  section.setAttribute("data-reveal", "fade-up");
  return section;
}
