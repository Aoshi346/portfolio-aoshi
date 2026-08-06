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
import { construirSilueta } from "./sceneNav.siluetas";

export function mountSceneNav(root: HTMLElement): { destroy: () => void } {
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

  /*
   * Marca decorativa: sin caja, el disparador y el resto de enlaces
   * subrayados del tema (email, creditos) se leian igual de "solo texto".
   * `aria-hidden` porque no aporta nada al arbol de accesibilidad — el
   * boton ya se anuncia via `aria-haspopup`/`aria-expanded` — y vacia de
   * estilo propio en Hyprland/Caelestia, que se quedan con su caja
   * compartida (ver themes.css).
   */
  const triggerMark = document.createElement("span");
  triggerMark.className = "scene-nav-trigger-mark";
  triggerMark.setAttribute("aria-hidden", "true");
  trigger.append(triggerMark);

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

  /*
   * La barra de luz del barrido de apertura. Solo Hyprland la usa (ver
   * themes.css, `display: none` de base). Va al final del panel para que
   * quede por encima de los fotogramas sin necesidad de z-index alto.
   */
  const bar = document.createElement("span");
  bar.className = "scene-index-bar";
  bar.setAttribute("aria-hidden", "true");

  for (const [i, entry] of TARGETS.entries()) {
    const row = document.createElement("a");
    row.className = "scene-index-row";
    /*
     * Ancla real en el href: sin JavaScript sigue navegando. Y el id va SOLO
     * ahi — nada de `dataset.scene`.
     *
     * `data-scene` es el atributo con el que este proyecto marca las escenas
     * de verdad, y ponerselo a las filas del indice las metia en ese conjunto
     * con dos consecuencias: heredaban `padding: calc(9rem + 6.5vh)` de la
     * regla `:root[data-theme="vice"] [data-scene]` —202,5px arriba y abajo,
     * medidos— con lo que cada fila pasaba a medir 405px de alto, las cinco no
     * cabian en la pantalla y la primera quedaba en `top: -545`, fuera de
     * viewport y sin poder pulsarse; y ademas la coreografia de Vice recorre
     * `[data-scene]` para saber en que escena esta, asi que se le colaban
     * cinco escenas fantasma.
     */
    row.href = `#${entry.id}`;

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

    /*
     * Silueta y golpe de luz: los añaden los tres temas y solo Hyprland les da
     * estilo (ver themes.css, `display: none` de base). Mismo patron que
     * `.scene-nav-trigger-mark`. `aria-hidden` en el envoltorio, no pieza a
     * pieza: la silueta es decorativa y ademas lleva fragmentos de copy
     * ("Aoshi Blanco Sanz", "Hablemos") que un lector de pantalla leeria
     * fuera de contexto y duplicados respecto al descriptor.
     */
    const shot = construirSilueta(entry.id);
    shot.setAttribute("aria-hidden", "true");

    const flash = document.createElement("span");
    flash.className = "scene-index-flash";
    flash.setAttribute("aria-hidden", "true");

    row.append(shot, flash, num, name, guide, blurb);
    panel.append(row);
  }

  let abierto = false;

  // Las filas del indice, recalculadas en cada uso: son un `Array.from` sobre
  // una NodeList viva, nunca una referencia guardada de antemano.
  const filas = (): HTMLAnchorElement[] =>
    Array.from(panel.querySelectorAll<HTMLAnchorElement>(".scene-index-row"));

  const setAbierto = (v: boolean): void => {
    abierto = v;
    panel.classList.toggle("is-open", v);
    trigger.setAttribute("aria-expanded", v ? "true" : "false");

    /*
     * Con la cortinilla abierta, la pagina no rueda por debajo.
     *
     * Se atrapo el tabulador y se dejo suelta la rueda, y el panel se declara
     * `aria-modal="true"`: medido, un `wheel` de 4000px con el menu abierto
     * desplazaba la pagina entera detras del telon, el `IntersectionObserver`
     * seguia corriendo, el resaltado ambar saltaba de la fila 01 a la 03 y el
     * disparador se reetiquetaba solo. Nadie habia navegado. Al cerrar
     * aparecias en un sitio distinto del que abriste, y los ScrollTrigger de
     * Vice —incluido el pin del carril de obra— corrian a ciegas.
     *
     * Dos cerrojos, porque hacen falta los dos. `overflow: hidden` para el
     * scroll nativo, y un aviso para Lenis: medido, `overflow` SOLO no para
     * nada cuando Lenis esta montado, porque Lenis escucha la rueda y llama a
     * `scrollTo` — el desplazamiento es programatico y `overflow` no lo ve.
     *
     * Va por evento y no importando Lenis aqui: vive dentro de
     * `initSmoothScroll` en `utils/reveal.ts`, carga en diferido y puede no
     * existir (movimiento reducido, o antes de que cargue). Un evento deja a
     * cada modulo con lo suyo, y si nadie escucha, el `overflow` hace de red.
     */
    document.documentElement.style.overflow = v ? "hidden" : "";
    window.dispatchEvent(new CustomEvent("scene-nav:toggle", { detail: { abierto: v } }));
    pinta(escenaActual);   // la etiqueta conmuta entre la escena y "Cerrar"

    if (v) filas()[0]?.focus();
    else trigger.focus();
  };

  const onTriggerClick = (): void => setAbierto(!abierto);
  trigger.addEventListener("click", onTriggerClick);

  /*
   * Foco atrapado: mientras la cortinilla esta abierta, tabular no debe
   * llevarte a la pagina que hay debajo, que esta tapada. Esc cierra y
   * devuelve el foco al disparador que la abrio.
   */
  const onKeydown = (event: KeyboardEvent): void => {
    if (!abierto) return;
    if (event.key === "Escape") {
      setAbierto(false);
      return;
    }
    if (event.key !== "Tab") return;
    const f = filas();
    if (f.length === 0) return;
    const i = f.indexOf(document.activeElement as HTMLAnchorElement);
    event.preventDefault();
    f[(i + (event.shiftKey ? -1 : 1) + f.length) % f.length].focus();
  };
  document.addEventListener("keydown", onKeydown);

  // Cerrar al pulsar fuera del panel y del disparador.
  const onDocClick = (event: MouseEvent): void => {
    if (!abierto) return;
    const t = event.target as HTMLElement;
    if (t.closest(".scene-index") || t.closest(".scene-nav-trigger")) return;
    setAbierto(false);
  };
  document.addEventListener("click", onDocClick);

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
  /** Ultima escena pintada, para poder volver a ella al cerrar la cortinilla. */
  let escenaActual = 0;

  const pinta = (i: number): void => {
    escenaActual = i;
    const n = String(i + 1).padStart(2, "0");
    /*
     * Con la cortinilla abierta el disparador es el boton de CERRAR, y tiene
     * que decirlo. Antes no cambiaba nada a la vista —misma caja, mismo borde,
     * misma etiqueta— y seguia diciendo en que escena estas, que es describir
     * donde te encuentras y no lo que va a pasar si lo pulsas. `aria-expanded`
     * conmutaba para el lector de pantalla; para el ojo, no conmutaba nada.
     */
    triggerLabel.textContent = abierto ? "Cerrar" : `${n} · ${TARGETS[i].label}`;
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

  panel.append(bar);

  root.append(trigger);
  root.append(panel);

  // Sonda para scripts/measure-nav.py. No afecta al render.
  (window as unknown as { __navDestino__?: (id: string) => number | null }).__navDestino__ =
    destinationFor;

  return {
    destroy: () => {
      trigger.removeEventListener("click", onTriggerClick);
      panel.removeEventListener("click", onPanelClick);
      document.removeEventListener("keydown", onKeydown);
      document.removeEventListener("click", onDocClick);
      observer.disconnect();
      trigger.remove();
      panel.remove();
      delete (window as unknown as { __navDestino__?: unknown }).__navDestino__;
    },
  };
}
