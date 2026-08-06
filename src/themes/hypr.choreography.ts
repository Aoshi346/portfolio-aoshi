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
};

export default hyprChoreography;
