import type { Choreography } from "./choreography";

const ID = "hypr";

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
 * Movimiento reducido: esta funcion entera (y por tanto sus 3 gestos) NUNCA
 * se ejecuta bajo `prefers-reduced-motion: reduce` — `initScrollReveal`
 * (`src/utils/reveal.ts`) hace early-return antes de invocar
 * `theme.choreography()`, y ese guardian es compartido por los tres temas
 * (no se toca aqui: tocarlo afectaria a Vice y Caelestia). Lo que sobrevive
 * bajo `reduce` es el contenido base en HTML/CSS, sin ninguna de las clases
 * que reparte el gesto 0 ni el escalonado de `--hypr-d`.
 */
/*
 * La coreografia de Hyprland ya no crea ningun tween: los gestos que lo
 * hacian (4 y 5, el catastro de creditos) se retiraron el 2026-09-09 junto
 * con su CSS y su arnes. Por eso `gsap` YA NO se desestructura del contexto
 * aqui — sin uso, `eslint` lo marca como variable muerta. Si un gesto futuro
 * vuelve a necesitar GSAP, desestructuralo de nuevo del contexto que recibe
 * esta funcion (`({ gsap, ScrollTrigger, root }) => {...}`), NUNCA de un
 * `gsap` suelto del ambito global: sin la palabra en el destructuring el
 * modulo compila y pasa el lint —el identificador existe como global en los
 * tipos— pero el chunk construido revienta con `gsap is not defined` en
 * cuanto `reveal.ts` llama a la coreografia, y la seccion de creditos se
 * queda sin sus gestos durante semanas sin que nada lo avise salvo la
 * consola del navegador. Ya paso una vez en este mismo tema.
 */
export const hyprChoreography: Choreography = ({ ScrollTrigger, root }) => {
  ScrollTrigger.getAll()
    .filter((t) => typeof t.vars.id === "string" && t.vars.id.startsWith(ID))
    .forEach((t) => t.kill());

  // Limpieza de un remonte anterior: la placa puede haber quedado
  // `placa-lit` de un montaje previo (HMR de Vite recargando este modulo sin
  // recargar la pagina entera; la produccion real solo invoca la
  // coreografia una vez por carga), asi que se retira para que su entrada
  // (gesto 0b) vuelva a correr entera.
  root.querySelector<HTMLElement>("[data-placa]")?.classList.remove("placa-lit");

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

    // La placa dispara su propia entrada, no la de la seccion: la placa
    // vive 239px por debajo del borde superior de la seccion en escritorio
    // y 161px en movil. Con `is-lit` de la seccion (arranca a `top 90%` de
    // la SECCION), las siete celdas aterrizaban a los 1200ms con la placa
    // 119px bajo el pliegue en una ventana de 900 (1019 sobre 900) y 41px
    // bajo el pliegue en una de 844 (885 sobre 844) — la entrada corria
    // entera fuera de pantalla. Umbral propio, anclado a la caja de la
    // placa, no a la seccion que la contiene.
    ScrollTrigger.create({
      id: `${ID}-placa`,
      trigger: placa,
      start: "top 80%",
      once: true,
      onEnter: () => placa.classList.add("placa-lit"),
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
  // callback. Sin esto, un scroll rapido deja secciones en blanco. La placa
  // entra en la misma red, con su propio umbral (0.8), para que un scroll
  // rapido tampoco la deje sin encender.
  const net = (): void => {
    scenes.forEach((scene) => {
      const r = scene.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.9 && r.bottom > 0) scene.classList.add("is-lit");
    });
    if (placa) {
      const r = placa.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.8 && r.bottom > 0) placa.classList.add("placa-lit");
    }
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
};

export default hyprChoreography;
