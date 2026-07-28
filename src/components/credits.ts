import { secondarySkills, skillGroups, type SkillGroup } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { getIconMarkup } from "../utils/icons";

interface CreditEntry {
  role: string;
  name: string;
  slug: string;
  detail: string;
}

/**
 * Aplana `skillGroups` + `secondarySkills` (ambos de `content.ts`, ninguna
 * cadena nueva) en una sola lista de creditos. Sin esto, las herramientas
 * secundarias (JavaScript, HTML, CSS, C, C++) se perderian: `createSkills`
 * dejaria de referenciarlas y quedarian huerfanas en `content.ts`.
 */
function flatten(): CreditEntry[] {
  const groups: SkillGroup[] = [...skillGroups, { label: "Otras herramientas", items: secondarySkills }];
  return groups.flatMap((group) =>
    group.items.map((item) => ({
      role: group.label,
      name: item.name,
      slug: item.slug,
      detail: item.detail,
    })),
  );
}

const PANEL_ID = "credits-panel";

/**
 * Creditos de pelicula interactivos: la lista a la izquierda y, a la derecha,
 * el icono real de la tecnologia y para que se usa. El panel nunca arranca
 * vacio. Responde a hover Y a foco de teclado (no solo raton): cada fila es
 * un `<button>` real, enfocable con Tab, que dispara el mismo `select()` en
 * `mouseenter`, `focus` y `click`.
 *
 * Accesibilidad: cada fila lleva `aria-pressed` (cual esta activa) y
 * `aria-controls` apuntando al panel; el panel es `aria-live="polite"` para
 * que un lector de pantalla anuncie el cambio de contenido sin que el foco
 * se mueva. El icono es decorativo puro (la info va en texto): se marca con
 * `aria-hidden` (fuera del arbol de accesibilidad) y `data-decorative`
 * (exento del gate de contraste — nunca `aria-hidden` para eso, ver
 * `scripts/verify.py::check_contrast_wcag`).
 */
export function createCredits(): HTMLElement {
  const entries = flatten();

  const icon = el("div", "credits-icon", []);
  icon.setAttribute("aria-hidden", "true");
  icon.setAttribute("data-decorative", "");

  const name = el("p", "credits-panel-name display-lg text-2xl", []);
  const role = el("p", "credits-panel-role", []);
  const detail = el("p", "credits-panel-detail", []);

  const panel = el("div", "credits-panel scene-surface", [icon, name, role, detail]);
  panel.id = PANEL_ID;
  panel.setAttribute("data-credit-panel", "");
  panel.setAttribute("role", "status");
  panel.setAttribute("aria-live", "polite");

  const rows = entries.map((entry, index) => {
    const row = el("button", "credit", [
      el("span", "credit-role", [entry.role]),
      el("span", "credit-name", [entry.name]),
    ]);
    row.type = "button";
    row.setAttribute("data-credit", "");
    row.dataset.index = String(index);
    row.setAttribute("aria-controls", PANEL_ID);
    row.setAttribute("aria-pressed", "false");

    const select = () => {
      rows.forEach((other) => {
        other.classList.remove("is-active");
        other.setAttribute("aria-pressed", "false");
      });
      row.classList.add("is-active");
      row.setAttribute("aria-pressed", "true");
      icon.replaceChildren(elFromMarkup("credits-svg", getIconMarkup(entry.slug)));
      name.textContent = entry.name;
      role.textContent = entry.role;
      detail.textContent = entry.detail;
    };

    row.addEventListener("mouseenter", select);
    row.addEventListener("focus", select);
    row.addEventListener("click", select);
    return row;
  });

  const list = el("div", "credits-list", rows);
  list.setAttribute("data-credit-roll", "");

  // Estado inicial: el panel muestra la primera entrada sin esperar a que
  // alguien interactue. `rows[0]` siempre existe: `flatten()` nunca devuelve
  // una lista vacia (skillGroups + secondarySkills traen contenido real).
  rows[0]?.dispatchEvent(new MouseEvent("mouseenter"));

  return el("div", "credits-grid", [list, panel]);
}
