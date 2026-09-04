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

  /*
   * `campo` y `troquel` SE INCLUYEN: si una timeline interrumpida (ver
   * `tlFundido` mas abajo) se mata a medio crecer, sus `scale` quedarian
   * congelados donde la mataron sin este reset — aterrizar de verdad
   * significa devolver TODO lo que la partitura toca, no solo el texto.
   */
  const aterrizado = (): void => {
    gsap.set([lead, ...lineas, ...actos, ...destinos, barras], { clearProps: "all" });
    if (estado) gsap.set(estado, { clearProps: "all" });
    if (svgBicho) gsap.set(svgBicho, { clearProps: "all" });
    if (ojo) ojo.setAttribute("x", String(OJO_DINO[0]));
    gsap.set([troquel, campo], { clearProps: "all" });
  };

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /*
   * Cuanto tiene que crecer el campo para tapar la ventana. NO es un numero a
   * ojo: es la distancia del centro de la figura a la esquina mas lejana,
   * dividida entre el radio MINIMO de la figura — los VALLES, no las crestas —
   * con un 4% de margen. Con el radio maximo se queda corto y el escritorio
   * asoma por una esquina.
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

  // `aterrizado()` referencia `campo`, asi que la primera llamada tiene que
  // ir aqui, DESPUES de crearlo — antes seria acceder a una `const` no
  // inicializada todavia.
  aterrizado();

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

  const linea = (): ReturnType<Gsap["timeline"]> => {
    const crece = factorCrecimiento();
    const tl = gsap.timeline();
    tl.fromTo(campo, { scale: 1 }, { scale: crece, duration: 0.48, ease: "power2.inOut" }, 0);
    tl.fromTo(troquel, { scale: 0 }, { scale: 1, duration: 0.52, ease: "power3.out" }, 0.38);
    // Todo lo que aparece se traza de izquierda a derecha: un gesto repetido,
    // no tres maneras distintas de aparecer.
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
  };

  return {
    destroy: () => {
      window.removeEventListener("resize", pintarSuelo);
      gsap.ticker.remove(tic);
      if (tlFundido) tlFundido.kill();
      if (tlEntrada) tlEntrada.kill();
    },
    reproducir: () => {
      if (tlFundido) tlFundido.kill();
      aterrizado();
      if (reduce) return; // No es una version corta: es ninguna version.
      tlFundido = linea();
      tlFundido.play(0);
    },
    entrar,
  };
}
