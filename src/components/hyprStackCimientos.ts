import { skillGroups } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { getIconMarkup } from "../utils/icons";

export interface HyprStackCimientosHandle {
  destroy: () => void;
}

/**
 * Los cimientos (spec 2026-09-09-hyprland-stack-cimientos): tres areas en
 * columnas sobre un suelo de brasa con los cinco lenguajes base. DOM propio
 * montado como HIJO de `.credits` (`[data-scene="credits"]` es la seccion
 * misma, no un contenedor distinto -- ver `src/sections/skills.ts`), hermano
 * de `.credits-grid` y del `<h2>` de la seccion; el generico (`.credits-grid`)
 * se oculta entero desde themes.css (patron B3/B4 de Caelestia).
 *
 * Sin GSAP: el disparo de la entrada es un IntersectionObserver anclado a la
 * caja del PROPIO dispositivo (top 80%), no a la seccion — con `is-lit` de
 * la seccion a `top 90%` la placa de "Quien soy" corria su montaje entero
 * 119px bajo el pliegue y nadie lo vio nunca (fallo 1 del repaso). Los
 * tiempos los marca el CSS.
 */
const ROTULO_SUELO = "Lenguajes base";

function construirNombre(name: string, slug: string, detail: string): HTMLButtonElement {
  // `elFromMarkup` devuelve un <div>, y un <div> dentro de un <button> (cuyo
  // modelo de contenido es contenido de frase) es invalido -- se envuelve en
  // un <span>, el mismo patron de `caelestiaCreditosBandeja.ts::construirPieza`
  // por este mismo motivo.
  const icono = el("span", "cim-icono", [elFromMarkup("", getIconMarkup(slug))]);
  icono.setAttribute("aria-hidden", "true");
  icono.setAttribute("data-decorative", "");
  const boton = el("button", "cim-nombre", [icono, el("span", "cim-txt", [name])]);
  boton.type = "button";
  boton.setAttribute("aria-pressed", "false");
  boton.dataset.cimNombre = name;
  boton.dataset.cimDetail = detail;
  return boton;
}

function construirLista(clase: string, items: ReadonlyArray<{ name: string; slug: string; detail: string }>): HTMLUListElement {
  return el(
    "ul",
    clase,
    items.map((it) => el("li", "", [construirNombre(it.name, it.slug, it.detail)])),
  );
}

export function mountHyprStackCimientos(root: HTMLElement): HyprStackCimientosHandle {
  const escena = root.querySelector<HTMLElement>('[data-scene="credits"]');
  if (!escena) return { destroy: () => undefined };

  const suelo = skillGroups.find((g) => g.label === ROTULO_SUELO);
  const areas = skillGroups.filter((g) => g.label !== ROTULO_SUELO);
  if (!suelo || areas.length !== 3) return { destroy: () => undefined };

  const columnas = areas.map((g, i) => {
    const col = el("section", "cim-col", [
      el("h3", "cim-rot", [g.label]),
      construirLista("cim-lista", g.items),
    ]);
    col.style.setProperty("--cim-c", String(i));
    return col;
  });

  const linea = el("span", "cim-linea", []);
  linea.setAttribute("aria-hidden", "true");
  const frase = el("p", "cim-frase", []);
  frase.setAttribute("aria-live", "polite");
  // `.cim-cab` se queda solo con el rotulo del suelo. La frase sube al aire
  // que ya existia entre el pie de las columnas y la linea y pasa a ser
  // HERMANA de `.cim-cols` y `.cim-suelo` (revision final de la rama: la
  // frase se leia bajo "LENGUAJES BASE" -- P0 de `lidia-naive-tester`, 78%
  // de las piezas segun `vera-art-director`).
  const cab = el("div", "cim-cab", [el("h3", "cim-rot", [suelo.label])]);
  const lenguajes = construirLista("cim-lenguajes", suelo.items);

  const cim = el("div", "cim", [
    el("div", "cim-cols", columnas),
    frase,
    el("div", "cim-suelo", [linea, cab, lenguajes]),
  ]);
  cim.setAttribute("data-cimientos", "");
  escena.append(cim);

  // El retardo de cada lenguaje sale de SU x real sobre el ancho del suelo:
  // la linea tarda 500ms en cruzar, y el nombre se enciende cuando la linea
  // llega a su columna. Se mide tras el append, con layout ya disponible.
  const anchoSuelo = lenguajes.getBoundingClientRect().width || 1;
  const izq = lenguajes.getBoundingClientRect().left;
  for (const boton of Array.from(lenguajes.querySelectorAll<HTMLElement>(".cim-nombre"))) {
    const x = boton.getBoundingClientRect().left - izq;
    boton.style.setProperty("--cim-d", `${Math.round((x / anchoSuelo) * 500)}ms`);
  }

  // Disparo anclado a la caja de los cimientos: top al 80% de la ventana.
  // `rootMargin` negativo abajo recorta el 20% inferior del viewport, asi que
  // "intersecta" equivale a "el borde superior ha cruzado el 80%". Con
  // movimiento reducido no hay entrada: el estado final se pone al montar.
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let observador: IntersectionObserver | null = null;
  if (reduce) {
    cim.classList.add("cimientos-lit");
  } else {
    observador = new IntersectionObserver(
      (entradas) => {
        if (entradas.some((e) => e.isIntersecting)) {
          cim.classList.add("cimientos-lit");
          observador?.disconnect();
          observador = null;
        }
      },
      { rootMargin: "0px 0px -20% 0px", threshold: 0 },
    );
    observador.observe(cim);
  }

  // El retardo `--cim-d` de la entrada solo hace falta la primera vez: sin
  // esta marca, soltar un lenguaje apuntado heredaria la transicion retardada
  // de la entrada y tardaria hasta medio segundo de mas en apagarse.
  const marcarEntrado = (ev: TransitionEvent): void => {
    // `transitionend` burbujea: `.cim-frase` tambien transiciona
    // `clip-path` (el recorte del apuntado), asi que sin `ev.target === cim`
    // cualquier apagado de una frase marcaria "entrado" de nuevo -- hoy
    // inalcanzable porque el listener se desconecta solo tras el primer
    // disparo real del propio `cim`, pero es gratis dejarlo explicito.
    if (ev.target === cim && ev.propertyName === "clip-path") cim.classList.add("cim-entrado");
  };
  cim.addEventListener("transitionend", marcarEntrado);
  if (reduce) cim.classList.add("cim-entrado");

  // El apuntado. Rozar (puntero) o dar foco escribe la frase; en tactil el
  // toque abre y el segundo toque sobre el mismo nombre cierra. `click` se
  // ignora cuando viene de raton: el hover ya lo ha hecho, y un toggle lo
  // cerraria. Un solo nombre encendido a la vez, y NUNCA se queda encendido
  // al salir: es el P0 del catastro.
  const botones = Array.from(cim.querySelectorAll<HTMLButtonElement>(".cim-nombre"));
  // Un solo nombre encendido en TODO el dispositivo (no por columna): el
  // raton gana al foco si compiten (ver `encender`, que apaga cualquier
  // otro `activo` antes de encender el nuevo).
  let activo: HTMLButtonElement | null = null;
  let ultimoPuntero = "mouse";

  // `is-viva` se anade a `cim` (no a `cab`): la frase ya no es descendiente
  // de `cab` -- es hermana de `.cim-cols`/`.cim-suelo`, asi que el ancla
  // comun mas cercana para el selector CSS (`.cim.is-viva .cim-frase`) es
  // el propio `cim`.
  const encender = (boton: HTMLButtonElement): void => {
    if (activo === boton) return;
    if (activo) activo.setAttribute("aria-pressed", "false");
    activo = boton;
    boton.setAttribute("aria-pressed", "true");
    frase.textContent = boton.dataset.cimDetail ?? "";
    cim.classList.add("is-viva");
  };
  const apagar = (): void => {
    if (!activo) return;
    activo.setAttribute("aria-pressed", "false");
    activo = null;
    cim.classList.remove("is-viva");
    // El texto se queda mientras la frase se retira por recorte y se vacia al
    // terminar la transicion. Con movimiento reducido no hay transicion ni
    // `transitionend`: se vacia en seco.
    if (reduce) frase.textContent = "";
  };
  const alTerminar = (ev: TransitionEvent): void => {
    if (ev.propertyName === "clip-path" && !cim.classList.contains("is-viva")) frase.textContent = "";
  };
  frase.addEventListener("transitionend", alTerminar);

  const escuchas: Array<() => void> = [];
  for (const boton of botones) {
    const entrar = (ev: PointerEvent): void => {
      if (ev.pointerType === "mouse") encender(boton);
    };
    // El foco de teclado (:focus-visible) SI enciende. El foco de un
    // puntero/toque NO: medido con una sonda temporal, el navegador enfoca
    // el boton durante el propio gesto de tap, ANTES del `click` — si
    // `foco` encendiera siempre, el primer toque quedaria ya activo cuando
    // `clic` decide, y su toggle ("si ya esta activo, apagar") lo apagaria
    // en el mismo tap en que debia abrir, desfasando el ciclo un toque para
    // siempre.
    const foco = (): void => {
      if (boton.matches(":focus-visible")) encender(boton);
    };
    const salir = (): void => apagar();
    // El foco perdido solo apaga si ESTE boton es el activo. Sin la guarda:
    // clic en A (foco en A) -> mover a B (pointerleave de A apaga, pointerenter
    // de B enciende B, activo = B) -> clic en B. El `pointerdown` del segundo
    // clic mueve el foco de A a B, asi que el `blur` de A dispara y
    // `apagar()` mata B, el nombre que esta bajo el cursor. Reproducido y
    // arreglado en la revision final de la rama (arreglo 1): un clic normal
    // despues del primero apagaba el nombre que el visitante tenia debajo
    // del puntero y vaciaba la frase hasta salir y volver a entrar.
    const desenfocar = (): void => {
      if (activo === boton) apagar();
    };
    // Igual que `entrar`, solo actua para raton: el touch no tiene hover
    // real y el navegador emite `pointerleave` al levantar el dedo, justo
    // ANTES del `click` (medido con la misma sonda) — sin la guarda, ese
    // pointerleave apagaba el nombre antes de que `clic` pudiera ver el
    // estado "ya activo", y el toggle nunca llegaba a cerrar por toque.
    const salirPointer = (ev: PointerEvent): void => {
      if (ev.pointerType === "mouse") salir();
    };
    const pulsar = (ev: PointerEvent): void => {
      ultimoPuntero = ev.pointerType;
    };
    // `detail === 0` es la senal del propio evento (no historia acumulada en
    // `ultimoPuntero`) para un `click` que viene de Enter/Espacio sobre un
    // <button>: el foco de teclado ya encendio el nombre, y este `click` no
    // tiene nada que hacer. Sin esto, un aparato hibrido que pasa de tactil a
    // teclado deja `ultimoPuntero` rancio en "touch", y una pulsacion normal
    // de Enter sobre un nombre recien encendido por Tab lo apagaba en el
    // acto (activo === boton -> salir()).
    const clic = (ev: MouseEvent): void => {
      if (ev.detail === 0) return;
      if (ultimoPuntero === "mouse") return;
      if (activo === boton) salir();
      else encender(boton);
    };
    boton.addEventListener("pointerenter", entrar);
    boton.addEventListener("pointerleave", salirPointer);
    boton.addEventListener("focus", foco);
    boton.addEventListener("blur", desenfocar);
    boton.addEventListener("pointerdown", pulsar);
    boton.addEventListener("click", clic);
    escuchas.push(() => {
      boton.removeEventListener("pointerenter", entrar);
      boton.removeEventListener("pointerleave", salirPointer);
      boton.removeEventListener("focus", foco);
      boton.removeEventListener("blur", desenfocar);
      boton.removeEventListener("pointerdown", pulsar);
      boton.removeEventListener("click", clic);
    });
  }

  return {
    destroy: () => {
      observador?.disconnect();
      cim.removeEventListener("transitionend", marcarEntrado);
      for (const off of escuchas) off();
      frase.removeEventListener("transitionend", alTerminar);
      cim.remove();
    },
  };
}
