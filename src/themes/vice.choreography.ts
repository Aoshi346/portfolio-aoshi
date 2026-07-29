import type { Choreography, Gsap, ScrollTriggerApi } from "./choreography";

/** Id fijo del ScrollTrigger del zoom: permite matarlo si la funcion se re-ejecuta. */
const HERO_ZOOM_TRIGGER_ID = "vice-hero-zoom";

/**
 * Timeline de entrada (sin scrollTrigger, por eso no la mata `ScrollTrigger.getById`).
 * Se guarda a nivel de modulo para poder matarla si `scene1Title` se re-ejecutara,
 * evitando que quede corriendo sobre spans de caracteres ya destruidos por el
 * siguiente `splitChars`.
 */
let introTimeline: ReturnType<Gsap["timeline"]> | null = null;

/**
 * Marca si el zoom ya forzo el final de la entrada. La entrada corre en tiempo
 * real (sin scrollTrigger) y escribe `scale`/`filter` sobre el MISMO nodo que
 * el zoom: si alguien scrollea antes de que termine (2.4 s) las dos timelines
 * pelean por esas propiedades frame a frame. Al primer scroll real dentro del
 * pin se salta la entrada a su fotograma final y a partir de ahi solo manda el
 * zoom. Es un flag aparte y no `introTimeline = null` porque esa referencia la
 * sigue necesitando el kill defensivo de `scene1Title`.
 */
let introSkipped = false;

/**
 * Parte el texto en spans por caracter, agrupados por palabra para que la
 * linea siga rompiendo donde toca. A mano en vez de con SplitText para no
 * atar el redisenio a la disponibilidad del plugin.
 */
function splitChars(target: HTMLElement): HTMLElement[] {
  const text = target.textContent ?? "";
  target.textContent = "";
  const chars: HTMLElement[] = [];
  const words = text.split(" ");

  words.forEach((word, index) => {
    const wordSpan = document.createElement("span");
    wordSpan.className = "inline-block overflow-hidden whitespace-nowrap align-bottom";
    for (const character of word) {
      const charSpan = document.createElement("span");
      charSpan.className = "inline-block";
      charSpan.textContent = character;
      wordSpan.append(charSpan);
      chars.push(charSpan);
    }
    target.append(wordSpan);
    if (index < words.length - 1) target.append(document.createTextNode(" "));
  });

  return chars;
}

/**
 * Gesto 1 — Titulo de apertura: el nombre se monta y luego te atraviesa.
 *
 * El estado "pre-animacion" (opacity:1, scale:1.08, blur) ya lo fija de forma
 * SINCRONA `prepareHeroIntro` en `utils/reveal.ts`, antes de que este modulo
 * siquiera se cargue (import dinamico -> hueco async). Lo unico que hace este
 * gesto es partir el texto (sincrono, no depende de fuentes) y montar encima
 * la entrada + el zoom de salida.
 *
 * El tween de salida usa `fromTo` con los valores de partida escritos a mano
 * (scale:1, opacity:1), nunca leidos del DOM en el instante del render: leer
 * del DOM fue la causa de la regresion original (ver docs/superpowers/sdd),
 * cuando la CSS de `.js-intro` todavia no se habia retirado y GSAP capturaba
 * opacity:0 como punto de partida, animando de 0 a 0 para siempre.
 */
function scene1Title(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const hero = root.querySelector<HTMLElement>('[data-scene="hero"]');
  const name = root.querySelector<HTMLElement>("[data-hero-name]");
  if (!hero || !name) return;

  // Defensivo: si esta funcion se llamara dos veces (hoy no ocurre: el tema se
  // elige una sola vez por carga), no dejar un trigger huerfano acumulandose.
  ScrollTrigger.getById(HERO_ZOOM_TRIGGER_ID)?.kill();
  // La timeline de entrada no tiene scrollTrigger propio, asi que
  // `ScrollTrigger.getById` no la alcanza: hay que matarla a mano.
  introTimeline?.kill();

  const chars = splitChars(name);
  const fading = Array.from(root.querySelectorAll<HTMLElement>("[data-hero-fade]"));

  gsap.set(chars, { yPercent: 115 });
  gsap.set(fading, { opacity: 0, y: 24 });

  const intro = gsap.timeline();
  introTimeline = intro;
  introSkipped = false;
  // Empuje de camara: lento y sostenido, da el aire de plano de apertura.
  intro.to(name, { scale: 1, filter: "blur(0px)", duration: 2.4, ease: "power2.out" }, 0);
  // La duracion percibida la manda el stagger, no el easing: con expo.out el
  // 96% del recorrido se gastaba en 250 ms y la entrada se leia instantanea.
  intro.to(chars, { yPercent: 0, duration: 1.0, ease: "power3.out", stagger: 0.075 }, 0.25);
  intro.to(fading, { opacity: 1, y: 0, duration: 0.9, ease: "power2.out", stagger: 0.14 }, 1.5);

  const leaveUp = fading.filter((element) => element.dataset.heroFade === "up");
  const leaveDown = fading.filter((element) => element.dataset.heroFade !== "up");

  const exit = gsap.timeline({
    scrollTrigger: {
      id: HERO_ZOOM_TRIGGER_ID,
      trigger: hero,
      start: "top top",
      end: "+=185%",
      pin: true,
      scrub: 1,
      invalidateOnRefresh: true,
      /*
       * Prioridad mas alta que la del carril de obra (1), y por el mismo
       * motivo por el que aquel lleva la suya: ScrollTrigger refresca de mayor
       * a menor prioridad, y un pin solo mide bien si los pines que le
       * PRECEDEN en el documento ya han reservado su hueco.
       *
       * Medido con el carril a 1 y este sin prioridad (0): el carril se
       * refrescaba primero, no veia los 1665px (185% del viewport) que este
       * pin reserva, y situaba su inicio 1605px antes de tiempo. El resultado
       * era el carril fijado en pantalla mientras "Quien es" seguia visible,
       * los dos dibujados uno encima del otro.
       *
       * La regla, si se anaden mas pines: prioridad DESCENDENTE segun el orden
       * del documento.
       */
      refreshPriority: 2,
      /*
       * La entrada (`introTimeline`) corre en tiempo real y escribe
       * `scale`/`filter` sobre el MISMO nodo que este zoom. Si alguien
       * scrollea antes de que termine (2.4 s), las dos timelines pelean por
       * esas propiedades frame a frame y el nombre acaba en un estado que no
       * es ni el de la entrada ni el del zoom (medido: scale 0.9987 en vez de
       * 1 al volver al principio). Al primer scroll real dentro del pin se
       * salta la entrada a su fotograma final; a partir de ahi solo manda el
       * zoom. `progress > 0` nunca se cumple al cargar: el pin arranca en
       * scrollY 0, donde progress vale exactamente 0.
       */
      onUpdate: (self) => {
        if (introSkipped || self.progress <= 0) return;
        introSkipped = true;
        introTimeline?.progress(1);
      },
    },
  });

  /*
   * Tres tiempos, no uno. Antes los tres bloques de acompanamiento se iban
   * juntos en el primer 28% con `ease: none` y el efecto era que el texto
   * "desaparecia" sin motivo mientras el nombre seguia quieto.
   *
   * 1. El acompanamiento se aparta abriendo hueco: lo que esta encima del
   *    nombre sube y lo que esta debajo baja, con desenfoque, de forma que la
   *    lectura del gesto sea "se retiran para dejar ver", no "se apagan".
   * 2. El nombre retrocede un poco mientras se queda solo: ese respiro es lo
   *    que da impulso al empuje siguiente en vez de arrancarlo en frio.
   * 3. La camara lo atraviesa. La opacidad NO acompana a la escala durante
   *    todo el recorrido (asi se evaporaba antes de llenar el encuadre): se
   *    mantiene entera hasta el ultimo tramo y se funde ya fuera de plano.
   *
   * TODOS los tweens de esta timeline son `fromTo` con el punto de partida
   * escrito a mano y `immediateRender: false`. No es una preferencia de
   * estilo: es el arreglo de una regresion medida.
   *
   * Un tween con `scrub` renderiza su primer fotograma al CREARSE, y esta
   * timeline se crea en el mismo tick que la entrada — o sea, antes de que la
   * entrada haya animado nada. En ese instante GSAP cachea como "punto de
   * partida" lo que hay en el DOM, que es el estado PRE-entrada:
   * `opacity: 0, y: 24` en los bloques de acompanamiento (lo deja el
   * `gsap.set` de arriba) y `blur(7px)` en el nombre (lo deja
   * `prepareHeroIntro`). Consecuencias medidas en 1440x900, bajando hasta el
   * final del pin y volviendo arriba:
   *
   *   - rol, subtitulo y esquina se apagaban a los ~200px de scroll y al
   *     volver al principio NO reaparecian nunca (opacity 0, y 24): la
   *     pantalla se quedaba con el nombre solo, sin contexto.
   *   - el nombre volvia con `blur(7px)` pegado para siempre, y de hecho ya
   *     salia desenfocado a los 600px de bajada.
   *
   * Es la misma clase de fallo que la regresion historica documentada arriba
   * (leer el punto de partida del DOM en el instante del render), pero en
   * `filter` y en los bloques de acompanamiento, donde no se aplico la
   * leccion. `immediateRender: false` ademas evita que este primer render
   * pise el estado que acaba de fijar `prepareHeroIntro`.
   */
  exit.fromTo(
    leaveUp,
    { opacity: 1, y: 0, filter: "blur(0px)" },
    {
      opacity: 0,
      y: -64,
      filter: "blur(5px)",
      ease: "power2.in",
      duration: 0.44,
      immediateRender: false,
    },
    0,
  );
  exit.fromTo(
    leaveDown,
    { opacity: 1, y: 0, filter: "blur(0px)" },
    {
      opacity: 0,
      y: 64,
      filter: "blur(5px)",
      ease: "power2.in",
      duration: 0.44,
      stagger: 0.07,
      immediateRender: false,
    },
    0.04,
  );
  exit.fromTo(
    name,
    { scale: 1, filter: "blur(0px)" },
    {
      scale: 0.94,
      filter: "blur(0px)",
      ease: "power2.out",
      duration: 0.52,
      immediateRender: false,
    },
    0,
  );
  exit.fromTo(
    name,
    { scale: 0.94, filter: "blur(0px)" },
    { scale: 9, filter: "blur(6px)", ease: "power2.in", duration: 1.05, immediateRender: false },
    0.6,
  );
  exit.fromTo(
    name,
    { opacity: 1 },
    { opacity: 0, ease: "power1.in", duration: 0.4, immediateRender: false },
    1.25,
  );
}

/**
 * Recomposicion de un rotulo al entrar: se parte en caracteres y cada uno sube
 * desde detras de su linea, estirado, como un cartel que se monta letra a
 * letra. Es el mismo gesto del titulo de apertura aplicado a las cabeceras de
 * escena, que es lo que da continuidad de pieza en vez de "secciones sueltas".
 *
 * Devuelve los caracteres por si quien llama quiere encadenar algo detras.
 */
function composeTitle(
  gsap: Gsap,
  target: HTMLElement,
  trigger: { trigger: HTMLElement; start: string; toggleActions: string },
  id: string,
  delay = 0,
): HTMLElement[] {
  const chars = splitChars(target);
  // `fromTo` con los dos extremos a mano por la misma razon que en el resto del
  // archivo: nunca dejar que GSAP deduzca un extremo leyendo el DOM.
  gsap.fromTo(
    chars,
    { yPercent: 118, opacity: 0, scaleY: 1.28 },
    {
      yPercent: 0,
      opacity: 1,
      scaleY: 1,
      transformOrigin: "50% 100%",
      duration: 0.72,
      ease: "power3.out",
      stagger: 0.028,
      delay,
      scrollTrigger: { ...trigger, id },
    },
  );
  return chars;
}

/** Timeline del leader de apertura: se guarda para poder matarla si esta funcion se re-ejecutara. */
let leaderTimeline: ReturnType<Gsap["timeline"]> | null = null;

/** Duracion de cada numero de la cuenta atras. Tres numeros ~= 0.96s. */
const LEADER_COUNT_STEP = 0.32;

/**
 * Gesto 0 — Leader de apertura. Cuenta atras de academia (3-2-1) con el brazo
 * barredor dando una vuelta por numero y, al llegar a uno, el propio circulo
 * se abre como un diafragma: el iris deja ver el hero por dentro.
 *
 * El iris es una MASCARA con un agujero que crece, no un `clip-path` que
 * encoge. La diferencia importa: encoger el recorte del leader revelaria la
 * pantalla desde los bordes hacia dentro, que es el gesto contrario. Un
 * radial-gradient transparente en el centro y opaco fuera, con el tamano de
 * mascara animado de 0% a 320%, abre justo donde estaba el numero.
 *
 * `[data-intro-leader]` solo existe si `main.ts` decidio montarlo (Vice, sin
 * `prefers-reduced-motion`). Si no esta, esta funcion no hace nada.
 */
function sceneIntro(gsap: Gsap): void {
  const leader = document.querySelector<HTMLElement>("[data-intro-leader]");
  if (!leader) return;

  leaderTimeline?.kill();

  const ring = leader.querySelector<HTMLElement>("[data-leader-ring]");
  const sweep = leader.querySelector<HTMLElement>("[data-leader-sweep]");
  const num = leader.querySelector<HTMLElement>("[data-leader-num]");
  const cue = leader.querySelector<HTMLElement>("[data-leader-cue]");

  const iris = leader.querySelector<HTMLElement>("[data-leader-iris]");

  const tl = gsap.timeline({
    onComplete: () => {
      document.documentElement.classList.remove("js-leader");
      leader.remove();
    },
  });
  leaderTimeline = tl;

  // Avisa a `main.ts` de que el gesto arranca AHORA, para que rearme su seguro
  // contando desde aqui y no desde la carga de la pagina: entre una cosa y
  // otra pasa cerca de un segundo (GSAP + Lenis + este modulo).
  window.dispatchEvent(new Event("leader:start"));

  // Cuenta atras: cada numero, una vuelta completa del brazo.
  ["3", "2", "1"].forEach((label, index) => {
    const at = index * LEADER_COUNT_STEP;
    if (num) {
      tl.call(() => {
        num.textContent = label;
      }, [], at);
      // El numero entra con un punto de escala: acompana al golpe de la vuelta.
      tl.fromTo(
        num,
        { scale: 1.35, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.18, ease: "power3.out" },
        at,
      );
    }
    if (sweep) {
      tl.fromTo(
        sweep,
        { rotation: 0 },
        { rotation: 360, duration: LEADER_COUNT_STEP, ease: "none" },
        at,
      );
    }
    if (cue) {
      // El punto de bobina marca cada numero con un destello corto.
      tl.fromTo(
        cue,
        { opacity: 0 },
        { opacity: 1, duration: 0.06, ease: "none", yoyo: true, repeat: 1 },
        at,
      );
    }
  });

  const irisAt = LEADER_COUNT_STEP * 3;

  /*
   * El anillo crece y se desvanece a la vez que el agujero: es el borde del
   * diafragma abriendose, no un elemento que desaparece por su cuenta. Sin
   * esto, el circulo se quedaba quieto mientras la mascara crecia y el gesto
   * perdia la relacion entre "lo que contaba" y "la puerta".
   */
  if (ring) {
    tl.to(ring, { scale: 3.4, opacity: 0, duration: 0.52, ease: "power2.in" }, irisAt);
  }
  if (num) {
    tl.to(num, { opacity: 0, duration: 0.16, ease: "power1.in" }, irisAt);
  }

  if (iris) {
    /*
     * Abre el agujero de la mascara (ver `--iris` en `style.css`). El 100% es
     * la esquina mas lejana del viewport; se va hasta 150% para que el ultimo
     * tramo del recorrido no se pase el rato retirando esquinas ya vacias.
     * `fromTo` con los dos extremos a mano, como todo lo demas de este
     * archivo: leer el extremo del DOM es justo lo que ha causado aqui tres
     * regresiones.
     */
    tl.fromTo(
      iris,
      { "--iris": "0%" },
      { "--iris": "150%", duration: 0.66, ease: "power2.inOut" },
      irisAt,
    );
  }
}

/** Ids fijos de los ScrollTrigger del gesto 2: permiten matarlos si la funcion se re-ejecuta. */
const ABOUT_TRIGGER_IDS = ["vice-about-head", "vice-about-pairs"];

/**
 * Las dos timelines del gesto 2, a nivel de modulo. Matar el ScrollTrigger por
 * id no mata la timeline que lo lleva colgado, y esta parte spans de caracteres
 * con `splitChars`: si `scene2Card` se re-ejecutara, la timeline vieja seguiria
 * corriendo sobre nodos que el nuevo `splitChars` ya ha destruido. Mismo motivo
 * y mismo patron que `introTimeline` en el gesto 1.
 */
let aboutTimelines: ReturnType<Gsap["timeline"]>[] = [];

/**
 * Gesto 2 — Afirmacion y prueba.
 *
 * Spec: docs/superpowers/specs/2026-07-29-about-afirmacion-prueba-design.md
 *
 * Cuatro cosas cambian respecto de la version anterior, y las cuatro salen de
 * un defecto medido:
 *
 * 1. NINGUN trigger se ancla a `[data-scene]`. A 1440x900, 202,5px de esa caja
 *    son padding de tema (`themes.css`) y la seccion es `min-h-screen
 *    justify-center`, asi que el primer pixel util caia en 924px — 24px POR
 *    DEBAJO del pliegue. Con `start: "top 78%"` los delays de 0,35s y 0,5s se
 *    gastaban con el bloque fuera de pantalla: el usuario veia el fotograma
 *    final, no el gesto. Y el desplazamiento variaba con el alto del
 *    contenido, o sea que el ancla estaba calibrada contra algo que se mueve.
 *    Cada timeline se ancla ahora a su primer nodo de contenido.
 * 2. Timelines, no tweens sueltos con `delay`. Con cuatro tweens
 *    independientes la reversa colapsaba simultanea en vez de ser el inverso
 *    del montaje: el `delay` se consume al final del recorrido inverso.
 * 3. Cero `gsap.from`. Deduce un extremo leyendo el estado de reposo del DOM, y
 *    este rediseno cambia ese estado de reposo (el conector reposa al 22%).
 * 4. El parallax de la ficha muere. ~1800px de scroll invalidando un
 *    `backdrop-filter: blur(6px)` encima del canvas WebGL cada frame, a cambio
 *    de 39px de recorrido total imperceptible.
 */
function scene2Card(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const about = root.querySelector<HTMLElement>('[data-scene="about"]');
  if (!about) return;

  // Defensivo, igual que en `scene1Title`: si esta funcion se llamara dos
  // veces no dejar triggers ni timelines huerfanas acumulandose.
  for (const id of ABOUT_TRIGGER_IDS) ScrollTrigger.getById(id)?.kill();
  for (const timeline of aboutTimelines) timeline.kill();
  aboutTimelines = [];

  const head = about.querySelector<HTMLElement>(".about-head");
  const pairs = about.querySelector<HTMLElement>("[data-focus-pairs]");

  if (head) {
    /*
     * T1 — la cabecera. `start: "top 86%"` deja ~126px de contenido visible al
     * disparar: espacio para que el retrato (188px) acabe de entrar antes de
     * que el nombre termine de subir.
     */
    const portrait = head.querySelector<HTMLElement>("[data-portrait]");
    const chip = head.querySelector<HTMLElement>(".about-status");
    // El par "Estudia" esta oculto en Vice: incluirlo desbarataria el escalonado
    // (cuatro tiempos para tres datos visibles) sin que se vea nada moverse.
    const meta = Array.from(
      head.querySelectorAll<HTMLElement>('.about-facts dd:not([data-fact="estudia"])'),
    );
    const lead = about.querySelector<HTMLElement>('[data-line="lead"] > *');
    // Las dos lineas del nombre se parten por separado para que cada una siga
    // siendo una linea: `splitChars` agrupa por palabra, no reflowea el bloque.
    const chars = Array.from(
      head.querySelectorAll<HTMLElement>(".about-name-first, .about-name-rest"),
    ).flatMap((line) => splitChars(line));

    const tl = gsap.timeline({
      scrollTrigger: {
        id: ABOUT_TRIGGER_IDS[0],
        trigger: head,
        start: "top 86%",
        toggleActions: "play none none reverse",
      },
    });
    aboutTimelines.push(tl);

    if (portrait) {
      // El retrato se revela desde arriba, no se desliza: es una foto que
      // aparece, y el `clipPath` recorta tambien la capa de duotono (por eso el
      // tween va en el envoltorio y no en el `<img>`).
      tl.fromTo(
        portrait,
        { scale: 0.9, opacity: 0, clipPath: "inset(0 0 20% 0)" },
        { scale: 1, opacity: 1, clipPath: "inset(0 0 0% 0)", duration: 0.52, ease: "power3.out" },
        0,
      );
    }
    if (chars.length > 0) {
      tl.fromTo(
        chars,
        { yPercent: 118, opacity: 0 },
        { yPercent: 0, opacity: 1, duration: 0.72, ease: "power3.out", stagger: 0.028 },
        0.06,
      );
    }
    if (chip) {
      tl.fromTo(
        chip,
        { y: 12, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.4, ease: "power2.out" },
        0.4,
      );
    }
    if (meta.length > 0) {
      tl.fromTo(
        meta,
        { y: 10, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.4, ease: "power2.out", stagger: 0.05 },
        0.44,
      );
    }
    if (lead) {
      tl.fromTo(
        lead,
        { yPercent: 105, opacity: 0 },
        { yPercent: 0, opacity: 1, duration: 0.62, ease: "power3.out" },
        0.56,
      );
    }
  }

  if (pairs) {
    /*
     * T2 — el bloque firma. Se ancla al bloque, no a la seccion, por lo mismo
     * que T1: cuando este trigger dispara, las parejas estan a ~108px del
     * pliegue y el escalonado se ve entero.
     */
    const rule = pairs.querySelector<HTMLElement>("[data-pairs-rule]");
    const claims = Array.from(pairs.querySelectorAll<HTMLElement>("[data-claim]"));
    const links = Array.from(pairs.querySelectorAll<HTMLElement>("[data-link]"));
    const proofs = Array.from(pairs.querySelectorAll<HTMLElement>("[data-proof]"));
    const footItems = Array.from(
      about.querySelectorAll<HTMLElement>(
        '[data-track-col="path"] .about-h, [data-track-col="path"] .about-item',
      ),
    );
    const note = about.querySelector<HTMLElement>('[data-line="note"] > *');

    const tl = gsap.timeline({
      scrollTrigger: {
        id: ABOUT_TRIGGER_IDS[1],
        trigger: pairs,
        start: "top 88%",
        toggleActions: "play none none reverse",
      },
    });
    aboutTimelines.push(tl);

    if (rule) {
      // `transformOrigin` explicito en todos los `scaleX` de este gesto: GSAP
      // lee el valor computado si no se le dice, y el default del navegador es
      // el centro — la regla se abriria desde el medio hacia los dos lados.
      tl.fromTo(
        rule,
        { scaleX: 0 },
        { scaleX: 1, transformOrigin: "0% 50%", duration: 0.5, ease: "power2.inOut" },
        0,
      );
    }
    if (claims.length > 0) {
      tl.fromTo(
        claims,
        { x: -14, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.42, ease: "power2.out", stagger: 0.09 },
        0.14,
      );
    }
    if (links.length > 0) {
      /*
       * El conector entra a `scaleX: 1` de SU ENVOLTORIO, que multiplica el
       * 0.22 que el CSS mantiene en `.about-ln`: el resultado visible es el 22%,
       * que es el reposo del elemento firma y el punto de partida del hover. El
       * reparto en dos nodos no es adorno — un transform inline de GSAP gana
       * siempre a una regla CSS, asi que si la timeline escribiera el mismo
       * nodo que el hover, el hover se quedaria sin recorrido.
       */
      tl.fromTo(
        links,
        { scaleX: 0 },
        { scaleX: 1, transformOrigin: "0% 50%", duration: 0.36, ease: "power2.out", stagger: 0.09 },
        0.22,
      );
    }
    if (proofs.length > 0) {
      /*
       * La prueba entra como un bloque: el detalle (`description`) NO lleva
       * tween propio. Se lo sumaria al `x` del padre y entraria desde -32px
       * mientras los demas entran desde -16px. No rompe, pero se ve.
       */
      tl.fromTo(
        proofs,
        { x: 16, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.42, ease: "power2.out", stagger: 0.09 },
        0.26,
      );
    }
    if (footItems.length > 0) {
      // Por elemento y no como bloque: mover una masa de texto de golpe deja al
      // ojo sin saber donde mirar. Escalonado, la lectura va de arriba abajo,
      // que es el orden en que se lee igualmente.
      tl.fromTo(
        footItems,
        { x: -18, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.42, ease: "power2.out", stagger: 0.045 },
        0.62,
      );
    }
    if (note) {
      tl.fromTo(
        note,
        { yPercent: 105, opacity: 0 },
        { yPercent: 0, opacity: 1, duration: 0.62, ease: "power3.out" },
        0.78,
      );
    }
  }
}

/** Ids fijos del gesto 3, parametrizados por indice: puede haber varias escenas de obra. */
function obraTriggerIds(index: number): string[] {
  return [
    `vice-obra-ord-${index}`,
    `vice-obra-title-${index}`,
    `vice-obra-lead-${index}`,
    `vice-obra-meta-${index}`,
    `vice-obra-mask-${index}`,
    `vice-obra-gallery-${index}`,
    `vice-obra-parallax-${index}`,
  ];
}

/**
 * Contexto de media queries del carril de obra. Se guarda a nivel de modulo
 * para poder revertirlo si `scene3Slate` se re-ejecutara: al revertir, GSAP
 * deshace TODO lo creado dentro (tweens, triggers y el pin), que es justo lo
 * que hace falta al cambiar entre recorrido horizontal y pila vertical.
 */
let obraContext: ReturnType<Gsap["matchMedia"]> | null = null;

/**
 * Entrada de UNA cartela. `container` es la timeline del recorrido horizontal
 * cuando la obra se recorre de lado: sin ella, ScrollTrigger mediria la
 * posicion de la escena contra el scroll vertical, y en un carril fijado en
 * pantalla esa posicion no cambia nunca (todas las cartelas entrarian a la vez
 * al fijarse el carril). Con `containerAnimation` mide contra el avance
 * horizontal, que es el eje real por el que la escena cruza el encuadre.
 */
function buildSlate(
  gsap: Gsap,
  scene: HTMLElement,
  ids: string[],
  container: gsap.core.Tween | null,
): void {
  // En horizontal el borde de referencia es el izquierdo, no el superior.
  const trigger = container
    ? ({
        trigger: scene,
        containerAnimation: container,
        start: "left 78%",
        toggleActions: "play none none reverse",
      } as const)
    : ({
        trigger: scene,
        start: "top 76%",
        toggleActions: "play none none reverse",
      } as const);
  {
    const ordinal = scene.querySelector<HTMLElement>("[data-ord]");
    const title = scene.querySelector<HTMLElement>("[data-title]");
    const lead = scene.querySelector<HTMLElement>(".lead");
    const meta = scene.querySelector<HTMLElement>("[data-meta]");
    const masks = Array.from(scene.querySelectorAll<HTMLElement>("[data-mask]"));
    const gallery = scene.querySelector<HTMLElement>("[data-gallery]");

    if (ordinal) {
      gsap.from(ordinal, {
        y: -70,
        scale: 1.35,
        opacity: 0,
        duration: 0.7,
        ease: "expo.out",
        scrollTrigger: { ...trigger, id: ids[0] },
      });
    }
    if (title) {
      // El titulo de la cartela se monta letra a letra, como el de apertura:
      // es la cabecera de la escena y merece el mismo gesto, no un fundido.
      composeTitle(gsap, title, trigger, ids[1], 0.08);
    }
    if (lead) {
      gsap.from(lead, {
        y: 20,
        opacity: 0,
        duration: 0.6,
        ease: "power2.out",
        delay: 0.16,
        scrollTrigger: { ...trigger, id: ids[2] },
      });
    }
    if (meta) {
      gsap.from(meta, {
        y: 14,
        opacity: 0,
        duration: 0.6,
        ease: "power2.out",
        delay: 0.24,
        scrollTrigger: { ...trigger, id: ids[3] },
      });
    }
    // La mascara barre de izquierda a derecha, desfasada entre columnas.
    if (masks.length > 0) {
      gsap.from(masks, {
        clipPath: "inset(0 100% 0 0)",
        duration: 0.9,
        ease: "power3.out",
        stagger: 0.1,
        delay: 0.32,
        scrollTrigger: { ...trigger, id: ids[4] },
      });
    }
    if (gallery) {
      // Entra desde la derecha, que es de donde viene el visor en el encuadre
      // de escritorio (ver la reasignacion de themes.css).
      gsap.from(gallery, {
        x: 46,
        opacity: 0,
        duration: 0.85,
        ease: "power3.out",
        delay: 0.42,
        scrollTrigger: { ...trigger, id: ids[5] },
      });
      /*
       * Parallax de la captura mientras la escena cruza el encuadre: le da
       * profundidad respecto al texto, que va quieto. El eje es el del
       * recorrido — `xPercent` cuando la obra pasa de lado, `yPercent` cuando
       * baja — y en los dos casos es una propiedad DISTINTA de la que anima la
       * entrada de arriba (`x`), asi que las dos timelines no se pisan sobre
       * el mismo nodo.
       */
      gsap.fromTo(
        gallery,
        container ? { xPercent: -3.5 } : { yPercent: -4 },
        {
          ...(container ? { xPercent: 3.5 } : { yPercent: 4 }),
          ease: "none",
          scrollTrigger: container
            ? {
                id: ids[6],
                trigger: scene,
                containerAnimation: container,
                start: "left right",
                end: "right left",
                scrub: 1,
              }
            : {
                id: ids[6],
                trigger: scene,
                start: "top bottom",
                end: "bottom top",
                scrub: 1,
              },
        },
      );
    }
  }
}

/**
 * Gesto 3 — Cartela. En escritorio las obras se recorren DE LADO: el carril se
 * fija en pantalla y el scroll lo traslada en X, de modo que pasar de un
 * proyecto al siguiente es pasar una cartela en una moviola. Por debajo de
 * 901px se vuelve a la pila vertical (ver el comentario del CSS).
 *
 * El reparto de responsabilidades entre los dos modos lo hace `gsap.matchMedia`
 * y no un `if` con `matchMedia().matches`: al cruzar el breakpoint
 * redimensionando, el contexto que deja de aplicar se REVIERTE entero — pin,
 * transformaciones y triggers incluidos. Con un `if` suelto, el carril se
 * quedaria fijado y desplazado en X al pasar a movil.
 */
function scene3Slate(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const scenes = Array.from(root.querySelectorAll<HTMLElement>('[data-scene="obra"]'));
  if (scenes.length === 0) return;

  const rail = root.querySelector<HTMLElement>("[data-obra-rail]");
  const track = root.querySelector<HTMLElement>("[data-obra-track]");

  // Defensivo, igual que en los gestos 1 y 2: si esta funcion se re-ejecutara,
  // revertir el contexto anterior en vez de acumular un segundo pin.
  obraContext?.revert();
  obraContext = gsap.matchMedia();

  obraContext.add("(min-width: 901px)", () => {
    if (!rail || !track) return;

    /*
     * Recorrido lateral. `end` y el destino se calculan con funcion, no con un
     * numero fijo: `invalidateOnRefresh` los vuelve a pedir en cada refresh de
     * ScrollTrigger (resize, cambio de fuentes, imagenes que terminan de
     * cargar), que es lo que evita que el carril se quede corto o se pase de
     * largo cuando el ancho del track cambia despues del montaje.
     */
    const distance = (): number => Math.max(track.scrollWidth - window.innerWidth, 0);
    const horizontal = gsap.to(track, {
      x: () => -distance(),
      ease: "none",
      scrollTrigger: {
        id: "vice-obra-rail",
        trigger: rail,
        pin: true,
        scrub: 1,
        start: "top top",
        end: () => `+=${distance()}`,
        invalidateOnRefresh: true,
        anticipatePin: 1,
        /*
         * El pin reserva ~5760px de recorrido extra, asi que TODO lo que va
         * despues en el documento (creditos, contacto y sus regiones de cromo)
         * se desplaza hacia abajo. Sin prioridad, esos triggers se refrescan
         * antes que este y calculan su posicion como si el pin no existiera:
         * medido, la barra de orientacion anunciaba "05 · Fundido" mientras el
         * carril de obra ocupaba la pantalla entera, y con el el letterbox se
         * apagaba. Prioridad alta = se refresca antes que ellos y ya miden
         * sobre el documento con el hueco del pin reservado.
         *
         * Pero SOLO 1, no mas: el pin del hero lleva 2 porque va antes en el
         * documento y reserva 1665px. Si este se refrescase primero, no los
         * veria y situaria su inicio 1605px antes de tiempo — medido: el
         * carril quedaba fijado en pantalla encima de "Quien es".
         */
        refreshPriority: 1,
      },
    });

    scenes.forEach((scene, index) => buildSlate(gsap, scene, obraTriggerIds(index), horizontal));
  });

  obraContext.add("(max-width: 900px)", () => {
    scenes.forEach((scene, index) => buildSlate(gsap, scene, obraTriggerIds(index), null));
  });

  // El pin del carril cambia la altura del documento: sin este refresco, los
  // triggers de las escenas posteriores (creditos, contacto) conservan las
  // posiciones calculadas antes de reservarlo.
  ScrollTrigger.refresh();
  // El pin acaba de cambiar el alto del documento: avisar a la barra de
  // progreso, que cachea ese valor en vez de leerlo en cada fotograma.
  window.dispatchEvent(new Event("scrollrail:refresh"));
}

/** Id fijo del gesto 4: permite matarlo si la funcion se re-ejecuta. */
const CREDITS_TRIGGER_ID = "vice-credits-roll";
const CREDITS_MARKS_TRIGGER_ID = "vice-credits-marks";

/**
 * Gesto 4 — Creditos: ruedan al entrar y SE DETIENEN. Un rodillo perpetuo
 * seria imposible de usar (la seccion es interactiva: hover/foco cambian el
 * panel de detalle), asi que el ScrollTrigger solo dispara la entrada una
 * vez por scroll, `toggleActions` incluido — nunca un loop.
 *
 * El panel de detalle recibe ademas un pulso corto cada vez que cambia de
 * fila. `credits.ts` (compartido por los tres temas) ya sustituye texto e
 * icono de forma SINCRONA en mouseenter/focus/click, y estos listeners se
 * anaden despues, al montar la coreografia: aqui solo se anima el contenido
 * YA actualizado. El orden de mutacion del DOM no cambia, asi que el
 * `aria-live="polite"` del panel sigue anunciando el cambio con normalidad.
 */
function scene4Credits(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const roll = root.querySelector<HTMLElement>("[data-credit-roll]");
  if (!roll) return;

  // Defensivo, igual que en los gestos 1 a 3: matar el trigger huerfano si
  // esta funcion se re-ejecutara.
  ScrollTrigger.getById(CREDITS_TRIGGER_ID)?.kill();
  ScrollTrigger.getById(CREDITS_MARKS_TRIGGER_ID)?.kill();

  /*
   * `fromTo` sobre un array materializado, no `from` sobre `roll.children`.
   * Con `from` y una HTMLCollection viva, GSAP registraba como destino el
   * propio estado de partida: las doce filas terminaban la entrada con
   * `translate(0, 34px)` pegado para siempre (medido), es decir, la seccion
   * se pintaba 34px por debajo de su sitio y el gesto de subida no existia.
   * El mismo fallo aparecio en el pie de contacto (`scene5Contact`) y es de
   * la familia de la regresion documentada en `scene1Title`: nunca dejar que
   * GSAP deduzca un extremo leyendo el DOM.
   *
   * El desenfoque que se despeja evoca un proyector enfocando: es el mismo
   * recurso que abre el titulo del hero, aqui a escala de fila.
   */
  gsap.fromTo(
    Array.from(roll.children),
    { y: 34, opacity: 0, filter: "blur(6px)" },
    {
      y: 0,
      opacity: 1,
      filter: "blur(0px)",
      duration: 0.7,
      ease: "power3.out",
      stagger: 0.07,
      scrollTrigger: {
        id: CREDITS_TRIGGER_ID,
        trigger: roll,
        start: "top 80%",
        toggleActions: "play none none reverse",
      },
    },
  );

  /*
   * El friso de marcas entra despues del reparto y no a la vez: en un cartel
   * los logos del pie son lo ultimo que se lee, asi que son lo ultimo que
   * aparece. Escalonado mucho mas corto que el de las filas (0.02 contra
   * 0.07) porque son 23 piezas pequenas en una sola linea: con el ritmo de
   * los creditos, el friso tardaria mas de un segundo y medio en cerrarse.
   *
   * `fromTo` sobre `Array.from(...)`, nunca `from` sobre la HTMLCollection
   * viva de `.children`: es exactamente el fallo que dejo doce filas de
   * creditos con `translate(0, 34px)` pegado para siempre y el pie de
   * contacto invisible.
   *
   * La opacidad se anima en el CONTENEDOR, no en las marcas. Cada marca vive
   * a `opacity: .26` y sube a 1 solo cuando es la activa: si la entrada las
   * animara a ellas, GSAP les dejaria un `opacity: 1` inline que gana a la
   * regla CSS y el friso entero quedaria encendido, perdiendo justo la
   * funcion por la que existe. Mismo principio que el `transform` del hover.
   */
  const frieze = root.querySelector<HTMLElement>("[data-credit-marks]");
  if (frieze) {
    const marksIn = gsap.timeline({
      scrollTrigger: {
        id: CREDITS_MARKS_TRIGGER_ID,
        trigger: frieze,
        start: "top 92%",
        toggleActions: "play none none reverse",
      },
    });

    marksIn.fromTo(frieze, { opacity: 0 }, { opacity: 1, duration: 0.45, ease: "power2.out" }, 0);
    marksIn.fromTo(
      Array.from(frieze.children),
      { y: 10 },
      { y: 0, duration: 0.4, ease: "power2.out", stagger: 0.02 },
      0,
    );
  }

  const panel = root.querySelector<HTMLElement>("[data-credit-panel]");
  if (!panel) return;

  const icon = panel.querySelector<HTMLElement>(".credits-icon");
  const usedList = panel.querySelector<HTMLElement>("[data-credit-used-list]");

  let panelTween: ReturnType<Gsap["timeline"]> | null = null;
  /*
   * Corte de montaje, no parpadeo. El panel entra recortandose desde arriba
   * (un barrido de cortinilla, coherente con las mascaras de la obra), el
   * icono gira un poco al posarse y las fichas de proyecto entran escalonadas
   * detras: son lo ultimo que se lee, asi que son lo ultimo que aparece.
   *
   * Se mata la timeline anterior en cada cambio porque recorrer la lista con
   * el raton dispara esto muchas veces por segundo; sin matarla, los tweens se
   * encadenan y el panel se queda a medio camino.
   */
  const pulse = (): void => {
    panelTween?.kill();
    const tl = gsap.timeline();
    panelTween = tl;

    tl.fromTo(
      panel,
      { opacity: 0.4, clipPath: "inset(0 0 100% 0)" },
      { opacity: 1, clipPath: "inset(0 0 0% 0)", duration: 0.34, ease: "power2.out" },
      0,
    );
    if (icon) {
      tl.fromTo(
        icon,
        { scale: 0.82, rotate: -8, opacity: 0 },
        { scale: 1, rotate: 0, opacity: 1, duration: 0.42, ease: "back.out(2)" },
        0.04,
      );
    }
    if (usedList && usedList.children.length > 0) {
      // `Array.from`: nunca una HTMLCollection viva (ver `scene4Credits`).
      tl.fromTo(
        Array.from(usedList.children),
        { opacity: 0, y: 8, scale: 0.94 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.3,
          ease: "power2.out",
          stagger: 0.06,
        },
        0.16,
      );
    }
  };

  for (const row of root.querySelectorAll<HTMLElement>("[data-credit]")) {
    row.addEventListener("mouseenter", pulse);
    row.addEventListener("focus", pulse);
  }
}

/** Ids fijos del gesto 5: permiten matarlos si la funcion se re-ejecuta. */
const CONTACT_TRIGGER_IDS = [
  "vice-contact-kick",
  "vice-contact-title",
  "vice-contact-status",
  "vice-contact-mail",
  "vice-contact-corner",
];

/**
 * Gesto 5 — Fundido de cierre. Era la unica escena sin ninguna entrada: el
 * bloque de contacto aparecia ya montado, lo que rompia la continuidad de una
 * pieza donde todas las demas escenas se componen a la vista. El titulo entra
 * despejando desenfoque, igual que el del hero: es el eco de cierre del mismo
 * gesto que abrio la pieza.
 */
function scene5Contact(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const contacto = root.querySelector<HTMLElement>('[data-scene="contacto"]');
  if (!contacto) return;

  for (const id of CONTACT_TRIGGER_IDS) ScrollTrigger.getById(id)?.kill();

  const base = { trigger: contacto, start: "top 68%", toggleActions: "play none none reverse" } as const;
  const kick = contacto.querySelector<HTMLElement>(".hero-kick");
  const title = contacto.querySelector<HTMLElement>("h2");
  const status = contacto.querySelector<HTMLElement>(".contacto-status");
  // El envoltorio del CTA, no el enlace: ver el comentario de `contacto.ts`.
  const mail = contacto.querySelector<HTMLElement>(".contacto-cta");
  const corner = contacto.querySelector<HTMLElement>(".contacto-corner");

  if (kick) {
    gsap.from(kick, {
      opacity: 0,
      y: 14,
      duration: 0.5,
      ease: "power2.out",
      scrollTrigger: { ...base, id: CONTACT_TRIGGER_IDS[0] },
    });
  }
  if (title) {
    // "Hablemos" se monta letra a letra: cierra la pieza con el mismo gesto
    // con el que se abrio el nombre, que es lo que lo hace leer como final y
    // no como una seccion mas.
    composeTitle(gsap, title, base, CONTACT_TRIGGER_IDS[1], 0.08);
  }
  if (status) {
    gsap.from(status, {
      opacity: 0,
      y: 14,
      duration: 0.5,
      ease: "power2.out",
      delay: 0.22,
      scrollTrigger: { ...base, id: CONTACT_TRIGGER_IDS[2] },
    });
  }
  if (mail) {
    // El CTA entra el ultimo y con un punto de escala: es la accion, tiene que
    // ser lo ultimo que se posa en el encuadre.
    gsap.from(mail, {
      opacity: 0,
      y: 18,
      scale: 0.94,
      duration: 0.6,
      ease: "back.out(1.6)",
      delay: 0.32,
      scrollTrigger: { ...base, id: CONTACT_TRIGGER_IDS[3] },
    });
  }
  if (corner) {
    /*
     * `fromTo` con los dos extremos escritos a mano, no `from`. Con `from`,
     * GSAP toma el valor final leyendo el DOM y aqui registraba `opacity: 0`
     * como destino: el tween corria (la `y` si llegaba a 0) pero los tres
     * enlaces del pie se quedaban invisibles para siempre. Es la misma clase
     * de fallo que la regresion del gesto 1, documentada en `scene1Title`.
     */
    gsap.fromTo(
      Array.from(corner.children),
      { opacity: 0, y: 14 },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power2.out",
        stagger: 0.08,
        delay: 0.44,
        scrollTrigger: { ...base, id: CONTACT_TRIGGER_IDS[4] },
      },
    );
  }
}

/** Id fijo por escena: permite matar cada ScrollTrigger si la funcion se re-ejecuta. */
function chromeTriggerId(index: number): string {
  return `vice-chrome-${index}`;
}

/**
 * Gesto 5 — Recursos globales de lenguaje de cine: la barra de orientacion
 * dice donde estas, el letterbox entra solo durante la obra ("esto es la
 * pelicula") y el atenuador de fondo baja la luz fuera de hero/contacto para
 * que el texto largo de las secciones intermedias no compita con el video.
 */
function cinemaChrome(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const bars = Array.from(document.querySelectorAll<HTMLElement>("[data-letterbox]"));
  const now = document.querySelector<HTMLElement>(".rail-now");
  const dim = document.querySelector<HTMLElement>("[data-dim]");
  // La firma del tema vive fija abajo a la derecha, justo donde la escena de
  // contacto despliega su barra de pie: en esa escena estorba al enlace de
  // GitHub, asi que se retira. Es decoracion (`aria-hidden`), no informacion.
  const signature = document.querySelector<HTMLElement>(".theme-signature");
  /*
   * Regiones, no escenas sueltas. Las obras viven dentro del carril
   * (`[data-obra-rail]`), que en escritorio esta FIJADO en pantalla: un
   * trigger por cartela medido contra el scroll vertical se activaria con el
   * carril entero, porque mientras dura el pin la posicion vertical de las
   * cartelas no cambia. El carril cuenta como una sola region — que ademas es
   * como se lee: "la pelicula" es un bloque, no cinco.
   *
   * De paso, la numeracion de la barra vuelve a ser 01..05 (las cinco partes
   * de la pieza) en vez de 01..09 contando cada obra por separado.
   */
  const rail = root.querySelector<HTMLElement>("[data-obra-rail]");
  const scenes = Array.from(root.querySelectorAll<HTMLElement>("[data-scene]")).filter(
    (scene) => scene.dataset.scene !== "obra",
  );
  if (rail) {
    // El carril ocupa el sitio de la primera obra en el orden del documento.
    const firstObraIndex = scenes.findIndex(
      (scene) => scene.compareDocumentPosition(rail) & Node.DOCUMENT_POSITION_PRECEDING,
    );
    scenes.splice(firstObraIndex < 0 ? scenes.length : firstObraIndex, 0, rail);
  }
  const labels: Record<string, string> = {
    hero: "Título",
    about: "Ficha",
    obra: "Cartela",
    credits: "Créditos",
    contacto: "Fundido",
  };
  /** Solo hero y contacto a plena luz; el resto atenuado para que el texto lea. */
  const brightScenes = new Set(["hero", "contacto"]);

  scenes.forEach((scene, index) => {
    // Defensivo, igual que en los gestos 1 a 4: matar el trigger huerfano si
    // esta funcion se re-ejecutara.
    ScrollTrigger.getById(chromeTriggerId(index))?.kill();

    // El carril no lleva `data-scene` propio (es el envoltorio de las obras):
    // se le asigna el tipo "obra", que es lo que contiene.
    const kind = scene === rail ? "obra" : (scene.dataset.scene ?? "");
    /*
     * El carril de obra esta FIJADO en pantalla mientras dura su recorrido
     * lateral: su caja deja de desplazarse, asi que un `end: "bottom 50%"`
     * se cumple casi en el mismo instante que el `start` y el letterbox se
     * apagaba nada mas encenderse (medido por el arnes: 0.0156px de alto en
     * vez de 6.5vh). El final se deriva del mismo recorrido que consume el
     * pin — el ancho sobrante del track mas una pantalla — y se recalcula en
     * cada refresh, igual que el propio pin.
     */
    /*
     * Cuando el carril esta fijado, su propia caja deja de moverse: es
     * `position: fixed`, asi que `getBoundingClientRect()` devuelve siempre lo
     * mismo y un trigger montado sobre el mide contra algo inmovil. Medido:
     * con el carril ocupando la pantalla entera, la barra de orientacion
     * anunciaba primero "Fundido" y luego "Ficha", nunca "Cartela".
     *
     * Quien SI ocupa el hueco reservado en el flujo del documento es el
     * espaciador que ScrollTrigger inserta como padre al fijar. Ese es el
     * elemento contra el que hay que medir.
     *
     * Se comprueba en TODAS las regiones, no solo en el carril: el hero
     * tambien se fija (el zoom de apertura, `scene1Title`) y arrastraba el
     * mismo defecto. Se veia al volver hacia arriba desde el final — la barra
     * anunciaba "01 · Titulo" con el carril de obra llenando la pantalla, y
     * el letterbox se quedaba apagado. Cuando no hay pin (pila vertical en
     * pantallas estrechas) no hay espaciador y se mide contra la escena, que
     * ahi si es un elemento normal.
     */
    const spacer = scene.parentElement;
    const isRail = scene === rail;

    /*
     * El carril no se mide contra ningun elemento: se mide contra el propio
     * pin, leido por id en cada refresco.
     *
     * Guardar una referencia al elemento espaciador no vale. GSAP lo destruye
     * y lo vuelve a crear al refrescar el contexto de `matchMedia`, y el
     * trigger se quedaba apuntando al nodo viejo, ya descolgado del DOM: un
     * trigger sobre un elemento desconectado no se activa NUNCA. Medido en el
     * arnes — al bajar, "about" se desactivaba a y=4485 y despues no saltaba
     * ningun toggle mas, asi que el letterbox se quedaba apagado durante toda
     * la obra. Preguntando por el pin cada vez, la region no puede quedarse
     * huerfana: si el pin se recrea, la siguiente lectura da el nuevo.
     */
    const railBound = (edge: "start" | "end") => (): number => {
      const pin = ScrollTrigger.getById("vice-obra-rail");
      if (pin) return edge === "start" ? pin.start : pin.end;
      // Sin pin (pila vertical): el borde equivalente del propio carril.
      const box = scene.getBoundingClientRect();
      const y = (edge === "start" ? box.top : box.bottom) + window.scrollY;
      return y - window.innerHeight * 0.5;
    };

    ScrollTrigger.create({
      id: chromeTriggerId(index),
      // Sin `trigger` en el carril: `start`/`end` son posiciones absolutas.
      ...(isRail
        ? { start: railBound("start"), end: railBound("end") }
        : {
            trigger: spacer?.classList.contains("pin-spacer") ? spacer : scene,
            start: "top 50%",
            end: "bottom 50%",
          }),
      invalidateOnRefresh: true,
      onToggle: (self) => {
        if (!self.isActive) return;
        if (now) {
          const label = `${String(index + 1).padStart(2, "0")} · ${labels[kind] ?? ""}`;
          /*
           * La barra corta entre escenas en vez de saltar: fundido de salida
           * corto, cambio de texto, fundido de entrada.
           *
           * `killTweensOf` antes de montar el nuevo fundido NO es adorno. Al
           * saltar muchos pixeles de golpe (volver arriba desde el final, un
           * ancla, restaurar scroll al recargar) se cruzan varios toggles en
           * pocos milisegundos, y como el texto se escribe A MITAD del
           * fundido, el rotulo que quedaba era el del ultimo fundido en
           * TERMINAR, no el de la escena en la que estas. Medido: la barra
           * anunciaba "01 · Titulo" con el carril de obra llenando la
           * pantalla. Al matar el anterior, su callback intermedio ya no
           * llega a ejecutarse y solo escribe el vigente.
           */
          gsap.killTweensOf(now);
          gsap
            .timeline()
            .to(now, { opacity: 0, duration: 0.15, ease: "power1.in" })
            .add(() => {
              now.textContent = label;
            })
            .to(now, { opacity: 1, duration: 0.25, ease: "power1.out" });
        }
        // Las franjas entran solo durante la obra: dicen "esto es la pelicula".
        // `overwrite` por el mismo motivo que el `killTweensOf` de arriba: en
        // un salto largo se encadenan varios toggles y sin el gana el ultimo
        // tween en terminar, que no tiene por que ser el de la escena actual.
        gsap.to(bars, {
          height: kind === "obra" ? "6.5vh" : "0vh",
          duration: 0.45,
          ease: "power3.out",
          overwrite: "auto",
        });
        if (signature) {
          gsap.to(signature, {
            opacity: kind === "contacto" ? 0 : 1,
            duration: 0.35,
            ease: "power2.out",
          });
        }
        if (dim) {
          gsap.to(dim, {
            opacity: brightScenes.has(kind) ? 0 : 0.62,
            duration: 0.6,
            ease: "power2.out",
            overwrite: "auto",
          });
        }
      },
    });
  });
}

export const viceChoreography: Choreography = ({ gsap, ScrollTrigger, root }) => {
  sceneIntro(gsap);
  scene1Title(gsap, ScrollTrigger, root);
  scene2Card(gsap, ScrollTrigger, root);
  scene3Slate(gsap, ScrollTrigger, root);
  scene4Credits(gsap, ScrollTrigger, root);
  scene5Contact(gsap, ScrollTrigger, root);
  cinemaChrome(gsap, ScrollTrigger, root);
};
