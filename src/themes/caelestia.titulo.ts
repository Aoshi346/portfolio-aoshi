/**
 * La escena Titulo de Caelestia: lo que no se puede hacer con CSS.
 *
 * Spec: docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md
 */
import type { Gsap } from "./choreography";

/**
 * Estira las lineas del titular hasta que todas midan lo mismo.
 *
 * DOS TRAMPAS, las dos pagadas ya:
 *
 * 1. Medir la caja del <span> NO es medir el texto. Los `.cae-ln` son de
 *    bloque: `getBoundingClientRect().width` devuelve el ancho del CONTENEDOR.
 *    Con esa medida las tres lineas salen del MISMO tamano y el bloque solo
 *    PARECE justificado. Hay que usar `Range` + `selectNodeContents`.
 *
 * 2. La medida comun no puede ser fija. Con esta frase las lineas son de 18, 24
 *    y 9 caracteres: forzarlas a una medida ancha dispara el alto de la ultima
 *    y se come el dock (medido: 400 px de bloque, -138 px de aire). Por eso el
 *    bucle estrecha la medida en pasos hasta que cabe.
 *
 * TERCERA TRAMPA, pagada al medir contra el arnes: `Math.round()` en el
 * tamano de fuente. Con lineas de 18/24/9 caracteres los tres tamanos salen
 * MUY distintos entre si (medido: 75 / 56 / 145 px) y el error de redondear a
 * entero es proporcional al tamano — 0.5 px de 56 pesa el triple, en
 * proporcion, que 0.5 px de 145. Sumados los tres, los anchos finales
 * quedaban a 7.9 px entre si (tope del arnes: 4 px). Sin redondear (tamano de
 * fuente fraccionario, que CSS acepta sin problema) el error baja a ~3 px.
 */
export function justificarTitular(root: HTMLElement, medida = 1080, altoMax = 250): void {
  const tit = root.querySelector<HTMLElement>(".cae-tit");
  if (!tit) return;
  const lineas = Array.from(tit.querySelectorAll<HTMLElement>(".cae-ln"));
  if (lineas.length === 0) return;

  const aplicar = (objetivo: number): void => {
    for (const linea of lineas) {
      linea.style.fontSize = "100px";
      const rango = document.createRange();
      rango.selectNodeContents(linea);
      const ancho = rango.getBoundingClientRect().width;
      if (ancho > 0) linea.style.fontSize = `${(objetivo / ancho) * 100}px`;
    }
  };

  let objetivo = medida;
  aplicar(objetivo);
  while (objetivo > 380 && tit.getBoundingClientRect().height > altoMax) {
    objetivo -= 30;
    aplicar(objetivo);
  }
}

export interface TituloHandle {
  destroy: () => void;
}

export function montarTitulo(root: HTMLElement): TituloHandle {
  const rejustificar = (): void => justificarTitular(root);

  // Las fuentes variables cargan despues del primer pintado: justificar antes
  // mide Georgia (el respaldo) y los tamanos salen mal.
  void document.fonts.ready.then(rejustificar);
  rejustificar();
  window.addEventListener("resize", rejustificar);

  return {
    destroy: () => window.removeEventListener("resize", rejustificar),
  };
}

export interface EntradaHandle {
  destroy: () => void;
}

const NULO: EntradaHandle = { destroy: () => {} };

/**
 * La entrada de escena: una terminal falsa teclea `whoami`, el nombre se
 * traza con los contornos reales de Fraunces (`caelestia.firma.ts`, mismos
 * ejes que el display), se rellena y aterriza sobre `.cae-firma`.
 *
 * Firma DISTINTA de `montarTitulo`: esta funcion SI recibe `gsap` (threaded
 * desde la coreografia, igual que en el resto de temas — `gsap` no se
 * importa directo en este fichero) porque construye una timeline. No hay que
 * unificar las dos firmas.
 *
 * SIN ESCALA DEL BASTIDOR. El companion de brainstorming dividia x/y/scale
 * por un factor `k` porque su ventana de previsualizacion iba con
 * `transform: scale()`. Aqui NO HAY escalado — `.cae-term`/`.cae-trazo-stage`
 * son `position: fixed` contra el viewport real, asi que las deltas de
 * `getBoundingClientRect()` se usan tal cual. Dividir por `k` aqui sacaria el
 * aterrizaje fuera de sitio.
 */
export function montarEntrada(gsap: Gsap, root: HTMLElement): EntradaHandle {
  const hero = root.querySelector<HTMLElement>("#hero");
  const term = hero?.querySelector<HTMLElement>(".cae-term") ?? null;
  const typed = hero?.querySelector<HTMLElement>(".cae-term-typed") ?? null;
  const cursor = hero?.querySelector<HTMLElement>(".cae-term-cursor") ?? null;
  const trazo = hero?.querySelector<SVGSVGElement>(".cae-trazo") ?? null;
  const firma = hero?.querySelector<HTMLElement>(".cae-firma") ?? null;
  const regla = hero?.querySelector<HTMLElement>(".cae-regla") ?? null;
  const meta = hero?.querySelector<HTMLElement>(".cae-meta") ?? null;
  const lineas = hero ? Array.from(hero.querySelectorAll<HTMLElement>(".cae-ln")) : [];
  const bloques = hero ? Array.from(hero.querySelectorAll<HTMLElement>(".cae-statcol > div")) : [];
  if (!term || !typed || !cursor || !trazo || !firma) return NULO;

  const paths = Array.from(trazo.querySelectorAll<SVGPathElement>("path"));

  // Movimiento reducido: sin timeline, salto directo al estado final. La
  // terminal desaparece del arbol visual (`display: none`, no solo
  // opacidad) y la firma queda puesta — es lo que comprueba
  // `scripts/measure-caelestia-titulo.py` (`entrada`).
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    gsap.set(term, { display: "none" });
    gsap.set(trazo, { opacity: 0 });
    gsap.set(firma, { opacity: 1 });
    return NULO;
  }

  gsap.set(firma, { opacity: 0 });
  for (const path of paths) {
    const longitud = path.getTotalLength();
    gsap.set(path, {
      strokeDasharray: longitud,
      strokeDashoffset: longitud,
      fillOpacity: 0,
      strokeOpacity: 1,
    });
  }

  const tl = gsap.timeline();

  // 1. La terminal aparece.
  tl.fromTo(term, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.26, ease: "power2.out" });

  // 2. Se escribe "whoami" caracter a caracter.
  const COMANDO = "whoami";
  const escritura = { i: 0 };
  tl.to(escritura, {
    i: COMANDO.length,
    duration: 0.46,
    ease: "none",
    onUpdate: () => {
      typed.textContent = COMANDO.slice(0, Math.round(escritura.i));
    },
  });

  // 3. El cursor parpadea.
  tl.to(cursor, { opacity: 0, duration: 0.14, repeat: 3, yoyo: true });

  // 4. El trazo: cada glifo dibuja su contorno.
  tl.to(paths, {
    strokeDashoffset: 0,
    duration: 0.52,
    ease: "power1.inOut",
    stagger: 0.045,
  });

  // 5. Relleno, con el trazo desvaneciendose a la vez.
  tl.to(paths, { fillOpacity: 1, duration: 0.3, stagger: 0.03, ease: "power1.out" }, "-=0.42");
  tl.to(paths, { strokeOpacity: 0, duration: 0.3 }, "<");

  // 6. La terminal se va.
  tl.to(term, { opacity: 0, y: -8, duration: 0.26, ease: "power2.in" }, "-=0.15");

  // 7. El aterrizaje: hay que medir en este instante, no antes (el layout de
  // .cae-firma depende de la justificacion del titular, que ya corrio, pero
  // medir fuera del callback capturaria el rect de ANTES de que el trazo
  // llegue a este punto de la timeline).
  tl.add(() => {
    const a = trazo.getBoundingClientRect();
    const b = firma.getBoundingClientRect();
    gsap.to(trazo, {
      x: b.left + b.width / 2 - (a.left + a.width / 2),
      y: b.top + b.height / 2 - (a.top + a.height / 2),
      scale: b.width / a.width,
      duration: 0.66,
      ease: "power3.inOut",
    });
    gsap.to(trazo, { opacity: 0, duration: 0.2, delay: 0.54, ease: "power2.in" });
    gsap.to(firma, { opacity: 1, duration: 0.2, delay: 0.56, ease: "power2.out" });
  });

  // 8. La regla se abre y la meta entra detras de ella.
  if (regla) tl.fromTo(regla, { scaleX: 0 }, { scaleX: 1, duration: 0.4, ease: "power3.out" });
  if (meta) {
    tl.fromTo(
      meta,
      { opacity: 0, x: -8 },
      { opacity: 1, x: 0, duration: 0.4, ease: "power3.out" },
      regla ? "<" : undefined,
    );
  }

  // 9. Barrido de tinta: cada linea del titular se descubre de izquierda a
  // derecha, como si se pasara un pincel.
  if (lineas.length > 0) {
    tl.fromTo(
      lineas,
      { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0% 0 0)", duration: 0.72, ease: "power2.inOut", stagger: 0.11 },
    );
  }

  // 10. Volteo de las cifras: cada bloque cae de boca abajo, en el eje X, con
  // perspectiva propia para que se note el giro.
  if (bloques.length > 0) {
    gsap.set(bloques, { transformPerspective: 600 });
    tl.fromTo(
      bloques,
      { opacity: 0, rotateX: -82, y: 6 },
      { opacity: 1, rotateX: 0, y: 0, duration: 0.6, ease: "power3.out", stagger: 0.09 },
    );
  }

  return {
    destroy: () => tl.kill(),
  };
}

const ROCE_SELECTOR = ".cae-widget, .cae-statcol > div, .cae-ws, .cae-dock-item";

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

  const salirDe = (el: HTMLElement): void => {
    const lienzo = document.querySelector<HTMLCanvasElement>("canvas");
    // `clearProps: "transform"` (no solo x/y a 0) porque un `matrix(1, 0, 0,
    // 1, 0, 0)` no es lo mismo que "sin tocar": el lienzo debe volver al
    // `transform: none` de reposo, no a un identity matrix inline.
    if (lienzo) {
      gsap.to(lienzo, { x: 0, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
    }
    gsap.to(el, { y: 0, duration: 0.3, ease: "power3.out", clearProps: "transform" });
  };

  const entrarEn = (el: HTMLElement): void => {
    const lienzo = document.querySelector<HTMLCanvasElement>("canvas");
    if (!lienzo) return;
    const ventana = root.getBoundingClientRect();
    const r = el.getBoundingClientRect();
    const dx = (r.left + r.width / 2 - (ventana.left + ventana.width / 2)) / (ventana.width / 2);
    const dy = (r.top + r.height / 2 - (ventana.top + ventana.height / 2)) / (ventana.height / 2);
    gsap.to(lienzo, { x: -dx * 14, y: -dy * 10, duration: 0.7, ease: "power3.out" });
    gsap.to(el, { y: -2, duration: 0.3, ease: "power3.out" });
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
