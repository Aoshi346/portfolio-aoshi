export interface CaelestiaCursorHandle {
  destroy: () => void;
}

/*
 * Cursor propio de Caelestia: una gota del pigmento de la hora.
 *
 * Spec: docs/superpowers/specs/2026-09-04-caelestia-cursor-design.md
 *
 * Sobre lo que se pulsa se tensa en perla y espera; al pulsar se derrama y
 * encharca la diana. Sobre lo que YA elige al rozarlo (las 23 piezas de
 * Creditos) se derrama al entrar: ya esta mojado. Los dos estados no son dos
 * simbolos -- son el MISMO gesto disparado en dos momentos, que es lo que
 * permite tener dos estados sin que el cursor necesite manual.
 *
 * Reparto de senales, identico al cerrado en Vice y en Hyprland porque el
 * problema es el mismo -- sustituir el puntero es legitimo, borrar las otras
 * senales no:
 *
 *   `pointer`  -> lo sustituye esta gota.
 *   `grab` / `grabbing` (`.gallery-track`) -> NATIVOS.
 *   I-beam en texto -> NATIVO.
 *   Enlaces `target="_blank"` -> NATIVOS. Abren pestana nueva.
 *
 * DOM y no `<canvas>`, al reves que Hyprland: la perla necesita
 * `backdrop-filter` y `mix-blend-mode`, que un contexto 2D no da.
 *
 * SIN GSAP. Todo el movimiento son transiciones y animaciones CSS: asi el
 * montaje no tiene que volverse `async` por un `import()` de la libreria, y
 * un dispositivo que se repinta con el raton no arrastra una timeline.
 *
 * NINGUN color se calcula aqui. Todo sale de los tokens que escribe
 * `caelestia.color.ts`, y el esquema lo dice `[data-cae-esquema]`.
 *
 * ---------------------------------------------------------------------
 * CONTRATO CON EL ARNES (`scripts/measure-caelestia-cursor.py`):
 *
 *  1. Este modulo NUNCA escribe `display` en la mancha. El arnes lo apaga
 *     con `display: none` para su comparacion A/B, y necesita que el
 *     siguiente fotograma no se lo pise.
 *  2. `__caeCursor__.mancha()` devuelve el avance PINTADO, leido de
 *     `getComputedStyle`, no el valor objetivo que este modulo acaba de
 *     escribir. Un gate que leyera el objetivo mediria la intencion y no el
 *     resultado: seria tautologico.
 * ---------------------------------------------------------------------
 */

// Pulsables que la gota viste. El enlace externo queda fuera aposta.
const PRESSABLE = 'button, a[href]:not([target="_blank"])';
// Zonas donde manda el navegador y la gota se apaga.
const NATIVE_ZONE = '.gallery-track, a[target="_blank"], p, li, dd, dt, figcaption, blockquote';
/*
 * De entre los pulsables, los que YA responden al roce: ahi la gota se
 * derrama al entrar, sin esperar clic.
 *
 * `aria-pressed` no es taxonomia inventada para el cursor: las 23 piezas de
 * Creditos lo llevan porque SON botones de estado
 * (`caelestiaCreditosBandeja.ts:76`), y ni las tarjetas de Obra ni las
 * pastillas del shell lo llevan. Si manana una diana nueva elige al rozar,
 * llevara `aria-pressed` porque es lo correcto para ella, y la gota la
 * vestira sola.
 *
 * OJO: el selector casa 46 nodos, no 23 -- las filas `.credit` del
 * `credits.ts` generico tambien lo llevan, ocultas por
 * `.credits-grid { display: none }`. No es un problema (un nodo oculto no
 * recibe `pointerover`), pero NADIE puede contar nodos para decidir nada.
 */
const HOVER_SELECT = "button[aria-pressed]";

type Estado = "reposo" | "perla" | "derrame" | "apagada";

export function mountCaelestiaCursor(host: HTMLElement): CaelestiaCursorHandle {
  const controller = new AbortController();
  const { signal } = controller;

  const perla = document.createElement("div");
  perla.className = "cae-cursor-perla";
  const nucleo = document.createElement("i");
  nucleo.className = "cae-cursor-nucleo";
  const cursor = document.createElement("div");
  cursor.className = "cae-cursor";
  cursor.setAttribute("aria-hidden", "true");
  cursor.dataset.estado = "reposo";
  cursor.append(perla, nucleo);

  /*
   * El derrame es un elemento APARTE, no un `background-image` en la diana
   * como hace Hyprland. Aquel necesita quedar debajo del texto; este es
   * pigmento sobre papel y va encima de todo. La ventaja no es menor: este
   * modulo NO toca el DOM de ninguna diana, asi que no hay estado previo que
   * guardar ni que restaurar, que es la clase de fallo que a Hyprland le
   * costo una tarea entera.
   */
  const mancha = document.createElement("div");
  mancha.className = "cae-cursor-mancha";
  mancha.setAttribute("aria-hidden", "true");
  const gota = document.createElement("i");
  gota.className = "cae-cursor-gota";
  mancha.append(gota);

  /*
   * Se cuelga de `host` (`#app`) y NUNCA de `main`: `main` es el carril de
   * workspaces y lleva `transform`, y un `position: fixed` dentro de un
   * elemento transformado deja de ser relativo al viewport -- se colocaria
   * contra un carril desplazado 4320px. Medido: `#app` no tiene transform.
   */
  host.append(cursor, mancha);

  let x = 0;
  let y = 0;
  let dentro = false;
  let diana: HTMLElement | null = null;
  let estadoActual: Estado = "reposo";
  let stale = false;
  let frame = 0;
  let mojada: HTMLElement | null = null;
  let objetivo = 0;
  let cajaAncho = 0;
  let cajaAlto = 0;
  let pulsado = false;

  /*
   * Los cercos vivos. Se guardan porque `destroy()` tiene que llevarselos:
   * un cerco lanzado en el ultimo clic antes de navegar sobrevive a su
   * modulo si nadie lo recoge, y eso es DOM huerfano.
   */
  const cercos = new Set<HTMLElement>();
  // El temporizador de respaldo de cada cerco, para poder cancelarlo si
  // `animationend` llega primero. La clave es el propio anillo.
  const cercosTemporizador = new Map<HTMLElement, ReturnType<typeof window.setTimeout>>();

  /*
   * Retira un cerco del DOM y de `cercos`, y cancela su temporizador de
   * respaldo si seguia pendiente. Idempotente a proposito: `animationend` y
   * el `setTimeout` de respaldo pueden acabar llamando a esto por el mismo
   * anillo, y la segunda llamada no debe hacer nada.
   */
  const retirarCerco = (anillo: HTMLElement): void => {
    const temporizador = cercosTemporizador.get(anillo);
    if (temporizador !== undefined) {
      window.clearTimeout(temporizador);
      cercosTemporizador.delete(anillo);
    }
    if (!cercos.delete(anillo)) return;
    anillo.remove();
  };

  /*
   * El anillo que deja una gota al secarse sobre papel. Es la constancia de
   * que el clic ocurrio, sin escribir un solo caracter -- la regla dura
   * heredada de Hyprland: un cursor no puede tener manual.
   *
   * Solo en el clic REAL, nunca en el roce: la gota deja huella donde ha
   * actuado, nunca por donde pasa. (Por lo mismo no hay estela.)
   */
  const dejarCerco = (): void => {
    const anillo = document.createElement("i");
    anillo.className = "cae-cursor-cerco";
    anillo.setAttribute("aria-hidden", "true");
    anillo.style.left = `${x}px`;
    anillo.style.top = `${y}px`;
    anillo.addEventListener("animationend", () => retirarCerco(anillo), { once: true });
    /*
     * Respaldo: el modulo nunca da por hecho que vio terminar la animacion.
     * Si `prefers-reduced-motion` se activa DESPUES de montar (el caso real:
     * alguien lo prueba con la emulacion de devtools a mitad de sesion), la
     * guardia CSS deja el anillo en `display: none` para siempre -- un
     * elemento que nunca se pinta nunca dispara `animationend`, y tampoco
     * `animationcancel` (la animacion nunca llega a arrancar). Sin este
     * respaldo el anillo se queda colgado de `host` y en `cercos` el resto
     * de la sesion, y cada clic siguiente anade otro.
     *
     * 1200ms: la animacion dura 800ms: 400ms de margen cubre el jitter de un
     * tick de rAF perdido sin dejar el anillo visible de mas en el camino
     * feliz, donde `animationend` ya lo habra retirado mucho antes.
     */
    cercosTemporizador.set(
      anillo,
      window.setTimeout(() => retirarCerco(anillo), 1200),
    );
    cercos.add(anillo);
    host.append(anillo);
  };

  const setEstado = (siguiente: Estado): void => {
    if (estadoActual === siguiente) return;
    estadoActual = siguiente;
    cursor.dataset.estado = siguiente;
  };

  /*
   * `closest()` con los dos selectores a la vez devuelve el ancestro (o el
   * propio nodo) MAS CERCANO que case cualquiera de los dos: el mas cercano
   * gana con independencia del orden en que se escriban. Eso ya resuelve el
   * caso de Hyprland (un boton anidado dentro de un `<p>`).
   *
   * Lo que NO resuelve es el inverso, que en esta pagina es la norma: la
   * leyenda de una tarjeta de Obra (`figcaption.cae-obra-caption`) y el
   * nombre de una pieza de Creditos (`figcaption.cae-cred-nom`) son zona
   * nativa y viven DENTRO del boton. Con `closest()` a secas la gota se
   * apagaria justo encima de las dianas. De ahi la segunda vuelta: si la
   * zona nativa esta dentro de un pulsable, manda el pulsable.
   *
   * El CSS lleva la misma inversion (`:not(button *, a[href] *)`), y las dos
   * tienen que moverse juntas: si divergen, el glifo del sistema y el estado
   * de la gota se contradicen sobre el mismo pixel.
   */
  // Radio en px del circulo base de `.cae-cursor-gota` (20px de lado).
  const RADIO_GOTA = 10;

  /** Escala a la que la gota cubre la caja entera desde donde cayo. */
  const alcanceDe = (caja: DOMRect): number => {
    const dx = Math.max(x - caja.left, caja.right - x);
    const dy = Math.max(y - caja.top, caja.bottom - y);
    return Math.hypot(dx, dy) / RADIO_GOTA + 0.2;
  };

  /** Coloca la caja de la mancha sobre la diana mojada. */
  const colocarMancha = (caja: DOMRect): void => {
    mancha.style.left = `${caja.left}px`;
    mancha.style.top = `${caja.top}px`;
    mancha.style.width = `${caja.width}px`;
    mancha.style.height = `${caja.height}px`;
  };

  const mojar = (destino: HTMLElement): void => {
    mojada = destino;
    const caja = destino.getBoundingClientRect();
    colocarMancha(caja);
    cajaAncho = caja.width;
    cajaAlto = caja.height;
    // El radio se lee UNA vez por diana, no por fotograma: `getComputedStyle`
    // es caro y el radio de una diana no cambia mientras la senalas.
    mancha.style.borderRadius = getComputedStyle(destino).borderRadius;
    // El centro del derrame es donde cayo la gota, en coordenadas de la caja,
    // y se queda ahi: una mancha no persigue al raton.
    gota.style.left = `${x - caja.left}px`;
    gota.style.top = `${y - caja.top}px`;
    /*
     * Un fotograma a escala 0 antes de crecer. Sin esto el navegador no tiene
     * dos valores que interpolar -- si la gota venia de estar seca ya estaba
     * a 0, pero si venia de otra diana venia de su escala anterior, y el
     * derrame arrancaria a medio camino.
     */
    gota.style.transform = "translate(-50%, -50%) scale(0)";
    void gota.offsetWidth;
    objetivo = alcanceDe(caja);
    gota.style.transform = `translate(-50%, -50%) scale(${objetivo.toFixed(3)})`;
  };

  const secar = (): void => {
    if (!mojada) return;
    mojada = null;
    objetivo = 0;
    gota.style.transform = "translate(-50%, -50%) scale(0)";
  };

  const resolver = (objetivo: Element | null): void => {
    const zona = objetivo?.closest<HTMLElement>(`${PRESSABLE}, ${NATIVE_ZONE}`) ?? null;
    if (!zona) {
      diana = null;
      secar();
      setEstado(dentro ? "reposo" : "apagada");
      return;
    }
    const pulsable = zona.matches(PRESSABLE)
      ? zona
      : (zona.parentElement?.closest<HTMLElement>(PRESSABLE) ?? null);
    if (!pulsable) {
      diana = null;
      secar();
      setEstado("apagada");
      return;
    }
    if (pulsable !== diana) {
      diana = pulsable;
      /*
       * La familia se decide UNA vez por diana, no por fotograma. Los dos
       * momentos del mismo gesto: la que ya elige al rozarla se moja al
       * entrar, la de clic espera al clic.
       */
      if (diana.matches(HOVER_SELECT) || pulsado) mojar(diana);
      else secar();
    }
    setEstado(mojada ? "derrame" : "perla");
  };

  /*
   * Todo evento de puntero trae `buttons`: nunca hay que fiarse de haber
   * visto el `pointerup` (el caso mas comun de perderlo: soltar fuera del
   * viewport, donde `window` no recibe nada). Tiene que correr ANTES de que
   * `resolver()` lea `pulsado` en el mismo evento -- por eso va primero en
   * `alEntrar`, no solo en `alMover`: en un `pointerover` que aterriza
   * directo sobre una diana nueva (el salto de un `hover()`, o un usuario
   * real que suelta fuera de la ventana y su primer movimiento dentro cae ya
   * sobre otro elemento), el `pointerover` llega ANTES que cualquier
   * `pointermove` -- si solo viviera en `alMover`, `resolver()` ya habria
   * mojado la diana con el `pulsado` viejo para cuando el self-heal corriera.
   */
  const sincronizarPulsado = (evento: PointerEvent): void => {
    if (pulsado && evento.buttons === 0) pulsado = false;
  };

  /*
   * La posicion se escribe en el propio evento, sin suavizar. Un cursor con
   * inercia miente sobre donde esta el raton, y en Creditos hay 23 dianas
   * contiguas donde eso se lee como retraso. Lo que se interpola es el
   * TAMANO y la opacidad, en CSS.
   */
  const alMover = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
    sincronizarPulsado(evento);
    x = evento.clientX;
    y = evento.clientY;
    if (!dentro) {
      dentro = true;
      setEstado(diana ? "perla" : "reposo");
    }
    cursor.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  };

  /*
   * El estado se resuelve en `pointerover`, que solo dispara al cambiar de
   * elemento: asi los `closest()` cuestan una vez por transicion y no sesenta
   * veces por segundo.
   *
   * `dentro` se marca AQUI y no solo en `alMover`: `pointerover` siempre
   * dispara antes que el `pointermove` de la misma entrada al elemento. Si
   * el primer movimiento real del visitante aterriza directo sobre zona
   * nativa (un parrafo, sin pasar antes por ningun otro nodo), sin esta
   * linea `alMover` encontraria `dentro` todavia en `false` y pisaria el
   * "apagada" que este resolver acaba de decidir con su propio fallback de
   * "reposo" -- la gota parpadearia encendida un fotograma sobre texto
   * corrido. Medido con un `hover()` de Playwright, que mueve el puntero de
   * un solo salto (sin pasos intermedios que ya hubieran marcado `dentro`).
   */
  const alEntrar = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
    if (!(evento.target instanceof Element)) return;
    sincronizarPulsado(evento);
    dentro = true;
    resolver(evento.target);
  };

  const alPulsar = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
    pulsado = true;
    if (diana && !mojada) mojar(diana);
    if (diana) setEstado("derrame");
  };

  const alSoltar = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
    pulsado = false;
    if (!diana) return;
    // La familia de roce se queda mojada: ahi el derrame no lo trajo el clic.
    if (!diana.matches(HOVER_SELECT)) {
      secar();
      dejarCerco();
    }
    setEstado(mojada ? "derrame" : "perla");
  };

  const alSalirDelDocumento = (): void => {
    dentro = false;
    diana = null;
    // Salir del documento borra el estado transitorio del puntero: si el
    // clic se solto fuera del viewport, este es el unico evento que lo sabe.
    pulsado = false;
    secar();
    setEstado("apagada");
  };

  /*
   * Cuando cambia lo que hay bajo un raton QUIETO no llega ningun evento de
   * puntero. En Caelestia pasa de dos formas, y las dos son la norma y no la
   * excepcion: al cambiar de workspace (el carril se lleva la diana y deja
   * otra escena debajo) y si algun contenedor desplaza su contenido. La
   * comprobacion se aplaza al siguiente fotograma en vez de hacerse en el
   * propio evento, porque llegan en rafagas.
   *
   * El `scroll` va en fase de CAPTURA sobre `document`: los eventos de
   * scroll de un contenedor interno NO burbujean, asi que un oyente en
   * `window` no los ve. Hoy ningun contenedor de Caelestia desborda -- es
   * red preventiva, y esta escrito para que nadie la confunda con algo
   * medido.
   */
  const marcarRancio = (): void => {
    stale = true;
  };

  window.addEventListener("pointermove", alMover, { passive: true, signal });
  window.addEventListener("pointerover", alEntrar, { passive: true, signal });
  window.addEventListener("pointerdown", alPulsar, { passive: true, signal });
  window.addEventListener("pointerup", alSoltar, { passive: true, signal });
  window.addEventListener("resize", marcarRancio, { passive: true, signal });
  document.addEventListener("scroll", marcarRancio, { passive: true, capture: true, signal });
  document.addEventListener("pointerleave", alSalirDelDocumento, { passive: true, signal });
  /*
   * Medido en Chromium (`scripts/measure-caelestia-cursor.py`, gate 5): al
   * cambiar de workspace, `aislarInactivos()` pone `inert = true` en la
   * escena saliente y el navegador dispara `pointerout`/`pointerleave`
   * NATIVOS y reales sobre la diana mojada, sin que el raton se mueva --
   * esos eventos llegan a `alEntrar` y curan el estado solos, mas rapido de
   * lo que tarda esta escucha en disparar. En este motor la via nativa gana
   * la carrera y esta escucha es defensa en profundidad, no la unica via.
   *
   * Se queda de todos modos, por dos razones -- no es codigo muerto:
   * 1. El mismo `marcarRancio` tambien sirve a `scroll` y a `resize`, que
   *    NO tienen sanacion nativa ninguna: no es una escucha de un solo uso
   *    que se pueda aislar y quitar.
   * 2. La sanacion nativa de arriba es incidental: depende de que la fase A
   *    elija marcar `inert` las escenas inactivas. Un cambio futuro que
   *    mueva el carril sin `inert`, o un motor que no dispare `pointerout`
   *    ante ese cambio, se lleva la sanacion por delante en silencio -- y el
   *    modo de fallo es una mancha pintada sobre la escena siguiente, que es
   *    justo lo que este dispositivo no puede hacer nunca.
   */
  document.documentElement.addEventListener("caelestia:workspace", marcarRancio, {
    passive: true,
    signal,
  });

  const tick = (): void => {
    frame = window.requestAnimationFrame(tick);
    if (stale) {
      stale = false;
      // Fuera de la ventana devuelve null: ahi no hay zona que resolver.
      if (dentro) resolver(document.elementFromPoint(x, y));
    }
    if (!mojada) return;
    /*
     * defensive: el carril de workspaces puede llevarse la diana del arbol
     * mientras esta mojada. Sin esto la mancha se queda pintada sobre una
     * caja que ya no existe.
     */
    if (!mojada.isConnected) {
      secar();
      diana = null;
      setEstado(dentro ? "reposo" : "apagada");
      return;
    }
    const caja = mojada.getBoundingClientRect();
    colocarMancha(caja);
    /*
     * La escala objetivo solo se recalcula si la caja CAMBIA DE TAMANO -- la
     * tarjeta de Obra se endereza al rozarla y crece unos pixeles. Reescribir
     * la escala cada fotograma reiniciaria la transicion sesenta veces por
     * segundo y el derrame no llegaria a crecer nunca.
     */
    if (Math.abs(caja.width - cajaAncho) > 1 || Math.abs(caja.height - cajaAlto) > 1) {
      cajaAncho = caja.width;
      cajaAlto = caja.height;
      objetivo = alcanceDe(caja);
      gota.style.transform = `translate(-50%, -50%) scale(${objetivo.toFixed(3)})`;
    }
  };
  frame = window.requestAnimationFrame(tick);

  // La clase solo se pone tras montar con exito: si este modulo no llega a
  // cargar o revienta antes, el CSS no oculta nada y el cursor del sistema
  // sigue intacto en toda la pagina.
  document.documentElement.classList.add("caelestia-cursor-ready");

  const destroy = (): void => {
    window.cancelAnimationFrame(frame);
    controller.abort();
    document.documentElement.classList.remove("caelestia-cursor-ready");
    /*
     * Los cercos vivos se retiran POR `retirarCerco`, no con un `remove()`
     * suelto: es lo unico que ademas cancela su temporizador de respaldo.
     * Un `remove()` crudo dejaria el nodo fuera del DOM pero el `setTimeout`
     * de 1200 ms corriendo contra un nodo huerfano y un modulo desmontado.
     * Se itera sobre una COPIA porque `retirarCerco` borra del propio `Set`.
     */
    for (const anillo of Array.from(cercos)) retirarCerco(anillo);
    cursor.remove();
    mancha.remove();
    delete (window as unknown as { __caeCursor__?: unknown }).__caeCursor__;
  };

  // Sonda de verificacion: la consume scripts/measure-caelestia-cursor.py.
  // No afecta al render mientras nadie la llame.
  Object.defineProperty(window, "__caeCursor__", {
    value: {
      estado: (): Estado => estadoActual,
      diana: (): HTMLElement | null => mojada,
      /*
       * El avance PINTADO, no el objetivo que este modulo acaba de escribir:
       * un gate que leyera el objetivo mediria la intencion y no el
       * resultado. Ver el contrato de la cabecera.
       */
      mancha: (): number => {
        if (!mojada || objetivo <= 0) return 0;
        const m = new DOMMatrixReadOnly(getComputedStyle(gota).transform);
        return Math.min(m.a / objetivo, 1);
      },
      destroy,
    },
    writable: false,
    configurable: true,
  });

  return { destroy };
}
