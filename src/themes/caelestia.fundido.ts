import type { Gsap } from "./choreography";
import { dibujoDino, OJO_DINO, svgDino, svgHorizonte, svgNube, type Fotograma } from "./caelestia.dino";
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
  // Lo usa `entrar`, para saber de que lado vienes.
  indiceEscena: number,
): FundidoHandle | null {
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
  /*
   * Nombre y ubicacion van en nodos separados, no en un solo `textContent`:
   * a 390px el hueco de la derecha (240px medidos) no alcanza para la frase
   * entera a este tracking y el navegador la parte en dos renglones (medido:
   * 27px de alto en un `<span>` de una sola linea de texto). El CSS de 390px
   * oculta `.cae-fundido-corn-loc` con la misma tecnica de recorte que ya usa
   * `.contacto-title` (visible para lectores de pantalla, fuera de la vista),
   * asi que el dato sigue completo en el arbol de accesibilidad y en
   * escritorio se ve exactamente igual que antes: los dos nodos, unidos por
   * el separador, ocupan el mismo `cornDer`.
   */
  const cornNombre = document.createElement("span");
  cornNombre.textContent = identity.name;
  const cornUbicacion = document.createElement("span");
  cornUbicacion.className = "cae-fundido-corn-loc";
  cornUbicacion.textContent = ` · ${identity.location}`;
  cornDer.append(cornNombre, cornUbicacion);
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
   * La figura de reposo del troquel, leida UNA VEZ del CSS (nunca se toca el
   * `clip-path` de la hoja de estilos). `figurasM3.ts` (`poly`) escribe los
   * 240 pares como `polygon(x1% y1%, x2% y2%, ...)`; se parsean a numeros
   * aqui para poder rotarlos alrededor de (50, 50) mientras se arrastra.
   *
   * Si algun dia deja de ser un `polygon()` de 240 pares -- otra figura, otro
   * generador -- esto falla en silencio y el troquel deja de girar en vez de
   * escribir un clip roto: girar una figura a medio parsear es peor que no
   * girarla.
   */
  // defensive: figura ausente o con otro conteo de puntos no debe romper el clip
  const figuraReposo: Array<[number, number]> | null = (() => {
    const m = window.getComputedStyle(troquel).clipPath.match(/^polygon\((.+)\)$/);
    if (!m) return null;
    const pares = [...m[1].matchAll(/(-?[\d.]+)%\s+(-?[\d.]+)%/g)].map(
      (par): [number, number] => [Number(par[1]), Number(par[2])],
    );
    return pares.length === 240 ? pares : null;
  })();

  /*
   * El estado del giro: no se escribe el angulo del arrastre directamente en
   * el clip, se persigue con un muelle. `grados` es el angulo actual (no el
   * objetivo) y `factor` la escala de los lobulos alrededor del centro (50,
   * 50) — 1 en reposo, hasta 1,04 cuando el vistazo va rapido. Los dos viven
   * en el MISMO objeto porque los dos tweens (persecucion y vuelta) tienen
   * que poder pisarse entre si con `overwrite: "auto"`.
   */
  const estadoTroquel = { grados: 0, factor: 1 };
  let anguloAnterior = 0;
  let instanteAnterior = 0;

  /**
   * Escala la figura de reposo por `estadoTroquel.factor` alrededor de su
   * centro y despues la rota `estadoTroquel.grados`, escribiendola como
   * `clip-path` en linea con el mismo formato de dos decimales que
   * `figurasM3.ts`. El dino, el horizonte y la nube NO giran ni escalan:
   * solo se transforma el recorte.
   */
  const pintarTroquel = (): void => {
    if (!figuraReposo) return;
    const rad = (estadoTroquel.grados * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    const factor = estadoTroquel.factor;
    const puntos = figuraReposo.map(([x, y]) => {
      const dx = (x - 50) * factor;
      const dy = (y - 50) * factor;
      const rx = (dx * cos - dy * sin + 50).toFixed(2);
      const ry = (dx * sin + dy * cos + 50).toFixed(2);
      return `${rx}% ${ry}%`;
    });
    troquel.style.clipPath = `polygon(${puntos.join(", ")})`;
  };

  /*
   * Los lobulos respiran con la velocidad angular del PROPIO muelle: se mide
   * cuanto avanza `estadoTroquel.grados` entre dos fotogramas, se persigue
   * un factor objetivo acotado a 1,04 y se suaviza hacia el (nunca se salta
   * de golpe, que se notaria como un parpadeo de tamano).
   *
   * Vive en el ticker de gsap (`gsap.ticker.add`), NO en el `onUpdate` del
   * tween de persecucion: un `onUpdate` solo se dispara mientras ESE tween
   * sigue vivo, y con el puntero quieto la persecucion termina a los 0,55s
   * de su ULTIMA llamada -- ahi se apaga el `onUpdate` y el factor se queda
   * congelado en lo que le diera tiempo a suavizar durante esa ventana, para
   * siempre, aunque el objetivo (factor 1, velocidad 0) siga sin alcanzar.
   * El ticker de gsap no tiene ese limite: sigue corriendo mientras
   * `arrastrando` sea `true`, ya sea porque el puntero se sigue moviendo o
   * porque se quedo quieto a mitad del muelle -- que es justo cuando mas
   * falta hace terminar de asentar la respiracion.
   */
  const respirarTroquel = (): void => {
    if (!figuraReposo || !arrastrando) return;
    const ahora = performance.now();
    const dt = (ahora - instanteAnterior) / 1000;
    if (dt > 0) {
      const velocidad = (estadoTroquel.grados - anguloAnterior) / dt;
      const objetivo = 1 + Math.min(0.04, Math.abs(velocidad) / 900);
      estadoTroquel.factor += (objetivo - estadoTroquel.factor) * 0.2;
    }
    anguloAnterior = estadoTroquel.grados;
    instanteAnterior = ahora;
    pintarTroquel();
  };
  gsap.ticker.add(respirarTroquel);

  /**
   * Lanza el muelle hacia `objetivo` grados. Se llama como mucho una vez por
   * fotograma (la programa `programarArrastre`) y cada llamada relanza el
   * tween con `overwrite: "auto"`: la persecucion nunca escribe el angulo de
   * golpe, sigue corriendo fotogramas despues de que el puntero se pare. El
   * pintado en si va por `respirarTroquel()`, que corre en el mismo ticker.
   */
  const girarTroquel = (objetivo: number): void => {
    if (!figuraReposo) return;
    gsap.to(estadoTroquel, {
      grados: objetivo,
      duration: 0.55,
      ease: "power3.out",
      overwrite: "auto",
    });
  };

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

  /*
   * TODO lo que las partituras tocan, anotado desde LAS PARTITURAS MISMAS en
   * cuanto se construyen.
   *
   * `aterrizado()` mantenia la lista a mano y se desincronizo: le faltaban el
   * bicho, la nube y el suelo, asi que interrumpir el fundido a media pasada
   * los dejaba congelados donde el `kill()` los pillo —el bicho a
   * `translateX(-105px)`, medio fuera del sello; la nube en `opacity: 0`; el
   * horizonte a 0,91 de su trazo— y ahi se quedaban EL RESTO DE LA VISITA,
   * porque `fundidoVisto` ya es `true` y el fundido no vuelve a sonar. Una
   * lista en dos sitios se rompe en cuanto alguien anade un tween; anotarla al
   * construir la partitura no puede romperse.
   *
   * Se anota al CONSTRUIR y no al aterrizar a proposito: `aterrizado()` corre
   * despues del `kill()`, y que una timeline muerta conserve sus hijos es
   * detalle interno de gsap, no contrato. El conjunto solo crece, asi que
   * limpiar de mas es inofensivo y no depender de eso es gratis.
   */
  const tocados = new Set<Element>();
  const anotar = <T extends ReturnType<Gsap["timeline"]>>(tl: T): T => {
    // `(anidadas, tweens, timelines)`: los tweens, tambien los de timelines
    // hijas por si la partitura llega a anidar alguna.
    for (const hijo of tl.getChildren(true, true, false)) {
      // Una `Timeline` no tiene `targets()`; un `Tween` si. Se comprueba en vez
      // de castear a ciegas: `strict` esta puesto y `any` esta prohibido.
      const leer = (hijo as { targets?: () => unknown[] }).targets;
      if (typeof leer !== "function") continue;
      for (const d of leer.call(hijo)) if (d instanceof Element) tocados.add(d);
    }
    return tl;
  };

  /*
   * Aterrizar de verdad: devolver todo lo que las partituras tocan, parar la
   * zancada y retirar lo que gsap no puso y por tanto `clearProps` no alcanza.
   */
  const aterrizado = (): void => {
    if (tocados.size > 0) gsap.set([...tocados], { clearProps: "all" });
    /*
     * `pararZancada()` NO se dispara solo: es el `onComplete` del tween del
     * bicho y `kill()` no llama a `onComplete`. Sin esta linea el reloj de
     * fotogramas se queda encendido y el dino corre en el sitio para siempre.
     * Va DESPUES del `clearProps` porque repone el fotograma de pie.
     */
    pararZancada();
    /*
     * Los ejes variables del titular los escribe el `onUpdate` de la partitura
     * directamente en `style`, no gsap sobre el elemento: `clearProps` no los
     * ve. Interrumpido a media pasada, el titular se quedaba con un `wght`
     * intermedio en linea, ganandole al token.
     */
    lead.style.fontVariationSettings = "";
    if (ojo) {
      ojo.setAttribute("x", String(OJO_DINO[0]));
      ojo.setAttribute("y", String(OJO_DINO[1]));
    }
    /*
     * Los tres gestos del juguete, aterrizados tambien: si la escena se
     * abandona a media pasada de cualquiera de ellos, no deben quedarse
     * congelados (el salto en el aire, el reloj forzado por el arrastre).
     */
    if (tlSalto) tlSalto.kill();
    saltando = false;
    if (arrastrando) {
      arrastrando = false;
      const gancho = ganchoMinutos();
      if (gancho) gancho(null);
    }
    /*
     * El muelle del troquel (persecucion o vuelta) tambien se mata aqui,
     * SIEMPRE, no solo `if (arrastrando)`: la vuelta elastica sigue corriendo
     * 1,1s despues de soltar, con `arrastrando` ya en `false` -- justo el
     * hueco que dejaba congelado el sello a medio muelle si la escena se
     * abandonaba en ese tramo. `kill()` no dispara `onComplete`, asi que el
     * inline y el estado se reponen a mano, igual que hace `soltarArrastre()`
     * en el camino normal.
     */
    gsap.killTweensOf(estadoTroquel);
    troquel.style.clipPath = "";
    estadoTroquel.grados = 0;
    estadoTroquel.factor = 1;
    bajando = false;
  };

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /*
   * Cuanto tiene que crecer el campo para tapar la ventana. NO es un numero a
   * ojo: es la distancia del centro de la figura a la esquina mas lejana,
   * dividida entre el radio MINIMO de la figura — los VALLES, no las crestas —
   * con un 4% de margen. Con el radio maximo se queda corto y el escritorio
   * asoma por una esquina.
   *
   * Lee el `clip-path` COMPUTADO, que durante un arrastre es el inline que
   * escribe `girarTroquel()`. No desvia nada: al soltar ya queda vacio
   * (`soltarArrastre()`/`aterrizado()`), y el fundido (`linea()`, la unica
   * que llama a esto) nunca corre a mitad de un arrastre -- para llegar a
   * "contacto" hay que cambiar de workspace, y eso ya suelta el puntero.
   */
  const factorCrecimiento = (): number => {
    const v = escena.getBoundingClientRect();
    const c = troquel.getBoundingClientRect();
    const cx = c.left + c.width / 2 - v.left;
    const cy = c.top + c.height / 2 - v.top;
    const lejos = Math.max(
      Math.hypot(cx, cy),
      Math.hypot(v.width - cx, cy),
      Math.hypot(cx, v.height - cy),
      Math.hypot(v.width - cx, v.height - cy),
    );
    const clip = window.getComputedStyle(troquel).clipPath;
    const puntos = [...clip.matchAll(/([\d.]+)%\s+([\d.]+)%/g)];
    if (puntos.length === 0) return 1;
    const radios = puntos.map((m) => Math.hypot(Number(m[1]) - 50, Number(m[2]) - 50));
    const rMin = (Math.min(...radios) / 50) * (c.width / 2);
    return rMin > 0 ? (lejos / rMin) * 1.04 : 1;
  };

  // El campo de color: la MISMA figura que el troquel, en la misma posicion,
  // pintada en `--cae-primary`. Un solo mecanismo en dos direcciones — es un
  // iris de cine, no dos efectos sueltos.
  const campo = document.createElement("span");
  campo.className = "cae-fundido-campo";
  campo.setAttribute("aria-hidden", "true");
  banda.append(campo);

  /*
   * La zancada la lleva un reloj propio y no la linea de tiempo: son doce
   * cambios de fotograma y meterlos como tweens ensuciaria la partitura sin
   * aportar nada. Se enciende y se apaga desde el tween del desplazamiento,
   * asi que sigue atado a el.
   */
  const ZANCADA = 0.085;
  let corriendo = false;
  let paso = 0;
  let ultimo = 0;

  const ponFotograma = (cual: Fotograma): void => {
    const cuerpo = bicho.querySelector<SVGGElement>("[data-dino-cuerpo]");
    if (cuerpo) cuerpo.innerHTML = dibujoDino(cual);
    // El ojo movible SOLO existe de pie: en los de zancada el ojo es el hueco
    // del propio sprite, y con el rect encima se veria doble.
    if (ojo) ojo.style.opacity = cual === "quieto" ? "1" : "0";
  };

  const tic = (): void => {
    if (!corriendo) return;
    const ahora = performance.now() / 1000;
    if (ahora - ultimo < ZANCADA) return;
    ultimo = ahora;
    paso ^= 1;
    ponFotograma(paso ? "carrera1" : "carrera2");
  };
  gsap.ticker.add(tic);

  const arrancarZancada = (): void => {
    paso = 0;
    ultimo = 0;
    corriendo = true;
  };
  const pararZancada = (): void => {
    corriendo = false;
    ponFotograma("quieto");
  };

  /*
   * EL DINO ES UN JUGUETE. Tres gestos, ninguno entra en el orden de
   * tabulacion (no `tabindex`, no `role`): los cuatro canales siguen siendo
   * las unicas paradas. Pero si es pulsable -- `cursor: pointer` y
   * `pointer-events: auto` los pone el CSS.
   */

  // --- 1. Salta al pulsar -------------------------------------------------
  let saltando = false;
  let tlSalto: ReturnType<Gsap["timeline"]> | null = null;

  const salto = (): void => {
    if (reduce || saltando) return;
    saltando = true;
    const tl = gsap.timeline({ onComplete: () => { saltando = false; } });
    tl.fromTo(bicho, { y: 0 }, { y: -70, duration: 0.26, ease: "power2.out" }, 0);
    tl.to(bicho, { y: 0, duration: 0.26, ease: "power2.in" }, 0.26);
    if (svgBicho) {
      tl.fromTo(
        svgBicho,
        { scaleY: 1 },
        { scaleY: 0.9, duration: 0.08, transformOrigin: "50% 100%" },
        0.52,
      );
      tl.to(svgBicho, { scaleY: 1, duration: 0.12, ease: "power2.out", transformOrigin: "50% 100%" }, 0.6);
    }
    tlSalto = anotar(tl);
  };

  // --- 2. Los ojos siguen al cursor ---------------------------------------
  // Distancia maxima a la que el bicho se fija en el cursor.
  const DISTANCIA_MIRADA = 260;
  // El cursor mueve el ojo, como mucho, 1 unidad del lienzo de 40x43 en cada
  // eje -- pixel art, sin fraccion. 130 es el radio a partir del cual ya se
  // satura al maximo (dx/130 >= 1).
  const RADIO_MIRADA = 130;

  const alMoverPuntero = (e: PointerEvent): void => {
    if (!ojo) return;
    // No pisa la mirada de `entrar()`, que fija `x` durante su propio tramo.
    if (tlEntrada && tlEntrada.isActive()) return;
    // El ojo movible solo existe de pie: en zancada es el hueco del sprite.
    if (corriendo) return;
    const r = bicho.getBoundingClientRect();
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;
    const dx = e.clientX - cx;
    const dy = e.clientY - cy;
    if (Math.hypot(dx, dy) < DISTANCIA_MIRADA) {
      const dox = Math.round(Math.max(-1, Math.min(1, dx / RADIO_MIRADA)));
      const doy = Math.round(Math.max(-1, Math.min(1, dy / RADIO_MIRADA)));
      ojo.setAttribute("x", String(OJO_DINO[0] + dox));
      ojo.setAttribute("y", String(OJO_DINO[1] + doy));
    } else {
      ojo.setAttribute("x", String(OJO_DINO[0]));
      ojo.setAttribute("y", String(OJO_DINO[1]));
    }
  };
  if (!reduce) escena.addEventListener("pointermove", alMoverPuntero);

  // --- 3. El arrastre es un vistazo ---------------------------------------
  // Los 30px por hora y el `<< 4px es un clic` son los umbrales del diseno.
  const PX_POR_HORA = 30;
  const UMBRAL_ARRASTRE = 4;

  interface VentanaConGancho {
    __CAE_SET_MINUTOS__?: (minutos: number | null) => void;
  }
  const ganchoMinutos = (): ((minutos: number | null) => void) | undefined =>
    (window as unknown as VentanaConGancho).__CAE_SET_MINUTOS__;

  let bajando = false;
  let arrastrando = false;
  let inicioX = 0;
  let inicioY = 0;
  let minutosInicio = 0;
  // El gancho se llama como mucho una vez por fotograma: sin este cerrojo,
  // cada `pointermove` (varios por fotograma en un raton de verdad) llamaria
  // a `aplicar()` -- que reescribe TODOS los tokens de color -- de mas. El
  // giro del troquel viaja en el MISMO rAF: son 240 puntos por fotograma,
  // solo mientras se arrastra, y no hace falta un segundo reloj para eso.
  let rafPendiente = false;
  let minutosPendientes: number | null = null;
  let gradosPendientes: number | null = null;

  const programarArrastre = (minutos: number, grados: number): void => {
    minutosPendientes = minutos;
    gradosPendientes = grados;
    if (rafPendiente) return;
    rafPendiente = true;
    requestAnimationFrame(() => {
      rafPendiente = false;
      const gancho = ganchoMinutos();
      if (gancho && minutosPendientes !== null) gancho(minutosPendientes);
      // Con movimiento reducido el reloj se sigue moviendo (ya lo hacia antes
      // de este gesto) pero el troquel se queda quieto.
      if (!reduce && gradosPendientes !== null) girarTroquel(gradosPendientes);
    });
  };

  const soltarArrastre = (): void => {
    if (!arrastrando) return;
    arrastrando = false;
    const gancho = ganchoMinutos();
    // El color SI corta de golpe al soltar: solo la forma asienta con
    // muelle. Es el mismo reparto que ya tenia el gesto, no uno nuevo.
    if (gancho) gancho(null);
    pararZancada();
    if (reduce || !figuraReposo) {
      // Sin muelle que animar, la vuelta es la de siempre: directa.
      troquel.style.clipPath = "";
      estadoTroquel.grados = 0;
      estadoTroquel.factor = 1;
      return;
    }
    // De la figura girada a la de reposo con un rebote, no de golpe: el
    // `onComplete` es quien limpia el inline, para no dejar un fotograma
    // intermedio del muelle leyendo ya la regla del CSS (angulo 0 seco).
    gsap.to(estadoTroquel, {
      grados: 0,
      factor: 1,
      duration: 1.1,
      ease: "elastic.out(1, 0.55)",
      overwrite: "auto",
      onUpdate: pintarTroquel,
      onComplete: () => {
        troquel.style.clipPath = "";
      },
    });
  };

  const alBajarPuntero = (e: PointerEvent): void => {
    bicho.setPointerCapture(e.pointerId);
    bajando = true;
    arrastrando = false;
    inicioX = e.clientX;
    inicioY = e.clientY;
    const ahora = new Date();
    minutosInicio = ahora.getHours() * 60 + ahora.getMinutes();
  };

  const alMoverArrastre = (e: PointerEvent): void => {
    if (!bajando) return;
    const dx = e.clientX - inicioX;
    const dy = e.clientY - inicioY;
    if (!arrastrando) {
      if (Math.hypot(dx, dy) <= UMBRAL_ARRASTRE) return;
      arrastrando = true;
      // Arranca la respiracion desde el angulo actual (0 salvo que un
      // vistazo anterior no llegara a asentar del todo): sin este reinicio,
      // el primer fotograma de `respirarTroquel()` mediria una velocidad
      // inventada contra el estado de la ULTIMA vez que se arrastro.
      anguloAnterior = estadoTroquel.grados;
      instanteAnterior = performance.now();
      if (!reduce && !corriendo) arrancarZancada();
    }
    const horas = Math.round(dx / PX_POR_HORA);
    const minutos = (((minutosInicio + horas * 60) % 1440) + 1440) % 1440;
    // 15 grados por hora de vistazo (360 en 24h), mismo sentido que la hora.
    programarArrastre(minutos, horas * 15);
  };

  const alSoltarPuntero = (e: PointerEvent): void => {
    if (bicho.hasPointerCapture(e.pointerId)) bicho.releasePointerCapture(e.pointerId);
    if (!bajando) return;
    bajando = false;
    if (arrastrando) {
      soltarArrastre();
    } else {
      // Un pointerdown/up sin mas de 4px de recorrido es un clic: salta.
      salto();
    }
  };

  const alCancelarPuntero = (e: PointerEvent): void => {
    if (bicho.hasPointerCapture(e.pointerId)) bicho.releasePointerCapture(e.pointerId);
    if (!bajando) return;
    bajando = false;
    soltarArrastre();
  };

  bicho.addEventListener("pointerdown", alBajarPuntero);
  bicho.addEventListener("pointermove", alMoverArrastre);
  bicho.addEventListener("pointerup", alSoltarPuntero);
  bicho.addEventListener("pointercancel", alCancelarPuntero);

  const linea = (): ReturnType<Gsap["timeline"]> => {
    const crece = factorCrecimiento();
    const tl = gsap.timeline();
    tl.fromTo(campo, { scale: 1 }, { scale: crece, duration: 0.48, ease: "power2.inOut" }, 0);
    tl.fromTo(troquel, { scale: 0 }, { scale: 1, duration: 0.52, ease: "power3.out" }, 0.38);
    // Todo lo que aparece se traza de izquierda a derecha: un gesto repetido,
    // no tres maneras distintas de aparecer.
    //
    // El encabezado corrido va PRIMERO, antes que la frase: es el filete de
    // arriba, y el spec promete «filetes» en plural. El de abajo entra con
    // `barras`, que lo lleva en su propia caja; este no colgaba de nada y se
    // pintaba de golpe mientras el resto se trazaba.
    tl.fromTo(
      corn,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.5, ease: "power2.inOut" },
      0.44,
    );
    tl.fromTo(
      lineas,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.62, ease: "power2.inOut", stagger: 0.12 },
      0.52,
    );
    // La frase se ABLANDA al llegar: entra con la voz de cabecera y aterriza en
    // la de cierre. `opsz` no se toca: se lee a 159,66 px de principio a fin.
    const ejes = { wght: 900, soft: 0 };
    tl.fromTo(
      ejes,
      { wght: 900, soft: 0 },
      {
        wght: 300,
        soft: 100,
        duration: 0.78,
        ease: "power2.out",
        onUpdate: () => {
          lead.style.fontVariationSettings =
            `"opsz" 144, "wght" ${Math.round(ejes.wght)}, "SOFT" ${Math.round(ejes.soft)}, "WONK" 1`;
        },
        onComplete: () => {
          // Se QUITA el valor en linea en vez de repetir el numero: un numero
          // repetido es un numero que se desincroniza del token.
          lead.style.fontVariationSettings = "";
        },
      },
      0.52,
    );
    tl.fromTo(suelo, { scaleX: 0 }, { scaleX: 1, duration: 0.34, ease: "power2.inOut" }, 0.74);
    if (svgBicho) {
      // Entra CORRIENDO: el idioma del propio bicho. La zancada es finita, solo
      // mientras entra, asi que no infringe la prohibicion de animacion
      // infinita en la escena de cierre.
      tl.fromTo(
        bicho,
        { x: -280 },
        {
          x: 0,
          duration: 0.66,
          ease: "power2.out",
          onStart: () => arrancarZancada(),
          onComplete: () => pararZancada(),
        },
        0.8,
      );
      tl.to(svgBicho, { scaleY: 0.9, scaleX: 1.07, duration: 0.07, transformOrigin: "50% 100%" }, 1.46);
      tl.to(svgBicho, { scaleY: 1, scaleX: 1, duration: 0.16, ease: "power2.out" }, 1.53);
    }
    tl.fromTo(nube, { opacity: 0, x: 26 }, { opacity: 1, x: 0, duration: 0.28, ease: "power2.out" }, 1.55);
    tl.fromTo(
      barras,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.42, ease: "power2.inOut" },
      0.82,
    );
    // La escalonada DICE algo: los actos antes que los destinos, que es la
    // jerarquia de la escena. Si se cambia esa jerarquia, esto se cae con ella.
    tl.fromTo(
      actos,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.46, ease: "power2.inOut", stagger: 0.1 },
      0.9,
    );
    tl.fromTo(
      destinos,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.42, ease: "power2.inOut", stagger: 0.09 },
      1.16,
    );
    if (estado) {
      tl.fromTo(
        estado,
        { clipPath: "inset(-12% 100% -12% -2%)" },
        { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.34, ease: "power2.inOut" },
        1.3,
      );
    }
    return tl;
  };

  /*
   * LA ENTRADA. El carril de la fase A ya desliza 520 ms; esto son 440 y cabe
   * dentro, asi que no anade espera: la rellena. No es un fundido acortado —
   * un final que suena cada vez no es un final.
   *
   * `ENTRADA_MS` NO ES UN COMENTARIO CON NUMERO: los cinco tiempos de abajo
   * son fracciones de `ENTRADA` (la version en segundos), sacadas de la
   * partitura original (0/0.12/0.22/0.3/0.36/0.41 sobre un total de 0.44).
   * Si alguien cambia `ENTRADA_MS` sin tocar nada mas, la entrada entera se
   * reescala con el — la promesa del comentario se rompe sola si deja de
   * caber en el carril, en vez de quedarse fingiendo mientras el numero real
   * vive suelto en las llamadas de abajo.
   */
  const ENTRADA_MS = 440;
  const ENTRADA = ENTRADA_MS / 1000;
  let tlEntrada: ReturnType<Gsap["timeline"]> | null = null;

  /*
   * `tlFundido` guarda la timeline de `reproducir()` con el MISMO patron que
   * `tlEntrada` de arriba: si el visitante se va de «contacto» antes de que
   * acaben los 1,9 s (la primera visita, con el carril libre, esto pasa) la
   * timeline seguia corriendo sobre una escena inerte hasta agotarse sola —
   * viola literalmente "kill timelines on teardown". Se declara AQUI, antes
   * de `entrar`, porque `entrar` tambien la mata: `fundidoVisto` (en
   * `caelestia.choreography.ts`) se pone a `true` en cuanto arranca
   * `reproducir()`, no cuando termina, asi que un regreso a esta escena
   * ANTES de que la primera pasada acabe llama a `entrar()`, no otra vez a
   * `reproducir()` — matarla solo "si `reproducir()` se repite" nunca
   * llegaria a ejecutarse en ese camino real.
   */
  let tlFundido: ReturnType<Gsap["timeline"]> | null = null;

  /*
   * La primera llamada va AQUI, no donde nace el troquel: `aterrizado()` lee
   * `tlFundido`, `tlEntrada` y `pararZancada`, y los tres se declaran arriba
   * de esta linea. Llamarla antes seria tocarlos en su zona muerta.
   */
  aterrizado();

  const entrar = (desde: number): void => {
    if (tlEntrada) tlEntrada.kill();
    if (tlFundido) tlFundido.kill();
    aterrizado();
    if (reduce) return;
    // Vienes de un workspace menor => el contenido se queda atras hacia la
    // derecha y alcanza; y el bicho mira hacia donde estabas.
    const sentido = desde < indiceEscena ? 1 : -1;
    tlEntrada = gsap.timeline();
    tlEntrada.fromTo(
      escena,
      { x: 28 * sentido },
      { x: 0, duration: ENTRADA * (0.38 / 0.44), ease: "power2.out" },
      0,
    );
    tlEntrada.fromTo(
      troquel,
      { scale: 0.965 },
      { scale: 1, duration: ENTRADA * (0.26 / 0.44), ease: "power2.out" },
      ENTRADA * (0.12 / 0.44),
    );
    if (ojo) {
      tlEntrada.call(
        () => ojo.setAttribute("x", String(OJO_DINO[0] - sentido)),
        undefined,
        ENTRADA * (0.22 / 0.44),
      );
      tlEntrada.call(
        () => ojo.setAttribute("x", String(OJO_DINO[0])),
        undefined,
        ENTRADA * (0.36 / 0.44),
      );
      // El parpadeo: el ojo es un hueco TAPADO, asi que apagar el rect no lo
      // borra — lo cierra, porque debajo queda el cuerpo.
      tlEntrada.to(ojo, { opacity: 0, duration: 0.001 }, ENTRADA * (0.3 / 0.44));
      tlEntrada.to(ojo, { opacity: 1, duration: 0.001 }, ENTRADA * (0.41 / 0.44));
    }
    // Al final: `tlEntrada` se arma por partes y solo aqui esta completa.
    anotar(tlEntrada);
  };

  return {
    destroy: () => {
      window.removeEventListener("resize", pintarSuelo);
      escena.removeEventListener("pointermove", alMoverPuntero);
      bicho.removeEventListener("pointerdown", alBajarPuntero);
      bicho.removeEventListener("pointermove", alMoverArrastre);
      bicho.removeEventListener("pointerup", alSoltarPuntero);
      bicho.removeEventListener("pointercancel", alCancelarPuntero);
      gsap.ticker.remove(tic);
      gsap.ticker.remove(respirarTroquel);
      if (tlFundido) tlFundido.kill();
      if (tlEntrada) tlEntrada.kill();
      if (tlSalto) tlSalto.kill();
      if (arrastrando) {
        const gancho = ganchoMinutos();
        if (gancho) gancho(null);
      }
      // Mismo motivo que en `aterrizado()`: el muelle de vuelta puede seguir
      // corriendo con `arrastrando` ya en `false`.
      gsap.killTweensOf(estadoTroquel);
      troquel.style.clipPath = "";
      estadoTroquel.grados = 0;
      estadoTroquel.factor = 1;
    },
    reproducir: () => {
      if (tlFundido) tlFundido.kill();
      aterrizado();
      if (reduce) return; // No es una version corta: es ninguna version.
      tlFundido = anotar(linea());
      tlFundido.play(0);
    },
    entrar,
  };
}
