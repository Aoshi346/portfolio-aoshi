import { skillGroups } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { getIconMarkup } from "../utils/icons";

export interface HyprStackCimientosHandle {
  destroy: () => void;
}

/**
 * Los cimientos (spec 2026-09-09-hyprland-stack-cimientos): tres areas en
 * columnas sobre un suelo de brasa con los cinco lenguajes base. DOM propio
 * montado como hermano de `.credits` dentro de `[data-scene="credits"]`; el
 * generico se oculta entero desde themes.css (patron B3/B4 de Caelestia).
 *
 * Sin GSAP: el disparo de la entrada es un IntersectionObserver anclado a la
 * caja del PROPIO dispositivo (top 80%), no a la seccion — con `is-lit` de
 * la seccion a `top 90%` la placa de "Quien soy" corria su montaje entero
 * 119px bajo el pliegue y nadie lo vio nunca (fallo 1 del repaso). Los
 * tiempos los marca el CSS.
 */
const ROTULO_SUELO = "Lenguajes base";

function construirNombre(name: string, slug: string, detail: string): HTMLButtonElement {
  const icono = elFromMarkup("cim-icono", getIconMarkup(slug));
  icono.setAttribute("aria-hidden", "true");
  icono.setAttribute("data-decorative", "");
  const boton = el("button", "cim-nombre", [icono, el("span", "cim-txt", [name])]);
  boton.type = "button";
  boton.setAttribute("aria-pressed", "false");
  boton.dataset.cimNombre = name;
  boton.dataset.cimDetail = detail;
  return boton;
}

function construirLista(clase: string, items: ReadonlyArray<{ name: string; slug: string; detail: string }>): HTMLUListElement {
  return el(
    "ul",
    clase,
    items.map((it) => el("li", "", [construirNombre(it.name, it.slug, it.detail)])),
  );
}

export function mountHyprStackCimientos(root: HTMLElement): HyprStackCimientosHandle {
  const escena = root.querySelector<HTMLElement>('[data-scene="credits"]');
  if (!escena) return { destroy: () => undefined };

  const suelo = skillGroups.find((g) => g.label === ROTULO_SUELO);
  const areas = skillGroups.filter((g) => g.label !== ROTULO_SUELO);
  if (!suelo || areas.length !== 3) return { destroy: () => undefined };

  const columnas = areas.map((g, i) => {
    const col = el("section", "cim-col", [
      el("h3", "cim-rot", [g.label]),
      construirLista("cim-lista", g.items),
    ]);
    col.style.setProperty("--cim-c", String(i));
    return col;
  });

  const linea = el("span", "cim-linea", []);
  linea.setAttribute("aria-hidden", "true");
  const frase = el("p", "cim-frase", []);
  frase.setAttribute("aria-live", "polite");
  const cab = el("div", "cim-cab", [el("h3", "cim-rot", [suelo.label]), frase]);
  const lenguajes = construirLista("cim-lenguajes", suelo.items);

  const cim = el("div", "cim", [
    el("div", "cim-cols", columnas),
    el("div", "cim-suelo", [linea, cab, lenguajes]),
  ]);
  cim.setAttribute("data-cimientos", "");
  escena.append(cim);

  // El retardo de cada lenguaje sale de SU x real sobre el ancho del suelo:
  // la linea tarda 500ms en cruzar, y el nombre se enciende cuando la linea
  // llega a su columna. Se mide tras el append, con layout ya disponible.
  const anchoSuelo = lenguajes.getBoundingClientRect().width || 1;
  const izq = lenguajes.getBoundingClientRect().left;
  for (const boton of Array.from(lenguajes.querySelectorAll<HTMLElement>(".cim-nombre"))) {
    const x = boton.getBoundingClientRect().left - izq;
    boton.style.setProperty("--cim-d", `${Math.round((x / anchoSuelo) * 500)}ms`);
  }

  // Disparo anclado a la caja de los cimientos: top al 80% de la ventana.
  // `rootMargin` negativo abajo recorta el 20% inferior del viewport, asi que
  // "intersecta" equivale a "el borde superior ha cruzado el 80%". Con
  // movimiento reducido no hay entrada: el estado final se pone al montar.
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let observador: IntersectionObserver | null = null;
  if (reduce) {
    cim.classList.add("cimientos-lit");
  } else {
    observador = new IntersectionObserver(
      (entradas) => {
        if (entradas.some((e) => e.isIntersecting)) {
          cim.classList.add("cimientos-lit");
          observador?.disconnect();
          observador = null;
        }
      },
      { rootMargin: "0px 0px -20% 0px", threshold: 0 },
    );
    observador.observe(cim);
  }

  return {
    destroy: () => {
      observador?.disconnect();
      cim.remove();
    },
  };
}
