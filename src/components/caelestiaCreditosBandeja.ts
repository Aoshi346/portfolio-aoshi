import { caseStudies, skillGroups } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import {
  FIGURA_CIRCULO,
  figuraDe,
  figuraSuaveDe,
  radioInscritoDe,
} from "../utils/figurasM3";
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
  fig.style.setProperty("--fig-circ", FIGURA_CIRCULO);
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

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const botones = Array.from(
    escena.querySelectorAll<HTMLButtonElement>(".cae-cred-pieza"),
  );
  const grid = escena.querySelector<HTMLElement>(".cae-cred-grid");
  let elegida = piezas[0].name;
  // La cabecera ya muestra la primera pieza al montar: el estado accesible
  // tiene que decir lo mismo desde el primer fotograma, no solo tras la
  // primera interaccion.
  for (const b of botones) {
    b.setAttribute("aria-pressed", String(b.dataset.pieza === elegida));
  }

  function elegir(nombrePieza: string): void {
    if (elegida === nombrePieza) return;
    const p = piezas.find((x) => x.name === nombrePieza);
    if (!p) return;
    elegida = nombrePieza;
    pintarFicha(p);
    for (const b of botones) {
      b.setAttribute("aria-pressed", String(b.dataset.pieza === nombrePieza));
    }
    if (reduce) return;
    // La cabecera se releva con barridos de clip-path: nada se desvanece, todo
    // se recorta. Es la ley de seccion heredada del cartel.
    gsap.fromTo(
      [nombre, detalle, territorio, cruceLista],
      { clipPath: "inset(0px 100% 0px 0px)" },
      {
        clipPath: "inset(0px 0% 0px 0px)",
        duration: 0.22,
        stagger: 0.03,
        ease: "power2.out",
      },
    );
    gsap.fromTo(
      marca,
      { clipPath: "circle(0% at 50% 50%)" },
      { clipPath: figuraDe(p.slug), duration: 0.26, ease: "power2.out" },
    );
  }

  // Rozar elige: no hace falta pulsar. Clic y foco hacen lo mismo, para que el
  // teclado llegue adonde llega el raton.
  const escuchas: Array<() => void> = [];
  for (const b of botones) {
    const nombrePieza = b.dataset.pieza ?? "";
    const entrar = (): void => {
      grid?.classList.add("is-tocando");
      elegir(nombrePieza);
    };
    const salir = (): void => grid?.classList.remove("is-tocando");
    b.addEventListener("mouseenter", entrar);
    b.addEventListener("focus", entrar);
    b.addEventListener("click", entrar);
    b.addEventListener("blur", salir);
    b.addEventListener("mouseleave", salir);
    escuchas.push(() => {
      b.removeEventListener("mouseenter", entrar);
      b.removeEventListener("focus", entrar);
      b.removeEventListener("click", entrar);
      b.removeEventListener("blur", salir);
      b.removeEventListener("mouseleave", salir);
    });
  }

  // «La instalacion»: las 23 llegan como circulos identicos —paquetes sin
  // abrir— y cada una morfa a su figura mientras crece y se endereza. La
  // onda va POR TERRITORIOS: cada familia arranca 190 ms detras de la
  // anterior, y dentro de cada una las piezas se escalonan 34 ms.
  const offEntrada: Array<() => void> = [];
  if (!reduce) {
    escena.setAttribute("data-cred-entrando", "");
    let indice = 0;
    skillGroups.forEach((g, gi) => {
      g.items.forEach((_, i) => {
        const fig = botones[indice]?.querySelector<HTMLElement>(".cae-cred-fig");
        fig?.style.setProperty("--retardo", `${260 + gi * 190 + i * 34}ms`);
        indice += 1;
      });
    });
    // Cada nodo SUELTA su animacion al acabar. Con `both`, `transform` y
    // `clip-path` se quedan congelados en el ultimo fotograma y le ganan al
    // `:hover` y al estado elegido: el morfado al rozar no ocurria, sin error
    // ninguno.
    for (const b of botones) {
      const fig = b.querySelector<HTMLElement>(".cae-cred-fig");
      if (!fig) continue;
      const soltar = (): void => {
        fig.style.animation = "none";
      };
      fig.addEventListener("animationend", soltar, { once: true });
      offEntrada.push(() => fig.removeEventListener("animationend", soltar));
    }
  }

  return {
    destroy: () => {
      for (const off of escuchas) off();
      for (const off of offEntrada) off();
      gsap.killTweensOf(escena.querySelectorAll("*"));
      wrap.remove();
    },
  };
}
