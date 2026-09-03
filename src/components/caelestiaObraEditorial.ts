import { caseStudies } from "../data/content";
import { el } from "../utils/dom";

export interface CaelestiaObraEditorialHandle {
  destroy: () => void;
}

const TILTS = [-5, 4, -3, 5, -4];

/**
 * La Editorial: la fila de cinco tarjetas nunca se mueve (es la "lista
 * quieta" del eje compartido de Material 3) y el cajon que abre debajo es
 * lo unico que entra o cambia. Construye TODO desde `caseStudies`, no
 * desde el DOM generico de `projectScene.ts` — ese DOM sigue existiendo
 * para Vice/Hyprland pero `themes.css` lo oculta entero bajo Caelestia
 * (Task 1), asi que raspar su texto seria leer un arbol invisible.
 */
export async function mountCaelestiaObraEditorial(
  root: HTMLElement,
): Promise<CaelestiaObraEditorialHandle> {
  const rail = root.querySelector<HTMLElement>("[data-obra-rail]");
  if (!rail) throw new Error("La Editorial de Obra necesita [data-obra-rail]");

  const row = el(
    "div",
    "cae-obra-row",
    caseStudies.map((project, index) => buildCard(project.title, project.tag, index)),
  );

  rail.append(row);

  return {
    destroy: () => {
      row.remove();
    },
  };
}

function buildCard(title: string, tag: string, index: number): HTMLButtonElement {
  const project = caseStudies[index];
  const shot = project.gallery[0];

  const thumb = el("div", "cae-obra-thumb", []);
  if (shot) {
    const img = el("img") as HTMLImageElement;
    img.src = shot.src;
    img.alt = shot.caption;
    img.loading = "lazy";
    img.decoding = "async";
    thumb.append(img);
  }

  const card = el("button", "cae-obra-card", [
    thumb,
    el("figcaption", "cae-obra-caption", [title, el("span", "cae-obra-tag", [tag])]),
  ]);
  card.type = "button";
  card.dataset.obraCard = String(index);
  card.setAttribute("aria-label", `Ver ${title}`);
  card.style.setProperty("--cae-obra-tilt", `${TILTS[index % TILTS.length]}deg`);

  return card;
}
