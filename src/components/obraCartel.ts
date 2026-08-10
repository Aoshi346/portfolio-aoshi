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
  pista.append(lupa, ficha, anuncio);

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
    relevo(gsap, fila, true, motionReducido);

    // La miniatura y la grande son EL MISMO nodo: Flip mide donde esta, se
    // reubica, y se anima el recorrido real entre las dos posiciones.
    const estado = Flip.getState(fila.mini);
    lupa.appendChild(fila.mini);
    Flip.from(estado, { duration: motionReducido ? 0 : 0.62, ease: "hard", absolute: true });

    const arriba = fila.seccion.offsetTop;
    const alturaPista = pista.clientHeight;
    filas.forEach((otra, j) => {
      const destino =
        j === indice ? -arriba : j < indice ? -(arriba + alturaPista) : alturaPista;
      gsap.to(otra.seccion, {
        y: destino,
        duration: motionReducido ? 0 : 0.62,
        ease: "hard",
        delay: motionReducido ? 0 : Math.abs(j - indice) * 0.03,
      });
    });

    const piezas = bloquesDeFicha(fila.seccion);
    anclas = piezas.map((nodo) => ({ nodo, padre: nodo.parentNode as Node, siguiente: nodo.nextSibling }));
    ficha.replaceChildren(...piezas);
    gsap.set(ficha, { pointerEvents: "auto" });
    // La banda de capturas restantes (Task 8) NO viaja a la ficha: vive
    // bajo la lupa, en `.obra-track`, para que la miniatura pueda seguir
    // llenando el 100% de la lupa (contrato que ya median las pruebas de
    // `apertura()`). Si el proyecto solo tiene una captura, `otras` esta
    // vacia y no se mueve -- no hay nada que mostrar ni hueco que dejar.
    if (fila.otras.childElementCount > 0) {
      anclas.push({
        nodo: fila.otras,
        padre: fila.otras.parentNode as Node,
        siguiente: fila.otras.nextSibling,
      });
      pista.appendChild(fila.otras);
    }
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
      for (const fila of filas) fila.seccion.classList.remove("is-abierto");
      lupa.remove();
      ficha.remove();
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

/** Devuelve la miniatura a su PRIMERA captura y limpia el estado "activo" de
 * los tiles. Se llama SIEMPRE al cerrar: sin esto, reabrir una fila donde se
 * pulso un tile mostraria la ultima foto vista, no `gallery[0]`. */
function restauraMini(gsap: Gsap, fila: Fila): void {
  gsap.killTweensOf(fila.mini);
  gsap.set(fila.mini, { clipPath: "inset(0 0 0 0)" });
  const img = fila.mini.querySelector<HTMLImageElement>(".obra-mini-img");
  const pie = fila.mini.querySelector<HTMLElement>(".obra-mini-pie");
  if (img) {
    img.src = fila.miniOriginal.src;
    img.alt = fila.miniOriginal.alt;
  }
  if (pie) pie.textContent = fila.miniOriginal.pie;
  for (const tile of fila.otras.querySelectorAll(".obra-otra")) tile.classList.remove("is-activa");
}

/**
 * Engancha cada tile de `[data-obra-otras]` para que, al pulsarlo,
 * intercambie lo que muestra la lupa por SU captura: dos recortes de 210ms
 * en `hard` (oculta -> cambia el contenido -> revela), 420ms en total, sin
 * fundido. El tile pulsado queda marcado "activo" (filete de --l1); el
 * anterior lo pierde. No hay Flip aqui: solo viaja `fila.mini`, la banda de
 * tiles se queda quieta bajo la lupa.
 *
 * Devuelve la funcion que suelta los listeners, para `destroy()`.
 */
function engancharOtras(gsap: Gsap, fila: Fila, reducido: boolean): () => void {
  const tiles = Array.from(fila.otras.querySelectorAll<HTMLButtonElement>(".obra-otra"));
  const soltar: Array<() => void> = [];
  for (const tile of tiles) {
    const alPulsar = (): void => {
      const img = tile.querySelector<HTMLImageElement>(".obra-otra-img");
      const miniImg = fila.mini.querySelector<HTMLImageElement>(".obra-mini-img");
      const miniPie = fila.mini.querySelector<HTMLElement>(".obra-mini-pie");
      if (!img || !miniImg || !miniPie) return;
      const nuevoSrc = img.src;
      const nuevoAlt = img.alt;
      gsap.killTweensOf(fila.mini);
      const tl = gsap.timeline();
      tl.to(fila.mini, { clipPath: "inset(0 0 0 100%)", duration: reducido ? 0 : 0.21, ease: "hard" }).call(
        () => {
          miniImg.src = nuevoSrc;
          miniImg.alt = nuevoAlt;
          miniPie.textContent = nuevoAlt;
          for (const t of tiles) t.classList.toggle("is-activa", t === tile);
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
