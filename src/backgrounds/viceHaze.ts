import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Vice: bruma de neon a la deriva. Nubes de fbm con warp de dominio, teñidas
 * de magenta y cian sobre un negro muy profundo — la tipografia manda y el
 * fondo es atmosfera, nunca ilustracion.
 *
 * Sustituye al backdrop de video (`cinematicBackdrop`), que servia el fixture
 * sintetico de barras SMPTE: franjas de color primario puro que obligaban a
 * tapar el texto con un scrim casi opaco para pasar el gate de contraste. Con
 * una base oscura y de baja varianza ese parche deja de hacer falta.
 *
 * Reacciona al scroll por dos vias:
 *   - `uScroll` (0..1, progreso del documento) desplaza la bruma y gira su
 *     temperatura de magenta a cian y de ahi al ambar del acento, de modo que
 *     cada escena tiene un color de luz propio sin cortes.
 *   - `uVelocity` (-1..1) estira la bruma en el eje del movimiento: al
 *     desplazarse rapido la atmosfera se alarga, como un barrido de camara, y
 *     se reasienta al parar.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  uniform float uScroll;
  uniform float uVelocity;
  uniform float uPointerX;
  uniform float uPointerY;
  varying vec2 vUv;

  void main() {
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    vec2 p = (vUv * 2.0 - 1.0) * vec2(aspect, 1.0);

    float t = uTime * 0.045;
    float drift = uScroll * 2.4;

    /*
     * Estirado por velocidad: comprimir la coordenada vertical alarga la
     * bruma en ese eje. Se acota a 2.6 para que un scroll violento no la
     * aplane hasta convertirla en bandas planas.
     */
    float smear = 1.0 + min(abs(uVelocity), 1.0) * 1.6;
    vec2 q = vec2(p.x, p.y / smear);

    /*
     * Parallax de puntero: la bruma se desplaza en sentido contrario al raton,
     * muy poco (0.09 del rango normalizado). Da sensacion de profundidad sin
     * que el fondo persiga el cursor, que es el efecto que envejece mal. En
     * tactil los dos uniforms se quedan en 0 y esto es un no-op.
     */
    vec2 pointer = vec2(uPointerX, uPointerY) * 0.09;

    // Warp de dominio: el segundo muestreo se desplaza con el primero, que es
    // lo que da el plegado de humo en vez de manchas redondas.
    vec2 warp = vec2(
      fbm(q * 1.25 + vec2(t, drift * 0.6) - pointer),
      fbm(q * 1.25 + vec2(4.7 - t * 0.8, 2.3 + drift * 0.45) - pointer * 0.6)
    );
    float haze = fbm(q * 1.9 + warp * 1.7 + vec2(-t * 0.5, drift));
    float veil = fbm(q * 3.4 - warp * 0.8 + vec2(t * 1.3, drift * 1.4));

    vec3 ink = vec3(0.043, 0.024, 0.086);
    vec3 magenta = vec3(1.000, 0.176, 0.584);
    vec3 cyan = vec3(0.000, 0.878, 1.000);
    vec3 amber = vec3(1.000, 0.820, 0.400);

    /*
     * Temperatura por recorrido: magenta en la apertura, cian en el centro y
     * ambar en el cierre. Dos smoothstep encadenados en vez de un mix lineal
     * para que cada tramo tenga meseta propia y una escena no herede el tinte
     * de la siguiente a medio camino.
     */
    vec3 warm = mix(magenta, cyan, smoothstep(0.05, 0.55, uScroll));
    vec3 neon = mix(warm, amber, smoothstep(0.62, 0.98, uScroll));

    // Los dos focos no coinciden: uno es la masa de bruma y el otro un velo
    // mas fino por encima, desfasado, que evita la lectura de "una sola nube".
    float body = smoothstep(0.32, 0.92, haze);
    float wisp = pow(smoothstep(0.55, 1.0, veil), 2.0);

    vec3 col = mix(ink, neon, body * 0.30);
    col += neon * wisp * 0.16;
    // El foco secundario en el complementario abre el rango sin subir el brillo.
    col += mix(cyan, magenta, uScroll) * pow(smoothstep(0.62, 1.0, haze), 3.0) * 0.10;

    // Vinieta amplia: sostiene el centro sin dibujar un borde reconocible.
    col *= smoothstep(2.25, 0.30, length(p));

    /*
     * Suelo de oscuridad. Es lo que permite retirar el scrim del texto: el
     * gate de contraste (check_contrast_wcag en scripts/verify.py) necesita
     * franjas planas y oscuras bajo los titulos, y limitar el brillo aqui es
     * mas barato y mas bonito que tapar el fondo con una elipse opaca.
     */
    col = min(col, vec3(0.30, 0.26, 0.36));

    // Grano: rompe el banding de un degradado tan oscuro en pantallas de 8 bits.
    col += (hash(vUv * uResolution + t) - 0.5) * 0.020;

    gl_FragColor = vec4(col, 1.0);
  }
`;

/** Suaviza la velocidad instantanea: sin esto el estirado parpadea fotograma a fotograma. */
const VELOCITY_SMOOTHING = 0.12;

/** Escala de normalizacion: ~90 px de scroll por fotograma ya satura el estirado. */
const VELOCITY_SCALE = 90;

/** Cuanto persigue la bruma al puntero por fotograma: mas bajo, mas inercia. */
const POINTER_SMOOTHING = 0.06;

export function mountViceHaze(container: HTMLElement): BackgroundHandle {
  let lastScroll = window.scrollY;
  let velocity = 0;

  // Objetivo (donde esta el raton) y valor servido (donde va la bruma): el
  // segundo persigue al primero con inercia, si no el fondo da tirones.
  let pointerTargetX = 0;
  let pointerTargetY = 0;
  let pointerX = 0;
  let pointerY = 0;

  const onPointerMove = (event: PointerEvent): void => {
    // Solo raton: con el dedo, "mover el puntero" ya es scrollear y el fondo
    // acabaria dando un tiron en cada gesto.
    if (event.pointerType !== "mouse") return;
    pointerTargetX = (event.clientX / window.innerWidth) * 2 - 1;
    pointerTargetY = (event.clientY / window.innerHeight) * 2 - 1;
  };
  window.addEventListener("pointermove", onPointerMove, { passive: true });

  /*
   * El scroll se lee del propio `window`, no de Lenis ni de ScrollTrigger: el
   * fondo no debe depender de que la coreografia haya cargado (es un import
   * dinamico que puede tardar o fallar) ni de que el usuario no tenga
   * `prefers-reduced-motion`, caso en el que Lenis nunca llega a montarse.
   */
  const readProgress = (): number => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollable <= 0) return 0;
    return Math.min(Math.max(window.scrollY / scrollable, 0), 1);
  };

  const readVelocity = (): number => {
    const current = window.scrollY;
    const delta = (current - lastScroll) / VELOCITY_SCALE;
    lastScroll = current;
    // Media exponencial: el valor cae solo cuando el scroll para, sin timers.
    velocity += (delta - velocity) * VELOCITY_SMOOTHING;
    return Math.min(Math.max(velocity, -1), 1);
  };

  const inner = mountShaderBackground(container, FRAGMENT_SHADER, {
    uScroll: readProgress,
    uVelocity: readVelocity,
    uPointerX: () => {
      pointerX += (pointerTargetX - pointerX) * POINTER_SMOOTHING;
      return pointerX;
    },
    uPointerY: () => {
      pointerY += (pointerTargetY - pointerY) * POINTER_SMOOTHING;
      return pointerY;
    },
  });

  return {
    destroy() {
      // El listener es nuestro, no de `mountShaderBackground`: hay que
      // retirarlo aqui o queda vivo tras destruir el fondo.
      window.removeEventListener("pointermove", onPointerMove);
      inner.destroy();
    },
  };
}
