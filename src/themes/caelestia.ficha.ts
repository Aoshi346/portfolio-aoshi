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
    const ancho = anchoDelTexto();

    if (reduce) {
      // Escena montada, sin recorrido. La regla del repo.
      gsap.set(grupos, { opacity: 1, x: 0, scale: 1, clearProps: "transform" });
      gsap.set([...filas, ...tonos], { opacity: 1, x: 0, scaleX: 1, clearProps: "transform" });
      gsap.set(nombre, { clipPath: "inset(0 0% 0 0)" });
      comando.textContent = COMANDO;
      cursor.style.opacity = "0";
      regla.style.width = `${ancho}px`;
      return;
    }

    const cuenta = { i: 0 };
    // fromTo con los dos extremos escritos a mano: `gsap.from` esta prohibido.
    const tl = gsap.timeline({
      onComplete: () => {
        latido = gsap.fromTo(
          cursorFinal,
          { opacity: 1 },
          { opacity: 0, duration: 0.55, repeat: -1, yoyo: true, ease: "none" },
        );
      },
    });
    gsap.set(nombre, { clipPath: "inset(0 100% 0 0)" });
    gsap.set(grupos, { opacity: 0 });
    gsap.set(filas, { opacity: 0, x: -6 });
    gsap.set(tonos, { opacity: 0, scaleX: 0.2 });
    regla.style.width = "0px";
    comando.textContent = "";

    tl.fromTo(cursor, { opacity: 1 },
      { opacity: 0, duration: 0.085, repeat: 3, yoyo: true, ease: "none" }, 0);
    tl.to(cuenta, {
      i: COMANDO.length, duration: 0.44, ease: "none",
      onUpdate: () => { comando.textContent = COMANDO.slice(0, Math.round(cuenta.i)); },
    }, 0.34);
    tl.fromTo(cursor, { opacity: 1 },
      { opacity: 0.2, duration: 0.04, yoyo: true, repeat: 1, ease: "power1.inOut" }, 0.78);
    tl.fromTo(grupos[0] ?? ficha, { opacity: 0, scale: 1.06 },
      { opacity: 1, scale: 1, duration: 0.55, ease: "power2.out" }, 0.86);
    tl.set(grupos[1] ?? ficha, { opacity: 1 }, 1.05);
    // El barrido de tinta: el mismo gesto que el titular de B1. Es lo que ata
    // las dos escenas.
    tl.fromTo(nombre, { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0% 0 0)", duration: 0.72, ease: "power2.inOut" }, 1.05);
    tl.to(cursor, { opacity: 0, duration: 0.2 }, 1.05);
    tl.fromTo(grupos[2] ?? ficha, { opacity: 0, x: -6 },
      { opacity: 1, x: 0, duration: 0.28, ease: "power2.out" }, 1.45);
    tl.fromTo(regla, { width: 0 },
      { width: ancho, duration: 0.42, ease: "power2.inOut" }, 1.6);
    tl.fromTo(grupos.slice(3), { opacity: 0 },
      { opacity: 1, duration: 0.22, ease: "power2.out" }, 1.85);
    tl.fromTo(filas, { opacity: 0, x: -6 },
      { opacity: 1, x: 0, duration: 0.22, ease: "power2.out", stagger: 0.07 }, 1.85);
    tl.to(tonos, { opacity: 1, scaleX: 1, duration: 0.18, ease: "power2.out", stagger: 0.035 }, 2.45);

    linea = tl;
  };

  /*
   * El filete se remide al redimensionar: el ancho del texto cambia con el
   * tamano de fuente, y un filete congelado en el ancho de otra ventana miente
   * justo sobre lo que viene a decir.
   */
  const alRedimensionar = (): void => {
    if (!linea || !linea.isActive()) regla.style.width = `${anchoDelTexto()}px`;
  };
  window.addEventListener("resize", alRedimensionar);
  limpiadores.push(() => window.removeEventListener("resize", alRedimensionar));

  return {
    reproducir,
    destroy: () => {
      if (linea) linea.kill();
      if (latido) latido.kill();
      for (const limpiar of limpiadores) limpiar();
    },
  };
}
