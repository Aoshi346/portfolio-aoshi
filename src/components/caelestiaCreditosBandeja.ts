import { caseStudies, skillGroups } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { figuraDe, figuraSuaveDe, radioInscritoDe } from "../utils/figurasM3";
import { getIconMarkup } from "../utils/icons";

export interface CaelestiaCreditosHandle {
  destroy: () => void;
}

interface Pieza {
  readonly territorio: string;
  readonly name: string;
  readonly slug: string;
  readonly detail: string;
  readonly obras: readonly string[];
}

/** 88 y no 96: al rozar, la figura crece un 7 % (unos 3 px por lado) y con 96
 *  el canto superior llegaba a tocar el filete de la banda anterior. Medido:
 *  22,5 px de holgura en reposo, 19,2 rozando. */
const LADO = 88;

/**
 * El cruce contra las obras se hace contra `stack` Y `tooling`, que es el mismo
 * cruce que hace `credits.ts::toEntry`. Sin el segundo array, Git, GitHub y las
 * dos CLI saldrian como "sin obra publicada" siendo justo lo contrario: estan
 * en todos los proyectos, y no aparecen en `stack` porque `stack` se pinta
 * literal en la ficha de obra y ahi cuatro nombres repetidos no distinguen nada.
 */
function obrasDe(name: string): string[] {
  return caseStudies
    .filter((p) => [...p.stack, ...(p.tooling ?? [])].includes(name))
    .map((p) => p.title);
}

/** Mismo resumen que `credits.ts::textoCruce`, sin duplicar la decision: con
 *  cuatro o cinco obras no se listan los titulos porque no distinguen nada. */
function cruceTexto(obras: readonly string[]): string[] {
  if (obras.length === 5) return ["Los cinco proyectos"];
  if (obras.length === 4) return ["Cuatro de los cinco proyectos"];
  return [...obras];
}

/** El icono se acota por el radio inscrito de SU figura, no por la caja. */
function ladoIcono(slug: string): number {
  const cabe = (LADO * radioInscritoDe(slug) * 0.88) / Math.SQRT2;
  return Math.max(17, Math.round(Math.min(LADO * 0.3, cabe)));
}

function construirPieza(p: Pieza): HTMLButtonElement {
  const fig = el("span", "cae-cred-fig", [
    elFromMarkup("cae-cred-icono", getIconMarkup(p.slug)),
  ]);
  fig.style.setProperty("--fig", figuraDe(p.slug));
  fig.style.setProperty("--fig-suave", figuraSuaveDe(p.slug));
  fig.style.width = `${LADO}px`;
  fig.style.height = `${LADO}px`;
  const icono = fig.firstElementChild as HTMLElement;
  icono.style.width = `${ladoIcono(p.slug)}px`;
  icono.style.height = `${ladoIcono(p.slug)}px`;
  icono.setAttribute("aria-hidden", "true");
  icono.setAttribute("data-decorative", "");

  const boton = el("button", "cae-cred-pieza", [
    fig,
    el("figcaption", "cae-cred-nom", [p.name]),
  ]) as HTMLButtonElement;
  boton.type = "button";
  boton.dataset.pieza = p.name;
  boton.setAttribute("aria-pressed", "false");
  return boton;
}

export async function mountCaelestiaCreditosBandeja(
  root: HTMLElement,
): Promise<CaelestiaCreditosHandle> {
  const escena = root.querySelector<HTMLElement>('[data-scene="credits"]');
  if (!escena) throw new Error("La bandeja de Creditos necesita [data-scene=credits]");

  const { default: gsap } = await import("gsap");

  const piezas: Pieza[] = skillGroups.flatMap((g) =>
    g.items.map((it) => ({
      territorio: g.label,
      name: it.name,
      slug: it.slug,
      detail: it.detail,
      obras: obrasDe(it.name),
    })),
  );

  // La cabecera se releva EN EL SITIO: 96 px fijos, nada mas se mueve.
  const marca = el("span", "cae-cred-marca", []);
  const nombre = el("h3", "cae-cred-nombre", []);
  const detalle = el("p", "cae-cred-detalle", []);
  const territorio = el("p", "cae-cred-terr", []);
  const cruceLista = el("ul", "cae-cred-cruce-lista", []);
  const cruce = el("div", "cae-cred-cruce", [
    el("span", "", ["Aparece en"]),
    cruceLista,
  ]);
  const cabecera = el("div", "cae-cred-cab", [
    marca,
    el("div", "", [nombre, detalle, territorio]),
    cruce,
  ]);

  const bandas = skillGroups.map((g) => {
    const tira = el(
      "div",
      "cae-cred-tira",
      g.items.map((it) =>
        construirPieza(piezas.find((p) => p.name === it.name) as Pieza),
      ),
    );
    // El filete de la banda llega solo hasta su ultima pieza, asi que su LARGO
    // es la masa del territorio. Dice el recuento sin escribir el numero, y
    // sale de `items.length`, no de un dato nuevo.
    tira.style.setProperty("--piezas", String(g.items.length));
    return el("div", "cae-cred-banda", [
      el("div", "cae-cred-rot", [el("h4", "", [g.label])]),
      tira,
    ]);
  });

  const wrap = el("div", "cae-cred-wrap", [cabecera, el("div", "cae-cred-grid", bandas)]);
  escena.append(wrap);

  function pintarFicha(p: Pieza): void {
    marca.replaceChildren(elFromMarkup("", getIconMarkup(p.slug)));
    marca.style.clipPath = figuraDe(p.slug);
    nombre.textContent = p.name;
    detalle.textContent = p.detail;
    territorio.textContent = p.territorio;
    const lineas = cruceTexto(p.obras);
    cruceLista.replaceChildren(
      ...(p.obras.length === 0
        ? [el("li", "is-vacia", ["Sin obra publicada"])]
        : lineas.map((t) => el("li", "", [t]))),
    );
  }

  pintarFicha(piezas[0]);

  return {
    destroy: () => {
      gsap.killTweensOf(escena.querySelectorAll("*"));
      wrap.remove();
    },
  };
}
