import type { Choreography } from "./choreography";
import { montarFicha } from "./caelestia.ficha";
import { montarFundido } from "./caelestia.fundido";
import { montarEntrada, montarRoce, montarTitulo } from "./caelestia.titulo";

/**
 * La coreografia de Caelestia: las cinco escenas dejan de apilarse en vertical
 * y pasan a ser un carril horizontal de workspaces. Un espacio de trabajo no
 * se desplaza, se cambia — es el gesto que sostiene la metafora de escritorio.
 *
 * `root` YA ES el `<main>`: `reveal.ts` invoca `initScrollReveal(main, theme)`
 * y de ahi sale el `root` del contexto. Buscar un `main` descendiente devuelve
 * `null` y toda la coreografia se iria por un `return` temprano en silencio.
 * Por eso el carril es `root`, sin `querySelector`.
 *
 * El `data-cae-shell`, en cambio, va en `document.documentElement`: el CSS lo
 * selecciona como `:root[data-theme="caelestia"][data-cae-shell="workspaces"]`
 * y desde `<main>` no casaria con nada.
 *
 * El oyente del evento va tambien en `document.documentElement`. El shell lo
 * despacha sobre `#app` con `bubbles: true`, y `<main>` es HIJO de `#app`: los
 * eventos burbujean hacia arriba, nunca hacia abajo, asi que un oyente en el
 * propio carril no lo veria jamas.
 *
 * Lenis NO interviene aqui: `reveal.ts` solo lo monta para `motion.style ===
 * "cinematic"`, que es Vice. Ver la correccion del 2026-08-20 en el spec.
 *
 * ScrollTrigger tampoco: en Caelestia no hay ni un solo pin ni trigger, asi
 * que no se destructura del contexto (el contrato es comun a los tres temas,
 * pero nada obliga a usar cada pieza). El `resize` solo re-fija la posicion
 * del carril con `gsap.set` — ver el comentario junto a `alRedimensionar`.
 *
 * DOS DUENOS PARA UNA SOLA POSICION, Y UNO NO LO SABIA. El carril lo mueve el
 * `transform` de esta coreografia, pero los workspaces inactivos seguian en el
 * arbol, visibles y ENFOCABLES. Tres pulsaciones de Tab desde una carga limpia
 * metian el foco en el workspace 2, y el navegador desplazaba el contenedor de
 * scroll mas cercano — el `body`, cuyo `overflow: hidden` sigue siendo
 * desplazable POR PROGRAMA — para traerlo a la vista: `railX=0` con
 * `bodySL=2705`. Las dos posiciones se sumaban y no volvian, la barra mentia
 * sobre lo que habia en pantalla y solo se recuperaba recargando. Y lo sufria
 * exactamente el usuario de teclado: el camino de accesibilidad.
 *
 * Se cierra por los dos lados a la vez, porque cada uno solo tapa la mitad:
 *
 *   1. `inert` en todo workspace que no sea el activo. El foco no puede entrar
 *      donde no se ve, y de paso el contenido oculto sale del arbol de
 *      accesibilidad — que es lo que un lector de pantalla espera de algo que
 *      no esta en pantalla. El activo nunca lleva `inert`: sigue navegable
 *      entero por teclado.
 *   2. Un anclaje del scroll del documento. `inert` quita la via conocida,
 *      pero no es la unica (un ancla `#obra`, un `scrollIntoView` de terceros,
 *      un `focus()` por programa). El oyente en fase de captura devuelve el
 *      documento a cero venga de donde venga, asi que `body.scrollLeft` no
 *      puede quedar desincronizado del `transform` POR NINGUNA VIA.
 *
 * Ninguno de los dos depende de GSAP ni del perfil de movimiento: cuando la
 * Tarea 10 haga que la coreografia corra tambien con `prefers-reduced-motion`,
 * siguen valiendo tal cual.
 */
const DURACION = 0.52;
const CURVA = "power3.inOut";

export const caelestiaChoreography: Choreography = ({ gsap, root }) => {
  const escenas = Array.from(root.children).filter(
    (nodo): nodo is HTMLElement => nodo instanceof HTMLElement,
  );
  if (escenas.length === 0) return;

  root.dataset.caeTrack = "";
  document.documentElement.dataset.caeShell = "workspaces";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let actual = 0;
  let fundidoVisto = false;

  const cuerpo = document.body;
  const raiz = document.documentElement;

  /**
   * Devuelve el documento a cero. El unico dueno de donde esta el carril es el
   * `transform`; el scroll del documento no participa y cualquier valor que
   * tenga es deriva.
   */
  const anclarDocumento = (): void => {
    if (raiz.scrollLeft !== 0) raiz.scrollLeft = 0;
    if (raiz.scrollTop !== 0) raiz.scrollTop = 0;
    if (cuerpo.scrollLeft !== 0) cuerpo.scrollLeft = 0;
    if (cuerpo.scrollTop !== 0) cuerpo.scrollTop = 0;
  };

  /** Solo el activo queda navegable; los demas salen del foco y del arbol a11y. */
  const aislarInactivos = (activo: number): void => {
    escenas.forEach((escena, indice) => {
      escena.inert = indice !== activo;
    });
  };

  /*
   * La ficha de «Quien soy» se lanza cuando SU workspace se activa, no al
   * cargar: es una aplicacion arrancando, y arranca cuando la abres. Se monta
   * una sola vez; `reproducir()` es lo que se repite.
   *
   * `gsap` sale del contexto de esta coreografia y se le pasa por parametro:
   * el modulo NO importa `gsap` por su cuenta.
   *
   * VA ANTES DE `irA` A PROPOSITO. `irA` lo lee, y con las declaraciones mas
   * abajo la unica razon de que hoy funcione es que `irA` solo se invoca desde
   * el oyente, que se registra despues: una TDZ armada esperando a que alguien
   * añada un deep-link por hash y llame a `irA()` durante la inicializacion.
   * Eso reventaria con `ReferenceError` SOLO en el navegador, que es el modo
   * de fallo mas caro de este proyecto. Declarado arriba, no puede pasar.
   */
  const escenaFicha = escenas.find((escena) => escena.querySelector('[data-ficha="neofetch"]'));
  const ficha = escenaFicha ? montarFicha(gsap, escenaFicha) : null;
  const indiceFicha = escenaFicha ? escenas.indexOf(escenaFicha) : -1;

  // El fundido de cierre (tarea 5, provisional): el troquel y el bicho
  // montados sin animacion todavia. La tarea 6 lo deja definitivo, llamando
  // a `reproducir`/`entrar` desde `irA`.
  const indiceFundido = escenas.findIndex((escena) => escena.dataset.scene === "contacto");
  const fundido =
    indiceFundido >= 0 ? montarFundido(gsap, escenas[indiceFundido], indiceFundido) : null;

  const irA = (indice: number): void => {
    const destino = Math.max(0, Math.min(indice, escenas.length - 1));
    // El extremo de partida es la posicion ACTUAL, capturada antes de
    // reasignarla: con origen igual a destino un `fromTo` no anima nada y el
    // carril saltaria de golpe siempre.
    const origen = actual;
    actual = destino;
    aislarInactivos(destino);
    // Solo al ENTRAR en su workspace, no al pulsar la pastilla del que ya
    // esta delante: no vuelves a abrir la aplicacion en la que ya estas, y
    // sin ningun affordance que prometa repeticion, 2,6 s de tecleo donde ya
    // estabas se lee como parpadeo. No es un caso que falte: es el arreglo.
    if (ficha && destino === indiceFicha && destino !== origen) ficha.reproducir();
    /*
     * EL FUNDIDO SUENA UNA VEZ; LA ENTRADA, TODAS. Es la misma regla que ya
     * gobierna la ficha de B2 dos lineas mas arriba: no vuelves a abrir la
     * aplicacion en la que ya estas. Un final de 1,9 s reproducido en la
     * quinta visita deja de ser un final y pasa a ser un peaje.
     */
    if (fundido && destino === indiceFundido && destino !== origen) {
      if (fundidoVisto) fundido.entrar(origen);
      else {
        fundido.reproducir();
        fundidoVisto = true;
      }
    }
    anclarDocumento();
    // fromTo con los dos extremos escritos a mano: `gsap.from` esta prohibido
    // en este proyecto y ya provoco tres regresiones reales.
    gsap.fromTo(
      root,
      { xPercent: -100 * origen },
      {
        xPercent: -100 * destino,
        duration: reduce ? 0 : DURACION,
        ease: CURVA,
        overwrite: "auto",
      },
    );
  };

  // Estado inicial explicito, sin leer el DOM.
  gsap.set(root, { xPercent: 0 });
  aislarInactivos(0);
  anclarDocumento();

  // El titular se justifica midiendo texto real, asi que necesita el DOM ya
  // colocado. `root` ES el <main>: ver el docstring de arriba.
  //
  // Sin `titulo.destroy()`: esta coreografia no tiene mecanismo de limpieza
  // propio (`Choreography` devuelve `void` — ver el docstring de
  // hypr.choreography.ts, "ningun tema tiene destroy()") y ninguno de sus
  // otros oyentes de `window`/`document` (scroll, focusin, resize, el evento
  // de workspace) se retira tampoco: todos viven tanto como la pagina, igual
  // que explica el comentario "Sin destroy() propio" al final de este
  // fichero. El oyente de resize de `montarTitulo` sigue exactamente el mismo
  // patron.
  montarTitulo(root);

  // La entrada (tarea 6): terminal + trazo del nombre, aterrizando sobre
  // `.cae-firma`. Sin `destroy()` propio por el mismo motivo que el resto de
  // esta coreografia (ver el comentario "Sin destroy() propio" al final del
  // fichero) — el handle que devuelve existe para tests/composicion futura.
  montarEntrada(gsap, root);

  // El roce (tarea 7): el fondo se aparta y el elemento se levanta al pasar
  // el raton por encima del widget, las cifras, las pastillas de la barra o
  // el dock. Sin `destroy()` propio por el mismo motivo que el resto de esta
  // coreografia — ver el comentario "Sin destroy() propio" al final del
  // fichero, y el docstring de `montarRoce` en caelestia.titulo.ts.
  montarRoce(gsap, root);

  /*
   * Fase de CAPTURA: los eventos de scroll no burbujean, asi que un oyente en
   * `document` solo los ve bajando. Se filtra por diana para no tocar el
   * desplazamiento vertical que cada ventana hace de su propio contenido, que
   * es legitimo y tiene que seguir funcionando.
   */
  const alDesplazar = (evento: Event): void => {
    const diana: EventTarget | null = evento.target;
    if (diana !== document && diana !== cuerpo && diana !== raiz) return;
    anclarDocumento();
  };
  document.addEventListener("scroll", alDesplazar, true);

  /*
   * Segunda red, por si el navegador desplaza sin emitir `scroll` observable a
   * tiempo: al entrar el foco en cualquier sitio, el documento vuelve a cero.
   */
  document.addEventListener("focusin", anclarDocumento, true);

  const alCambiar = (evento: Event): void => {
    if (!(evento instanceof CustomEvent)) return;
    const detalle: unknown = evento.detail;
    if (typeof detalle !== "object" || detalle === null || !("index" in detalle)) return;
    const indice = Number((detalle as { index: unknown }).index);
    if (!Number.isFinite(indice)) return;
    irA(indice);
  };
  document.documentElement.addEventListener("caelestia:workspace", alCambiar);

  // Sin `ScrollTrigger.refresh()`: Caelestia no crea ni un solo ScrollTrigger
  // (ni pin, ni trigger de ningun tipo), asi que refrescar no tiene nada que
  // recalcular y solo fuerza un layout forzado en cada evento de `resize` —
  // en movil eso dispara cada vez que aparece o se retira la barra de
  // direcciones. Lo unico que hace falta aqui es re-fijar la posicion del
  // carril. No lo "restaures" pensando que faltaba: es a proposito.
  const alRedimensionar = (): void => {
    gsap.set(root, { xPercent: -100 * actual });
  };
  window.addEventListener("resize", alRedimensionar);

  /*
   * Sin `destroy()` propio: la coreografia se invoca una vez por carga y el
   * arbol muere con la pagina. Los oyentes van sobre `document`,
   * `document.documentElement` y `window`, que tienen el mismo ciclo de vida. Si esto deja de ser cierto
   * (navegacion sin recarga), hay que devolver un limpiador y llamarlo desde
   * `pagehide`.
   */
};
