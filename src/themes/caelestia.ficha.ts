import type { Gsap } from "./choreography";

/**
 * Lo unico de la ficha de «Quien soy» que el CSS no puede hacer: medir el
 * filete, escribir el comando y ponerle rotulo a la tira de color.
 *
 * Vive aparte de `caelestia.choreography.ts` a proposito: la coreografia
 * gobierna el carril de workspaces y no tiene por que saber que hay dentro de
 * cada ventana. Aqui no se toca el carril.
 *
 * El `gsap` llega SIEMPRE por parametro, desde el contexto de la coreografia.
 * Un `import gsap from "gsap"` suelto compila, pasa el linter y revienta en el
 * navegador: le paso a Hyprland y su coreografia no corrio durante semanas.
 */

export interface FichaHandle {
  destroy: () => void;
  reproducir: () => void;
}

const COMANDO = "neofetch";

export function montarFicha(gsap: Gsap, escena: HTMLElement): FichaHandle | null {
  const ficha = escena.querySelector<HTMLElement>('[data-ficha="neofetch"]');
  if (!ficha) return null;

  const comando = ficha.querySelector<HTMLElement>("[data-ficha-cmd]");
  const cursor = ficha.querySelector<HTMLElement>("[data-ficha-cursor]");
  const cursorFinal = ficha.querySelector<HTMLElement>("[data-ficha-prompt]");
  const host = ficha.querySelector<HTMLElement>("[data-ficha-host]");
  const regla = ficha.querySelector<HTMLElement>("[data-ficha-regla]");
  const nombre = ficha.querySelector<HTMLElement>("[data-ficha-nombre]");
  const rotulo = ficha.querySelector<HTMLElement>(".ficha-rotulo");
  const grupos = Array.from(ficha.querySelectorAll<HTMLElement>("[data-ficha-grupo]"));
  const filas = Array.from(ficha.querySelectorAll<HTMLElement>("[data-ficha-fila]"));
  const tonos = Array.from(ficha.querySelectorAll<HTMLElement>("[data-ficha-tono]"));

  if (!comando || !cursor || !cursorFinal || !host || !regla || !nombre) return null;

  const limpiadores: (() => void)[] = [];
  // Los tipos salen del propio `gsap` que llega por parametro: escribir
  // `gsap.core.Timeline` aqui referencia el ESPACIO DE NOMBRES global y choca
  // con el parametro, que es un valor con el mismo nombre.
  let linea: ReturnType<Gsap["timeline"]> | null = null;
  let latido: ReturnType<Gsap["fromTo"]> | null = null;
  /*
   * Si la ficha ya esta PUESTA. No basta con mirar `linea`: antes de la
   * primera entrada es `null`, asi que una condicion `!linea || !linea.isActive()`
   * da verdadero con la escena aun sin abrir y pinta el filete por adelantado
   * (medido: un `resize` la llevaba de 0 a 249 sin haber pulsado nada). Y al
   * reves, bajo `prefers-reduced-motion` no hay timeline y la ficha SI esta
   * puesta. Solo una bandera propia dice la verdad en los dos casos.
   */
  let aterrizada = false;
  /** El modulo sigue vivo: corta las promesas en vuelo tras `destroy()`. */
  let vivo = true;

  /*
   * El filete del largo EXACTO del correo, como hace neofetch con
   * `usuario@host`. Se mide con Range: la caja del <a> devolveria el ancho del
   * contenedor, no el del texto. Es la trampa que B1 ya pago con su
   * justificacion.
   */
  const anchoDelTexto = (): number => {
    const rango = document.createRange();
    rango.selectNodeContents(host);
    return rango.getBoundingClientRect().width;
  };

  // La tira dice que token es y cuanto vale a esta hora. Solo al rozarla.
  for (const tono of tonos) {
    const alEntrar = (): void => {
      if (!rotulo) return;
      const token = tono.dataset.fichaTono ?? "";
      const valor = getComputedStyle(document.documentElement).getPropertyValue(token).trim();
      rotulo.textContent = `${token}  ${valor}`;
    };
    tono.addEventListener("mouseenter", alEntrar);
    limpiadores.push(() => tono.removeEventListener("mouseenter", alEntrar));
  }

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const reproducir = (): void => {
    if (linea) linea.kill();
    if (latido) latido.kill();
    latido = null;
    aterrizada = false;
    /*
     * El latido deja el cursor del prompt final en cualquier punto de su yoyo
     * (medido: 0.83). Matarlo NO restablece la opacidad, asi que sin esto una
     * entrada nueva corre 2,6 s con el cursor congelado en una opacidad
     * rancia que no significa nada.
     */
    gsap.set(cursorFinal, { opacity: 1 });
    const ancho = anchoDelTexto();

    if (reduce) {
      // Escena montada, sin recorrido. La regla del repo.
      gsap.set(grupos, { opacity: 1, x: 0, scale: 1, clearProps: "transform" });
      gsap.set([...filas, ...tonos], { opacity: 1, x: 0, scaleX: 1, clearProps: "transform" });
      gsap.set(nombre, { clipPath: "inset(0 0% 0 0)" });
      comando.textContent = COMANDO;
      cursor.style.opacity = "0";
      regla.style.width = `${ancho}px`;
      aterrizada = true;
      return;
    }

    /*
     * B6: si la escena esta en una columna (el retrato es pequeno porque no
     * pinta a su tamano de escritorio), la entrada conserva solo el tecleo;
     * las capas de grupos y filas aterrizan de golpe al terminar el comando.
     * Testigo: el ancho pintado de `ficha`, medido con `getClientRects` a
     * 1440x900 (1412px, la ventana real, no el viewport — ver
     * `docs/superpowers/specs/2026-09-07-caelestia-movil-design.md`) y a
     * 390x844 (362px): 700 cae limpio entre los dos.
     */
    const corto = (ficha.getClientRects()[0]?.width ?? 0) < 700;

    const cuenta = { i: 0 };
    // fromTo con los dos extremos escritos a mano: `gsap.from` esta prohibido.
    const tl = gsap.timeline({
      onComplete: () => {
        aterrizada = true;
        latido = gsap.fromTo(
          cursorFinal,
          { opacity: 1 },
          { opacity: 0, duration: 0.55, repeat: -1, yoyo: true, ease: "none" },
        );
      },
    });
    gsap.set(nombre, { clipPath: "inset(0 100% 0 0)" });
    regla.style.width = "0px";
    comando.textContent = "";

    if (corto) {
      // Columna estrecha: solo el tecleo y el barrido del nombre se ven. El
      // resto de la ficha aterriza de golpe al terminar el comando — no hay
      // sitio para capas secundarias por debajo de 900ms (regla del spec).
      gsap.set([...grupos, ...filas, ...tonos], {
        opacity: 1, x: 0, scale: 1, scaleX: 1, clearProps: "transform",
      });
    } else {
      gsap.set(grupos, { opacity: 0 });
      gsap.set(filas, { opacity: 0, x: -6 });
      gsap.set(tonos, { opacity: 0, scaleX: 0.2 });
    }

    /*
     * Los tiempos, por rama. El spec de B6 fija el techo de la version corta
     * en 900 ms DECLARADOS («un gesto por escena, por debajo de 900 ms»), y
     * la partitura de escritorio dura 2,02 s: no basta con quitarle capas,
     * hay que apretarla. Se conservan los dos gestos que el spec dice que
     * Quien soy mantiene —el tecleo y el barrido de tinta del nombre, que es
     * lo que ata esta escena con el titular de B1— y lo que cede es el
     * reposo entre ellos. Total declarado en corto: 0,86 s.
     *
     * No hay gate que mida esto: la duracion DECLARADA de una timeline no se
     * puede leer desde fuera de la pagina sin exponer el handle, y el
     * cronometro de esta sandbox no sirve de proxy (mide 351 ms para una
     * partitura de 2,02 s, por el hambre de fotogramas de swiftshader). Los
     * numeros de abajo son la fuente: si alguien los cambia, que rehaga esta
     * cuenta a mano.
     */
    const T = corto
      ? { parpadeo: 0.06, tecleo: 0.06, dTecleo: 0.3, guino: 0.36, salida: 0.4,
          dSalida: 0.12, barrido: 0.4, dBarrido: 0.36, filete: 0.58, dFilete: 0.28 }
      : { parpadeo: 0.085, tecleo: 0.34, dTecleo: 0.44, guino: 0.78, salida: 1.05,
          dSalida: 0.2, barrido: 1.05, dBarrido: 0.72, filete: 1.6, dFilete: 0.42 };

    tl.fromTo(cursor, { opacity: 1 },
      { opacity: 0, duration: T.parpadeo, repeat: 3, yoyo: true, ease: "none" }, 0);
    tl.to(cuenta, {
      i: COMANDO.length, duration: T.dTecleo, ease: "none",
      onUpdate: () => { comando.textContent = COMANDO.slice(0, Math.round(cuenta.i)); },
    }, T.tecleo);
    tl.fromTo(cursor, { opacity: 1 },
      { opacity: 0.2, duration: 0.04, yoyo: true, repeat: 1, ease: "power1.inOut" }, T.guino);
    tl.to(cursor, { opacity: 0, duration: T.dSalida }, T.salida);
    // El barrido de tinta: el mismo gesto que el titular de B1. Es lo que ata
    // las dos escenas. Se queda en las dos ramas: es EL gesto que Quien soy
    // conserva por debajo del corte (tabla de la seccion "Las entradas").
    tl.fromTo(nombre, { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0% 0 0)", duration: T.dBarrido, ease: "power2.inOut" }, T.barrido);
    tl.fromTo(regla, { width: 0 },
      { width: ancho, duration: T.dFilete, ease: "power2.inOut" }, T.filete);

    if (!corto) {
      tl.fromTo(grupos[0] ?? ficha, { opacity: 0, scale: 1.06 },
        { opacity: 1, scale: 1, duration: 0.55, ease: "power2.out" }, 0.86);
      tl.set(grupos[1] ?? ficha, { opacity: 1 }, 1.05);
      tl.fromTo(grupos[2] ?? ficha, { opacity: 0, x: -6 },
        { opacity: 1, x: 0, duration: 0.28, ease: "power2.out" }, 1.45);
      tl.fromTo(grupos.slice(3), { opacity: 0 },
        { opacity: 1, duration: 0.22, ease: "power2.out" }, 1.85);
      tl.fromTo(filas, { opacity: 0, x: -6 },
        { opacity: 1, x: 0, duration: 0.22, ease: "power2.out", stagger: 0.07 }, 1.85);
      tl.to(tonos, { opacity: 1, scaleX: 1, duration: 0.18, ease: "power2.out", stagger: 0.035 }, 2.45);
    }

    linea = tl;
  };

  /*
   * El filete se remide cuando el ancho del texto puede haber cambiado: el
   * ancho depende del tamano de fuente, y un filete congelado en la medida de
   * otra ventana miente justo sobre lo que viene a decir.
   *
   * Solo si la ficha ya esta aterrizada: durante la entrada el ancho lo
   * gobierna la timeline y escribirlo aqui la pisaria; antes de la entrada no
   * hay nada que remedir y pintarlo seria adelantar el gesto.
   */
  const remedirFilete = (): void => {
    if (aterrizada) regla.style.width = `${anchoDelTexto()}px`;
  };
  window.addEventListener("resize", remedirFilete);
  limpiadores.push(() => window.removeEventListener("resize", remedirFilete));

  /*
   * Y cuando aterriza la webfont. Martian Mono viene de Google Fonts: si llega
   * DESPUES de que el visitante abra «Quien soy» —red lenta, cache fria— el
   * filete se habria medido contra la fuente de reserva y se quedaria mintiendo
   * sobre el largo del correo, que es lo unico que promete no hacer.
   * `document.fonts.ready` no se puede desuscribir, de ahi la bandera `vivo`.
   */
  void document.fonts.ready.then(() => {
    if (vivo) remedirFilete();
  });

  return {
    reproducir,
    destroy: () => {
      vivo = false;
      if (linea) linea.kill();
      if (latido) latido.kill();
      for (const limpiar of limpiadores) limpiar();
    },
  };
}
