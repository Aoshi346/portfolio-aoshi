import type { Choreography, Gsap } from "./choreography";

const ID = "hypr";

// Los dos regimenes de tiempo del vocabulario global (corte / atmosfera),
// mismos valores que `--hard`/`--slow` en themes.css. Duplicados aqui porque
// GSAP no puede leer un `cubic-bezier()` desde una custom property de CSS.
const HARD = "cubic-bezier(0.7, 0, 0.2, 1)";
const SLOW = "cubic-bezier(0.16, 0.84, 0.28, 1)";

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
 */
export const hyprChoreography: Choreography = ({ gsap, ScrollTrigger, root }) => {
  ScrollTrigger.getAll()
    .filter((t) => typeof t.vars.id === "string" && t.vars.id.startsWith(ID))
    .forEach((t) => t.kill());

  const scenes = Array.from(root.querySelectorAll<HTMLElement>("[data-scene]"));

  // Gesto 0 — repartir la gramatica.
  // El DOM lo construyen las secciones, que son COMPARTIDAS por los tres
  // temas y no pueden llevar clases de uno solo. Asi que las reparte aqui el
  // tema, junto con su escalonado: sin este paso, `.hypr-cut` y compania
  // existirian en la hoja sin aplicarse a nada, y `--hypr-d` se quedaria a 0
  // dejando todas las entradas simultaneas.
  const RECETA: ReadonlyArray<readonly [string, string]> = [
    [".hero-kick", "hypr-cut"],
    [".display-xl, .display-lg, .contacto-title, .about-name", "hypr-up"],
    [".lead, .contacto-lead", "hypr-up"],
    [".about-pair", "hypr-up"],
    [".contacto-estado", "hypr-up"],
    ['[class*="contacto-bar--"]', "hypr-up"],
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

  // Gesto 2 — la tira de exposicion. Solo en escritorio y sin movimiento
  // reducido: el mismo contrato de breakpoint que el CSS de la tarea 4.
  const mm = gsap.matchMedia();
  mm.add("(min-width: 821px) and (prefers-reduced-motion: no-preference)", () => {
    const obras = Array.from(root.querySelectorAll<HTMLElement>('[data-scene="obra"]'));
    if (obras.length === 0) return;

    obras.forEach((obra, i) => {
      obra.style.setProperty("--hypr-e", String(16 + i * 13));
      const open = (): void => {
        obras.forEach((o) => o.classList.toggle("is-open", o === obra));
      };
      obra.addEventListener("pointerenter", open);
      obra.addEventListener("focusin", open);
    });
    obras[0].classList.add("is-open");

    return () => {
      obras.forEach((o) => o.classList.remove("is-open"));
    };
  });

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
          window.setTimeout(() => {
            for (const n of nombres) n.classList.add("is-caught-still");
          }, 1100);
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
  }
};

export default hyprChoreography;
