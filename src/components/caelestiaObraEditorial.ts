import { caseStudies } from "../data/content";
import type { CaseStudy } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { getIconMarkup } from "../utils/icons";
import { slugDeStack } from "../utils/stackIcons";

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

  const cards = Array.from(row.querySelectorAll<HTMLButtonElement>(".cae-obra-card"));
  const drawer = el("div", "cae-obra-drawer", []);
  drawer.setAttribute("aria-live", "polite");
  rail.append(drawer);

  let seleccionado = -1;

  function poblarCajon(index: number): void {
    const project = caseStudies[index];
    drawer.replaceChildren(
      el("div", "cae-obra-drawer-title", [
        el("div", "cae-obra-drawer-kick", [project.tag]),
        el("h3", "", [project.title]),
        el("p", "cae-obra-drawer-lead", [project.lead]),
        buildFoot(project),
      ]),
      buildPreview(project),
      buildMeta(project),
      el("div", "cae-obra-prose", [
        el("div", "", [el("h4", "", ["Problema"]), el("p", "", [project.problem])]),
        el("div", "", [el("h4", "", ["Solución"]), el("p", "", [project.solution])]),
      ]),
    );
  }

  function abrir(index: number): void {
    if (index === seleccionado) return;
    cards[seleccionado]?.classList.remove("is-sel");
    seleccionado = index;
    cards[seleccionado]?.classList.add("is-sel");
    poblarCajon(index);
  }

  cards.forEach((card, index) => {
    card.addEventListener("click", () => abrir(index));
  });

  abrir(0);

  return {
    destroy: () => {
      row.remove();
      drawer.remove();
    },
  };
}

function buildPreview(project: CaseStudy): HTMLElement {
  const shot = project.gallery[0];
  const thumb = el("div", "cae-obra-thumb is-sel", []);
  if (shot) {
    const img = el("img") as HTMLImageElement;
    img.src = shot.src;
    img.alt = shot.caption;
    img.loading = "lazy";
    img.decoding = "async";
    thumb.append(img);
  }
  return el("div", "cae-obra-drawer-preview", [thumb]);
}

function buildMeta(project: CaseStudy): HTMLElement {
  const rows: HTMLElement[] = [
    el("div", "", [el("dt", "", ["Rol"]), el("dd", "", [project.role])]),
  ];
  if (project.period) {
    rows.push(el("div", "", [el("dt", "", ["Periodo"]), el("dd", "", [project.period])]));
  }
  rows.push(
    el("div", "", [
      el("dt", "", ["Stack"]),
      el(
        "dd",
        "cae-obra-stack",
        project.stack.map((nombre) => {
          const slug = slugDeStack(nombre);
          if (!slug) return el("span", "cae-obra-stack-text", [nombre]);
          const tile = el("span", "obra-marca", [
            elFromMarkup("obra-marca-svg", getIconMarkup(slug)),
          ]);
          tile.title = nombre;
          return tile;
        }),
      ),
    ]),
  );
  rows.push(el("div", "", [el("dt", "", ["Estado"]), el("dd", "", [project.status])]));
  return el("dl", "cae-obra-drawer-meta", rows);
}

function buildFoot(project: CaseStudy): HTMLElement {
  const foot = el("div", "cae-obra-foot", []);
  if (project.link) {
    const link = el("a", "", [`${project.link.label} →`]) as HTMLAnchorElement;
    link.href = project.link.href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    foot.append(link);
  } else if (project.privateProject) {
    foot.append(
      el("span", "cae-obra-foot-private", [
        el("i", "", []),
        "Proyecto privado de empresa",
      ]),
    );
  }
  return foot;
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
