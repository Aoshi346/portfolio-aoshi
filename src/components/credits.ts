import { caseStudies, skillGroups, type SkillGroup } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { getIconMarkup } from "../utils/icons";

interface CreditEntry {
  role: string;
  name: string;
  slug: string;
  detail: string;
  /**
   * Proyectos de `caseStudies` cuyo `stack` incluye esta tecnologia. Es la
   * prueba de uso real, y sale de datos que ya estaban en `content.ts` sin
   * cruzar: ninguna cadena nueva. Se prefiere a una etiqueta de nivel
   * ("avanzado", "intermedio") porque dice DONDE se uso, que es verificable,
   * en vez de cuanto dice el autor que sabe, que no lo es.
   *
   * Si sale vacio, el bloque entero se oculta: cinco de las doce tecnologias
   * no aparecen en ningun proyecto publicado y rellenarlas con una frase
   * generica seria justo el tipo de relleno que el proyecto prohibe.
   */
  usedIn: string[];
}

const PANEL_ID = "credits-panel";

type Tier = "alto" | "medio" | "bajo";

function toEntry(role: string, item: SkillGroup["items"][number]): CreditEntry {
  return {
    role,
    name: item.name,
    slug: item.slug,
    detail: item.detail,
    // Se cruza contra `stack` Y `tooling`: Git, GitHub y las dos CLI de IA no
    // estan en el stack de ningun proyecto porque `stack` se pinta literal en
    // la ficha de obra y ahi cuatro nombres repetidos en los cinco proyectos
    // no distinguen nada. Sin este segundo array, esas cuatro tecnologias
    // saldrian como "sin proyecto publicado" siendo falso.
    usedIn: caseStudies
      .filter((project) => [...project.stack, ...(project.tooling ?? [])].includes(item.name))
      .map((project) => project.title),
  };
}

/*
 * El nivel sale del dato: en cuantas obras aparece la tecnologia, cruzando
 * `stack` Y `tooling` — el mismo cruce que ya hace `toEntry`.
 *
 * Se normaliza contra el maximo de SU PROPIA parcela, no contra un maximo
 * global. Con vara global las cinco herramientas caen a cero y un cuarto del
 * catastro queda apagado, cuando `tooling` existe precisamente porque Git,
 * GitHub y las dos CLI estan en TODOS los proyectos: medirlas contra `stack`
 * las declara vacias siendo lo contrario. Y comparar entre territorios nunca
 * fue el mensaje de esta escena.
 */
function tiersDeGrupo(group: SkillGroup): Map<string, Tier> {
  const cuenta = new Map<string, number>();
  for (const item of group.items) {
    cuenta.set(item.slug, toEntry(group.label, item).usedIn.length);
  }
  const max = Math.max(...cuenta.values());
  const tiers = new Map<string, Tier>();
  for (const [slug, n] of cuenta) {
    tiers.set(slug, n === 0 ? "bajo" : n === max ? "alto" : "medio");
  }
  return tiers;
}

/*
 * Con 4 o 5 obras no se listan los proyectos: "Los cinco proyectos" dice mas
 * y ocupa menos. Listar los cinco no distingue nada y descuadraba el pie, que
 * tiene altura fija.
 */
function textoCruce(usedIn: string[]): string {
  if (usedIn.length === 5) return "Los cinco proyectos";
  if (usedIn.length === 4) return "Cuatro de los cinco proyectos";
  return "";
}

/**
 * Contenido de una franja: icono + nombre, detalle, y el cruce con las obras
 * publicadas (o "Sin obra publicada" si no hay ninguna). Devuelve el nodo
 * `.credits-strip-in` completo — el rodillo lo sustituye entero, nunca lo
 * muta, porque los dos nodos del rodillo van siempre en `position: absolute`
 * (ver comentario de `.credits-strip-in` en `themes.css`).
 */
function pintarFranja(_strip: HTMLElement, entry: CreditEntry): HTMLElement {
  const dentro = el("div", "credits-strip-in", []);
  const marca = elFromMarkup("credits-strip-mark", getIconMarkup(entry.slug));
  marca.setAttribute("aria-hidden", "true");
  marca.setAttribute("data-decorative", "");

  const hijos: HTMLElement[] = [
    el("div", "credits-strip-top", [marca, el("span", "credits-strip-name", [entry.name])]),
    el("p", "credits-strip-detail", [entry.detail]),
  ];

  if (entry.usedIn.length === 0) {
    const vacio = el("p", "credits-strip-none", ["Sin obra publicada"]);
    hijos.push(vacio);
  } else {
    const resumen = textoCruce(entry.usedIn);
    const items = resumen
      ? [el("span", "credits-used-item", [resumen])]
      : entry.usedIn.map((t) => el("span", "credits-used-item", [t]));
    hijos.push(
      el("div", "credits-used", [el("p", "credits-used-label", ["Aparece en"]), ...items]),
    );
  }

  dentro.replaceChildren(...hijos);
  return dentro;
}

/**
 * Creditos de pelicula interactivos, agrupados por area. La lista a la
 * izquierda y, a la derecha, el icono real de la tecnologia, para que se usa y
 * en que proyectos aparece. El panel nunca arranca vacio.
 *
 * El encabezado de grupo (`.credit-group-label`) NO envuelve a sus filas: es
 * un hermano plano mas dentro de `.credits-list`. Dos razones, las dos
 * comprobadas antes de escribir esto:
 *
 *  1. `scene4Credits` (vice.choreography.ts) anima los hijos DIRECTOS de
 *     `[data-credit-roll]`. Un envoltorio por grupo reduciria el escalonado de
 *     doce filas a tres bloques; asi, ademas, los encabezados entran tambien.
 *  2. `scripts/verify.py` exige que `.credit-role` exista en el DOM y este
 *     oculto por CSS en Hyprland/Caelestia — es el gate que protege el re-skin
 *     a pildoras. Por eso ese `<span>` sigue aqui aunque en Vice no se vea: se
 *     oculta con CSS, no se elimina.
 *
 * Accesibilidad: cada fila es un `<button>` real, enfocable con Tab, que
 * dispara el mismo `select()` en `mouseenter`, `focus` y `click`, con
 * `aria-pressed` (cual esta activa) y `aria-controls` apuntando al panel; el
 * panel es `aria-live="polite"` para que un lector anuncie el cambio sin mover
 * el foco. El icono es decorativo puro: `aria-hidden` (fuera del arbol de
 * accesibilidad) y `data-decorative` (exento del gate de contraste — nunca
 * `aria-hidden` para eso, ver `scripts/verify.py::check_contrast_wcag`).
 */
export function createCredits(): HTMLElement {
  // `skillGroups` ya trae los seis bloques del reparto. Antes habia que
  // coserle a mano un grupo "Otras herramientas" desde `secondarySkills`; ese
  // array desaparecio al reorganizar el contenido y su contenido vive ahora en
  // el bloque "Lenguajes base".
  const groups: SkillGroup[] = skillGroups;

  const icon = el("div", "credits-icon", []);
  icon.setAttribute("aria-hidden", "true");
  icon.setAttribute("data-decorative", "");

  const name = el("p", "credits-panel-name display-lg text-2xl", []);
  const role = el("p", "credits-panel-role", []);
  const detail = el("p", "credits-panel-detail", []);

  const usedList = el("div", "credits-used-list", []);
  usedList.setAttribute("data-credit-used-list", "");
  const used = el("div", "credits-used", [
    el("p", "credits-used-label", ["Aparece en"]),
    usedList,
  ]);
  used.setAttribute("data-credit-used", "");

  const panel = el("div", "credits-panel scene-surface", [icon, name, role, detail, used]);
  panel.id = PANEL_ID;
  panel.setAttribute("data-credit-panel", "");
  panel.setAttribute("role", "status");
  panel.setAttribute("aria-live", "polite");

  const rows: HTMLButtonElement[] = [];
  const listChildren: HTMLElement[] = [];

  // Contabilidad que usan tambien las tareas 6, 8 y 9 para encontrar nodos
  // por grupo sin recorrer el DOM.
  const labels: HTMLElement[] = []; // un rotulo por grupo
  const filasPorGrupo: HTMLButtonElement[][] = []; // los botones de cada grupo
  const marcasPorGrupo: Map<string, HTMLElement>[] = []; // slug -> marca, O(1) por grupo
  const toggles: HTMLButtonElement[] = []; // un boton de apertura por grupo (movil)
  // Relleno fantasma por grupo (movil): null si el grupo ya tiene el maximo
  // de filas de nombres. Ver comentario grande junto al bucle que lo llena.
  const fillersPorGrupo: (HTMLElement | null)[] = [];

  const MAX_ITEMS = Math.max(...groups.map((g) => g.items.length)); // 8 hoy
  const FILA_NOMBRES = 3; // 1 cabecera, 2 mojones, 3..(2+MAX) nombres, luego franja
  const MAX_FILAS_NOMBRES_M = Math.ceil(MAX_ITEMS / 2); // 4 hoy: filas de a dos del grupo mas largo

  /*
   * Los nombres se REPARTEN por el alto de la parcela, no se amontonan
   * arriba: las tres parcelas de 5 dejaban un agujero visible al pie y el
   * recuento se decia dos veces (ancho Y alto). Repartidos, la segunda
   * senal pasa a ser densidad. Las 5 filas de una parcela corta se estiran
   * sobre las 8 ranuras de la mas larga, asi que las cuatro parcelas miden
   * lo mismo y las cuatro chispas llegan abajo a la vez.
   */
  function filaDe(i: number, n: number): number {
    if (n <= 1) return FILA_NOMBRES;
    return Math.round((i * (MAX_ITEMS - 1)) / (n - 1)) + FILA_NOMBRES;
  }

  /*
   * Friso de marcas: donde un cartel de cine pone los logos de estudio y
   * distribuidora. Va al pie y no delante de cada nombre porque una marca por
   * nombre convierte la linea de reparto en una lista con vinetas — el
   * defecto exacto que la direccion de cartel elimina.
   *
   * El encendido de marca es por parcela (`marcasPorGrupo`, declarado junto
   * al resto de la contabilidad mas abajo): cada Map indexa por slug para
   * encender la marca en O(1) dentro de su territorio, porque `mouseenter`
   * se dispara muchas veces por segundo al recorrer el cartel con el raton y
   * no puede volver a recorrer el DOM en cada disparo.
   */

  /*
   * El catastro de Hyprland: cuatro parcelas, cuatro franjas de detalle y
   * cuatro filas de friso, una por grupo. Se construyen ANTES del bucle de
   * items porque `markRows[gi]` recibe cada marca segun se crea mas abajo.
   * Son hermanas de `.credits-list`, nunca envoltorios: `scene4Credits`
   * anima los hijos directos de `[data-credit-roll]`, igual que con el
   * friso de Vice (ver comentario de `frieze`).
   */
  const parcelas: HTMLElement[] = [];
  const strips: HTMLElement[] = [];
  const markRows: HTMLElement[] = [];

  groups.forEach((group, gi) => {
    /*
     * Caja decorativa de columna. NO es un envoltorio: la lista sigue plana
     * y esta caja es una hermana que ocupa la columna entera de la rejilla.
     * Es lo que permite tener un lindero continuo de arriba abajo y un
     * sitio donde vive la luz, sin agrupar los `.credit` bajo un padre.
     */
    const parcela = el("div", "credits-parcela", [
      el("span", "credits-rail", []),
      el("span", "credits-glow", []),
      el("span", "credits-spark", []),
    ]);
    parcela.setAttribute("data-credit-parcela", "");
    parcela.dataset.parcela = String(gi);
    parcela.style.setProperty("--parcela-i", String(gi));
    parcela.setAttribute("aria-hidden", "true");
    parcela.setAttribute("data-decorative", "");
    parcelas.push(parcela);

    const strip = el("div", "credits-strip", [el("div", "credits-strip-in", [])]);
    strip.setAttribute("data-credit-strip", "");
    strip.dataset.parcela = String(gi);
    strip.id = `credits-strip-${gi}`;
    strip.setAttribute("role", "status");
    strip.setAttribute("aria-live", "polite");
    strip.style.setProperty("--skill-col-strip", String(gi + 1));
    strip.style.setProperty("--skill-span-m", String(3 + Math.ceil(group.items.length / 2)));
    strips.push(strip);

    const row = el("div", "credits-marks-row", []);
    row.setAttribute("data-credit-marks-row", "");
    row.dataset.parcela = String(gi);
    row.setAttribute("aria-hidden", "true");
    row.setAttribute("data-decorative", "");
    // Simetrico con --skill-col-strip en `strip` y con --skill-col en
    // `groupLabel`: sin esto la fila de friso cae en grid-column: auto en
    // Hyprland y crea columnas implicitas (catastro, tarea 4).
    row.style.setProperty("--skill-col", String(gi + 1));
    markRows.push(row);
  });

  /*
   * La franja arranca LLENA para no dejar un hueco esperando interaccion,
   * pero llenar no es encender: en reposo todavia no ha pasado nada, asi
   * que ningun nombre lleva acento ni desplazamiento. Sembrar marcando el
   * primero como seleccionado producia un falso hover en movil — por eso
   * este bucle solo pinta contenido, nunca toca `.is-active` ni
   * `aria-pressed` ni dispara `select()`.
   */
  groups.forEach((group, gi) => {
    const primera = toEntry(group.label, group.items[0]);
    strips[gi].replaceChildren(pintarFranja(strips[gi], primera));
  });

  /*
   * Abre el territorio `gi`: es el estado de "cual estoy mirando" en movil
   * (parcela, nombres y franja), independiente del acento de abajo ("cual
   * tecnologia estoy senalando"). Compartida por dos disparadores: `select()`
   * (una interaccion real o el sembrado sobre una tecnologia concreta) y
   * `toggles[gi]` (tocar la cabecera de un territorio PLEGADO, sin senalar
   * ningun nombre — la unica via para abrir un territorio en movil, porque
   * sus `.credit` nacen `display: none` y un boton oculto no es alcanzable
   * ni por raton ni por teclado).
   */
  function abrirTerritorio(gi: number): void {
    parcelas.forEach((p, idx) => p.classList.toggle("is-open", idx === gi));
    filasPorGrupo.forEach((filas, idx) => {
      const abierto = idx === gi;
      for (const fila of filas) fila.classList.toggle("is-open", abierto);
    });
    fillersPorGrupo.forEach((f, idx) => f?.classList.toggle("is-open", idx === gi));
    strips.forEach((s, idx) => s.classList.toggle("is-open", idx === gi));
    toggles.forEach((t, idx) => t.setAttribute("aria-expanded", String(idx === gi)));
  }

  groups.forEach((group, gi) => {
    /*
     * El recuento es derivado (`group.items.length`), no un dato nuevo de
     * `content.ts`: nace oculto (`style.css`) y solo Hyprland en movil lo
     * enciende, como cabecera de un territorio plegado que no muestra sus
     * nombres.
     */
    const count = el("span", "credit-group-count", [String(group.items.length)]);
    /*
     * Marca de plegado ("+" cerrado, "-" abierto): puramente decorativa, el
     * estado accesible ya lo lleva `aria-expanded` en `.credit-group-toggle`
     * (de ahi `aria-hidden`, no duplicar el estado). Vive DENTRO del boton
     * para heredar su color de estado sin un segundo selector de estado.
     */
    const mark = el("span", "credit-group-mark", []);
    mark.setAttribute("aria-hidden", "true");
    /*
     * El unico tap target para abrir un territorio plegado en movil. Cubre
     * toda la cabecera (`position: absolute; inset: 0` sobre el `<p>`
     * relativo, en `themes.css`) y nace oculto: en escritorio y en los
     * otros dos temas no hay nada que abrir, y un boton `display: none` no
     * entra en el orden de tabulacion de Vice/Caelestia — el patron
     * aditivo no se rompe por tener el nodo en el DOM de los tres temas.
     */
    const toggle = el("button", "credit-group-toggle", [mark]);
    toggle.type = "button";
    toggle.setAttribute("aria-controls", `credits-strip-${gi}`);
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", `${group.label}, ${group.items.length} tecnologias`);
    toggle.addEventListener("click", () => abrirTerritorio(gi));
    toggles.push(toggle);

    const groupLabel = el("p", "credit-group-label", [group.label, count, toggle]);
    groupLabel.setAttribute("data-credit-group", String(gi));
    groupLabel.style.setProperty("--skill-col", String(gi + 1));
    groupLabel.style.setProperty("--skill-row", "1");
    listChildren.push(groupLabel);
    labels.push(groupLabel);

    const tiers = tiersDeGrupo(group);
    const filaButtons: HTMLButtonElement[] = [];
    const marcasDeEsteGrupo = new Map<string, HTMLElement>();
    filasPorGrupo.push(filaButtons);
    marcasPorGrupo.push(marcasDeEsteGrupo);

    group.items.forEach((item, i) => {
      const entry = toEntry(group.label, item);
      const row = el("button", "credit", [
        el("span", "credit-role", [entry.role]),
        el("span", "credit-name", [entry.name]),
      ]);
      row.type = "button";
      row.setAttribute("data-credit", "");
      row.dataset.index = String(rows.length);
      row.dataset.parcela = String(gi);
      row.dataset.creditTier = tiers.get(item.slug) ?? "bajo";
      /*
       * Apunta a los DOS destinos que la fila puede actualizar: el panel
       * compartido (Vice/Caelestia) y la franja de su propia parcela
       * (Hyprland). Es valido tener dos ids en `aria-controls` y sirve a los
       * tres temas sin ramificar el atributo por tema.
       */
      row.setAttribute("aria-controls", `${PANEL_ID} credits-strip-${gi}`);
      row.setAttribute("aria-pressed", "false");
      row.style.setProperty("--skill-col", String(gi + 1));
      row.style.setProperty("--skill-row", String(filaDe(i, group.items.length)));
      // El retardo de la lampara ES la posicion de la chispa: si cambia la
      // altura de fila y no cambia esto, el gesto miente. Los dos numeros
      // van juntos.
      row.style.setProperty(
        "--skill-d",
        `${Math.round((i / Math.max(1, group.items.length - 1)) * 620)}ms`,
      );
      /*
       * Marcas cuyo nombre se escribe en minuscula (n8n hoy) para que el
       * cartel no las suba a versalita: "N8N" no es como se escribe la marca.
       * La regla sale del dato, no de una lista de nombres a mano: si en
       * `content.ts` esta todo en minuscula, es deliberado.
       */
      if (entry.name === entry.name.toLowerCase()) {
        row.setAttribute("data-credit-verbatim", "");
      }

      /*
       * Decorativa pura: `aria-hidden` la saca del arbol de accesibilidad
       * (el nombre ya esta en el boton, la marca no anade informacion) y
       * `data-decorative` la exime del gate de contraste. Nunca `aria-hidden`
       * para eximir contraste: ver `scripts/verify.py::check_contrast_wcag`.
       */
      const mark = elFromMarkup("credits-mark", getIconMarkup(entry.slug));
      mark.setAttribute("aria-hidden", "true");
      mark.setAttribute("data-decorative", "");
      mark.dataset.markSlug = entry.slug;
      marcasDeEsteGrupo.set(entry.slug, mark);
      markRows[gi].appendChild(mark);

      const select = (ev?: Event) => {
        for (const other of rows) {
          other.classList.remove("is-active");
          other.setAttribute("aria-pressed", "false");
        }
        row.classList.add("is-active");
        row.setAttribute("aria-pressed", "true");
        icon.replaceChildren(elFromMarkup("credits-svg", getIconMarkup(entry.slug)));
        name.textContent = entry.name;
        role.textContent = entry.role;
        detail.textContent = entry.detail;
        usedList.replaceChildren(
          ...entry.usedIn.map((title) => el("span", "credits-used-item", [title])),
        );
        /*
         * Sin proyectos publicados el bloque no se muestra, pero COMO se deja
         * de mostrar lo decide cada tema, no este componente: Hyprland y
         * Caelestia lo quitan del flujo, y Vice solo lo hace invisible para
         * que el pie del cartel no cambie de altura.
         *
         * Por eso un `data-` y no el atributo `hidden`: el preflight de
         * Tailwind 4 declara `[hidden] { display: none !important }`, y con
         * eso puesto ningun tema puede elegir otra forma de ocultarlo — se
         * midio, el `visibility` entraba y el `display` no. `aria-hidden`
         * cubre lo que cubria `hidden`: el bloque vacio sale del arbol de
         * accesibilidad y el panel `aria-live` no lo anuncia.
         */
        const vacio = entry.usedIn.length === 0;
        used.toggleAttribute("data-credit-empty", vacio);
        used.setAttribute("aria-hidden", String(vacio));
        // La marca encendida es una segunda senal de seleccion que no depende
        // del hover: en tactil no lo hay, y el cartel no tiene recuadros ni
        // bordes que delaten que un nombre responde. Se recorren las marcas
        // de todos los grupos porque el hover puede desactivar la marca
        // encendida de otra parcela.
        for (const grupoDeMarcas of marcasPorGrupo) {
          for (const [slug, node] of grupoDeMarcas) {
            node.classList.toggle("is-active", slug === entry.slug);
          }
        }
        /*
         * Territorio movil: la parcela, sus nombres y su franja "abiertos"
         * son el estado de "cual estoy mirando", distinto del acento de mas
         * abajo. `abrirTerritorio` se llama en CUALQUIER `select()`, incluida
         * la sintetica de sembrado — por eso el sembrado inicial de `rows[0]`
         * deja la primera parcela abierta sin encender ningun nombre (el
         * acento sigue detras del guardia `ev?.isTrusted`, mas abajo). El
         * friso NO entra en este reparto: decision de producto, se ve en las
         * cuatro parcelas a la vez en movil (es la evidencia que sostiene el
         * territorio plegado).
         */
        abrirTerritorio(gi);

        /*
         * Marcador propio de Hyprland, encima del `.is-active` global de
         * arriba: uno por parcela (cuatro a la vez), nunca uno solo para las
         * 23. `.is-active`/`aria-pressed` no se tocan aqui — siguen siendo
         * globales y siguen alimentando el panel compartido de Vice y
         * Caelestia sin cambiar de semantica. Solo el CSS de Hyprland lee
         * `data-credit-picked`.
         *
         * `ev.isTrusted` distingue una interaccion real (mouseenter/focus/
         * click del navegador, siempre `isTrusted: true`) del disparo
         * sintetico de sembrado al final de `createCredits` (`new
         * MouseEvent(...)`, siempre `isTrusted: false`). Sin este filtro el
         * sembrado dejaria la primera tecnologia con acento encendido desde
         * el arranque — sembrar la franja no es encender el nombre.
         */
        if (ev?.isTrusted) {
          for (const otra of filasPorGrupo[gi]) {
            otra.toggleAttribute("data-credit-picked", otra === row);
          }
          strips[gi].replaceChildren(pintarFranja(strips[gi], entry));
        }
      };

      row.addEventListener("mouseenter", select);
      row.addEventListener("focus", select);
      row.addEventListener("click", select);

      rows.push(row);
      filaButtons.push(row);
      listChildren.push(row);
    });
  });

  /*
   * Movil: rejilla de DOS columnas por parcela, apiladas. Se calcula aqui y
   * no se deja a la colocacion automatica porque las franjas y los frisos
   * inactivos van en `display: none` y desaparecen del flujo, lo que
   * descuadraria una rejilla automatica.
   *
   * Por parcela: fila base = cabecera, +1 = mojones, +2..+1+MAX_FILAS_NOMBRES_M
   * = nombres de dos en dos (mas relleno si el grupo tiene menos de
   * MAX_FILAS_NOMBRES_M filas), y la franja al final.
   *
   * `--skill-span-m` de la parcela usa SIEMPRE `MAX_FILAS_NOMBRES_M` (el
   * numero de filas del grupo mas largo), nunca "las filas de ESTE grupo":
   * si cada parcela reservara solo lo suyo, una parcela de 5 tecnologias (3
   * filas) mediria ABIERTA menos que una de 8 (4 filas) y "la altura total
   * no puede cambiar al cambiar de una a otra" — el requisito de la
   * decision de producto de Aoshi — se rompe (medido: 930.8px con Interfaz
   * abierta contra 903.6px con Herramientas abierta). Un `[data-credit-
   * filler-m]` fantasma (aria-hidden, oculto salvo `is-open` igual que
   * `.credit`) cubre la diferencia: nace SOLO en los grupos mas cortos que
   * el mayor, mide `44px * relleno` y ocupa las filas que a ese grupo le
   * faltan para llegar a MAX_FILAS_NOMBRES_M.
   */
  let filaM = 1;
  groups.forEach((group, gi) => {
    const base = filaM;
    const filasNombres = Math.ceil(group.items.length / 2); // filas REALES de este grupo
    const relleno = MAX_FILAS_NOMBRES_M - filasNombres;
    // La parcela decorativa no sobrevive al apilado por si sola: el CSS de
    // movil le pide grid-row a partir de --skill-row-m/--skill-span-m igual
    // que a la etiqueta, el friso y la franja. Sin escribirlas aqui cae en
    // colocacion automatica y el lindero deja de cubrir su territorio.
    parcelas[gi].style.setProperty("--skill-row-m", String(base));
    parcelas[gi].style.setProperty("--skill-span-m", String(3 + MAX_FILAS_NOMBRES_M));
    labels[gi].style.setProperty("--skill-row-m", String(base));
    markRows[gi].style.setProperty("--skill-row-m", String(base + 1));
    group.items.forEach((_, i) => {
      const row = filasPorGrupo[gi][i];
      row.style.setProperty("--skill-col-m", String((i % 2) + 1));
      row.style.setProperty("--skill-row-m", String(base + 2 + Math.floor(i / 2)));
    });
    if (relleno > 0) {
      const filler = el("div", "credit-filler-m", []);
      filler.setAttribute("aria-hidden", "true");
      filler.setAttribute("data-decorative", "");
      filler.dataset.parcela = String(gi);
      filler.style.setProperty("--skill-row-m", String(base + 2 + filasNombres));
      filler.style.setProperty("--skill-relleno-m", String(relleno));
      fillersPorGrupo.push(filler);
      listChildren.push(filler);
    } else {
      fillersPorGrupo.push(null);
    }
    strips[gi].style.setProperty("--skill-row-m", String(base + 2 + MAX_FILAS_NOMBRES_M));
    filaM = base + 3 + MAX_FILAS_NOMBRES_M;
  });

  const list = el("div", "credits-list", listChildren);
  list.setAttribute("data-credit-roll", "");

  /*
   * El friso es hermano de la lista y del panel, NUNCA hijo de
   * `[data-credit-roll]`: `scene4Credits` anima los hijos DIRECTOS de ese
   * contenedor, y meter aqui 23 nodos mas ahogaria el escalonado del reparto.
   * Los otros dos temas lo apagan con una sola regla sin tocar su flex-wrap.
   * Ahora contiene las cuatro `markRows` (una por parcela) en vez de las 23
   * marcas sueltas; Vice las disuelve con `display: contents` en
   * `themes.css` para conservar su `flex-wrap` de 23 items.
   */
  const frieze = el("div", "credits-marks", markRows);
  frieze.setAttribute("data-credit-marks", "");
  frieze.setAttribute("aria-hidden", "true");
  frieze.setAttribute("data-decorative", "");

  // Estado inicial: el panel muestra la primera entrada sin esperar a que
  // alguien interactue. `rows[0]` siempre existe: `skillGroups` nunca esta
  // vacio.
  rows[0]?.dispatchEvent(new MouseEvent("mouseenter"));

  const grid = el("div", "credits-grid", [list, panel, frieze, ...parcelas, ...strips]);
  /*
   * El ancho de cada parcela es proporcional a cuantas tecnologias contiene:
   * el area en pantalla ES el dato. Sale de `content.ts`, no de una lista a
   * mano: si manana cambian los grupos, la proporcion se actualiza sola.
   */
  grid.style.setProperty("--parcela-cols", groups.map((g) => `${g.items.length}fr`).join(" "));
  return grid;
}
