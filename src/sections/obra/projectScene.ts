import { createGallery } from "../../components/gallery";
import type { CaseStudy } from "../../data/content";
import { el } from "../../utils/dom";

function metaEntry(label: string, value: string): HTMLElement {
  const entry = el("div", "", [el("dt", "", [label]), el("dd", "", [value])]);
  entry.setAttribute("data-stagger-item", "");
  return entry;
}

/**
 * Una escena a pantalla completa por proyecto: la obra es la protagonista.
 * El ordinal gigante hace de telon con scrub de scroll; la superficie usa
 * `--radius-card`, asi que el redondeo cambia con el tema.
 *
 * Cada pieza lleva DOS juegos de ganchos:
 *  - `data-reveal` / `data-stagger-item` (genericos, `utils/reveal.ts`): los
 *    consumen Hyprland y Caelestia, que no definen coreografia propia.
 *  - `data-ord` / `data-title` / `data-meta` / `data-mask` / `data-gallery`
 *    (bespoke): los consume en exclusiva `vice.choreography.ts`. Cuando un
 *    tema define `choreography`, `initScrollReveal` NO ejecuta las recetas
 *    genericas (ver comentario en `utils/reveal.ts`), asi que ambos juegos de
 *    atributos conviven en el mismo nodo sin pelear por el mismo tween.
 */
export function createProjectScene(project: CaseStudy, index: number): HTMLElement {
  const ordinal = el(
    "span",
    "pointer-events-none absolute right-0 top-[10%] select-none font-display text-[clamp(7rem,26vw,22rem)] font-black leading-none text-paper/[0.06]",
    [String(index + 1).padStart(2, "0")],
  );
  ordinal.setAttribute("aria-hidden", "true");
  ordinal.setAttribute("data-reveal", "ordinal");
  ordinal.setAttribute("data-ord", "");
  ordinal.setAttribute("data-decorative", "");

  const tag = el("p", "hero-kick", [project.tag]);

  // Un <h2> no puede ir dentro de un <button> (el modelo de contenido del
  // boton es phrasing), asi que va al reves: el boton dentro del encabezado.
  const abrir = el("button", "obra-abrir", [project.title]);
  abrir.setAttribute("data-obra-abrir", "");
  abrir.type = "button";

  const title = el("h2", "display-lg mt-5 max-w-3xl text-[clamp(2rem,6vw,4.6rem)]", [abrir]);
  title.setAttribute("data-reveal", "chars");
  title.setAttribute("data-title", "");

  const lead = el("p", "lead mt-3 max-w-[34ch] text-paper/85", [project.lead]);
  lead.setAttribute("data-reveal", "fade-up");

  // Fila de metadatos: reemplaza los chips de tecnologia por una lectura mas
  // completa (rol, periodo, stack, estado) sin duplicar los creditos de obra.
  const meta = el("dl", "obra-meta", [
    metaEntry("Rol", project.role),
    ...(project.period ? [metaEntry("Periodo", project.period)] : []),
    metaEntry("Stack", project.stack.join(" · ")),
    metaEntry("Estado", project.status),
  ]);
  meta.setAttribute("data-reveal", "stagger");
  meta.setAttribute("data-meta", "");

  function column(head: string, text: string): HTMLElement {
    const wrapper = el("div", "overflow-hidden", [
      // 70%, no 40%: al instrumentar la escena con `data-scene="obra"` (mas
      // abajo) el gate de contraste bajo el pliegue alcanzo por primera vez
      // esta etiqueta y midio 2.41:1 / 3.43:1 en Caelestia/Hyprland — el
      // mismo defecto de `.hero-corner`, aqui via opacidad de Tailwind en vez
      // de un color fijado a mano. 70% es el valor ya verificado con margen
      // en ese caso.
      el("p", "font-mono text-[0.65rem] uppercase tracking-[0.3em] text-paper/70", [head]),
      el("p", "mt-3 text-base leading-relaxed text-paper/80", [text]),
    ]);
    wrapper.setAttribute("data-mask", "");
    return wrapper;
  }

  const columns = el("div", "mt-10 grid max-w-4xl gap-8 md:grid-cols-2", [
    column("Problema", project.problem),
    column("Solución", project.solution),
  ]);
  columns.setAttribute("data-reveal", "fade-up");

  // El cartel de Hyprland necesita UNA captura por proyecto, no el carril
  // arrastrable: `gallery.ts` construye un carril y aqui hace falta un solo
  // nodo que pueda viajar con Flip. Nace oculto para los tres temas
  // (`style.css`) y solo el bloque Hyprland lo enciende.
  const mini = el("figure", "obra-mini", []);
  mini.setAttribute("data-obra-mini", "");
  const primera = project.gallery[0];
  if (primera) {
    const shot = el("img", "obra-mini-img") as HTMLImageElement;
    shot.src = primera.src;
    shot.alt = primera.caption;
    shot.loading = "lazy";
    shot.decoding = "async";
    mini.append(shot, el("figcaption", "obra-mini-pie", [primera.caption]));
  }

  // Las marcas del stack las rellena `stackIcons.ts` en la Task 5.
  const marcas = el("div", "obra-marcas", []);
  marcas.setAttribute("data-obra-marcas", "");
  marcas.setAttribute("aria-hidden", "true");

  const children: HTMLElement[] = [tag, title, lead, meta, columns, mini, marcas];

  // Las capturas reales de la galeria (Task 11) ya existen y devuelven 200;
  // la galeria se construye siempre que el caso de estudio declare piezas,
  // con su propio fallback por imagen (ver `components/gallery.ts`) como red
  // de seguridad honesta ante un fallo de carga puntual, no el estado
  // esperado.
  if (project.gallery.length > 0) {
    const gallery = createGallery(project.gallery);
    gallery.setAttribute("data-reveal", "fade-up");
    children.push(gallery);
  }

  const footerChildren: HTMLElement[] = [];
  if (project.link) {
    // El foco de teclado replica exactamente lo que hace el hover: sin el par
    // `focus-visible`, quien navega con Tab no veia moverse la flecha ni
    // tenia mas indicador que el outline por defecto del navegador, que se
    // pierde sobre el video de fondo.
    const link = el(
      "a",
      "group/link inline-flex items-center gap-2 rounded-sm font-mono text-sm text-paper transition-colors duration-300 hover:text-accent focus-visible:text-accent focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent",
      [
        project.link.label,
        el(
          "span",
          "transition-transform duration-300 group-hover/link:translate-x-1 group-focus-visible/link:translate-x-1",
          ["→"],
        ),
      ],
    );
    link.href = project.link.href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    footerChildren.push(link);
  } else if (project.privateProject) {
    footerChildren.push(
      // 70%, mismo motivo que en `column()`: 40% no llega a 4.5:1 en
      // Hyprland/Caelestia.
      el("p", "font-mono text-xs uppercase tracking-[0.2em] text-paper/70", [
        "Proyecto privado de empresa",
      ]),
    );
  }

  if (footerChildren.length > 0) {
    children.push(el("div", "mt-10", footerChildren));
  }

  // `scene-surface` es el gancho compartido que Caelestia viste como tarjeta
  // Material You (themes.css); en Vice/Hyprland no aporta nada por si solo.
  // Quitarlo dejaria "Obra" como texto suelto sobre el degradado en
  // Caelestia — el mismo defecto que ya rompio el hero en la Task 6.
  const surface = el("div", "scene-surface relative", children);

  const section = el(
    "section",
    "scene relative flex min-h-screen flex-col justify-center overflow-hidden border-t border-line px-6 py-24 md:px-12",
    [ordinal, surface],
  );
  section.setAttribute("data-scene", "obra");
  return section;
}
