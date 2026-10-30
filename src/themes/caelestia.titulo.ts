/**
 * La escena Titulo de Caelestia: lo que no se puede hacer con CSS.
 *
 * Spec: docs/superpowers/specs/2026-10-29-caelestia-titulo-nombre-design.md
 */
import type { Gsap } from "./choreography";

export interface EntradaHandle {
  destroy: () => void;
}

const NULO: EntradaHandle = { destroy: () => {} };

/**
 * Curva cubic-bezier(x1, y1, x2, y2) de CSS como funcion `t -> y` que GSAP
 * acepta en `ease`. No se usa CustomEase: es un plugin aparte que el proyecto
 * no registra, y asi la curva es IDENTICA a la de la maqueta aprobada (no una
 * aproximacion con un ease con nombre). Se resuelve x(s) = t con Newton y, si
 * la pendiente es casi plana, con biseccion.
 */
function bezier(x1: number, y1: number, x2: number, y2: number): (t: number) => number {
  const eje = (a: number, b: number, s: number): number =>
    3 * a * (1 - s) * (1 - s) * s + 3 * b * (1 - s) * s * s + s * s * s;
  const deriv = (a: number, b: number, s: number): number =>
    3 * a * (1 - s) * (1 - s) + 6 * (b - a) * (1 - s) * s + 3 * (1 - b) * s * s;
  return (t: number): number => {
    if (t <= 0) return 0;
    if (t >= 1) return 1;
    let s = t;
    for (let i = 0; i < 8; i++) {
      const err = eje(x1, x2, s) - t;
      if (Math.abs(err) < 1e-6) return eje(y1, y2, s);
      const d = deriv(x1, x2, s);
      if (Math.abs(d) < 1e-6) break;
      s -= err / d;
    }
    let lo = 0;
    let hi = 1;
    s = t;
    for (let i = 0; i < 24; i++) {
      const x = eje(x1, x2, s);
      if (Math.abs(x - t) < 1e-6) break;
      if (x < t) lo = s;
      else hi = s;
      s = (lo + hi) / 2;
    }
    return eje(y1, y2, s);
  };
}

// Los tres valores de la maqueta aprobada (variante B, Trazo).
const EASE_TRAZO = bezier(0.45, 0, 0.25, 1);
const EASE_RELLENO = bezier(0, 0, 0.58, 1); // CSS `ease-out`
const EASE_CORTE = bezier(0.7, 0, 0.2, 1);

const CLIP_CERRADO = "inset(0 100% 0 0)";
const CLIP_ABIERTO = "inset(0 0% 0 0)";

declare global {
  interface Window {
    /** Duraciones declaradas de la entrada (la lee el arnes; ver `montarEntrada`). */
    __CAE_ENTRADA__?: { duracion: number };
  }
}

/**
 * La entrada de la escena Titulo: el nombre se DIBUJA a trazo, en su sitio,
 * y luego el rol se corta de izquierda a derecha. Spec "La entrada: B · Trazo".
 *
 *   0 ms      cada glifo traza su contorno (`stroke-dashoffset` 1 -> 0, 760 ms),
 *             escalonado 55 ms por glifo de forma continua a lo largo de los 15
 *   1550 ms   el contorno se rellena: `fill-opacity` 0 -> 1 y `stroke-opacity`
 *             1 -> 0 en 420 ms
 *   2100 ms   el rol se descubre con `clip-path` inset(0 100% 0 0) -> inset(0)
 *             en 400 ms. Total 2,5 s.
 *
 * Los `path` llevan `pathLength="1"`, asi que el trazo se normaliza a 1 sin
 * medir nada. El DOM tiene TRES svg a la vez (uno de 15 glifos y dos de 5 + 10,
 * que el CSS muestra por ancho) y `--i` va de 0 a 14 continuo dentro de cada
 * juego: se anima el DOM entero con el mismo tiempo por `--i`, asi un cambio
 * de breakpoint a media o despues de la entrada nunca ensena un nombre vacio
 * o a medias.
 *
 * Las curvas son las `cubic-bezier` de la maqueta, resueltas por `bezier()`.
 * `gsap` llega por parametro (nunca se importa directo aqui).
 *
 * `window.__CAE_ENTRADA__.duracion` expone la duracion de la timeline para el
 * arnes (mismo patron que `__CONTENT_SHAPE__`): los tiempos declarados son
 * deterministas, el cronometro solo es una comprobacion con margen.
 *
 * `js-cae-entrada`: la pone `main.ts` ANTES del primer pintado (oculta con
 * `visibility: hidden` el dibujo del nombre y el rol, `themes.css`) y esta
 * funcion la retira en los TRES caminos de salida: sin las piezas minimas, con
 * movimiento reducido, y en el camino normal en cuanto ha escrito los estados
 * iniciales con `gsap.set` de forma sincrona -- nunca despues, o el nombre se
 * veria un fotograma ya relleno antes de partir de su estado inicial.
 */
export function montarEntrada(gsap: Gsap, root: HTMLElement): EntradaHandle {
  const descubrir = (): void => document.documentElement.classList.remove("js-cae-entrada");

  const hero = root.querySelector<HTMLElement>("#hero");
  const paths = hero ? Array.from(hero.querySelectorAll<SVGPathElement>(".cae-nombre-dib path")) : [];
  const rol = hero?.querySelector<HTMLElement>(".cae-rol") ?? null;
  if (paths.length === 0) {
    // Sin el dibujo no hay timeline que lo revele: si no se retira aqui, el
    // rol queda invisible hasta el timeout de 3s de main.ts.
    descubrir();
    return NULO;
  }

  // Movimiento reducido: sin timeline, salto directo al estado final.
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    gsap.set(paths, { strokeDasharray: 1, strokeDashoffset: 0, fillOpacity: 1, strokeOpacity: 0 });
    if (rol) gsap.set(rol, { clipPath: CLIP_ABIERTO });
    descubrir();
    return NULO;
  }

  // Estados iniciales, sincronos y antes de construir la timeline.
  gsap.set(paths, { strokeDasharray: 1, strokeDashoffset: 1, fillOpacity: 0, strokeOpacity: 1 });
  if (rol) gsap.set(rol, { clipPath: CLIP_CERRADO });
  descubrir();

  const indice = (path: SVGPathElement, posicion: number): number => {
    const crudo = Number.parseInt(path.style.getPropertyValue("--i"), 10);
    return Number.isNaN(crudo) ? posicion : crudo;
  };

  const tl = gsap.timeline();
  paths.forEach((path, k) => {
    tl.fromTo(
      path,
      { strokeDashoffset: 1 },
      { strokeDashoffset: 0, duration: 0.76, ease: EASE_TRAZO },
      indice(path, k) * 0.055,
    );
  });
  tl.fromTo(
    paths,
    { fillOpacity: 0, strokeOpacity: 1 },
    { fillOpacity: 1, strokeOpacity: 0, duration: 0.42, ease: EASE_RELLENO },
    1.55,
  );
  if (rol) {
    tl.fromTo(rol, { clipPath: CLIP_CERRADO }, { clipPath: CLIP_ABIERTO, duration: 0.4, ease: EASE_CORTE }, 2.1);
  }

  window.__CAE_ENTRADA__ = { duracion: tl.duration() };

  return {
    destroy: () => {
      tl.kill();
      gsap.set(paths, { strokeDashoffset: 0, fillOpacity: 1, strokeOpacity: 0 });
      if (rol) gsap.set(rol, { clipPath: CLIP_ABIERTO });
    },
  };
}

const ROCE_SELECTOR = ".cae-ws, .cae-dock-item";

/**
 * El roce: el fondo se aparta y el elemento se levanta un poco cuando el
 * puntero pasa por encima de un pulsable clave. Vive FUERA de la timeline de
 * `montarEntrada` — es un gesto continuo de interaccion, no de entrada.
 *
 * DELEGADO EN `document`, no un `addEventListener` por elemento. `.cae-ws`
 * (las pastillas de la barra) y `.cae-dock-item` NO cuelgan de `root` (el
 * `<main>` de esta coreografia): `mountCaelestiaShell` los cuelga de `#app`,
 * un hermano de `<main>`, y llega por su PROPIO `import()` dinamico en
 * `main.ts` — una carrera distinta a la de `caelestiaChoreography`, sin orden
 * garantizado entre las dos. Un `querySelectorAll(root)` snapshot tomado
 * aqui puede correr antes de que el shell exista todavia y se quedaria sin
 * pastillas ni dock para siempre. Delegar en `document` con `pointerover` /
 * `pointerout` (que SI burbujean — `pointerenter`/`pointerleave` no) evita la
 * carrera: no importa cuando aparezca el nodo, el oyente ya esta puesto.
 *
 * Sin `destroy()`: mismo patron que el resto de `caelestia.choreography.ts`
 * (ver su comentario final "Sin destroy() propio" — `Choreography` devuelve
 * `void` y ningun tema de este proyecto tiene mecanismo de limpieza).
 *
 * `prefers-reduced-motion`: SOLO de este gesto. El transform del carril de
 * workspaces (`caelestiaChoreography`) todavia no respeta la preferencia —
 * es un hueco previo, ya anotado como "Tarea 10" en el docstring de ese
 * fichero, y queda fuera de esta funcion a proposito. Pero el roce es codigo
 * nuevo de esta tarea, asi que se comprueba UNA VEZ al montar: si el visitante
 * pide movimiento reducido, ni siquiera se ponen los oyentes — no hay nada
 * que "desactivar" en cada evento, no hay fondo que apartar ni elemento que
 * levantar.
 */
export function montarRoce(gsap: Gsap, root: HTMLElement): void {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  let activo: HTMLElement | null = null;

  // Revision final (Importante 2): `.cae-dock-item` ya tiene su propio
  // `:hover { transform: translateY(-0.4375rem) }` en CSS (themes.css) y un
  // `transform` inline de GSAP gana SIEMPRE a una regla de hoja de estilos
  // (ver CLAUDE.md, Never-Do) — con el `gsap.to(el, {y:-2})` de aqui puesto
  // sobre el dock, el hover se quedaba en -2px en vez de los -7px del CSS
  // mientras el puntero seguia encima. El lienzo SI debe seguir apartandose
  // (eso no lo cubre ningun CSS), asi que solo se salta la mitad que levanta
  // el propio elemento cuando la diana es el dock.
  const esDock = (el: HTMLElement): boolean => el.matches(".cae-dock-item");

  const salirDe = (el: HTMLElement): void => {
    const lienzo = document.querySelector<HTMLCanvasElement>("canvas");
    // `clearProps: "transform"` (no solo x/y a 0) porque un `matrix(1, 0, 0,
    // 1, 0, 0)` no es lo mismo que "sin tocar": el lienzo debe volver al
    // `transform: none` de reposo, no a un identity matrix inline.
    if (lienzo) {
      gsap.to(lienzo, { x: 0, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
    }
    if (!esDock(el)) {
      gsap.to(el, { y: 0, duration: 0.3, ease: "power3.out", clearProps: "transform" });
    }
  };

  const entrarEn = (el: HTMLElement): void => {
    const lienzo = document.querySelector<HTMLCanvasElement>("canvas");
    if (!lienzo) return;
    const ventana = root.getBoundingClientRect();
    const r = el.getBoundingClientRect();
    const dx = (r.left + r.width / 2 - (ventana.left + ventana.width / 2)) / (ventana.width / 2);
    const dy = (r.top + r.height / 2 - (ventana.top + ventana.height / 2)) / (ventana.height / 2);
    gsap.to(lienzo, { x: -dx * 14, y: -dy * 10, duration: 0.7, ease: "power3.out" });
    if (!esDock(el)) {
      gsap.to(el, { y: -2, duration: 0.3, ease: "power3.out" });
    }
  };

  const alPasar = (evento: PointerEvent): void => {
    const diana =
      evento.target instanceof Element ? evento.target.closest<HTMLElement>(ROCE_SELECTOR) : null;
    if (diana === activo) return;
    if (activo) salirDe(activo);
    activo = diana;
    if (activo) entrarEn(activo);
  };

  // Si el puntero sale del documento entero (relatedTarget nulo) sin pasar
  // por otra diana, `alPasar` nunca se dispara para "apagar" el gesto:
  // segunda red, igual que `pg.mouse.move(2, 2)` en el arnes.
  const alSalirDelDocumento = (evento: PointerEvent): void => {
    if (evento.relatedTarget) return;
    if (activo) {
      salirDe(activo);
      activo = null;
    }
  };

  document.addEventListener("pointerover", alPasar);
  document.addEventListener("pointerout", alSalirDelDocumento);
}
