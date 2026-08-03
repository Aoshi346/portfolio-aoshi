/**
 * Navegacion de escenas. Corte seco, decidido sobre la alternativa de un
 * desplazamiento de un segundo: la continuidad ya la da el scroll normal, y
 * quien usa el menu lo usa justamente porque no quiere recorrer el camino.
 *
 * Vive FUERA de `.cinema-chrome`: ese contenedor es `aria-hidden="true"` y una
 * navegacion escondida del arbol de accesibilidad no es una navegacion. Ademas
 * los tres temas la necesitan y el cromo de cine solo corre en Vice.
 */
interface NavTarget {
  id: string;
  label: string;
}

const TARGETS: NavTarget[] = [
  { id: "hero", label: "Título" },
  { id: "quien-es", label: "Quién es" },
  { id: "obra", label: "Obra" },
  { id: "creditos", label: "Créditos" },
  { id: "contacto", label: "Fundido" },
];

/*
 * El carril de obra se recorre en horizontal dentro de un pin. Su borde de
 * inicio deja la primera cartela a medio montar: el fotograma asentado esta en
 * u ~ 0,42 de los 6,25 que dura la timeline maestra. Se lee EN EL MOMENTO del
 * clic y nunca se cachea: el presupuesto del pin cambia con cada refresh de
 * ScrollTrigger.
 *
 * OBRA_TOTAL_U REIMPLEMENTA un dato de `vice.choreography.ts`: sale de
 * 4 * OBRA_TRANSIT + 5 * OBRA_REST. No se importa de alli a proposito — ese
 * modulo carga en diferido y solo en Vice, y traerlo aqui lo metaria en el
 * bundle de arranque de los tres temas. El precio de la copia es que puede
 * derivar, y derivada NO falla: el ancla de obra aterriza mal en silencio.
 * Por eso `scripts/measure-nav.py` recalcula la suma y compara antes de medir
 * nada. Si tocas OBRA_TRANSIT u OBRA_REST, el arnes te lo dira.
 */
const OBRA_SETTLED_U = 0.42;
const OBRA_TOTAL_U = 6.25;

function destinationFor(id: string): number | null {
  const target = document.getElementById(id);
  if (!target) return null;

  const top = target.getBoundingClientRect().top + window.scrollY;

  if (id === "obra") {
    // La altura del envoltorio menos una pantalla es el recorrido que el pin
    // reserva. Si el carril no esta fijado (Hyprland, Caelestia, movil) el
    // termino sale <= 0 y el destino es el borde, que es lo correcto ahi.
    const budget = Math.max(0, target.offsetHeight - window.innerHeight);
    return top + (OBRA_SETTLED_U / OBRA_TOTAL_U) * budget;
  }

  return top;
}

export function mountSceneNav(root: HTMLElement): { destroy: () => void } {
  const nav = document.createElement("nav");
  nav.className = "scene-nav";
  nav.setAttribute("aria-label", "Secciones");

  const list = document.createElement("ul");
  for (const target of TARGETS) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    // Ancla real en el href: sin JavaScript sigue navegando, y el navegador
    // la muestra al pasar por encima.
    link.href = `#${target.id}`;
    link.textContent = target.label;
    item.append(link);
    list.append(item);
  }
  nav.append(list);

  /*
   * UN solo punto de ejecucion del desplazamiento, delegado en el `ul`. Y
   * nunca se escribe `location.hash`: eso dispara el salto nativo del
   * navegador y competiria con este.
   */
  const onClick = (event: MouseEvent): void => {
    const link = (event.target as HTMLElement).closest<HTMLAnchorElement>("a[href^='#']");
    if (!link) return;
    const id = link.hash.slice(1);
    const destination = destinationFor(id);
    if (destination === null) return;

    event.preventDefault();
    /*
     * `behavior: "instant"` explicito. `html { scroll-behavior: smooth }` hace
     * que "auto" acabe resolviendo a suave, incluso con prefers-reduced-motion
     * puesto — que es justo el camino donde Lenis no existe para corregirlo.
     */
    window.scrollTo({ top: destination, behavior: "instant" });
    history.replaceState(null, "", `#${id}`);
  };

  list.addEventListener("click", onClick);
  root.append(nav);

  /*
   * El rail se aparta mientras la pagina se mueve, y solo en su forma de movil.
   *
   * Ahi va `fixed` sobre el pie, y las vias de contacto ocupan el ancho entero:
   * en tranquilo no se pisan (la ultima via reserva sitio), pero DURANTE el
   * scroll cualquiera de las cuatro cruza su banda. Medido barriendo el scroll
   * de la escena: en todos los offsets hay puntos dentro de una via donde el
   * toque se lo lleva un enlace del rail. Y al darle fondo propio para que se
   * leyera como capa aparte, paso a TAPAR el dato en vez de solaparlo — mejor
   * de entender y peor de ver.
   *
   * Interceptar es inherente a una capa fija sobre contenido que se mueve, asi
   * que no se arregla donde esta: se arregla cuando esta. Mientras el dedo
   * arrastra, el rail no pinta ni recibe toques; al detenerse vuelve. Que es el
   * momento exacto del fallo — soltar el dedo justo cuando el dato pasa por
   * detras.
   *
   * `pointer-events` es la mitad que importa: sin el, un rail invisible
   * seguiria robando el toque, que es el fallo entero.
   */
  // 1079: el mismo ancho al que el CSS lo pasa al pie y al que las vias de
  // contacto se apilan a sangre. Un numero, una decision.
  const movil = window.matchMedia("(max-width: 1079px)");
  let quieto: ReturnType<typeof setTimeout> | undefined;

  const onScroll = (): void => {
    if (!movil.matches) return;
    nav.classList.add("scene-nav--transito");
    clearTimeout(quieto);
    // 180 ms: por debajo parpadea entre gestos de un mismo arrastre; por
    // encima se nota que tarda en volver.
    quieto = setTimeout(() => nav.classList.remove("scene-nav--transito"), 180);
  };

  /*
   * `scroll` NO basta por si solo: se emite un fotograma DESPUES de que la
   * pagina empiece a moverse, y en ese fotograma el rail todavia esta encima
   * (medido: 52 puntos robados con solo `scroll`). `touchmove` es el gesto de
   * verdad en un movil y llega antes de que nada se mueva; `wheel` es su
   * equivalente con raton para poder medirlo en el arnes. Los tres apuntan al
   * mismo sitio: el que llegue primero aparta el rail.
   */
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("touchmove", onScroll, { passive: true });
  window.addEventListener("wheel", onScroll, { passive: true });

  // Sonda para scripts/measure-nav.py. No afecta al render.
  (window as unknown as { __navDestino__?: (id: string) => number | null }).__navDestino__ =
    destinationFor;

  return {
    destroy: () => {
      list.removeEventListener("click", onClick);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("touchmove", onScroll);
      window.removeEventListener("wheel", onScroll);
      clearTimeout(quieto);
      nav.remove();
      delete (window as unknown as { __navDestino__?: unknown }).__navDestino__;
    },
  };
}
