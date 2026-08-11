import type { Gsap } from "../themes/choreography";

export interface ObraCartelHandle {
  destroy: () => void;
}

/** Ancla de donde vivia un bloque de la ficha antes de viajar, para poder
 * devolverlo exactamente ahi cuando la ficha cierra. Sin esto, la segunda
 * apertura de una fila que ya se abrio una vez encuentra su `.lead`/`.obra-meta`
 * huerfanos (los dejo colgando el `replaceChildren` de la fila que abrio
 * despues) y `bloquesDeFicha` no los recupera. */
interface Ancla {
  nodo: HTMLElement;
  padre: Node;
  siguiente: Node | null;
}

interface Fila {
  seccion: HTMLElement;
  boton: HTMLButtonElement;
  /** una tira por letra: arriba la apagada, debajo la encendida */
  tiras: HTMLElement[];
  /** capa de entrada, independiente de la del relevo */
  entradas: HTMLElement[];
  mini: HTMLElement;
  /** banda de capturas restantes (Task 8) — vacia si el proyecto solo tiene una */
  otras: HTMLElement;
  /** contenido original de la miniatura, para devolverla a la primera
   * captura al cerrar. Sin esto, reabrir una fila donde se pulso un tile
   * dejaria la lupa con la ultima foto vista, no con `gallery[0]`. */
  miniOriginal: { src: string; alt: string; pie: string };
  /** Intercambio de captura EN VUELO, si lo hay. Su `.call()` muta `src` a
   * mitad de la linea de tiempo: si `pagehide` (o un cierre) llega entre el
   * recorte de ida y esa llamada, el DOM se queda mutado DESPUES de que
   * `restauraMini()` ya lo haya devuelto a su sitio. Ventana estrecha, mismo
   * sintoma que ya se corrigio una vez. Se guarda para poder matarla. */
  intercambio: ReturnType<Gsap["timeline"]> | null;
}

const PASO_RELEVO = 0.024;
const BARRIDO = 1.05;

/**
 * El cartel: cinco titulares, la captura a la altura de su titular.
 *
 * Va aqui y no en `hypr.choreography.ts` porque el contrato `Choreography`
 * devuelve `void` y este dispositivo tiene estado y listeners que hay que
 * poder soltar. Mismo patron que `hyprIgnition.ts`.
 *
 * Cada letra lleva DOS transforms independientes: `.obra-en` para la entrada y
 * `.obra-rl` para el relevo. Sin esa separacion, la entrada y el hover se
 * pisan — se comprobo en el prototipo.
 */
export async function mountObraCartel(root: HTMLElement): Promise<ObraCartelHandle> {
  const { default: gsap } = await import("gsap");
  const { CustomEase } = await import("gsap/CustomEase");
  const { Flip } = await import("gsap/Flip");
  const { SplitText } = await import("gsap/SplitText");
  gsap.registerPlugin(CustomEase, Flip, SplitText);
  CustomEase.create("hard", "0.7,0,0.2,1");
  CustomEase.create("slow", "0.16,0.84,0.28,1");

  const secciones = Array.from(root.querySelectorAll<HTMLElement>('[data-scene="obra"]'));
  const filas: Fila[] = secciones.map((seccion) => partirTitulo(seccion));
  const finoPuntero = window.matchMedia("(hover: hover)").matches;
  const motionReducido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Tipado como no-nulo desde el arranque, no solo comprobado: `pista` se lee
  // dentro de `abre()`, una funcion anidada, y TypeScript no propaga el
  // estrechamiento de un `if (!x) throw` a traves de closures anidadas.
  const pista: HTMLElement = (() => {
    const nodo = root.querySelector<HTMLElement>("[data-obra-track]");
    if (!nodo) throw new Error("El cartel necesita [data-obra-track]");
    return nodo;
  })();

  // El estado abierto es UN panel, no tres hijos absolutos sueltos. Los tres
  // llevaban `top` en px contra un marco de 1400x820 que solo existia en el
  // prototipo (la pista real mide 482-548 y no recorta), y de ahi salieron la
  // ficha de alto 0 entre 821 y 1199px, la lupa 59px fuera del carril y la
  // banda de capturas pintando sobre la seccion siguiente. Con el panel en
  // rejilla, el alto lo dicta el contenido y no hay ningun numero que sumar a
  // mano en cada breakpoint.
  const panel = document.createElement("div");
  panel.className = "obra-panel";
  panel.setAttribute("data-obra-panel", "");
  const visor = document.createElement("div");
  visor.className = "obra-visor";
  visor.setAttribute("data-obra-visor", "");
  const lupa = document.createElement("div");
  lupa.className = "obra-lupa";
  lupa.setAttribute("data-obra-lupa", "");
  const ficha = document.createElement("div");
  ficha.className = "obra-ficha";
  ficha.setAttribute("data-obra-ficha", "");
  // La ficha entra y sale por RECORTE, nunca por opacidad: la ley de la
  // seccion es que aqui nada se desvanece. El `clip-path` de reposo vive en
  // el CSS (`.obra-ficha`); aqui solo se fija el estado de puntero.
  gsap.set(ficha, { pointerEvents: "none" });
  const anuncio = document.createElement("p");
  anuncio.className = "sr-only";
  anuncio.setAttribute("data-obra-anuncio", "");
  anuncio.setAttribute("aria-live", "polite");
  visor.appendChild(lupa);
  panel.append(visor, ficha);
  pista.append(panel, anuncio);

  let abierta = -1;
  let anclas: Ancla[] = [];
  let particion: InstanceType<typeof SplitText> | null = null;
  // Se incrementa en cada cierre: el `onComplete` de un cierre anterior lo
  // comprueba antes de tocar `anclas`, para no llevarse por delante el
  // contenido que una apertura posterior ya coloco en la ficha.
  let cierreEnCurso = 0;

  /** Los bloques salen de los nodos que ya existen: content.ts no se toca.
   *
   * El pie del proyecto (enlace al repositorio o nota de "Proyecto privado",
   * `data-obra-pie` en `projectScene.ts`) sustituye a `mascaras[0]`
   * ("Problema"): decision de Aoshi (2026-08-10) para que el enlace al
   * repositorio entre en la ficha sin sumar un sexto bloque. Va ANTES del
   * `meta` de Rol y Periodo, segun el spec. */
  function bloquesDeFicha(seccion: HTMLElement): HTMLElement[] {
    const piezas: HTMLElement[] = [];
    const lead = seccion.querySelector<HTMLElement>(".lead");
    const mascaras = Array.from(seccion.querySelectorAll<HTMLElement>("[data-mask]"));
    const meta = seccion.querySelector<HTMLElement>(".obra-meta");
    const marcas = seccion.querySelector<HTMLElement>("[data-obra-marcas]");
    const pie = seccion.querySelector<HTMLElement>("[data-obra-pie]");
    for (const pieza of [lead, mascaras[1], marcas, pie, meta]) {
      if (pieza) piezas.push(pieza);
    }
    return piezas;
  }

  /** Devuelve cada bloque de la ficha a donde vivia antes de viajar. Se llama
   * SIEMPRE antes de volver a poblar `ficha`, tanto al cerrar como al abrir
   * otra fila (que cierra la anterior primero).
   *
   * `siguiente` puede ser OTRO bloque de la misma ficha (p.ej. `.lead` guarda
   * como hermano siguiente a `.obra-meta`, que tambien viaja): si ese hermano
   * todavia no ha vuelto a su sitio, `insertBefore` lo rechaza porque no es
   * hijo de `padre` en ese instante y lanza, abortando el resto del bucle —
   * el bloque siguiente se queda huerfano fuera de su fila. Medido: reabrir
   * una fila tras visitar otra la deja sin ficha. Como estos bloques son
   * `display: none` en reposo, el orden entre ellos no importa: si el hueco
   * original ya no es valido, se aniade al final.
   */
  function devuelveBloques(): void {
    for (const { nodo, padre, siguiente } of anclas) {
      const hueco = siguiente && siguiente.parentNode === padre ? siguiente : null;
      padre.insertBefore(nodo, hueco);
    }
    anclas = [];
  }

  /** Corta en seco cualquier SplitText de la ficha a medio animar: sin esto,
   * cerrar antes de que `onComplete` revierta deja un tween vivo sobre nodos
   * que la siguiente apertura va a desconectar del DOM con `replaceChildren`. */
  function cortaParticion(): void {
    if (!particion) return;
    gsap.killTweensOf(particion.lines);
    particion.revert();
    particion = null;
  }

  const sueltas: Array<() => void> = [];

  // Sin hover (movil) el relevo no tiene disparador propio: lo hace la
  // apertura (`abre()` llama a `relevo(..., true, ...)` siempre, unas lineas
  // mas abajo). La separacion va por capacidad del puntero, no por ancho de
  // pantalla: un portatil tactil de 1440 tiene las dos cosas.
  for (const fila of filas) {
    if (finoPuntero) {
      const entra = (): void => relevo(gsap, fila, true, motionReducido);
      const sale = (): void => relevo(gsap, fila, false, motionReducido);
      fila.seccion.addEventListener("pointerenter", entra);
      fila.seccion.addEventListener("pointerleave", sale);
      sueltas.push(() => {
        fila.seccion.removeEventListener("pointerenter", entra);
        fila.seccion.removeEventListener("pointerleave", sale);
      });
    }
  }

  // Enganche de los tiles de capturas restantes (Task 8): se hace UNA vez al
  // montar, no en cada `abre()` -- los tiles son estaticos por fila.
  for (const fila of filas) {
    sueltas.push(engancharOtras(gsap, fila, motionReducido));
  }

  function abre(indice: number): void {
    if (abierta === indice) {
      cierra();
      return;
    }
    if (abierta >= 0) cierra();
    // Invalida cualquier cierre todavia en vuelo y devuelve sus bloques ya:
    // si la fila anterior cerro pero su recorte de salida no habia
    // terminado, sus piezas seguian dentro de `ficha` sin restaurar (el
    // `onComplete` que las iba a devolver aun no ha corrido). Sin este
    // flush, el `replaceChildren` de mas abajo las desconecta del DOM sin
    // que nadie las recupere: quedarian huerfanas para siempre.
    cierreEnCurso += 1;
    devuelveBloques();
    abierta = indice;
    const fila = filas[indice];
    fila.seccion.classList.add("is-abierto");
    fila.boton.setAttribute("aria-expanded", "true");
    relevo(gsap, fila, true, motionReducido);

    // La miniatura y la grande son EL MISMO nodo: Flip mide donde esta, se
    // reubica, y se anima el recorrido real entre las dos posiciones.
    const estado = Flip.getState(fila.mini);
    lupa.appendChild(fila.mini);
    Flip.from(estado, { duration: motionReducido ? 0 : 0.62, ease: "hard", absolute: true });

    const piezas = bloquesDeFicha(fila.seccion);
    anclas = piezas.map((nodo) => ({ nodo, padre: nodo.parentNode as Node, siguiente: nodo.nextSibling }));
    ficha.replaceChildren(...piezas);
    gsap.set(ficha, { pointerEvents: "auto" });
    // La banda de capturas restantes (Task 8) NO viaja a la ficha: viaja a
    // `.obra-visor`, la columna de la imagen, y queda debajo de la lupa por
    // flujo -- asi la miniatura sigue llenando el 100% de la lupa (contrato
    // que ya median las pruebas de `apertura()`). Si el proyecto solo tiene
    // una captura, `otras` esta vacia y no se mueve.
    if (fila.otras.childElementCount > 0) {
      anclas.push({
        nodo: fila.otras,
        padre: fila.otras.parentNode as Node,
        siguiente: fila.otras.nextSibling,
      });
      visor.appendChild(fila.otras);
    }

    // GEOMETRIA. Se hace DESPUES de poblar el panel y ANTES de apartar las
    // filas, y en este orden porque cada paso depende del anterior:
    //   1. el hueco de arriba es el alto REAL de la fila abierta (la unica
    //      que se queda), leido ya sin su miniatura -- que acaba de irse a la
    //      lupa. Un `top: 132px` a mano se equivocaba en 3 de los 4 anchos
    //      medidos y en movil se comia 26px del propio titular.
    //   2. la pista crece hasta contener el panel. El estado abierto pide
    //      ~683px a 1440 y el carril natural da 548: sin esto, la lupa, la
    //      ficha y la banda pintan fuera (y `.obra-track` ahora RECORTA, asi
    //      que "fuera" es "no se ve ni se puede pulsar").
    //   3. las filas se apartan por el alto FINAL de la pista, no por el que
    //      tenia antes de crecer: con el viejo, la fila siguiente aterrizaba
    //      dentro del carril ya crecido y se leia bajo el panel.
    // `Math.ceil`, no `Math.round`: igual que `alturaPista` unas lineas mas
    // abajo. Redondear hacia abajo dejaba hasta 0,5px de solape entre el
    // panel y el borde inferior de la fila abierta.
    pista.style.setProperty("--cartel-fila", `${Math.ceil(fila.seccion.getBoundingClientRect().height)}px`);
    // El `min-height` se suelta ANTES de medir: si esta apertura viene de
    // cerrar otra fila, el tween de vuelta sigue en vuelo y `clientHeight`
    // devolveria el alto inflado del panel anterior en vez del natural.
    gsap.killTweensOf(pista);
    const desde = pista.clientHeight;
    pista.style.minHeight = "";
    // Se mide con rectangulos, no con `offsetTop`/`offsetHeight`: esos dos
    // vienen REDONDEADOS al entero y contra el `offsetParent`, y el panel
    // encadena varias cajas con alturas fraccionarias -- la suma se quedaba
    // corta y la ficha asomaba por debajo del carril en movil.
    const alturaPista = Math.max(
      pista.clientHeight,
      Math.ceil(panel.getBoundingClientRect().bottom - pista.getBoundingClientRect().top),
    );
    gsap.fromTo(
      pista,
      { minHeight: desde },
      { minHeight: alturaPista, duration: motionReducido ? 0 : 0.62, ease: "hard" },
    );

    const arriba = fila.seccion.offsetTop;
    filas.forEach((otra, j) => {
      const destino =
        j === indice ? -arriba : j < indice ? -(arriba + alturaPista) : alturaPista;
      // `.obra-track` recorta (Requisito 2), y eso lo convierte en
      // CONTENEDOR DE SCROLL: las cuatro filas apartadas siguen su `y` fuera
      // del carril, pero su `<button data-obra-abrir>` seguia siendo
      // tabulable. Sin esto, tabular desde la fila abierta hacia la
      // siguiente apartada hacia que el navegador desplazara el carril para
      // revelar un boton invisible -- el panel se iba de cuadro sin barra ni
      // gesto para volver. `inert` saca la fila entera (boton, titular,
      // miniatura) del arbol de foco y de accesibilidad mientras esta
      // apartada; se retira en `cierra()` y en `destroy()`.
      if (j === indice) otra.seccion.removeAttribute("inert");
      else otra.seccion.setAttribute("inert", "");
      gsap.to(otra.seccion, {
        y: destino,
        duration: motionReducido ? 0 : 0.62,
        ease: "hard",
        delay: motionReducido ? 0 : Math.abs(j - indice) * 0.03,
      });
    });

    gsap.fromTo(
      ficha,
      { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0 0 0)", duration: motionReducido ? 0 : 0.42, ease: "hard" },
    );
    if (!motionReducido) {
      particion = new SplitText(ficha.querySelectorAll("p, .obra-stack"), {
        type: "lines",
        mask: "lines",
      });
      gsap.fromTo(
        particion.lines,
        { yPercent: 110 },
        {
          yPercent: 0,
          duration: 0.42,
          ease: "hard",
          stagger: 0.045,
          delay: 0.24,
          onComplete: cortaParticion,
        },
      );
    }
    // Las marcas del stack entran por corte, con escalonado propio: no van
    // dentro del `SplitText` de arriba (que parte parrafos en lineas) porque
    // `.obra-marca` no es texto, es un `<span>` con un SVG dentro.
    if (!motionReducido) {
      gsap.fromTo(
        ficha.querySelectorAll(".obra-marca"),
        { clipPath: "inset(0 100% 0 0)" },
        { clipPath: "inset(0 0 0 0)", duration: 0.42, ease: "hard", stagger: 0.05, delay: 0.42 },
      );
    } else {
      gsap.set(ficha.querySelectorAll(".obra-marca"), { clipPath: "inset(0 0 0 0)" });
    }
    anuncio.textContent = `${fila.boton.getAttribute("aria-label")?.replace("Mostrar ", "") ?? ""}, ficha abierta.`;
  }

  function cierra(): void {
    if (abierta < 0) return;
    const fila = filas[abierta];
    abierta = -1;
    fila.seccion.classList.remove("is-abierto");
    fila.boton.setAttribute("aria-expanded", "false");
    // Devuelve las cuatro filas apartadas al orden de tabulacion: `abre()`
    // les puso `inert` mientras estaban fuera del carril, y con el cartel
    // cerrado las cinco vuelven a ser alcanzables.
    for (const otra of filas) otra.seccion.removeAttribute("inert");
    relevo(gsap, fila, false, motionReducido);
    restauraMini(gsap, fila);
    const estado = Flip.getState(fila.mini);
    fila.seccion.appendChild(fila.mini);
    Flip.from(estado, { duration: motionReducido ? 0 : 0.52, ease: "hard", absolute: true });
    gsap.to(filas.map((f) => f.seccion), {
      y: 0,
      duration: motionReducido ? 0 : 0.52,
      ease: "hard",
      stagger: 0.03,
    });
    // La pista vuelve a su alto natural con la misma curva. Se anima hasta el
    // alto de las filas y solo entonces se suelta el `min-height`: bajar a 0
    // de golpe deja caer la seccion siguiente de un tiron a mitad del gesto.
    gsap.killTweensOf(pista);
    // Se mide con `fila.mini` ya de vuelta en `fila.seccion` (el `appendChild`
    // de arriba) pero todavia con el `position: absolute` que le puso el
    // `Flip.from({absolute: true})` de mas abajo -- GSAP lo revierte solo,
    // pero no antes de que arranque su propio tween, sino al terminarlo. En
    // este instante sincrono la miniatura NO contribuye al flujo de la fila,
    // asi que `alturaNatural()` puede quedarse corta durante los ~520ms del
    // cierre y dar un tiron pequeno cuando Flip la devuelve al flujo casi a
    // la vez que este tween llega a su propio final. No se corrige aqui:
    // forzar el orden exigiria o bien retrasar esta medida a un frame donde
    // Flip ya haya revertido (arriesga desincronizar el arranque del gesto
    // de cierre) o bien duplicar a mano el calculo de layout que ya hace
    // Flip. Documentado en vez de parcheado a ciegas sin poder verificarlo
    // fotograma a fotograma.
    const natural = alturaNatural(pista);
    gsap.to(pista, {
      minHeight: natural,
      duration: motionReducido ? 0 : 0.52,
      ease: "hard",
      onComplete: () => {
        pista.style.minHeight = "";
      },
    });
    cortaParticion();
    // Sale tambien por recorte, y el contenido se devuelve DESPUES: si se
    // vacia antes, lo que se anima durante el cierre es una caja vacia y el
    // gesto no existe. La guarda de turno evita que este `onComplete` —si ya
    // esta obsoleto porque se abrio otra fila mientras el recorte corria—
    // toque `anclas`, que para entonces ya apunta a la fila nueva.
    const turno = ++cierreEnCurso;
    gsap.to(ficha, {
      clipPath: "inset(0 100% 0 0)",
      duration: motionReducido ? 0 : 0.42,
      ease: "hard",
      onComplete: () => {
        if (turno !== cierreEnCurso) return;
        devuelveBloques();
        gsap.set(ficha, { pointerEvents: "none" });
      },
    });
    anuncio.textContent = "Ficha cerrada.";
  }

  // Solo en `fila.boton`: por CSS cubre la fila entera (`inset: 0`), asi que
  // ya es el objetivo tactil completo. Enganchar el mismo "click" tambien en
  // `fila.seccion` duplica la llamada por burbujeo (el clic en el boton
  // burbujea hasta la seccion) — se abre y el segundo disparo la cierra en
  // el mismo evento. Medido con el arnes: "no se abrio" en las cinco filas.
  filas.forEach((fila, i) => {
    const alPulsar = (evento: Event): void => {
      evento.preventDefault();
      abre(i);
    };
    fila.boton.addEventListener("click", alPulsar);
    sueltas.push(() => fila.boton.removeEventListener("click", alPulsar));
  });
  const alTeclado = (e: KeyboardEvent): void => {
    if (e.key === "Escape") cierra();
  };
  window.addEventListener("keydown", alTeclado);
  sueltas.push(() => window.removeEventListener("keydown", alTeclado));

  let entradaHandle: EntradaHandle | null = null;
  if (!motionReducido) entradaHandle = entrada(gsap, root, filas);
  else asentar(gsap, filas);

  return {
    destroy(): void {
      for (const soltar of sueltas) soltar();
      gsap.killTweensOf(filas.flatMap((f) => [...f.tiras, ...f.entradas, f.mini, f.seccion]));
      gsap.killTweensOf(ficha);
      // Las marcas del stack son hijos de `ficha`, no la propia `ficha`: su
      // tween de entrada no lo mata el `killTweensOf(ficha)` de arriba.
      gsap.killTweensOf(ficha.querySelectorAll(".obra-marca"));
      cortaParticion();
      // Deshace cualquier intercambio de captura ANTES de devolver nada a su
      // sitio: si `destroy()` llega con una ficha abierta y una foto
      // intercambiada, el DOM real (`obra-mini-img.src`, su `alt`, el pie)
      // se quedaria mutado tras `pagehide`. Con bfcache la pagina no se
      // remonta al volver -- el siguiente `partirTitulo()` leeria esa
      // mutacion como si fuera `gallery[0]`, y la primera captura quedaria
      // inaccesible el resto de la sesion. Se hace para TODAS las filas, no
      // solo la abierta: es un no-op seguro en las que nunca se tocaron.
      for (const fila of filas) restauraMini(gsap, fila);
      // Si `destroy()` llega a mitad de una apertura O de un cierre, la
      // miniatura y los bloques de la ficha no pueden quedar huerfanos fuera
      // de su fila. `devuelveBloques()` es un no-op seguro si no hay nada
      // pendiente (anclas vacio).
      if (abierta >= 0) {
        const fila = filas[abierta];
        fila.seccion.appendChild(fila.mini);
      }
      devuelveBloques();
      // Este modulo se destruye en `pagehide` precisamente por el bfcache: al
      // restaurar la pagina no se remonta, asi que sin esto el cartel
      // volveria con las cinco filas desplazadas fuera de pantalla (el `y`
      // que dejo el ultimo `abre()`/`cierra()`) y la miniatura con los
      // estilos inline que le fijo Flip (`absolute: true` escribe
      // position/top/left/width/height a mano).
      gsap.set(filas.map((f) => f.seccion), { clearProps: "all" });
      gsap.set(filas.map((f) => f.mini), { clearProps: "all" });
      for (const fila of filas) {
        fila.seccion.classList.remove("is-abierto");
        fila.boton.setAttribute("aria-expanded", "false");
        // Misma razon que en `cierra()`: sin esto, `destroy()` a mitad de
        // una apertura deja hasta cuatro filas `inert` para siempre. Con
        // bfcache la pagina no se remonta al volver, asi que quedarian
        // permanentemente fuera del foco y de la accesibilidad.
        fila.seccion.removeAttribute("inert");
      }
      // El crecimiento de la pista es un estilo en linea y una variable CSS:
      // con bfcache la pagina no se remonta, asi que sin soltarlos el carril
      // volveria con el alto del ultimo panel abierto.
      gsap.killTweensOf(pista);
      pista.style.minHeight = "";
      pista.style.removeProperty("--cartel-fila");
      panel.remove();
      anuncio.remove();
      // La barra de brasa vive fuera de `filas`: sin esto su tween sigue vivo
      // si `destroy()` llega a mitad del barrido (p.ej. bfcache).
      if (entradaHandle) {
        entradaHandle.tl.kill();
        entradaHandle.barra.remove();
      }
    },
  };
}

/** Alto de la pista SIN el `min-height` que le pone la apertura, es decir el
 * que le dan sus cinco filas. Se mide soltando el estilo y volviendolo a
 * poner en la misma tarea: entre las dos escrituras no hay pintado, asi que
 * no parpadea. */
function alturaNatural(nodo: HTMLElement): number {
  const previo = nodo.style.minHeight;
  nodo.style.minHeight = "";
  const alto = nodo.clientHeight;
  nodo.style.minHeight = previo;
  return alto;
}

/** Convierte el texto del boton en una letra por mirilla, con su gemela. */
function partirTitulo(seccion: HTMLElement): Fila {
  const boton = seccion.querySelector<HTMLButtonElement>("[data-obra-abrir]");
  const titulo = seccion.querySelector<HTMLElement>("h2.display-lg");
  const mini = seccion.querySelector<HTMLElement>("[data-obra-mini]");
  const otras = seccion.querySelector<HTMLElement>("[data-obra-otras]");
  if (!boton || !titulo || !mini || !otras) {
    throw new Error("Fila de obra sin boton, titulo, miniatura o banda de capturas");
  }

  const miniImg = mini.querySelector<HTMLImageElement>(".obra-mini-img");
  const miniPie = mini.querySelector<HTMLElement>(".obra-mini-pie");
  const miniOriginal = {
    src: miniImg?.src ?? "",
    alt: miniImg?.alt ?? "",
    pie: miniPie?.textContent ?? "",
  };

  // El disparador es un CONMUTADOR: abre y cierra la misma ficha, asi que
  // tiene que decir en que estado esta. Sin esto seguia anunciandose como
  // "Mostrar EchoPlan" con la ficha ya abierta.
  boton.setAttribute("aria-expanded", "false");

  // Se parte el TITULAR, no el boton: el boton es un hermano vacio que solo
  // hace de disparador accesible (ver Task 1).
  const texto = titulo.textContent ?? "";
  titulo.textContent = "";

  // Patron estandar para texto partido en letras: el CONTENEDOR (el <h2>)
  // lleva el nombre accesible real via `aria-label`, y los trozos visuales
  // quedan fuera del arbol de accesibilidad con `aria-hidden`. Sin esto, el
  // <h2> sigue siendo un encabezado pero su nombre calculado a partir del
  // contenido seria cada letra duplicada ("EEcchhooPPllaann"): el contenedor
  // se queda, el duplicado desaparece del arbol.
  titulo.setAttribute("aria-label", texto);
  const capas = document.createElement("span");
  capas.setAttribute("aria-hidden", "true");
  for (const caracter of texto) {
    const mirilla = document.createElement("span");
    mirilla.className = "obra-ch";
    if (caracter === " ") {
      mirilla.classList.add("obra-ch-hueco");
      capas.appendChild(mirilla);
      continue;
    }
    const capaEntrada = document.createElement("span");
    capaEntrada.className = "obra-en";
    const tira = document.createElement("span");
    tira.className = "obra-rl";
    for (let i = 0; i < 2; i += 1) {
      const glifo = document.createElement("i");
      glifo.textContent = caracter;
      tira.appendChild(glifo);
    }
    capaEntrada.appendChild(tira);
    mirilla.appendChild(capaEntrada);
    capas.appendChild(mirilla);
  }
  titulo.appendChild(capas);
  // El texto partido deja de ser legible para un lector de pantalla: se le
  // devuelve entero por `aria-label`.
  boton.setAttribute("aria-label", `Mostrar ${texto}`);

  return {
    seccion,
    boton,
    tiras: Array.from(titulo.querySelectorAll<HTMLElement>(".obra-rl")),
    entradas: Array.from(titulo.querySelectorAll<HTMLElement>(".obra-en")),
    mini,
    otras,
    miniOriginal,
    intercambio: null,
  };
}

/** El hover no es un estado, es un recorrido. */
function relevo(gsap: Gsap, fila: Fila, encendido: boolean, reducido: boolean): void {
  gsap.killTweensOf(fila.tiras);
  gsap.to(fila.tiras, {
    yPercent: encendido ? -50 : 0,
    duration: reducido ? 0 : 0.42,
    ease: "hard",
    stagger: reducido ? 0 : { each: PASO_RELEVO, from: encendido ? "start" : "end" },
  });
}

/** Devuelve la miniatura y los tiles a su estado ORIGINAL (`gallery[0]` en la
 * lupa, cada tile con SU captura), deshaciendo cualquier intercambio. Se
 * llama SIEMPRE al cerrar (`cierra()`) y al destruir el modulo
 * (`destroy()`): sin lo primero, reabrir una fila donde se pulso un tile
 * mostraria la ultima foto vista, no `gallery[0]`; sin lo segundo, el DOM
 * real se queda mutado tras `pagehide` y el siguiente `partirTitulo()` (al
 * volver de la bfcache) leeria esa mutacion como si fuera la primera
 * captura -- `gallery[0]` quedaria inaccesible el resto de la sesion. */
function restauraMini(gsap: Gsap, fila: Fila): void {
  // La linea de tiempo del intercambio PRIMERO: `killTweensOf(fila.mini)` mata
  // los dos recortes pero no el `.call()` que hay entre ellos, que muta
  // `src`/`alt`/pie. Si llega despues de esta funcion, deja el DOM real
  // intercambiado justo cuando se acaba de devolver a su sitio.
  if (fila.intercambio) {
    fila.intercambio.kill();
    fila.intercambio = null;
  }
  gsap.killTweensOf(fila.mini);
  gsap.set(fila.mini, { clipPath: "inset(0 0 0 0)" });
  const img = fila.mini.querySelector<HTMLImageElement>(".obra-mini-img");
  const pie = fila.mini.querySelector<HTMLElement>(".obra-mini-pie");
  if (img) {
    img.src = fila.miniOriginal.src;
    img.alt = fila.miniOriginal.alt;
  }
  if (pie) pie.textContent = fila.miniOriginal.pie;
  for (const tile of fila.otras.querySelectorAll<HTMLButtonElement>(".obra-otra")) {
    const tileImg = tile.querySelector<HTMLImageElement>(".obra-otra-img");
    if (!tileImg) continue;
    const origSrc = tileImg.dataset.origSrc;
    const origAlt = tileImg.dataset.origAlt;
    if (origSrc !== undefined) tileImg.src = origSrc;
    if (origAlt !== undefined) {
      tileImg.alt = origAlt;
      tile.setAttribute("aria-label", `Ver ${origAlt}`);
    }
  }
}

/**
 * Engancha cada tile de `[data-obra-otras]` para que, al pulsarlo,
 * INTERCAMBIE su captura con la que muestra la lupa: conmutador reversible,
 * sin marca de "activo" (no hace falta -- lo que ves en el tile es
 * precisamente lo que NO estas viendo en grande). Con un solo tile por
 * proyecto, un segundo clic sobre el mismo tile deshace el primero: vuelve a
 * la primera captura SIN cerrar la ficha.
 *
 * El intercambio es un recorte de 210ms en `hard` para ocultar + 210ms para
 * revelar (420ms en total, sin fundido). No hay Flip aqui: solo se anima
 * `fila.mini`, la banda de tiles se queda quieta bajo la lupa.
 *
 * `dataset.origSrc`/`dataset.origAlt` se fijan aqui, UNA vez al montar,
 * antes de cualquier clic: son el punto de retorno que usa `restauraMini()`
 * para devolver los tiles a su captura propia al cerrar/destruir.
 *
 * Devuelve la funcion que suelta los listeners, para `destroy()`.
 */
function engancharOtras(gsap: Gsap, fila: Fila, reducido: boolean): () => void {
  const tiles = Array.from(fila.otras.querySelectorAll<HTMLButtonElement>(".obra-otra"));
  const soltar: Array<() => void> = [];
  for (const tile of tiles) {
    const img = tile.querySelector<HTMLImageElement>(".obra-otra-img");
    if (img) {
      img.dataset.origSrc = img.src;
      img.dataset.origAlt = img.alt;
    }
    const alPulsar = (): void => {
      const miniImg = fila.mini.querySelector<HTMLImageElement>(".obra-mini-img");
      const miniPie = fila.mini.querySelector<HTMLElement>(".obra-mini-pie");
      if (!img || !miniImg || !miniPie) return;
      // Se guardan ANTES del `.call()`: para entonces `miniImg`/`img` ya
      // llevan su valor nuevo, y sin esta copia el intercambio se
      // duplicaria en vez de invertirse.
      const srcTile = img.src;
      const altTile = img.alt;
      const srcLupa = miniImg.src;
      const altLupa = miniImg.alt;
      gsap.killTweensOf(fila.mini);
      if (fila.intercambio) fila.intercambio.kill();
      const tl = gsap.timeline({ onComplete: () => { fila.intercambio = null; } });
      fila.intercambio = tl;
      tl.to(fila.mini, { clipPath: "inset(0 0 0 100%)", duration: reducido ? 0 : 0.21, ease: "hard" }).call(
        () => {
          miniImg.src = srcTile;
          miniImg.alt = altTile;
          miniPie.textContent = altTile;
          img.src = srcLupa;
          img.alt = altLupa;
          tile.setAttribute("aria-label", `Ver ${altLupa}`);
        },
      );
      tl.fromTo(
        fila.mini,
        { clipPath: "inset(0 0 0 100%)" },
        { clipPath: "inset(0 0 0 0)", duration: reducido ? 0 : 0.21, ease: "hard" },
      );
    };
    tile.addEventListener("click", alPulsar);
    soltar.push(() => tile.removeEventListener("click", alPulsar));
  }
  return () => {
    for (const fn of soltar) fn();
  };
}

interface EntradaHandle {
  tl: ReturnType<Gsap["timeline"]>;
  barra: HTMLElement;
}

/**
 * Entrada: UNA barra de brasa cruza el cartel y todo lo demas cuelga de ella.
 * El retardo de cada letra no se escribe a mano: sale de su posicion x real,
 * asi que la barra atraviesa los cinco titulares a la vez, por columnas.
 */
function entrada(gsap: Gsap, root: HTMLElement, filas: Fila[]): EntradaHandle | null {
  const pista = root.querySelector<HTMLElement>("[data-obra-track]");
  if (!pista) return null;
  const caja = pista.getBoundingClientRect();
  const ancho = caja.width || 1;

  const barra = document.createElement("i");
  barra.className = "obra-barrido";
  barra.setAttribute("aria-hidden", "true");
  pista.appendChild(barra);

  const tl = gsap.timeline({ onComplete: () => barra.remove() });
  tl.set(barra, { opacity: 1, x: 0 })
    // "none", no una de las dos curvas del tema: este barrido es lineal a
    // proposito. El retardo de cada letra sale de `(x / ancho) * BARRIDO`,
    // que asume velocidad constante — si la barra acelerase, dejaria de
    // coincidir con donde cada letra cree que esta y el gesto se partiria.
    .to(barra, { x: ancho, duration: BARRIDO, ease: "none" }, 0)
    .to(barra, { opacity: 0, duration: 0.22, ease: "slow" }, BARRIDO);

  for (const fila of filas) {
    fila.entradas.forEach((capa) => {
      const x = capa.getBoundingClientRect().left - caja.left;
      const retardo = Math.max(0, (x / ancho) * BARRIDO);
      tl.fromTo(capa, { yPercent: 112 }, { yPercent: 0, duration: 0.46, ease: "hard" }, retardo);
    });
    const xm = fila.mini.getBoundingClientRect().left - caja.left;
    tl.fromTo(
      fila.mini,
      { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0 0 0)", duration: 0.42, ease: "hard" },
      Math.max(0, (xm / ancho) * BARRIDO),
    );
  }

  return { tl, barra };
}

/** Con movimiento reducido el cartel esta tejido desde el primer fotograma. */
function asentar(gsap: Gsap, filas: Fila[]): void {
  for (const fila of filas) {
    gsap.set(fila.entradas, { yPercent: 0 });
    gsap.set(fila.mini, { clipPath: "inset(0 0 0 0)" });
  }
}
