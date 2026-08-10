import type { Gsap } from "../themes/choreography";

export interface ObraCartelHandle {
  destroy: () => void;
}

interface Fila {
  seccion: HTMLElement;
  boton: HTMLButtonElement;
  /** una tira por letra: arriba la apagada, debajo la encendida */
  tiras: HTMLElement[];
  /** capa de entrada, independiente de la del relevo */
  entradas: HTMLElement[];
  mini: HTMLElement;
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
  gsap.registerPlugin(CustomEase);
  CustomEase.create("hard", "0.7,0,0.2,1");
  CustomEase.create("slow", "0.16,0.84,0.28,1");

  const secciones = Array.from(root.querySelectorAll<HTMLElement>('[data-scene="obra"]'));
  const filas: Fila[] = secciones.map((seccion) => partirTitulo(seccion));
  const finoPuntero = window.matchMedia("(hover: hover)").matches;
  const motionReducido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const sueltas: Array<() => void> = [];

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

  if (!motionReducido) entrada(gsap, root, filas);
  else asentar(gsap, filas);

  return {
    destroy(): void {
      for (const soltar of sueltas) soltar();
      gsap.killTweensOf(filas.flatMap((f) => [...f.tiras, ...f.entradas, f.mini]));
    },
  };
}

/** Convierte el texto del boton en una letra por mirilla, con su gemela. */
function partirTitulo(seccion: HTMLElement): Fila {
  const boton = seccion.querySelector<HTMLButtonElement>("[data-obra-abrir]");
  const titulo = seccion.querySelector<HTMLElement>("h2.display-lg");
  const mini = seccion.querySelector<HTMLElement>("[data-obra-mini]");
  if (!boton || !titulo || !mini) throw new Error("Fila de obra sin boton, titulo o miniatura");

  // Se parte el TITULAR, no el boton: el boton es un hermano vacio que solo
  // hace de disparador accesible (ver Task 1).
  const texto = titulo.textContent ?? "";
  titulo.textContent = "";
  for (const caracter of texto) {
    const mirilla = document.createElement("span");
    mirilla.className = "obra-ch";
    if (caracter === " ") {
      mirilla.classList.add("obra-ch-hueco");
      titulo.appendChild(mirilla);
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
    titulo.appendChild(mirilla);
  }
  // El texto partido deja de ser legible para un lector de pantalla: se le
  // devuelve entero por `aria-label`.
  boton.setAttribute("aria-label", `Mostrar ${texto}`);

  return {
    seccion,
    boton,
    tiras: Array.from(titulo.querySelectorAll<HTMLElement>(".obra-rl")),
    entradas: Array.from(titulo.querySelectorAll<HTMLElement>(".obra-en")),
    mini,
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

/**
 * Entrada: UNA barra de brasa cruza el cartel y todo lo demas cuelga de ella.
 * El retardo de cada letra no se escribe a mano: sale de su posicion x real,
 * asi que la barra atraviesa los cinco titulares a la vez, por columnas.
 */
function entrada(gsap: Gsap, root: HTMLElement, filas: Fila[]): void {
  const pista = root.querySelector<HTMLElement>("[data-obra-track]");
  if (!pista) return;
  const caja = pista.getBoundingClientRect();
  const ancho = caja.width || 1;

  const barra = document.createElement("i");
  barra.className = "obra-barrido";
  barra.setAttribute("aria-hidden", "true");
  pista.appendChild(barra);

  const tl = gsap.timeline({ onComplete: () => barra.remove() });
  tl.set(barra, { opacity: 1, x: 0 })
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
}

/** Con movimiento reducido el cartel esta tejido desde el primer fotograma. */
function asentar(gsap: Gsap, filas: Fila[]): void {
  for (const fila of filas) {
    gsap.set(fila.entradas, { yPercent: 0 });
    gsap.set(fila.mini, { clipPath: "inset(0 0 0 0)" });
  }
}
