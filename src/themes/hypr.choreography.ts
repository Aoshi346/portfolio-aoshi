import { STRIP_REPAINT_EVENT, type StripRepaintDetail } from "../components/credits";
import type { Choreography, Gsap } from "./choreography";

const ID = "hypr";

// Los dos regimenes de tiempo del vocabulario global (corte / atmosfera),
// mismos valores que `--hard`/`--slow` en themes.css. Duplicados aqui porque
// GSAP no puede leer un `cubic-bezier()` desde una custom property de CSS.
const HARD = "cubic-bezier(0.7, 0, 0.2, 1)";
const SLOW = "cubic-bezier(0.16, 0.84, 0.28, 1)";

/**
 * Sonda de temporizadores del gesto 4: la lampara programa un `setTimeout`
 * de 1100ms para pasar de `is-caught` a `is-caught-still` (ver mas abajo).
 * `Choreography` devuelve `void` — ningun tema tiene `destroy()`, y
 * `main.ts` solo llama `destroy()` en `pagehide` sobre fondo/carril/cursor/
 * ignicion/nav — asi que este tema se limpia como ya limpia sus
 * ScrollTrigger: matando por prefijo AL ENTRAR, no al salir. Sin este
 * registro, un remonte (HMR de Vite recargando este modulo sin recargar la
 * pagina entera; la produccion real solo invoca la coreografia una vez por
 * carga) deja temporizadores del montaje anterior corriendo sueltos: si uno
 * dispara pasado el remonte, añade `is-caught-still` a nombres que el nuevo
 * montaje puede estar animando en ese mismo instante, cortando su lampara
 * antes de los 400ms que le tocan.
 */
type HyprTimerWindow = Window & { __hyprSkillTimers?: number[] };

/**
 * Ascua: tres gestos, no uno repetido a distintas escalas.
 *
 * El defecto de las propuestas descartadas era que TODO iba lento y suave —
 * eso es un ajuste global, no una coreografia. Aqui lo atmosferico va a 900ms
 * con curva blanda y los cortes a 400ms con `--hard`, sin rebote. La
 * diferencia de tiempos es lo que hace que el movimiento parezca decidido.
 *
 * El revelado NO se fia solo del observador de interseccion: con scroll
 * rapido se pierden callbacks y el contenido se queda invisible para siempre.
 * Va con red por posicion, que es justo lo que hace ScrollTrigger.
 *
 * Movimiento reducido: esta funcion entera (y por tanto sus 5 gestos) NUNCA
 * se ejecuta bajo `prefers-reduced-motion: reduce` — `initScrollReveal`
 * (`src/utils/reveal.ts`) hace early-return antes de invocar
 * `theme.choreography()`, y ese guardian es compartido por los tres temas
 * (no se toca aqui: tocarlo afectaria a Vice y Caelestia). Medido en el
 * arbol: con `reduce`, `window.__hyprSkills` es `undefined`, no aparece
 * ninguna clase `.hypr-cut`/`.hypr-up`/`.is-lit`/`.is-caught` y GSAP no
 * llega a importarse. Un `gsap.matchMedia` para `reduce` DENTRO de esta
 * funcion seria codigo muerto: nunca se registraria porque la funcion que lo
 * contiene no corre. Lo que SI sobrevive bajo `reduce` es contenido base
 * (HTML/CSS, sin JS: las 4 parcelas, los 4 rotulos, los 23 nombres en su
 * color de reposo y las 4 franjas se ven por la cascada normal) mas el
 * `:hover`/`:focus-visible` puro de `.credit-name` (themes.css) y el cambio
 * de contenido de la franja (`credits.ts::repintarFranja`, que hace
 * `replaceChildren` SIEMPRE, fuera de esta coreografia). Lo unico que faltaba
 * ahi era que ese `:hover` seguia animando 900ms bajo `reduce` porque
 * `:not(.is-caught)` es SIEMPRE cierto cuando `.is-caught` nunca se aplica —
 * arreglado en themes.css con `transition: none` bajo la media query, no
 * aqui. La luz decorativa del lindero (`.credits-glow`, `aria-hidden`) y el
 * resto del apuntado por GSAP no tienen equivalente CSS y quedan ausentes
 * bajo `reduce`, igual que en Vice: es una capa de refuerzo, no el canal por
 * el que se entiende que nombre esta enfocado.
 */
export const hyprChoreography: Choreography = ({ ScrollTrigger, root }) => {
  ScrollTrigger.getAll()
    .filter((t) => typeof t.vars.id === "string" && t.vars.id.startsWith(ID))
    .forEach((t) => t.kill());

  // Limpieza de un remonte anterior (ver comentario de `HyprTimerWindow`
  // arriba): borra los temporizadores pendientes de la lampara, el estado
  // `is-caught`/`is-caught-still` que hubieran dejado y la sonda del arnes,
  // para que la entrada vuelva a correr entera y `window.__hyprSkills`
  // apunte siempre a LA timeline de este montaje, no a la anterior.
  const timerWindow = window as HyprTimerWindow;
  for (const id of timerWindow.__hyprSkillTimers ?? []) window.clearTimeout(id);
  timerWindow.__hyprSkillTimers = [];
  for (const n of Array.from(root.querySelectorAll<HTMLElement>("[data-credit].is-caught"))) {
    n.classList.remove("is-caught", "is-caught-still");
  }
  delete (window as unknown as { __hyprSkills?: unknown }).__hyprSkills;

  const scenes = Array.from(root.querySelectorAll<HTMLElement>("[data-scene]"));

  // Gesto 0 — repartir la gramatica.
  // El DOM lo construyen las secciones, que son COMPARTIDAS por los tres
  // temas y no pueden llevar clases de uno solo. Asi que las reparte aqui el
  // tema, junto con su escalonado: sin este paso, `.hypr-cut` y compania
  // existirian en la hoja sin aplicarse a nada, y `--hypr-d` se quedaria a 0
  // dejando todas las entradas simultaneas.
  const RECETA: ReadonlyArray<readonly [string, string]> = [
    [".hero-kick", "hypr-cut"],
    // `.contacto-title` sale de aqui: recibe su propio gesto letra a letra. Si
    // se queda, `hypr-up` le pone opacity 0 y translateY(14px) a la vez que
    // sus glifos hacen su clip-path — dos gestos peleando por el mismo nodo.
    [".display-xl, .display-lg, .about-name", "hypr-up"],
    [".lead, .contacto-lead", "hypr-up"],
    [".about-pair", "hypr-up"],
    // El estado y las vias cambian de familia: dejan de "asentarse" (900ms
    // slow) y pasan a "encenderse" (420ms hard), que es lo que hace una barra
    // de estado. Y de eje: suben desde el borde en vez de deslizar en Y.
    [".contacto-estado", "hypr-cut-v"],
    ['[class*="contacto-bar--"]', "hypr-cut-v"],
  ];

  scenes.forEach((scene) => {
    // El hero lleva su propio gesto (ver themes.css, bloque
    // `.hero-name-word`/`.hero-kick`/`.hero-corner` bajo `.is-lit`): si
    // tambien recibe `hypr-cut`/`hypr-up` de la receta generica, las dos
    // animaciones compiten sobre las mismas propiedades (clip-path/opacity)
    // en el mismo elemento.
    if (scene.dataset.scene === "hero") return;

    let n = 0;
    RECETA.forEach(([selector, clase]) => {
      Array.from(scene.querySelectorAll<HTMLElement>(selector)).forEach((node) => {
        if (node.classList.contains(clase)) return;
        node.classList.add(clase);
        // 70ms por pieza: el mismo escalonado que el prototipo aprobado.
        node.style.setProperty("--hypr-d", `${n * 70}ms`);
        n += 1;
      });
    });
  });

  // Gesto 0c — el titular de cierre, letra a letra.
  // El corte horizontal por glifo NO es un gesto nuevo: es el mismo que
  // `.hero-name-word` usa para encender el nombre al abrir el sitio. La escena
  // que cierra cita a la que abre en vez de estrenar un verbo.
  const titulo = root.querySelector<HTMLElement>('[data-scene="contacto"] .contacto-title');

  if (titulo && !titulo.querySelector(".contacto-title-glyphs")) {
    const texto = titulo.textContent ?? "";
    // Ocho <span> de una letra hacen que un lector de pantalla DELETREE
    // "H-a-b-l-e-m-o-s". El arbol troceado se oculta y el texto real va en el
    // aria-label del h2. Esto es distinto de `.hero-name-word`, que trocea por
    // PALABRA: a nivel de palabra el lector concatena sin problema.
    titulo.setAttribute("aria-label", texto);
    const caja = document.createElement("span");
    caja.className = "contacto-title-glyphs";
    caja.setAttribute("aria-hidden", "true");
    // Array.from y no split(""): parte por punto de codigo, no por unidad
    // UTF-16, asi que un caracter fuera del plano basico no se rompe en dos.
    Array.from(texto).forEach((ch, i) => {
      const glifo = document.createElement("span");
      glifo.className = "contacto-glyph hypr-cut";
      glifo.textContent = ch;
      // 140ms de cabeza (el kick ya ha entrado) y 70 de escalon por letra.
      glifo.style.setProperty("--hypr-d", `${140 + i * 70}ms`);
      caja.appendChild(glifo);
    });
    titulo.replaceChildren(caja);
  }

  // Gesto 0d — el horario de la escena de cierre.
  // Un solo sentido, de izquierda a derecha, y dos ejes con dos sentidos: el
  // titular abre en horizontal porque es una palabra que se lee; la cinta sube
  // desde el borde inferior porque es de donde viene una barra de estado.
  // El dato de contacto entra ANTES que el estado a proposito: lo que importa
  // es el correo. El estado remata donde la luz del filete acabo su viaje.
  const cierre = root.querySelector<HTMLElement>('[data-scene="contacto"]');
  if (cierre) {
    const HORARIO: ReadonlyArray<readonly [string, number]> = [
      [".hero-kick", 0],
      [".contacto-lead", 760],
      [".contacto-estado", 1700],
    ];
    for (const [selector, ms] of HORARIO) {
      const nodo = cierre.querySelector<HTMLElement>(selector);
      nodo?.style.setProperty("--hypr-d", `${ms}ms`);
    }
    Array.from(cierre.querySelectorAll<HTMLElement>('[class*="contacto-bar--"]')).forEach(
      (via, i) => {
        via.style.setProperty("--hypr-d", `${1040 + i * 70}ms`);
      },
    );
  }

  // Gesto 0b — el montaje de la placa.
  // El retardo sale de la POSICION en la rejilla, no del orden del DOM: fila
  // mas columna, asi que la llegada cruza la placa en diagonal en vez de
  // recorrer una lista. Y la direccion sale de la misma lectura, no de una
  // tabla escrita a mano que habria que mantener en dos sitios.
  const placa = root.querySelector<HTMLElement>("[data-placa]");
  const celdas = Array.from(root.querySelectorAll<HTMLElement>("[data-placa-celda]"));
  if (placa && celdas.length > 0) {
    // Numero real de columnas: en escritorio son 6 y las celdas van colocadas a
    // mano; por debajo de la consulta de contenedor son 2 y van automaticas.
    const columnas = getComputedStyle(placa).gridTemplateColumns.split(" ").filter(Boolean).length;

    celdas.forEach((celda, i) => {
      const area = getComputedStyle(celda)
        .gridArea.split("/")
        .map((trozo) => parseInt(trozo, 10));

      // Con colocacion automatica `grid-area` sale `auto / auto / auto / auto`
      // y `parseInt` da NaN. Sin este respaldo, en movil ninguna celda recibe
      // la clase y la entrada desaparece entera — justo donde el dispositivo
      // tenia que ser el mismo que en escritorio.
      const explicita = area.length === 4 && !Number.isNaN(area[0]) && !Number.isNaN(area[1]);
      const fila = explicita ? (area[0] as number) : Math.floor(i / columnas) + 1;
      const col = explicita ? (area[1] as number) : (i % columnas) + 1;
      const filaFin = explicita ? (area[2] as number) : fila + 1;
      const colFin = explicita ? (area[3] as number) : col + 1;
      const ultimaFila = Math.ceil(celdas.length / columnas) + 1;

      celda.classList.add("placa-in");
      celda.style.setProperty("--placa-d", `${(fila - 1 + (col - 1)) * 70}ms`);
      celda.style.setProperty(
        "--placa-tx",
        col === 1 ? "-22px" : colFin > columnas ? "22px" : "0px",
      );
      celda.style.setProperty(
        "--placa-ty",
        fila === 1 ? "-18px" : filaFin >= (explicita ? 4 : ultimaFila) ? "18px" : "0px",
      );
    });
  }

  // Gesto 1 — la escena se enciende. Las clases hacen el trabajo; GSAP solo
  // decide CUANDO, para que el CSS siga siendo la fuente de los tiempos.
  scenes.forEach((scene, i) => {
    ScrollTrigger.create({
      id: `${ID}-lit-${i}`,
      trigger: scene,
      start: "top 90%",
      once: true,
      onEnter: () => scene.classList.add("is-lit"),
    });
  });

  // Red: cualquier escena ya dentro del cuadro se enciende sin esperar a un
  // callback. Sin esto, un scroll rapido deja secciones en blanco.
  const net = (): void => {
    scenes.forEach((scene) => {
      const r = scene.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.9 && r.bottom > 0) scene.classList.add("is-lit");
    });
  };
  net();
  window.addEventListener("scroll", net, { passive: true });

  // Gesto 3 — el titular lee la posicion de la luz, para que al desplazarte
  // la luz pase POR DENTRO de las palabras en vez de viajar con ellas.
  ScrollTrigger.create({
    id: `${ID}-light`,
    trigger: root,
    start: "top top",
    end: "bottom bottom",
    onUpdate: (self) => {
      const p = self.progress;
      // Base 70% (antes 52%, centrado): el nombre vive ahora en la columna
      // derecha del grid del "lomo" (themes.css), no centrado en el hero.
      root.style.setProperty("--bx", `${70 + Math.sin(p * Math.PI * 1.4) * 15}%`);
      root.style.setProperty("--by", `${26 + p * 32}%`);
    },
  });

  // Gesto 4 — la corriente. El orden ES el orden del argumento: primero el
  // limite (el carril), luego el nombre del sitio (el rotulo), luego lo que
  // hay dentro (los nombres), y al final donde se comprueba (las franjas).
  // Si los nombres entraran antes que los rotulos, la escena diria "23
  // tecnologias agrupadas de alguna manera", que es lo que decia antes.
  const parcelas = Array.from(root.querySelectorAll<HTMLElement>("[data-credit-parcela]"));
  if (parcelas.length > 0) {
    const R = 0.09; // entre territorios, no los 70ms del paso interno del tema
    const tl = gsap.timeline({
      scrollTrigger: { id: `${ID}-skills`, trigger: parcelas[0], start: "top 82%", once: true },
    });

    parcelas.forEach((parcela, c) => {
      const at = c * R;
      const rail = parcela.querySelector<HTMLElement>(".credits-rail");
      const spark = parcela.querySelector<HTMLElement>(".credits-spark");
      const gi = parcela.dataset.parcela ?? "0";
      const label = root.querySelector<HTMLElement>(`[data-credit-group="${gi}"]`);
      const nombres = Array.from(
        root.querySelectorAll<HTMLElement>(`[data-credit][data-parcela="${gi}"]`),
      );

      if (rail) {
        tl.fromTo(
          rail,
          { scaleY: 0, transformOrigin: "0 0" },
          { scaleY: 1, duration: 0.5, ease: HARD, immediateRender: false },
          at,
        );
      }
      if (label) {
        tl.fromTo(
          label,
          { clipPath: "inset(0 100% 0 0)" },
          { clipPath: "inset(0 0% 0 0)", duration: 0.42, ease: HARD, immediateRender: false },
          at + 0.14,
        );
      }
      if (spark) {
        // Velocidad constante y misma duracion en las cuatro: como las
        // parcelas miden lo mismo, las cuatro chispas llegan abajo A LA VEZ.
        tl.fromTo(
          spark,
          { yPercent: 0, opacity: 1 },
          {
            yPercent: 100 * (parcela.offsetHeight / spark.offsetHeight),
            opacity: 0,
            duration: 0.62,
            ease: "none",
            immediateRender: false,
          },
          at + 0.26,
        );
      }
      tl.call(
        () => {
          for (const n of nombres) n.classList.add("is-caught");
          /*
           * La lampara es un gesto de ENTRADA, no un estado permanente de
           * la `animation`. En movil solo la parcela activa muestra sus
           * nombres (`display: none` en las otras tres) y un nombre oculto
           * no ejecuta una animation aunque ya tenga la clase — el
           * navegador la retoma de cero en cuanto el nodo vuelve a
           * pintarse. Sin este ajuste, abrir despues un territorio plegado
           * hace destellar sus nombres como si acabaran de entrar, fuera
           * del scroll que le daba sentido al gesto.
           *
           * 1100ms cubre el peor caso real: 620ms (el maximo de
           * `--skill-d`) + 400ms (duracion de la lampara) + margen. Pasado
           * ese tiempo, `is-caught-still` apaga la `animation` (ver
           * themes.css) — visible o no en ese instante — y el color que
           * queda es el de reposo normal de la cascada: el fotograma 100%
           * de `hypr-lampara` ya esta vacio, asi que apagar la animation o
           * dejarla corriendo mas alla de su fin da el MISMO resultado
           * visual. `animation: none` de verdad libera el objeto
           * `Animation`, en vez de dejarlo para siempre en fase "after".
           */
          const timerId = window.setTimeout(() => {
            for (const n of nombres) n.classList.add("is-caught-still");
          }, 1100);
          timerWindow.__hyprSkillTimers?.push(timerId);
        },
        [],
        at + 0.26,
      );
    });

    const strips = Array.from(root.querySelectorAll<HTMLElement>("[data-credit-strip]"));
    tl.fromTo(
      strips,
      { opacity: 0, y: 14 },
      { opacity: 1, y: 0, duration: 0.62, ease: SLOW, immediateRender: false },
      0.9,
    );

    // Sonda del arnes: el ritmo se mide con tl.progress() desde dentro de la
    // pagina; page.screenshot() en headless perturba GSAP.
    (window as unknown as { __hyprSkills?: ReturnType<Gsap["timeline"]> }).__hyprSkills = tl;

    // Colores resueltos una vez, fuera del bucle de interaccion: `--l3` y
    // `--haze` son estaticos en Hyprland (themes.css), y GSAP interpola mejor
    // un hex resuelto que un `var()` crudo, que no siempre se parsea igual en
    // todos los navegadores dentro de un tween de color.
    const vars = getComputedStyle(root);
    const L3 = vars.getPropertyValue("--l3").trim() || "#ffa03c";
    const HAZE = vars.getPropertyValue("--haze").trim() || "#b18c86";

    // Gesto 5 — el apuntado. Vive FUERA de `tl` a proposito: la asercion 13
    // del arnes cuenta los targets de `window.__hyprSkills`, y estos tweens
    // no son del gesto de entrada (que pasa UNA vez) sino de una interaccion
    // que se repite sin fin. Colgarlos de `tl` los mezclaria y ademas
    // rompería esa cuenta.
    parcelas.forEach((parcela, gi) => {
      const glow = parcela.querySelector<HTMLElement>(".credits-glow");
      if (!glow) return;

      const strip = root.querySelector<HTMLElement>(`[data-credit-strip][data-parcela="${gi}"]`);
      const marcasRow = root.querySelector<HTMLElement>(
        `[data-credit-marks-row][data-parcela="${gi}"]`,
      );
      const marcas = marcasRow
        ? Array.from(marcasRow.querySelectorAll<HTMLElement>(".credits-mark"))
        : [];
      const label = root.querySelector<HTMLElement>(`[data-credit-group="${gi}"]`);
      const nombres = Array.from(
        root.querySelectorAll<HTMLElement>(`[data-credit][data-parcela="${gi}"]`),
      );

      /*
       * La luz del lindero no salta a la fila: la lleva un `quickTo`, asi
       * que al recorrer nombres VIAJA por el carril y un salto de Git a
       * Gemini CLI se ve recorrer. Es la misma idea de la entrada —
       * corriente por un cable — sostenida dentro del apuntado en vez de
       * abandonada al acabar: hay un objeto fisico moviendose, no estados
       * relevandose.
       */
      const mover = gsap.quickTo(glow, "y", { duration: 0.42, ease: "power4.out" });

      const apuntar = (boton: HTMLElement, i: number): void => {
        mover(boton.offsetTop + boton.offsetHeight / 2 - 19);
        gsap.to(glow, { opacity: 1, duration: 0.42 });
        // Se realza QUITANDO, no anadiendo: nada de `filter` ni
        // `box-shadow`, la linea roja con un shader a pantalla completa
        // detras.
        if (marcas.length > 0) {
          gsap.to(marcas, { opacity: 0.42, scale: 1, duration: 0.42, ease: "power3.out" });
          const marcaActiva = marcas[i];
          if (marcaActiva) {
            gsap.to(marcaActiva, { opacity: 1, scale: 1.28, duration: 0.42, ease: "power3.out" });
          }
        }
        // El rotulo del area va lento A PROPOSITO: apuntar Django no solo
        // enciende Django, calienta despacio "Backend y datos". Lo rapido es
        // la accion, lo lento es el contexto.
        if (label) gsap.to(label, { color: L3, duration: 0.9, ease: "power3.out" });
      };

      const apagar = (relatedTarget: EventTarget | null): void => {
        // Moverse ENTRE nombres de la MISMA parcela no apaga nada: solo la
        // luz viaja de uno a otro. Apagar aqui reintroduciria el parpadeo
        // fila a fila que el `quickTo` existe para evitar.
        if (relatedTarget instanceof HTMLElement && nombres.includes(relatedTarget)) return;
        gsap.to(glow, { opacity: 0, duration: 0.9 });
        if (marcas.length > 0) {
          gsap.to(marcas, { opacity: 1, scale: 1, duration: 0.9, ease: "power3.out" });
        }
        if (label) gsap.to(label, { color: HAZE, duration: 0.9, ease: "power3.out" });
      };

      /*
       * `credits.ts` registra SUS propios `mouseenter`/`focus`/`click` en
       * `select()` sobre estos mismos botones — pinta el panel/franja
       * compartidos y marca `.is-active`/`data-credit-picked`. Los dos
       * conjuntos de listeners son independientes (ninguno lee ni cancela
       * lo que escribe el otro: este solo mueve la luz, el friso y el
       * rotulo) y el navegador los ejecuta en el orden en que se
       * registraron, asi que el orden importa solo si algun dia uno de los
       * dos empieza a depender de un efecto secundario del otro dentro del
       * mismo evento — hoy no ocurre.
       */
      nombres.forEach((boton, i) => {
        boton.addEventListener("mouseenter", () => apuntar(boton, i));
        boton.addEventListener("focus", () => apuntar(boton, i));
        boton.addEventListener("mouseleave", (ev) => apagar((ev as MouseEvent).relatedTarget));
        boton.addEventListener("focusout", (ev) => apagar((ev as FocusEvent).relatedTarget));
      });

      /*
       * El rodillo de la franja: escucha `STRIP_REPAINT_EVENT` (ver
       * `credits.ts`, `repintarFranja`) en vez de parchear el
       * `replaceChildren` nativo del nodo. Diferencia real frente a la
       * version anterior: el gancho ahora es un evento tipado con nombre
       * propio, declarado y exportado por `credits.ts` — grepeable desde el
       * fichero que de verdad pinta la franja — en vez de depender de una
       * firma implicita ("select() llama `strip.replaceChildren(<nodo>)`")
       * que ningun tipo protegia. Si `repintarFranja` cambiara de metodo de
       * insercion, el rodillo se enteraria del cambio de compilar, no
       * dejaria de dispararse en silencio.
       *
       * `dataset.hyprRodillo` evita el enganche doble: `hyprChoreography`
       * puede volver a ejecutarse (resize, refresh de ScrollTrigger) sobre
       * el MISMO nodo `strip`, y un segundo `addEventListener` produciria
       * dos rodillos corriendo a la vez sobre la misma franja.
       */
      if (strip && !strip.dataset.hyprRodillo) {
        strip.dataset.hyprRodillo = "1";
        // Solo un `viejo` puede estar "saliendo" a la vez: si llega un
        // repintado nuevo mientras el anterior sigue en su animacion de
        // salida (barrido rapido, varias selecciones dentro de los 420ms
        // del rodillo), se corta ya en vez de dejar que se apilen dos
        // salidas — verificado con 6 selecciones en 600ms: debe quedar 1
        // `.credits-strip-in`.
        let saliendo: HTMLElement | null = null;
        strip.addEventListener(STRIP_REPAINT_EVENT, ((ev: CustomEvent<StripRepaintDetail>) => {
          const { nuevo, viejo } = ev.detail;
          if (saliendo) {
            gsap.killTweensOf(saliendo);
            saliendo.remove();
            saliendo = null;
          }
          // Lo nuevo entra por abajo. `credits.ts` ya lo dejo como hijo
          // real de `strip` antes de disparar el evento — `immediateRender`
          // (por defecto en `fromTo`) aplica el estado inicial en el mismo
          // tick, asi que no hay fotograma intermedio visible con el nodo a
          // pelo.
          gsap.fromTo(
            nuevo,
            { yPercent: 100, opacity: 0 },
            { yPercent: 0, opacity: 1, duration: 0.42, ease: "power4.out" },
          );
          // Lo viejo sale por arriba. `replaceChildren` ya lo retiro del
          // DOM antes de que este listener lo viera — se reinserta para
          // poder animarlo, superpuesto a `nuevo` (los dos van siempre en
          // `position: absolute`, ver `.credits-strip-in` en themes.css).
          if (viejo) {
            strip.appendChild(viejo);
            saliendo = viejo;
            gsap.to(viejo, {
              yPercent: -100,
              opacity: 0,
              duration: 0.3,
              ease: "power2.in",
              onComplete: () => {
                viejo.remove();
                if (saliendo === viejo) saliendo = null;
              },
            });
          }
        }) as EventListener);
      }
    });
  }
};

export default hyprChoreography;
