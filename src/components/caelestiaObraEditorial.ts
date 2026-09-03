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

  const { default: gsap } = await import("gsap");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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
  let tl: ReturnType<typeof gsap.timeline> | null = null;

  function refsCajon(): {
    h3: HTMLElement | null;
    kick: HTMLElement | null;
    lead: HTMLElement | null;
    foot: HTMLElement | null;
    preview: HTMLElement | null;
    rows: HTMLElement[];
    blocks: HTMLElement[];
  } {
    return {
      h3: drawer.querySelector<HTMLElement>("[data-cae-obra-h3]"),
      kick: drawer.querySelector<HTMLElement>(".cae-obra-drawer-kick"),
      lead: drawer.querySelector<HTMLElement>(".cae-obra-drawer-lead"),
      foot: drawer.querySelector<HTMLElement>(".cae-obra-foot"),
      preview: drawer.querySelector<HTMLElement>(".cae-obra-drawer-preview"),
      rows: Array.from(drawer.querySelectorAll<HTMLElement>(".cae-obra-drawer-meta > div")),
      blocks: Array.from(drawer.querySelectorAll<HTMLElement>(".cae-obra-prose > div")),
    };
  }

  function poblarCajon(index: number): void {
    const project = caseStudies[index];
    const titleBlock = el("div", "cae-obra-drawer-title", [
      el("div", "cae-obra-drawer-kick", [project.tag]),
      el("h3", "", [project.title]),
      el("p", "cae-obra-drawer-lead", [project.lead]),
      buildFoot(project),
    ]);
    titleBlock.querySelector("h3")?.setAttribute("data-cae-obra-h3", "");
    const preview = buildPreview(project);
    const meta = buildMeta(project);
    const prose = el("div", "cae-obra-prose", [
      el("div", "", [el("h4", "", ["Problema"]), el("p", "", [project.problem])]),
      el("div", "", [el("h4", "", ["Solución"]), el("p", "", [project.solution])]),
    ]);
    drawer.replaceChildren(titleBlock, preview, meta, prose);
  }

  function abrir(index: number): void {
    if (index === seleccionado) return;
    cards[seleccionado]?.classList.remove("is-sel");
    seleccionado = index;
    cards[seleccionado]?.classList.add("is-sel");
    poblarCajon(index);
    if (reduce) return;
    gsap.fromTo(
      drawer,
      { opacity: 0, y: 14 },
      { opacity: 1, y: 0, duration: 0.3, ease: "cubic-bezier(0.7,0,0.2,1)" },
    );
  }

  cards.forEach((card, index) => {
    card.addEventListener("click", () => abrir(index));
    if (reduce) return;
    card.addEventListener("pointerenter", () => {
      gsap.to(card, {
        y: -6,
        rotate: 0,
        boxShadow: "0 18px 34px -8px rgba(0,0,0,.5)",
        duration: 0.22,
        ease: "power2.out",
      });
    });
    card.addEventListener("pointerleave", () => {
      gsap.to(card, {
        y: 0,
        rotate: 0,
        boxShadow: "0 10px 22px -8px rgba(0,0,0,.4)",
        duration: 0.22,
        ease: "power2.out",
      });
    });
  });

  let entrado = false;

  /**
   * Deja la fila y el cajon en el estado de "listos pero ocultos" (tarjetas
   * arriba, giradas, cajon invisible) y puebla la tarjeta 0 como
   * seleccionada — igual que hacia `entrarConCaida()` antes de tocar el
   * timeline. Se llama una vez al montar (Obra esta fuera de pantalla e
   * `inert` en ese momento: la escena por defecto es Titulo) para que la
   * caida tenga algo que animar la primera vez que el visitante navegue de
   * verdad a Obra, en vez de jugarse y asentarse mientras nadie mira.
   */
  function prepararEstadoInicial(): void {
    cards.forEach((card, index) => {
      const tilt = TILTS[index] ?? 0;
      gsap.set(card, { opacity: 0, y: -46, rotate: tilt, transformOrigin: "50% 0%" });
    });

    seleccionado = 0;
    cards[0]?.classList.add("is-sel");
    poblarCajon(0);

    const { h3, kick, lead, foot, preview, rows, blocks } = refsCajon();

    gsap.set(drawer, { opacity: 0 });
    if (h3) gsap.set(h3, { clipPath: "inset(0 100% 0 0)" });
    gsap.set([kick, lead, foot].filter(Boolean), { opacity: 0, y: 6 });
    if (preview) gsap.set(preview, { opacity: 0, scale: 0.94 });
    gsap.set(rows, { opacity: 0, y: 8 });
    gsap.set(blocks, { opacity: 0, y: 8 });
  }

  /**
   * La animacion de la caida en si: cinco tarjetas cayendo con rotacion y
   * rebote, luego el cajon en cuatro capas. Se dispara solo al llegar de
   * verdad a la escena de Obra (evento `caelestia:workspace`), no al
   * montar — ver Task 7.
   */
  function jugarEntrada(): void {
    const { h3, kick, lead, foot, preview, rows, blocks } = refsCajon();

    tl = gsap.timeline();
    tl.fromTo(
      cards,
      { opacity: 0, y: -46, rotate: (i: number) => TILTS[i] ?? 0 },
      { opacity: 1, y: 0, rotate: 0, duration: 0.5, ease: "bounce.out", stagger: 0.08 },
    )
      .to(drawer, { opacity: 1, duration: 0.01 }, "-=.1")
      .to(kick, { opacity: 1, y: 0, duration: 0.2, ease: "power2.out" }, "-=.05")
      .to(h3, { clipPath: "inset(0 0% 0 0)", duration: 0.42, ease: "power2.inOut" }, "-=.05")
      .to(preview, { opacity: 1, scale: 1, duration: 0.32, ease: "power2.out" }, "-=.3")
      .to([lead, foot], { opacity: 1, y: 0, duration: 0.22, ease: "power2.out", stagger: 0.06 }, "-=.18")
      .to(rows, { opacity: 1, y: 0, duration: 0.24, ease: "power2.out", stagger: 0.06 }, "-=.1")
      .to(blocks, { opacity: 1, y: 0, duration: 0.26, ease: "power2.out", stagger: 0.08 }, "-=.12");
  }

  const alCambiarWorkspace = (evento: Event): void => {
    if (entrado) return;
    if (!(evento instanceof CustomEvent)) return;
    const detalle: unknown = evento.detail;
    if (typeof detalle !== "object" || detalle === null || !("id" in detalle)) return;
    if ((detalle as { id: unknown }).id !== "obra") return;
    entrado = true;
    jugarEntrada();
  };

  if (reduce) {
    abrir(0);
  } else {
    prepararEstadoInicial();
    document.documentElement.addEventListener("caelestia:workspace", alCambiarWorkspace);
    if (document.querySelector('[data-cae-ws="obra"][aria-current="true"]')) {
      entrado = true;
      jugarEntrada();
    }
  }

  return {
    destroy: () => {
      document.documentElement.removeEventListener("caelestia:workspace", alCambiarWorkspace);
      tl?.kill();
      gsap.killTweensOf([...cards, drawer]);
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

  return card;
}
