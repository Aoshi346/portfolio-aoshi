import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * El haz al mando: el fondo deja de ser un halo que respira y pasa a ser una
 * unica cuna de luz con canto duro, gobernada por el scroll. Dos cantos de
 * comportamiento distinto (uno duro, uno que se disuelve en el material) y un
 * derrame que sale del propio eje del haz, no de un foco con coordenadas
 * propias. Espeja la organizacion de Vice sin copiar su material: Vice es
 * tinta impresa, Hyprland es luz con canto.
 *
 * Reacciona por una sola via, `uScroll` (0..1, progreso del documento): el
 * balance de color, la posicion del origen, el angulo, el semiancho y la
 * entrada del segundo haz. Sin puntero y sin velocidad, misma razon que deja
 * escrita viceInk.ts: anadirlos aqui seria rediseñar, no portar.
 *
 * Portado literal del prototipo aprobado en el companion de brainstorming
 * (docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-prototipo.glsl), con
 * los seis uniforms de apagado de la maqueta (fAsim/fSangre/fEje/fCorte/
 * fDerrame/fMateria) colapsados a su lado "nuevo": esos uniforms solo
 * servian para comparar cada correccion con su version anterior en el
 * companion, no tienen sentido en produccion.
 *
 * Spec: docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime, uScroll, uCreditsEntry, uPixelRatio;
  uniform vec2 uResolution;
  varying vec2 vUv;

  /*
   * Techo de luminancia. Mecanismo importado de viceInk.ts (escala por
   * luminancia perceptual, no por canal: el verde aporta el 71% de la
   * luminancia percibida, asi que un tope por canal se calibra mirando un
   * tono concreto y se rompe en cuanto el fondo recorre otro), pero NO su
   * valor: 46 es el techo AA 4,5:1 de --haze (#b18c86, cuerpo de texto de
   * Hyprland), no el 62 de Vice, que esta calibrado contra su papel
   * #fff4e8.
   *
   * VA EL ULTIMO PASO, despues del grano. Medido: con el grano sumado
   * despues del recorte, su cola positiva se escapa del techo y el p99.5
   * sale a 48.1 en vez de 46.1.
   *
   * 44.3 y no 46: mismo ajuste que viceInk.ts documenta para su LUMA_MAX
   * (0.235 en vez del 0.243 naive de 62/255). El recorte por luminancia
   * garantiza matematicamente que NINGUN pixel supere el limite en el
   * fotograma que genera el shader, pero measure-fondo-haz.py contra
   * capturas reales (canvas -> PNG del pipeline de Playwright) media un
   * p99.5 de banda de 47.2-47.5 con el naive 46 -- un desvio sistematico
   * de esa conversion, no un fallo del recorte. 44.3 es el valor que hace
   * aterrizar el p99.5 medido por debajo de 46 con margen (medido:
   * scripts/measure-fondo-haz.py --base contra el build de produccion).
   */
  vec3 techo(vec3 c) {
    float lm = 44.3 / 255.0;
    float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
    return l > lm ? c * (lm / max(l, 1e-4)) : c;
  }

  const vec3 INK = vec3(0.043, 0.016, 0.016);
  const vec3 EMBER = vec3(1.0, 0.353, 0.204);
  const vec3 CRIM = vec3(0.878, 0.114, 0.235);
  const vec3 AMBER = vec3(1.0, 0.627, 0.235);

  /*
   * Grano de carbon atado a pixeles de DISPOSITIVO, no a uv: con la rejilla
   * atada a uv el paso cambia con la resolucion y bate contra la rejilla de
   * la pantalla, y eso hormiguea al scrollear. Misma razon por la que Vice
   * ata su lineatura al fragmento.
   *
   * Se divide por uPixelRatio para trabajar en pixeles CSS. Con el paso
   * fijo en pixeles de BUFFER el grano cambia de tamano fisico entre
   * pantallas: shaderBackground.ts acota el ratio a 1 en <=820px y a 1.5 en
   * escritorio, asi que sin esta division la textura saldria ~1.5 veces mas
   * fina en retina que sin retina. Mismo hallazgo que viceInk.ts, misma
   * decision.
   */
  float carbon(vec2 frag, float ang) {
    vec2 css = frag / max(uPixelRatio, 1.0);
    float c = cos(ang), s = sin(ang);
    vec2 r = vec2(css.x * c - css.y * s, css.x * s + css.y * c);
    return mix(fbm(r / 34.0), hash(floor(r / 1.4)), 0.30);
  }

  void main() {
    vec2 uv = vUv;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    vec2 p = (uv * 2.0 - 1.0) * vec2(aspect, 1.0);
    float px = 2.0 / uResolution.y;

    /*
     * MOVIL: no basta con enderezar el angulo. Medido a 390x844: con el
     * semiancho fijo, el haz cubre TODA la pantalla y su canto duro —lo
     * unico que define esta direccion— queda fuera del encuadre. Y con el
     * origen fijo el sitio abre con el fondo casi vacio, porque en un
     * encuadre estrecho el haz aun no ha entrado. El aspecto gobierna las
     * cuatro cosas, no solo el angulo.
     */
    float vertical = smoothstep(1.0, 0.62, aspect);
    float ang = mix(1.36, 1.52, vertical) - uScroll * mix(0.30, 0.14, vertical);

    vec2 dir = vec2(cos(ang), sin(ang));
    vec2 nrm = vec2(-dir.y, dir.x);
    vec2 o = vec2(mix(-0.62, -0.30, vertical) + uScroll * mix(0.95, 0.62, vertical),
                  mix(0.0, 0.30, vertical));
    vec2 rel = p - o;

    /* distancia CON SIGNO al eje: sin abs(), que hacia salir los dos cantos
       iguales y el haz se leia como una cinta pegada encima */
    float s = dot(rel, nrm);
    float hw = (0.26 + uScroll * 0.10) * mix(1.0, 0.42, vertical);

    /* CANTO ASIMETRICO: un canto duro que define el haz, el otro lado se
       pierde en el material a lo largo de 0.42 */
    float duro = 1.0 - smoothstep(-px * 0.7, px * 0.7, s - hw);
    float suave = smoothstep(-hw - 0.42, -hw + 0.02, s);
    float dentro = duro * suave;

    /* CAIDA POR SU EJE: se mide a lo largo del haz, no como degradado
       vertical de viewport, asi que gira con el haz al girar con el
       scroll */
    float alo = dot(rel, dir);
    float caida = smoothstep(1.45, -0.15, alo) * smoothstep(-1.6, -0.9, alo);

    vec3 col = INK;

    /* DERRAME: la luz que el haz suelta sobre el material, calculada desde
       su propio eje, no un foco con coordenadas propias */
    float derrame = exp(-abs(s - hw) * 2.6) * caida;
    col += mix(CRIM, EMBER, uScroll) * derrame * mix(0.30, 0.17, vertical);

    /* MATERIA dentro del haz, multiplicativa. Aditiva subiria el suelo del
       cuadro entero. El canto se queda liso a proposito. */
    float m = carbon(gl_FragCoord.xy, ang);
    float cuerpo = 0.55 + m * 0.85;

    col += mix(EMBER, AMBER, 0.5 + 0.5 * p.y) * dentro * caida * 0.19 * cuerpo;
    col += AMBER * (1.0 - smoothstep(0.0, px * 1.15, abs(s - hw))) * caida * 0.62;

    /*
     * CORTE EN FRONTERA. El segundo haz entra en el limite Obra->Creditos
     * real (uCreditsEntry, calculado en TS desde el offsetTop de #creditos
     * — nunca un literal escrito a mano aqui), con corte seco: algo que
     * aparece de la nada dentro de una escena se lee como fallo de render.
     */
    float ent = smoothstep(uCreditsEntry - 0.015, uCreditsEntry + 0.015, uScroll);
    vec2 o2 = vec2(0.55, 0.10);
    vec2 d2dir = vec2(cos(-0.95), sin(-0.95));
    float s2 = dot(p - o2, vec2(-d2dir.y, d2dir.x));
    float alo2 = dot(p - o2, d2dir);
    float caida2 = smoothstep(1.3, -0.9, alo2);
    col += AMBER * (1.0 - smoothstep(0.0, px * 1.15, abs(abs(s2) - 0.055))) * caida2 * 0.46 * ent;

    /* SALE A SANGRE: caida leve solo en el vertice contrario al haz, en vez
       de vinetado radial que moria justo en las esquinas por donde el haz
       sale del cuadro */
    col *= mix(1.0, 0.86, smoothstep(0.6, 1.9, length(p - vec2(0.9, -0.9))));

    col += (hash(uv * uResolution + uTime) - 0.5) * 0.026;
    col = techo(col);
    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountHyprEmber(container: HTMLElement): BackgroundHandle {
  /*
   * #creditos ya existe en el DOM cuando este modulo monta: main.ts compone
   * `main` completo (con las cinco secciones) y lo anexa a #app antes de
   * invocar `applyTheme` -> `mountBackground` (ver src/main.ts, orden entre
   * `app.append(backgroundHost, noise, main, ...)` y
   * `void applyTheme(theme, backgroundHost)`). La seccion no se recrea
   * durante la visita, asi que una lectura al montar basta.
   */
  const creditos = document.getElementById("creditos");

  const readScrollable = (): number =>
    Math.max(document.documentElement.scrollHeight - window.innerHeight, 0);

  /*
   * Modelo PULL, igual que uScroll en viceInk.ts: se lee del propio
   * `window` cada fotograma, no de Lenis ni de ScrollTrigger, para no
   * depender de que la coreografia (import dinamico) haya cargado.
   */
  const readScroll = (): number => {
    const scrollable = readScrollable();
    return scrollable <= 0 ? 0 : Math.min(Math.max(window.scrollY / scrollable, 0), 1);
  };

  /*
   * Se relee cada fotograma en vez de cachear una fraccion fija: un cambio
   * de layout por resize se refleja solo en el siguiente fotograma, sin
   * necesidad de un ResizeObserver propio (mountShaderBackground ya tiene
   * el suyo para el canvas, y este calculo no depende de el).
   */
  const readCreditsEntry = (): number => {
    const scrollable = readScrollable();
    if (scrollable <= 0 || !creditos) return 0.75; // respaldo: 75% del documento
    return Math.min(Math.max(creditos.offsetTop / scrollable, 0), 1);
  };

  return mountShaderBackground(container, FRAGMENT_SHADER, {
    uScroll: readScroll,
    uCreditsEntry: readCreditsEntry,
  });
}
