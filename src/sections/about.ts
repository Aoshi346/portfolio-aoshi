import {
  aboutCopy,
  education,
  experience,
  focusAreas,
  identity,
  skillGroups,
  stats,
} from "../data/content";
import { el } from "../utils/dom";

/**
 * Valor de una cifra por su rotulo, no por su indice. `stats` es un literal de
 * este mismo repo, pero el rediseno de Vice consume tres de las cuatro cifras
 * fuera de la franja y atarlas a `stats[2]`/`stats[3]` deja tres roturas
 * silenciosas la proxima vez que alguien reordene el array.
 */
function statValue(label: string): string {
  return stats.find((stat) => stat.label === label)?.value ?? "";
}

/**
 * Las primeras `count` tecnologias de un grupo de skills, por su rotulo.
 *
 * Existe para que la segunda pareja tenga una prueba de verdad. La primera
 * version usaba `focusAreas[1].detail` ("Estado complejo sin romperse en
 * produccion") como prueba de la afirmacion "Interfaces que aguantan", y en el
 * naive test salio el problema: eso no prueba, parafrasea. Una prueba tiene que
 * aportar un hecho que la afirmacion no contenga ya. El stack real lo aporta —
 * y ademas responde a lo que una reclutadora usa para filtrar, que "Full Stack"
 * a secas no le dice.
 */
function stackOf(groupLabel: string, count: number): string {
  const group = skillGroups.find((candidate) => candidate.label === groupLabel);
  return (group?.items ?? [])
    .slice(0, count)
    .map((item) => item.name)
    .join(" · ");
}

/** dt + dd de la ficha, etiquetados para que Vice pueda recomponerlos en fila. */
function fact(key: string, label: string, value: string): Node[] {
  const term = el("dt", "", [label]);
  const detail = el("dd", "", [value]);
  term.setAttribute("data-fact", key);
  detail.setAttribute("data-fact", key);
  return [term, detail];
}

function createCard(): HTMLElement {
  const avatar = el("img", "about-avatar");
  avatar.src = identity.githubAvatar;
  avatar.alt = identity.name;
  /*
   * 150x188 y no 50x50: en Vice el retrato se pinta a ese tamano (4:5) y los
   * atributos son lo que el navegador usa para reservar el hueco antes de que
   * la imagen llegue. Con 50x50 declarados y 188px pintados, el layout salta al
   * cargar. Los otros dos temas lo bajan a 50px por CSS, que es la direccion
   * correcta: reservar de mas y encoger no desplaza nada.
   */
  avatar.width = 150;
  avatar.height = 188;
  avatar.loading = "lazy";
  avatar.decoding = "async";

  /*
   * Envoltorio del retrato. Existe por una razon tecnica, no de maquetacion:
   * el duotono magenta/ambar de Vice es una capa de degradado en
   * `mix-blend-mode`, y un `<img>` es contenido reemplazado — no admite
   * `::before` ni `::after`. Sin el envoltorio habria que renderizar la foto
   * como `background-image` de un span, y ahi se pierden `alt` y `loading`.
   * En los otros dos temas es `display: contents` y no existe.
   *
   * T1 anima ESTE nodo, no la imagen: asi el `clipPath` recorta tambien la
   * capa de duotono, que de otro modo entraria de golpe sobre la foto a medio
   * revelar.
   */
  const portrait = el("span", "about-portrait", [avatar]);
  portrait.setAttribute("data-portrait", "");

  const status = el("p", "about-status", [el("span", "about-dot", []), identity.availability]);

  /*
   * Nombre partido en primera palabra y resto: en Vice se apilan en dos lineas
   * y el apellido va en contorno de 1,5px. Los dos temas de interfaz no
   * estilan estos spans, asi que siguen siendo texto en linea y renderizan
   * exactamente igual que antes.
   */
  const [first = identity.name, ...rest] = identity.name.split(" ");
  const name = el("p", "about-name display-lg text-2xl", [
    el("span", "about-name-first", [first]),
    " ",
    el("span", "about-name-rest", [rest.join(" ")]),
  ]);

  const facts = el("dl", "about-facts", [
    ...fact("rol", "Rol", identity.role),
    ...fact("base", "Base", identity.location),
    ...fact("ahora", "Ahora", identity.now),
    ...fact("estudia", "Estudia", education[0]?.institution ?? ""),
  ]);

  /*
   * Envoltorio de la columna de texto de la cabecera: en Vice la ficha pasa a
   * ser una cabecera horizontal (retrato | bloque de texto) y necesita esos
   * tres nodos agrupados. `display: contents` en la regla base los devuelve al
   * flujo de bloque de la tarjeta, asi que Hyprland y Caelestia maquetan igual
   * que antes de existir este div. Es seguro aqui, y solo aqui: `contents`
   * borra la caja, asi que ni una timeline ni un ScrollTrigger pueden anclarse
   * a este nodo — T1 apunta a `.about-head` y anima a los hijos.
   */
  const main = el("div", "about-head-main", [name, status, facts]);

  // `scene-surface` es el gancho compartido que Caelestia ya viste como
  // tarjeta Material You (ver themes.css); en Vice/Hyprland no aporta nada
  // por si sola, asi que el look cinematografico lo pone `.about-card`.
  const card = el("div", "about-card about-head scene-surface", [portrait, main]);
  card.setAttribute("data-card", "");
  return card;
}

function createStats(): HTMLElement {
  // `scene-surface`: en Caelestia el fondo detras de esta franja es un shader
  // animado (`caelestiaBlobs`), no un color fijo — sin una superficie encima,
  // el numero en accent cae por debajo de 3:1 en los frames donde el blob
  // se corre debajo del texto (medido con el arnes de contraste).
  //
  // En Vice la franja se oculta: sus cuatro cifras se reparten entre las
  // pruebas del bloque de parejas, y "2021 · Desde" desaparece por decision de
  // producto (insinuaba cinco anos de experiencia profesional). No se borra del
  // DOM: los otros dos temas la siguen usando tal cual.
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
    ...experience.map((item) => {
      const node = el("div", "about-item", [
        el("b", "", [`${item.role} · ${item.organization}`]),
        el("span", "", [item.period]),
      ]);
      node.setAttribute("data-item", "experience");
      return node;
    }),
    ...education.map((item) => {
      const node = el("div", "about-item", [
        el("b", "", [item.degree]),
        el("span", "", [`${item.institution} · ${item.period}`]),
      ]);
      // Etiquetado para que Vice pueda retirarlo del pie: la carrera es la
      // prueba de la tercera pareja y, sin esto, el grado y la universidad se
      // leen dos veces en el mismo encuadre. Es el defecto que el rediseno vino
      // a quitar, y verificando la escena aparecio otra vez aqui abajo.
      node.setAttribute("data-item", "education");
      return node;
    }),
  ]);
  path.setAttribute("data-track-col", "path");

  const focus = el("div", "about-track-col scene-surface", [
    el("h3", "about-h", ["En qué me enfoco"]),
    ...focusAreas.map((area) =>
      el("div", "about-item", [el("b", "", [area.title]), el("span", "", [area.detail])]),
    ),
  ]);
  // En Vice esta columna se oculta: las parejas de abajo SON el enfoque, y
  // mantener las dos produce justo la duplicacion que el rediseno viene a
  // quitar. En los otros dos temas sigue siendo la mitad derecha del track.
  focus.setAttribute("data-track-col", "focus");

  const track = el("div", "about-track", [path, focus]);
  track.setAttribute("data-track", "");
  return track;
}

/**
 * Una afirmacion, un conector y la prueba que la sostiene.
 *
 * Doble envoltorio a proposito (`about-claim` > `about-claim-in`): T2 escribe
 * `x`/`opacity` inline sobre el nodo exterior y un transform inline de GSAP
 * gana siempre a una regla CSS, asi que el `translateX` del hover tiene que
 * vivir en un nodo distinto del que anima la timeline. Mismo reparto en el
 * conector: GSAP escala `.about-link` (0 -> 1) y el CSS escala `.about-ln`
 * dentro (0.22 en reposo -> 1 en hover). Los dos scaleX se multiplican, asi
 * que la entrada acaba en el 22% que es el reposo y el hover parte de ahi.
 */
function createPair(claim: string, proofTitle: string, proofDetail: string): HTMLElement {
  const claimNode = el("span", "about-claim", [el("span", "about-claim-in", [claim])]);
  claimNode.setAttribute("data-claim", "");

  const link = el("span", "about-link", [el("span", "about-ln", []), el("span", "about-hd", [])]);
  link.setAttribute("data-link", "");
  // Puro dibujo: no aporta informacion que no este impresa a los lados.
  link.setAttribute("aria-hidden", "true");

  const proof = el("span", "about-proof", [
    el("span", "about-proof-in", [el("b", "", [proofTitle]), el("span", "", [proofDetail])]),
  ]);
  proof.setAttribute("data-proof", "");

  return el("div", "about-pair", [claimNode, link, proof]);
}

/**
 * Bloque firma de Vice: tres afirmaciones con su prueba. Se anade al DOM de los
 * tres temas y se envia oculto (`display: none` en la regla base de style.css,
 * visible solo bajo `:root[data-theme="vice"]`). Es el patron aditivo estricto,
 * y su coste esta declarado: contenido que dos temas transportan sin usar. La
 * alternativa —construirlo segun `data-theme`— no vale, porque el tema se
 * sortea por visita y se cambia sin recargar.
 *
 * Cero datos nuevos: todo sale de `content.ts` reagrupado. Ninguna cifra se
 * escribe a mano; las tres que aparecen se leen por su rotulo.
 */
function createPairs(): HTMLElement {
  const rule = el("span", "about-pairs-rule", []);
  rule.setAttribute("data-pairs-rule", "");

  /*
   * El rotulo nombra las DOS columnas, y por eso ya no hace falta la nota
   * "Cada afirmacion, con lo que la sostiene" que iba debajo. Dos hallazgos de
   * QA en uno: el rotulo anterior ("En que me enfoco", heredado de la columna
   * del pie) no describia lo que encabeza, y la nota que si lo describia era el
   * texto menos legible de la seccion (10,88px, peso 300, opacidad 0,55 — no se
   * leia en movil). Un rotulo legible hace el trabajo de los dos.
   *
   * Es un h3 distinto del de la columna "En que me enfoco" del pie, que sigue
   * intacta para Hyprland y Caelestia.
   */
  const head = el("div", "about-pairs-head", [
    el("h3", "about-h", ["Qué hago · con qué lo respaldo"]),
    rule,
  ]);

  const first = experience[0];
  const degree = education[0];
  const semester = statValue("Semestre");

  const pairs = el("div", "about-pairs", [
    head,
    createPair(
      focusAreas[0]?.title ?? "",
      first?.organization ?? "",
      first?.description ?? "",
    ),
    createPair(
      focusAreas[1]?.title ?? "",
      `${statValue("Proyectos")} proyectos · ${statValue("En producción")} en producción`,
      stackOf("Frontend", 4),
    ),
    // La tercera afirmacion es `identity.role`, que tambien vive en la fila de
    // meta de la cabecera. Es la unica reaparicion aceptada del plano: arriba
    // es dato de ficha, aqui es lo que se afirma, y la prueba es la carrera.
    createPair(
      identity.role,
      degree?.degree ?? "",
      `${degree?.institution ?? ""}${semester ? ` · ${semester}.º semestre` : ""}`,
    ),
  ]);
  pairs.setAttribute("data-focus-pairs", "");
  return pairs;
}

/**
 * Linea envuelta en su mascara: sube desde detras al entrar.
 *
 * El `slot` va como VALOR de `data-line`, no como atributo aparte: la
 * coreografia selecciona `[data-line] > *` y un atributo con valor sigue
 * casando con ese selector. En Vice el pie es una rejilla de dos columnas y
 * necesita distinguir el lead (arriba, ancho completo) de la nota (columna
 * derecha del pie) sin depender de `:nth-of-type`, que se rompe en cuanto
 * alguien anada una tercera linea de copy.
 */
function createLine(slot: string, className: string, text: string): HTMLElement {
  const line = el("span", "about-line", [el("span", className, [text])]);
  line.setAttribute("data-line", slot);
  return line;
}

export function createAbout(): HTMLElement {
  const body = el("div", "about-body", [
    createLine("lead", "lead text-paper/90", aboutCopy[0] ?? ""),
    createPairs(),
    createLine("note", "block mt-3 text-sm leading-relaxed text-paper/85", aboutCopy[1] ?? ""),
    createStats(),
    createTrack(),
  ]);

  const section = el(
    "section",
    "about relative flex min-h-screen flex-col justify-center px-6 py-24 md:px-12",
    [el("h2", "hero-kick", ["Quién soy"]), el("div", "about-grid", [createCard(), body])],
  );
  section.setAttribute("data-scene", "about");
  // Vice trae su propio gesto de subtitulado (vice.choreography.ts) y lo
  // aplica en exclusiva; Hyprland y Caelestia no definen coreografia propia,
  // asi que sin este atributo la seccion entraria sin animar en esos dos.
  section.setAttribute("data-reveal", "fade-up");
  return section;
}
