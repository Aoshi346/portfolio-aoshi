/**
 * Navegacion de escenas. Corte seco, decidido sobre la alternativa de un
 * desplazamiento de un segundo: la continuidad ya la da el scroll normal, y
 * quien usa el menu lo usa justamente porque no quiere recorrer el camino.
 *
 * Vive FUERA de `.cinema-chrome`: ese contenedor es `aria-hidden="true"` y una
 * navegacion escondida del arbol de accesibilidad no es una navegacion. Ademas
 * los tres temas la necesitan y el cromo de cine solo corre en Vice.
 */
import { TARGETS, destinationFor } from "./sceneNav.destino";

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
   * Disparador: vive FUERA de `.cinema-chrome` a proposito (ver cabecera del
   * fichero) y es quien dice ahora en que escena esta el visitante. Antes lo
   * hacia `.rail-now`, dentro del cromo — con `prefers-reduced-motion` ese
   * contenedor pasa a `display: none` y el rail queda en 0x0, dejando sin
   * indicador a quien pide movimiento reducido. Medido.
   */
  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.className = "scene-nav-trigger";
  trigger.setAttribute("aria-expanded", "false");
  trigger.setAttribute("aria-controls", "scene-index");
  trigger.setAttribute("aria-haspopup", "dialog");

  const triggerLabel = document.createElement("span");
  triggerLabel.className = "scene-nav-trigger-label";
  trigger.append(triggerLabel);

  /*
   * La cortinilla: panel a pantalla completa con el indice de las cinco
   * escenas. `id="scene-index"` porque el disparador ya apunta ahi via
   * `aria-controls`.
   */
  const panel = document.createElement("div");
  panel.className = "scene-index";
  panel.id = "scene-index";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-modal", "true");
  panel.setAttribute("aria-label", "Selección de escenas");

  const heading = document.createElement("p");
  heading.className = "scene-index-title";
  heading.textContent = "Selección de escenas";
  panel.append(heading);

  for (const [i, entry] of TARGETS.entries()) {
    const row = document.createElement("a");
    row.className = "scene-index-row";
    // Ancla real en el href: sin JavaScript sigue navegando.
    row.href = `#${entry.id}`;
    row.dataset.scene = entry.id;

    const num = document.createElement("span");
    num.className = "scene-index-num";
    num.textContent = String(i + 1).padStart(2, "0");

    const name = document.createElement("span");
    name.className = "scene-index-name";
    name.textContent = entry.label;

    const guide = document.createElement("span");
    guide.className = "scene-index-guide";
    guide.setAttribute("aria-hidden", "true"); // la guia es decorativa

    const blurb = document.createElement("span");
    blurb.className = "scene-index-blurb";
    blurb.textContent = entry.blurb;

    row.append(num, name, guide, blurb);
    panel.append(row);
  }

  let abierto = false;

  const setAbierto = (v: boolean): void => {
    abierto = v;
    panel.classList.toggle("is-open", v);
    trigger.setAttribute("aria-expanded", v ? "true" : "false");
  };

  const onTriggerClick = (): void => setAbierto(!abierto);
  trigger.addEventListener("click", onTriggerClick);

  const onPanelClick = (event: MouseEvent): void => {
    const row = (event.target as HTMLElement).closest<HTMLAnchorElement>("a[href^='#']");
    if (!row) return;
    const id = row.hash.slice(1);
    const destination = destinationFor(id);
    if (destination === null) return;
    event.preventDefault();
    setAbierto(false);
    // `instant` explicito: `html { scroll-behavior: smooth }` hace que "auto"
    // resuelva a suave incluso con prefers-reduced-motion puesto.
    window.scrollTo({ top: destination, behavior: "instant" });
    history.replaceState(null, "", `#${id}`);
  };
  panel.addEventListener("click", onPanelClick);

  /*
   * La escena "en curso" se mantiene por `IntersectionObserver`, no por la
   * coreografia de Vice: Hyprland y Caelestia no tienen coreografia que la
   * actualice, y el disparador vive en los tres temas.
   */
  const pinta = (i: number): void => {
    const n = String(i + 1).padStart(2, "0");
    triggerLabel.textContent = `${n} · ${TARGETS[i].label}`;
    panel.querySelectorAll<HTMLElement>(".scene-index-row").forEach((row, j) => {
      if (j === i) row.setAttribute("aria-current", "true");
      else row.removeAttribute("aria-current");
    });
  };
  pinta(0);

  // La escena "en curso" es la ultima cuyo borde superior ya cruzo el tercio
  // alto del viewport. Con `rootMargin` negativo arriba, una escena solo
  // cuenta como actual cuando de verdad esta ocupando la pantalla, no cuando
  // asoma.
  const observer = new IntersectionObserver(
    (entradas) => {
      for (const e of entradas) {
        if (!e.isIntersecting) continue;
        const i = TARGETS.findIndex((t) => t.id === e.target.id);
        if (i >= 0) pinta(i);
      }
    },
    { rootMargin: "-33% 0px -60% 0px", threshold: 0 },
  );
  for (const t of TARGETS) {
    const s = document.getElementById(t.id);
    if (s) observer.observe(s);
  }

  root.append(trigger);
  root.append(panel);

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
      trigger.removeEventListener("click", onTriggerClick);
      panel.removeEventListener("click", onPanelClick);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("touchmove", onScroll);
      window.removeEventListener("wheel", onScroll);
      clearTimeout(quieto);
      observer.disconnect();
      nav.remove();
      trigger.remove();
      panel.remove();
      delete (window as unknown as { __navDestino__?: unknown }).__navDestino__;
    },
  };
}
