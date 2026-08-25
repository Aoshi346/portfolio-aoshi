import type { Choreography } from "./choreography";

/**
 * La coreografia de Caelestia: las cinco escenas dejan de apilarse en vertical
 * y pasan a ser un carril horizontal de workspaces. Un espacio de trabajo no
 * se desplaza, se cambia — es el gesto que sostiene la metafora de escritorio.
 *
 * `root` YA ES el `<main>`: `reveal.ts` invoca `initScrollReveal(main, theme)`
 * y de ahi sale el `root` del contexto. Buscar un `main` descendiente devuelve
 * `null` y toda la coreografia se iria por un `return` temprano en silencio.
 * Por eso el carril es `root`, sin `querySelector`.
 *
 * El `data-cae-shell`, en cambio, va en `document.documentElement`: el CSS lo
 * selecciona como `:root[data-theme="caelestia"][data-cae-shell="workspaces"]`
 * y desde `<main>` no casaria con nada.
 *
 * El oyente del evento va tambien en `document.documentElement`. El shell lo
 * despacha sobre `#app` con `bubbles: true`, y `<main>` es HIJO de `#app`: los
 * eventos burbujean hacia arriba, nunca hacia abajo, asi que un oyente en el
 * propio carril no lo veria jamas.
 *
 * Lenis NO interviene aqui: `reveal.ts` solo lo monta para `motion.style ===
 * "cinematic"`, que es Vice. Ver la correccion del 2026-08-20 en el spec.
 *
 * ScrollTrigger tampoco: en Caelestia no hay pins. Se recibe en el contexto
 * porque el contrato es comun a los tres temas, y se usa solo para refrescar
 * al cambiar el tamano de la ventana.
 */
const DURACION = 0.52;
const CURVA = "power3.inOut";

export const caelestiaChoreography: Choreography = ({ gsap, ScrollTrigger, root }) => {
  const escenas = Array.from(root.children).filter(
    (nodo): nodo is HTMLElement => nodo instanceof HTMLElement,
  );
  if (escenas.length === 0) return;

  root.dataset.caeTrack = "";
  document.documentElement.dataset.caeShell = "workspaces";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let actual = 0;

  const irA = (indice: number): void => {
    const destino = Math.max(0, Math.min(indice, escenas.length - 1));
    // El extremo de partida es la posicion ACTUAL, capturada antes de
    // reasignarla: con origen igual a destino un `fromTo` no anima nada y el
    // carril saltaria de golpe siempre.
    const origen = actual;
    actual = destino;
    // fromTo con los dos extremos escritos a mano: `gsap.from` esta prohibido
    // en este proyecto y ya provoco tres regresiones reales.
    gsap.fromTo(
      root,
      { xPercent: -100 * origen },
      {
        xPercent: -100 * destino,
        duration: reduce ? 0 : DURACION,
        ease: CURVA,
        overwrite: "auto",
      },
    );
  };

  // Estado inicial explicito, sin leer el DOM.
  gsap.set(root, { xPercent: 0 });

  const alCambiar = (evento: Event): void => {
    if (!(evento instanceof CustomEvent)) return;
    const detalle: unknown = evento.detail;
    if (typeof detalle !== "object" || detalle === null || !("index" in detalle)) return;
    const indice = Number((detalle as { index: unknown }).index);
    if (!Number.isFinite(indice)) return;
    irA(indice);
  };
  document.documentElement.addEventListener("caelestia:workspace", alCambiar);

  const alRedimensionar = (): void => {
    gsap.set(root, { xPercent: -100 * actual });
    ScrollTrigger.refresh();
  };
  window.addEventListener("resize", alRedimensionar);

  /*
   * Sin `destroy()` propio: la coreografia se invoca una vez por carga y el
   * arbol muere con la pagina. Los oyentes van sobre `document.documentElement`
   * y `window`, que tienen el mismo ciclo de vida. Si esto deja de ser cierto
   * (navegacion sin recarga), hay que devolver un limpiador y llamarlo desde
   * `pagehide`.
   */
};
