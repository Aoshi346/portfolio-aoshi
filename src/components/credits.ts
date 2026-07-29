import { caseStudies, skillGroups, type SkillGroup } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { getIconMarkup } from "../utils/icons";

interface CreditEntry {
  role: string;
  name: string;
  slug: string;
  detail: string;
  /**
   * Proyectos de `caseStudies` cuyo `stack` incluye esta tecnologia. Es la
   * prueba de uso real, y sale de datos que ya estaban en `content.ts` sin
   * cruzar: ninguna cadena nueva. Se prefiere a una etiqueta de nivel
   * ("avanzado", "intermedio") porque dice DONDE se uso, que es verificable,
   * en vez de cuanto dice el autor que sabe, que no lo es.
   *
   * Si sale vacio, el bloque entero se oculta: cinco de las doce tecnologias
   * no aparecen en ningun proyecto publicado y rellenarlas con una frase
   * generica seria justo el tipo de relleno que el proyecto prohibe.
   */
  usedIn: string[];
}

const PANEL_ID = "credits-panel";

function toEntry(role: string, item: SkillGroup["items"][number]): CreditEntry {
  return {
    role,
    name: item.name,
    slug: item.slug,
    detail: item.detail,
    // Se cruza contra `stack` Y `tooling`: Git, GitHub y las dos CLI de IA no
    // estan en el stack de ningun proyecto porque `stack` se pinta literal en
    // la ficha de obra y ahi cuatro nombres repetidos en los cinco proyectos
    // no distinguen nada. Sin este segundo array, esas cuatro tecnologias
    // saldrian como "sin proyecto publicado" siendo falso.
    usedIn: caseStudies
      .filter((project) => [...project.stack, ...(project.tooling ?? [])].includes(item.name))
      .map((project) => project.title),
  };
}

/**
 * Creditos de pelicula interactivos, agrupados por area. La lista a la
 * izquierda y, a la derecha, el icono real de la tecnologia, para que se usa y
 * en que proyectos aparece. El panel nunca arranca vacio.
 *
 * El encabezado de grupo (`.credit-group-label`) NO envuelve a sus filas: es
 * un hermano plano mas dentro de `.credits-list`. Dos razones, las dos
 * comprobadas antes de escribir esto:
 *
 *  1. `scene4Credits` (vice.choreography.ts) anima los hijos DIRECTOS de
 *     `[data-credit-roll]`. Un envoltorio por grupo reduciria el escalonado de
 *     doce filas a tres bloques; asi, ademas, los encabezados entran tambien.
 *  2. `scripts/verify.py` exige que `.credit-role` exista en el DOM y este
 *     oculto por CSS en Hyprland/Caelestia — es el gate que protege el re-skin
 *     a pildoras. Por eso ese `<span>` sigue aqui aunque en Vice no se vea: se
 *     oculta con CSS, no se elimina.
 *
 * Accesibilidad: cada fila es un `<button>` real, enfocable con Tab, que
 * dispara el mismo `select()` en `mouseenter`, `focus` y `click`, con
 * `aria-pressed` (cual esta activa) y `aria-controls` apuntando al panel; el
 * panel es `aria-live="polite"` para que un lector anuncie el cambio sin mover
 * el foco. El icono es decorativo puro: `aria-hidden` (fuera del arbol de
 * accesibilidad) y `data-decorative` (exento del gate de contraste — nunca
 * `aria-hidden` para eso, ver `scripts/verify.py::check_contrast_wcag`).
 */
export function createCredits(): HTMLElement {
  // `skillGroups` ya trae los seis bloques del reparto. Antes habia que
  // coserle a mano un grupo "Otras herramientas" desde `secondarySkills`; ese
  // array desaparecio al reorganizar el contenido y su contenido vive ahora en
  // el bloque "Lenguajes base".
  const groups: SkillGroup[] = skillGroups;

  const icon = el("div", "credits-icon", []);
  icon.setAttribute("aria-hidden", "true");
  icon.setAttribute("data-decorative", "");

  const name = el("p", "credits-panel-name display-lg text-2xl", []);
  const role = el("p", "credits-panel-role", []);
  const detail = el("p", "credits-panel-detail", []);

  const usedList = el("div", "credits-used-list", []);
  usedList.setAttribute("data-credit-used-list", "");
  const used = el("div", "credits-used", [
    el("p", "credits-used-label", ["Aparece en"]),
    usedList,
  ]);
  used.setAttribute("data-credit-used", "");

  const panel = el("div", "credits-panel scene-surface", [icon, name, role, detail, used]);
  panel.id = PANEL_ID;
  panel.setAttribute("data-credit-panel", "");
  panel.setAttribute("role", "status");
  panel.setAttribute("aria-live", "polite");

  const rows: HTMLButtonElement[] = [];
  const listChildren: HTMLElement[] = [];

  /*
   * Friso de marcas: donde un cartel de cine pone los logos de estudio y
   * distribuidora. Va al pie y no delante de cada nombre porque una marca por
   * nombre convierte la linea de reparto en una lista con vinetas — el
   * defecto exacto que la direccion de cartel elimina.
   *
   * Se declara AQUI, antes del bucle, y no despues: `select()` se define
   * dentro del bucle y cierra sobre `marks`. Declararlo despues compila con
   * "used before its declaration".
   *
   * El Map indexa por slug para encender la marca en O(1): `mouseenter` se
   * dispara muchas veces por segundo al recorrer el cartel con el raton y no
   * puede volver a recorrer el DOM en cada disparo.
   */
  const marks = new Map<string, HTMLElement>();
  const markNodes: HTMLElement[] = [];

  for (const group of groups) {
    const groupLabel = el("p", "credit-group-label", [group.label]);
    groupLabel.setAttribute("data-credit-group", "");
    listChildren.push(groupLabel);

    for (const item of group.items) {
      const entry = toEntry(group.label, item);
      const row = el("button", "credit", [
        el("span", "credit-role", [entry.role]),
        el("span", "credit-name", [entry.name]),
      ]);
      row.type = "button";
      row.setAttribute("data-credit", "");
      row.dataset.index = String(rows.length);
      row.setAttribute("aria-controls", PANEL_ID);
      row.setAttribute("aria-pressed", "false");

      /*
       * Decorativa pura: `aria-hidden` la saca del arbol de accesibilidad
       * (el nombre ya esta en el boton, la marca no anade informacion) y
       * `data-decorative` la exime del gate de contraste. Nunca `aria-hidden`
       * para eximir contraste: ver `scripts/verify.py::check_contrast_wcag`.
       */
      const mark = elFromMarkup("credits-mark", getIconMarkup(entry.slug));
      mark.setAttribute("aria-hidden", "true");
      mark.setAttribute("data-decorative", "");
      mark.dataset.markSlug = entry.slug;
      marks.set(entry.slug, mark);
      markNodes.push(mark);

      const select = () => {
        for (const other of rows) {
          other.classList.remove("is-active");
          other.setAttribute("aria-pressed", "false");
        }
        row.classList.add("is-active");
        row.setAttribute("aria-pressed", "true");
        icon.replaceChildren(elFromMarkup("credits-svg", getIconMarkup(entry.slug)));
        name.textContent = entry.name;
        role.textContent = entry.role;
        detail.textContent = entry.detail;
        usedList.replaceChildren(
          ...entry.usedIn.map((title) => el("span", "credits-used-item", [title])),
        );
        // Sin proyectos publicados, la seccion desaparece entera en vez de
        // mostrar una etiqueta vacia o una excusa.
        used.hidden = entry.usedIn.length === 0;
        // La marca encendida es una segunda senal de seleccion que no depende
        // del hover: en tactil no lo hay, y el cartel no tiene recuadros ni
        // bordes que delaten que un nombre responde.
        for (const [slug, node] of marks) {
          node.classList.toggle("is-active", slug === entry.slug);
        }
      };

      row.addEventListener("mouseenter", select);
      row.addEventListener("focus", select);
      row.addEventListener("click", select);

      rows.push(row);
      listChildren.push(row);
    }
  }

  const list = el("div", "credits-list", listChildren);
  list.setAttribute("data-credit-roll", "");

  /*
   * El friso es hermano de la lista y del panel, NUNCA hijo de
   * `[data-credit-roll]`: `scene4Credits` anima los hijos DIRECTOS de ese
   * contenedor, y meter aqui 23 nodos mas ahogaria el escalonado del reparto.
   * Los otros dos temas lo apagan con una sola regla sin tocar su flex-wrap.
   */
  const frieze = el("div", "credits-marks", markNodes);
  frieze.setAttribute("data-credit-marks", "");
  frieze.setAttribute("aria-hidden", "true");
  frieze.setAttribute("data-decorative", "");

  // Estado inicial: el panel muestra la primera entrada sin esperar a que
  // alguien interactue. `rows[0]` siempre existe: `skillGroups` nunca esta
  // vacio.
  rows[0]?.dispatchEvent(new MouseEvent("mouseenter"));

  return el("div", "credits-grid", [list, panel, frieze]);
}
