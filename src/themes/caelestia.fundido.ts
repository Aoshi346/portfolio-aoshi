import type { Gsap } from "./choreography";
import { OJO_DINO, svgDino, svgHorizonte, svgNube } from "./caelestia.dino";
import { identity, sceneIndex } from "../data/content";

/**
 * Lo unico de «Fundido» que el CSS no puede hacer: partir el titular en
 * lineas, montar el troquel con su bicho, y correr el fundido y la entrada.
 *
 * Vive aparte de `caelestia.choreography.ts` a proposito, igual que la ficha
 * de B2: la coreografia gobierna el carril y no tiene por que saber que hay
 * dentro de cada ventana. Aqui no se toca el carril.
 *
 * `gsap` llega SIEMPRE por parametro. Un `import gsap from "gsap"` compila,
 * pasa el linter y revienta en el navegador — le paso a Hyprland y su
 * coreografia no corrio durante semanas.
 */

/** El tramo de horizonte que se ensena dentro del sello de movil. */
const TRAMO_MOVIL = 200;
/** Por debajo de este ancho de ventana, el troquel es un sello entero. */
const ANCHO_SELLO = 640;

export interface FundidoHandle {
  destroy: () => void;
  /** El fundido completo. Suena UNA vez, la primera visita al workspace. */
  reproducir: () => void;
  /** La entrada corta. Suena en cada llegada. `desde` es el workspace de origen. */
  entrar: (desde: number) => void;
}

/** Parte el titular en una linea por renglon natural, para poder trazarlas. */
function partirEnLineas(lead: HTMLElement): HTMLElement[] {
  const texto = lead.textContent ?? "";
  if (!texto.trim()) return [];
  /*
   * Se parte por PALABRAS y se deja que el navegador decida los renglones: el
   * texto sale de `identity.invitation` y no se puede trocear a mano sin
   * inventar contenido. Cada palabra va en un `<span>` en linea; despues se
   * agrupan por su `offsetTop`, que es donde el navegador las ha puesto de
   * verdad.
   */
  lead.textContent = "";
  const palabras = texto.split(/\s+/).filter(Boolean);
  const marcas = palabras.map((palabra, i) => {
    const span = document.createElement("span");
    span.className = "cae-fundido-palabra";
    span.textContent = i === palabras.length - 1 ? palabra : `${palabra} `;
    lead.append(span);
    return span;
  });

  const porFila = new Map<number, HTMLElement[]>();
  for (const marca of marcas) {
    const fila = Math.round(marca.offsetTop);
    const lista = porFila.get(fila);
    if (lista) lista.push(marca);
    else porFila.set(fila, [marca]);
  }

  const lineas: HTMLElement[] = [];
  for (const [, grupo] of [...porFila.entries()].sort((a, b) => a[0] - b[0])) {
    const linea = document.createElement("span");
    linea.className = "cae-fundido-linea";
    linea.setAttribute("data-fundido-linea", "");
    grupo[0].before(linea);
    linea.append(...grupo);
    lineas.push(linea);
  }
  return lineas;
}

export function montarFundido(
  gsap: Gsap,
  escena: HTMLElement,
  // Lo usa `entrar` en la Task 6, para saber de que lado vienes. Se recibe
  // desde ya: cambiar la firma entre tareas es como se rompen los planes.
  indiceEscena: number,
): FundidoHandle | null {
  // Sin uso todavia (lo estrena la Task 6 dentro de `entrar`): esta linea
  // solo lo mantiene "leido" para `noUnusedParameters`/ESLint sin renombrar
  // el parametro ni apagar ninguna regla.
  void indiceEscena;

  const lead = escena.querySelector<HTMLElement>("[data-fundido-lead]");
  const banda = escena.querySelector<HTMLElement>(".contacto-band");
  const barras = escena.querySelector<HTMLElement>(".contacto-bars");
  if (!lead || !banda || !barras) return null;

  /*
   * La linea de esquina: el encabezado corrido de la contraportada. Su texto
   * sale ENTERO de `content.ts` — la etiqueta de la escena y la identidad —,
   * no se inventa. Se crea aqui y no en `contacto.ts` porque el DOM de esa
   * seccion lo comparten los tres temas: meterlo ahi lo pintaria tambien en
   * Vice y en Hyprland, que estan cerrados.
   */
  const etiqueta = sceneIndex.find((e) => e.id === "contacto")?.label ?? "";
  const corn = document.createElement("p");
  corn.className = "cae-fundido-corn";
  corn.setAttribute("data-fundido-corn", "");
  const cornIzq = document.createElement("span");
  cornIzq.textContent = etiqueta;
  const cornDer = document.createElement("span");
  cornDer.className = "cae-fundido-corn-der";
  cornDer.textContent = `${identity.name} · ${identity.location}`;
  corn.append(cornIzq, cornDer);
  escena.prepend(corn);

  // El troquel: una figura de Material 3 recortando el escritorio sobre el
  // campo de color. El `clip-path` lo pone el CSS; aqui solo va el contenido.
  const troquel = document.createElement("span");
  troquel.className = "cae-fundido-troquel";
  troquel.setAttribute("data-fundido-troquel", "");
  troquel.setAttribute("aria-hidden", "true");

  const nube = document.createElement("span");
  nube.className = "cae-fundido-nube";
  nube.innerHTML = svgNube();

  const suelo = document.createElement("span");
  suelo.className = "cae-fundido-suelo";
  suelo.setAttribute("data-fundido-suelo", "");

  const bicho = document.createElement("span");
  bicho.className = "cae-fundido-bicho";
  bicho.setAttribute("data-fundido-bicho", "");
  bicho.innerHTML = svgDino();

  troquel.append(nube, suelo, bicho);
  banda.append(troquel);

  /*
   * El estado baja bajo el colofon. En el DOM compartido vive dentro de
   * `.contacto-band` —encima de las barras— y la contraportada lo quiere
   * abajo, con el pie de imprenta. Se mueve AQUI y no en `contacto.ts`
   * porque moverlo en el marcado le cambiaria el orden de lectura a Vice y a
   * Hyprland, y Vice esta cerrado.
   */
  const estadoDom = escena.querySelector<HTMLElement>(".contacto-estado");
  if (estadoDom) barras.after(estadoDom);

  const lineas = partirEnLineas(lead);
  const actos = Array.from(escena.querySelectorAll<HTMLElement>('[data-canal="acto"]'));
  const destinos = Array.from(escena.querySelectorAll<HTMLElement>('[data-canal="destino"]'));
  const estado = estadoDom;
  const ojo = bicho.querySelector<SVGRectElement>("[data-dino-ojo]");
  const svgBicho = bicho.querySelector<SVGSVGElement>("svg");

  /** El horizonte se re-dibuja al cambiar de ancho: ver `svgHorizonte`. */
  const pintarSuelo = (): void => {
    suelo.innerHTML = svgHorizonte(window.innerWidth <= ANCHO_SELLO ? TRAMO_MOVIL : undefined);
  };
  pintarSuelo();
  window.addEventListener("resize", pintarSuelo);

  const aterrizado = (): void => {
    gsap.set([lead, ...lineas, ...actos, ...destinos, barras], { clearProps: "all" });
    if (estado) gsap.set(estado, { clearProps: "all" });
    if (svgBicho) gsap.set(svgBicho, { clearProps: "all" });
    if (ojo) ojo.setAttribute("x", String(OJO_DINO[0]));
  };
  aterrizado();

  return {
    destroy: () => window.removeEventListener("resize", pintarSuelo),
    // Las dos se implementan en la Task 6; aqui dejan la escena puesta para
    // que la composicion se pueda revisar sin movimiento.
    reproducir: aterrizado,
    entrar: () => aterrizado(),
  };
}
