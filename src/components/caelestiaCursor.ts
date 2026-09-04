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
// Task 2 no la usa todavia -- el derrame por roce llega en el Task 3.
// `noUnusedLocals` exige esta referencia mientras tanto.
void HOVER_SELECT;

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
   * Se cuelga de `host` (`#app`) y NUNCA de `main`: `main` es el carril de
   * workspaces y lleva `transform`, y un `position: fixed` dentro de un
   * elemento transformado deja de ser relativo al viewport -- se colocaria
   * contra un carril desplazado 4320px. Medido: `#app` no tiene transform.
   */
  host.append(cursor);

  let x = 0;
  let y = 0;
  let dentro = false;
  let diana: HTMLElement | null = null;
  let estadoActual: Estado = "reposo";
  let stale = false;
  let frame = 0;

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
  const resolver = (objetivo: Element | null): void => {
    const zona = objetivo?.closest<HTMLElement>(`${PRESSABLE}, ${NATIVE_ZONE}`) ?? null;
    if (!zona) {
      diana = null;
      setEstado(dentro ? "reposo" : "apagada");
      return;
    }
    const pulsable = zona.matches(PRESSABLE)
      ? zona
      : (zona.parentElement?.closest<HTMLElement>(PRESSABLE) ?? null);
    if (!pulsable) {
      diana = null;
      setEstado("apagada");
      return;
    }
    diana = pulsable;
    setEstado("perla");
  };

  /*
   * La posicion se escribe en el propio evento, sin suavizar. Un cursor con
   * inercia miente sobre donde esta el raton, y en Creditos hay 23 dianas
   * contiguas donde eso se lee como retraso. Lo que se interpola es el
   * TAMANO y la opacidad, en CSS.
   */
  const alMover = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
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
    dentro = true;
    resolver(evento.target);
  };

  const alSalirDelDocumento = (): void => {
    dentro = false;
    diana = null;
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
  window.addEventListener("resize", marcarRancio, { passive: true, signal });
  document.addEventListener("scroll", marcarRancio, { passive: true, capture: true, signal });
  document.addEventListener("pointerleave", alSalirDelDocumento, { passive: true, signal });
  document.documentElement.addEventListener("caelestia:workspace", marcarRancio, {
    passive: true,
    signal,
  });

  const tick = (): void => {
    frame = window.requestAnimationFrame(tick);
    if (!stale) return;
    stale = false;
    if (!dentro) return;
    // Fuera de la ventana devuelve null: ahi no hay zona que resolver.
    resolver(document.elementFromPoint(x, y));
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
    cursor.remove();
    delete (window as unknown as { __caeCursor__?: unknown }).__caeCursor__;
  };

  // Sonda de verificacion: la consume scripts/measure-caelestia-cursor.py.
  // No afecta al render mientras nadie la llame.
  Object.defineProperty(window, "__caeCursor__", {
    value: {
      estado: (): Estado => estadoActual,
      diana: (): HTMLElement | null => null,
      mancha: (): number => 0,
      destroy,
    },
    writable: false,
    configurable: true,
  });

  return { destroy };
}
