export interface HyprCursorHandle {
  destroy: () => void;
}

/*
 * Cursor propio de Hyprland: no dibuja un objeto, ilumina.
 *
 * El charco de luz existe SOLO dentro de lo que se puede pulsar, recortado a
 * canto vivo por el borde del elemento. Sobre texto corrido no se enciende
 * nada. La lectura es anterior al lenguaje: lo que se ilumina responde.
 *
 * Reparto de senales, identico al ya cerrado en Vice porque el problema es el
 * mismo — sustituir el puntero es legitimo, borrar las otras senales no:
 *
 *   `pointer`  -> lo sustituye esta luz.
 *   `grab` / `grabbing` (`.gallery-track`) -> NATIVOS. Unica pista de que la
 *                 galeria se arrastra.
 *   I-beam en texto -> NATIVO. Ocultarlo quita la senal de que se selecciona.
 *   Enlaces externos (`target="_blank"`) -> NATIVOS. Abren pestana nueva.
 *
 * Diez direcciones cayeron antes que esta. Las tres ultimas (`hyprpicker`,
 * `col.active_border`, `slurp`) eran autenticas y se descartaron por escribir
 * medidas y etiquetas en pantalla: un cursor no puede tener manual. De ahi la
 * regla dura de este modulo — NO se dibuja ni un carater, ni un numero, ni
 * nada que cruce la pagina fuera del elemento apuntado.
 */

// Zonas donde manda el navegador y esta luz se apaga.
const NATIVE_ZONE = '.gallery-track, a[target="_blank"], p, li, dd, dt, figcaption, blockquote';
// Pulsables que esta luz ilumina. El enlace externo queda fuera aposta.
const PRESSABLE = 'button, a[href]:not([target="_blank"])';

// Suavizado de la POTENCIA, no de la posicion. La posicion del puntero se
// escribe sin suavizar: un cursor con inercia miente sobre donde esta el
// raton, y en creditos hay 23 dianas contiguas donde eso se lee como retraso.
const POT_SMOOTHING = 0.22;

// Radio del charco. Lo dicta la altura del elemento, no la seccion: asi una
// fila de creditos de 35px y un titular de 74px reciben la misma ley y se ven
// distintos sin que nadie programe casos por seccion.
const RADIO_FACTOR = 2.4;
const RADIO_MINIMO = 120;
const RADIO_PULSADO = 1.25;

// La mano.
const PUNTO_REPOSO = 3.2;
const PUNTO_PULSADO = 2.4;

// El DPR se acota: por encima de 2 el coste de pintado sube sin que se note.
const DPR_MAXIMO = 2;

export function mountHyprCursor(host: HTMLElement): HyprCursorHandle {
  const controller = new AbortController();
  const { signal } = controller;

  // Dos lienzos, no uno: el de abajo (`hueco`, z-index -4, debajo del
  // contenido) oscurece el fondo detras de las letras sin tocarlas. El de
  // arriba (`canvas`, z-index 70, el de siempre) se queda solo con el punto
  // de la mano y el filete del canto. Invertir el signo del efecto (oscurecer
  // en vez de aclarar) es lo que resuelve el conflicto con AA de raiz: ver
  // cabecera del modulo.
  const hueco = document.createElement("canvas");
  hueco.className = "hypr-cursor-hueco";
  hueco.setAttribute("aria-hidden", "true");
  const huecoCtx = hueco.getContext("2d");

  const canvas = document.createElement("canvas");
  canvas.className = "hypr-cursor-canvas";
  canvas.setAttribute("aria-hidden", "true");
  const ctx = canvas.getContext("2d");
  // defensive: sin los DOS contextos 2D no hay dispositivo posible. Se sale
  // sin montar ninguno de los dos lienzos y sin poner la clase, asi que el
  // cursor del sistema queda intacto.
  if (!ctx || !huecoCtx) {
    return { destroy: (): void => undefined };
  }
  host.append(hueco, canvas);

  let pointerX = 0;
  let pointerY = 0;
  let visible = false;
  let onNative = false;
  let pressable: HTMLElement | null = null;
  let rect: DOMRect | null = null;
  let pressed = false;
  let stale = false;
  let pot = 0;
  let frame = 0;
  let dpr = 1;

  // Diana que hoy pinta el hueco con su propio `background-image` en vez del
  // lienzo -4. Solo una a la vez, atada a `pressable`: se decide en
  // `resolveZone` (Paso 1 de la Task 9) y se sostiene hasta que la diana
  // cambie, nunca por fotograma.
  let imagenDiana: HTMLElement | null = null;
  let imagenPrevio = "";
  // Interruptor SOLO de verificacion (consumido por `__hyprCursor__.medirImagen()`
  // mas abajo): con esto en `true`, `tick()` deja de reescribir el
  // `background-image` de `imagenDiana` en cada fotograma. Necesario porque el
  // arnes ya no puede conmutar el efecto ocultando un lienzo -- en la diana
  // ocluida el efecto ES el `background-image` de la propia diana, y sin este
  // interruptor cualquier intento del arnes de "apagarlo" perderia la carrera
  // contra el propio `requestAnimationFrame` del modulo, que lo repintaria en
  // el fotograma siguiente. Nunca lo activa nada de la pagina real.
  let suspenderImagen = false;

  const resize = (): void => {
    dpr = Math.min(window.devicePixelRatio || 1, DPR_MAXIMO);
    const w = Math.floor(window.innerWidth * dpr);
    const h = Math.floor(window.innerHeight * dpr);
    canvas.width = w;
    canvas.height = h;
    canvas.style.width = `${window.innerWidth}px`;
    canvas.style.height = `${window.innerHeight}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    hueco.width = w;
    hueco.height = h;
    hueco.style.width = `${window.innerWidth}px`;
    hueco.style.height = `${window.innerHeight}px`;
    huecoCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  resize();

  /*
   * Mecanismo hibrido (Task 9). El lienzo -4 vive DEBAJO del contenido pero
   * TAMBIEN debajo de cualquier fondo opaco propio de la diana o de un
   * ancestro suyo (una fila de creditos con rejilla al 78%, una fila de
   * indice con `--shot-fondo` solido): ahi el hueco queda tapado y el
   * dispositivo degrada a un filete de 1px. La causa decide el mecanismo, no
   * una lista de selectores -- una lista se desactualiza en cuanto cambia el
   * marcado de una seccion.
   *
   * `background-image` de un elemento se pinta por ENCIMA de su propio
   * `background-color` y por DEBAJO de su texto: es exactamente el mismo
   * hueco, pintado en la capa que ya gana sobre cualquier fondo opaco propio
   * o heredado. Atraviesa la oclusion sin tocar el aspecto de la seccion.
   *
   * No sirve para `.obra-abrir`: es un boton transparente `position:
   * absolute; inset: 0` cuyo titular visible es un HERMANO de debajo (el
   * `<h2 data-title>`), no un descendiente. Pintarle background-image al
   * boton no ilumina nada que se vea -- el titular esta en otro nodo. Ahi
   * sigue mandando el lienzo -4, y de hecho no hace falta: nada opaco se
   * interpone entre `.obra-abrir`/su titular y el lienzo (pinta directo
   * sobre el shader), asi que `hayOclusion()` devuelve false y el lienzo
   * sigue siendo el mecanismo elegido.
   *
   * Verificado en el codigo real de este repo (no supuesto): ninguna de las
   * dianas ocluidas de hoy (`.credit`, `.scene-index-row`) trae su propio
   * `background-image` en CSS -- solo `background-color`/`background`
   * solido. Por eso "guardar el valor en linea previo y restaurar quitando
   * la propiedad" (mas abajo) no tiene hoy ningun caso real que pisar; se
   * implementa igual porque es la unica forma correcta de no romper una
   * diana futura que si trajera imagen propia.
   */
  /*
   * `getComputedStyle(...).backgroundColor` no siempre serializa como
   * `rgb()`/`rgba()`. Un `background: color-mix(in srgb, var(--void) 78%,
   * transparent)` (el scrim de `.credits-grid`, medido) resuelve como
   * `color(srgb 0.043 0.016 0.016 / 0.78)` -- sintaxis CSS Color 4, sin
   * "rgba" en ningun sitio. Un regex anclado a `rgba?\(` no la reconoce,
   * devuelve "no opaco" por defecto, y ESTA es justo la diana que este
   * modulo existe para atravesar: sin este caso, `.credit` (ocluida por
   * ese mismo scrim) se queda con el lienzo -4, que sigue tapado. Medido
   * en el arnes: `mecanismo()` daba "lienzo" en vez de "imagen" para
   * ".credit" antes de esta correccion.
   *
   * La regla general: si el color trae un canal alfa, viene marcado con
   * una barra al final (`.../ 0.78)`, sea cual sea la funcion de color
   * (`rgb`, `hsl`, `color`, `lab`...), o como cuarto argumento separado
   * por comas en la sintaxis clasica `rgba(r, g, b, a)`. Sin ninguna de
   * las dos marcas, el color no tiene canal alfa y es opaco por
   * definicion (`rgb(7, 3, 2)`, `hsl(0 0% 0%)`).
   */
  const ALFA_CON_BARRA_RE = /\/\s*([\d.]+)\s*\)\s*$/;
  const ALFA_RGBA_CLASICO_RE = /^rgba\(\s*[\d.]+[,\s]+[\d.]+[,\s]+[\d.]+[,\s]+([\d.]+)\s*\)$/;
  const colorOpaco = (color: string): boolean => {
    if (!color || color === "transparent") return false;
    const conBarra = ALFA_CON_BARRA_RE.exec(color);
    if (conBarra) return parseFloat(conBarra[1]) > 0;
    const rgbaClasico = ALFA_RGBA_CLASICO_RE.exec(color);
    if (rgbaClasico) return parseFloat(rgbaClasico[1]) > 0;
    return true;
  };

  // Lectura de estilo cara (`getComputedStyle` por cada ancestro): SOLO se
  // llama al resolver una diana nueva, nunca por fotograma (Paso 1).
  const hayOclusion = (nodo: HTMLElement): boolean => {
    let actual: HTMLElement | null = nodo;
    while (actual) {
      if (colorOpaco(getComputedStyle(actual).backgroundColor)) return true;
      if (actual === document.body) return false;
      actual = actual.parentElement;
    }
    return false;
  };

  // Devuelve la diana con `background-image` propio a su estado previo.
  // Quita la propiedad en vez de ponerla a `none`: un `none` en linea
  // pisaria un `background-image` que viniera del CSS de la propia diana.
  const restaurarImagen = (): void => {
    if (!imagenDiana) return;
    if (imagenPrevio) {
      imagenDiana.style.backgroundImage = imagenPrevio;
    } else {
      imagenDiana.style.removeProperty("background-image");
    }
    imagenDiana = null;
    imagenPrevio = "";
  };

  /*
   * `closest()` con los dos selectores a la vez devuelve el ancestro-o-el-
   * propio-nodo MAS CERCANO que matchee cualquiera de los dos, no el primero
   * de la lista: el mas cercano gana con independencia del orden en que se
   * escriban. Antes se resolvia NATIVE_ZONE primero y PRESSABLE solo si no
   * habia zona nativa, así que un boton pulsable ANIDADO dentro de un `p`
   * (`.credit-group-toggle` dentro de `.credit-group-label`, un `<p>`) caia
   * siempre del lado nativo: el `<p>` es zona nativa y `closest('p')` lo
   * encuentra sin mirar si hay un pulsable mas cerca del puntero. El CSS, en
   * cambio, ya le daba `cursor: none` a ese mismo boton por selector directo
   * — resultado: ni luz ni cursor del sistema sobre la diana. La zona la
   * decide quien esta MAS CERCA del puntero en el arbol, no una prioridad
   * fija por tipo de selector: si el pulsable es mas cercano (el puntero
   * esta sobre el boton, no sobre texto corrido suelto), gana el pulsable.
   */
  const resolveZone = (target: Element): void => {
    // Suelta la diana con imagen de la transicion anterior ANTES de decidir
    // la nueva: si la nueva diana tambien usa imagen, se recalcula limpia
    // (nunca se guarda el degradado propio como si fuera el valor previo).
    restaurarImagen();
    const zone = target.closest<HTMLElement>(`${PRESSABLE}, ${NATIVE_ZONE}`);
    const esPulsable = zone !== null && zone.matches(PRESSABLE);
    onNative = zone !== null && !esPulsable;
    pressable = esPulsable ? zone : null;
    rect = pressable ? pressable.getBoundingClientRect() : null;
    // Paso 1: la oclusion se lee UNA VEZ por diana nueva, no por fotograma.
    if (pressable && hayOclusion(pressable)) {
      imagenDiana = pressable;
      imagenPrevio = pressable.style.backgroundImage;
    }
  };

  const onMove = (event: PointerEvent): void => {
    if (event.pointerType !== "mouse") return;
    pointerX = event.clientX;
    pointerY = event.clientY;
    visible = true;
    if (stale) {
      stale = false;
      const under = document.elementFromPoint(pointerX, pointerY);
      // Fuera de la ventana devuelve null: ahi no hay zona que resolver.
      if (under) resolveZone(under);
    }
  };

  /*
   * El estado se resuelve en `pointerover`, no en `pointermove`: aquel solo
   * dispara al cambiar de elemento, asi que los `closest()` cuestan una vez
   * por transicion y no sesenta veces por segundo.
   */
  const onOver = (event: PointerEvent): void => {
    if (event.pointerType !== "mouse") return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    resolveZone(target);
  };

  /*
   * Al desplazar la pagina cambia el elemento bajo un raton QUIETO, y eso no
   * emite ningun evento de puntero: sin esto el charco se queda encendido en
   * una fila que ya no esta debajo. La comprobacion se aplaza al siguiente
   * movimiento en vez de hacerse en el propio evento, porque `scroll` llega
   * en rafagas.
   */
  const onScroll = (): void => {
    stale = true;
    if (pressable) rect = pressable.getBoundingClientRect();
  };

  const onLeave = (): void => {
    restaurarImagen();
    visible = false;
    pressable = null;
    rect = null;
    onNative = false;
  };

  const onDown = (): void => {
    pressed = true;
  };
  const onUp = (): void => {
    pressed = false;
  };

  window.addEventListener("pointermove", onMove, { passive: true, signal });
  window.addEventListener("pointerover", onOver, { passive: true, signal });
  window.addEventListener("pointerdown", onDown, { passive: true, signal });
  window.addEventListener("pointerup", onUp, { passive: true, signal });
  window.addEventListener("scroll", onScroll, { passive: true, signal });
  window.addEventListener("resize", resize, { passive: true, signal });
  document.addEventListener("pointerleave", onLeave, { passive: true, signal });

  const tick = (): void => {
    frame = window.requestAnimationFrame(tick);
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    huecoCtx.clearRect(0, 0, window.innerWidth, window.innerHeight);

    const on = visible && !onNative;
    const meta = on && pressable !== null ? 1 : 0;
    pot += (meta - pot) * POT_SMOOTHING;

    if (!on) return;

    // El rect se relee cada fotograma SOLO mientras hay diana: con el puntero
    // en reposo no se toca el layout.
    if (pressable) rect = pressable.getBoundingClientRect();

    if (pressable && rect && pot > 0.01) {
      const radio =
        Math.max(rect.height * RADIO_FACTOR, RADIO_MINIMO) * (pressed ? RADIO_PULSADO : 1);
      // Paso 3: un solo mecanismo activo por diana, nunca los dos.
      if (imagenDiana === pressable) {
        // Mismo centro, radio y rampa que el lienzo, escritos como
        // `radial-gradient` en linea. El centro va en coordenadas relativas
        // al elemento (`rect.left`/`rect.top` restados), porque
        // `background-image` posiciona contra la propia caja de la diana,
        // no contra el viewport.
        if (!suspenderImagen) {
          const cx = pointerX - rect.left;
          const cy = pointerY - rect.top;
          pressable.style.backgroundImage =
            `radial-gradient(circle at ${cx.toFixed(1)}px ${cy.toFixed(1)}px, ` +
            `rgb(11 4 4 / ${(0.88 * pot).toFixed(3)}) 0px, ` +
            `rgb(11 4 4 / ${(0.5 * pot).toFixed(3)}) ${(radio * 0.5).toFixed(1)}px, ` +
            `rgb(11 4 4 / 0) ${radio.toFixed(1)}px)`;
        }
      } else {
        // El recorte ES el canto: el hueco termina en el filo exacto del
        // elemento. Se pinta en el lienzo de ABAJO (-4), debajo del
        // contenido: oscurece el fondo detras de las letras sin tocar el
        // texto, asi que el contraste sube en vez de bajar.
        huecoCtx.save();
        huecoCtx.beginPath();
        huecoCtx.rect(rect.left, rect.top, rect.width, rect.height);
        huecoCtx.clip();
        const luz = huecoCtx.createRadialGradient(pointerX, pointerY, 0, pointerX, pointerY, radio);
        luz.addColorStop(0, `rgb(11 4 4 / ${(0.88 * pot).toFixed(3)})`);
        luz.addColorStop(0.5, `rgb(11 4 4 / ${(0.5 * pot).toFixed(3)})`);
        luz.addColorStop(1, "rgb(11 4 4 / 0)");
        huecoCtx.fillStyle = luz;
        huecoCtx.fillRect(rect.left, rect.top, rect.width, rect.height);
        huecoCtx.restore();
      }

      // El canto del elemento, encendido a la potencia del charco. Es lo que
      // delimita la zona pulsable. Se queda en el lienzo de ARRIBA: es
      // senal, no relleno, y necesita quedar por encima del contenido.
      ctx.strokeStyle = `rgb(255 90 52 / ${(0.85 * pot).toFixed(3)})`;
      ctx.lineWidth = 1;
      ctx.strokeRect(rect.left + 0.5, rect.top + 0.5, rect.width - 1, rect.height - 1);
    }

    // La mano. El anillo oscuro no es decoracion: garantiza contraste del
    // punto contra cualquier fotograma del shader sin depender del fondo.
    const r = pressed ? PUNTO_PULSADO : PUNTO_REPOSO;
    ctx.fillStyle = "#ffd9cc";
    ctx.beginPath();
    ctx.arc(pointerX, pointerY, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgb(11 4 4 / 0.9)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(pointerX, pointerY, r + 1, 0, Math.PI * 2);
    ctx.stroke();
  };

  frame = window.requestAnimationFrame(tick);

  // La clase solo se pone tras montar con exito: si este modulo no llega a
  // cargar o revienta antes, el CSS no oculta nada y el cursor del sistema
  // sigue intacto en toda la pagina.
  document.documentElement.classList.add("hypr-cursor-ready");

  const destroy = (): void => {
    window.cancelAnimationFrame(frame);
    controller.abort();
    // El `background-image` en linea de la diana ocluida es DOM ajeno al
    // lienzo: sin esto una diana se queda con el degradado pegado tras
    // salir, que es un fallo Critico (ver cabecera del modulo, Task 9).
    restaurarImagen();
    document.documentElement.classList.remove("hypr-cursor-ready");
    canvas.remove();
    hueco.remove();
    delete (window as unknown as { __hyprCursor__?: unknown }).__hyprCursor__;
  };

  // Sonda de verificacion: la consume scripts/measure-cursor-luz.py. No
  // afecta al render mientras nadie la llama.
  //
  // `mecanismo()` expone cual de los dos esta activo para la diana actual
  // (Task 9, Paso 4): el arnes lo necesita porque conmutar solo la
  // visibilidad de los lienzos ya no basta para medir el efecto en una diana
  // que usa `background-image` -- eso mediria cero y daria un falso
  // negativo.
  //
  // `medirImagen(oculto)` es el equivalente, para el mecanismo de imagen, de
  // ocultar/mostrar el lienzo: con `oculto=true` activa `suspenderImagen`
  // (tick() deja de repintar el degradado) Y ademas restaura de inmediato el
  // `background-image` previo de la diana, para que la captura "sin hueco"
  // vea el fondo real; con `oculto=false` desactiva el interruptor y deja
  // que `tick()` vuelva a pintar el degradado en el siguiente fotograma de
  // `requestAnimationFrame` -- el llamador tiene que esperar ese fotograma
  // (dos `requestAnimationFrame` anidados) antes de capturar "con hueco".
  (
    window as unknown as {
      __hyprCursor__?: {
        pot: () => number;
        mecanismo: () => "lienzo" | "imagen" | "ninguno";
        medirImagen: (oculto: boolean) => void;
        destroy: () => void;
      };
    }
  ).__hyprCursor__ = {
    pot: () => pot,
    mecanismo: () => (pressable === null ? "ninguno" : imagenDiana === pressable ? "imagen" : "lienzo"),
    medirImagen: (oculto: boolean): void => {
      suspenderImagen = oculto;
      if (oculto && imagenDiana) {
        if (imagenPrevio) {
          imagenDiana.style.backgroundImage = imagenPrevio;
        } else {
          imagenDiana.style.removeProperty("background-image");
        }
      }
    },
    destroy,
  };

  return { destroy };
}
