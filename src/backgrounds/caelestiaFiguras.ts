import { chromaScaleAt, hueAt, isDarkAt } from "../themes/caelestia.color";
import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * El wallpaper de Caelestia: figuras con nombre de Material 3 Expressive que
 * morfan con la hora del visitante.
 *
 * Spec: docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md
 * Prototipo aprobado: docs/superpowers/specs/2026-08-26-caelestia-titulo-prototipo.glsl
 *
 * Sustituye a `caelestiaBlobs.ts`, que su propio comentario marcaba como
 * PROVISIONAL.
 *
 * `mountShaderBackground` solo admite uniforms `float` (modelo pull, un
 * `Record<string, () => number>`): el prototipo usa `vec3 uFigA/uFigB` y
 * `vec2 uElong`, asi que aqui se reparten en floats sueltos (`uFigAn/a/s`,
 * `uFigBn/a/s`, `uElongA/B`) y se reconstruyen dentro del shader con dos
 * funciones auxiliares. `shaderBackground.ts` es compartido con Vice y no se
 * toca para esto.
 */

/** Los cinco estados del dia. `n` = puntas, `a` = profundidad del lobulo
 *  (negativa = lado concavo, que es lo que hace un "cookie"), `s` = segundo
 *  armonico, que afila la punta. Los nombres son los de la biblioteca de
 *  Material 3 Expressive. */
const FIGURAS: readonly (readonly [n: number, a: number, s: number, elong: number])[] = [
  [4, 0.15, 0.02, 1.1], // 00:00 puffy
  [9, 0.105, 0.03, 1.0], // 04:48 sunny
  [12, -0.058, 0.012, 1.0], // 09:36 12-sided cookie
  [4, 0.265, -0.045, 1.0], // 14:24 4-leaf clover
  [10, 0.175, 0.07, 1.0], // 19:12 soft burst
] as const;

/** El transito ocupa el ultimo 30 % de cada tramo: 86 minutos. */
const TRANSICION = 0.3;

interface Fase {
  a: number;
  b: number;
  s: number;
}

export function faseAt(minutes: number): Fase {
  const f = (minutes / 1440) * 5;
  const i = Math.floor(f) % 5;
  const frac = f - Math.floor(f);
  const bruto = frac <= 1 - TRANSICION ? 0 : (frac - (1 - TRANSICION)) / TRANSICION;
  return { a: i, b: (i + 1) % 5, s: bruto * bruto * (3 - 2 * bruto) };
}

/** Los cuatro rellenos: la superficie base y los tres wall. El croma NO es el
 *  mismo en los dos esquemas — croma 0.09 a claridad 0.30 cae en la zona parda
 *  de OkLCH y da barro. De noche baja a un tercio y la claridad se abre. */
export function rampaAt(minutes: number): readonly (readonly [number, number, number])[] {
  const hue = hueAt(minutes);
  const esc = chromaScaleAt(hue);
  const osc = isDarkAt(minutes);
  return [
    [osc ? 0.185 : 0.98, (osc ? 0.016 : 0.012) * esc, hue],
    [osc ? 0.265 : 0.93, (osc ? 0.034 : 0.09) * esc, hue],
    [osc ? 0.32 : 0.95, (osc ? 0.028 : 0.07) * esc, (hue + 42) % 360],
    [osc ? 0.375 : 0.96, (osc ? 0.022 : 0.06) * esc, (hue + 318) % 360],
  ] as const;
}

const FRAGMENT_SHADER = /* glsl */ `
  precision highp float;
  uniform float uTime; uniform vec2 uResolution;
  uniform float uL0, uC0, uH0, uL1, uC1, uH1, uL2, uC2, uH2, uL3, uC3, uH3;
  uniform float uFigAn, uFigAa, uFigAs;   // uFigA (n, a, s)
  uniform float uFigBn, uFigBa, uFigBs;   // uFigB (n, a, s)
  uniform float uElongA, uElongB;         // uElong (elongA, elongB)
  uniform float uMezcla;
  varying vec2 vUv;

  vec3 figA() { return vec3(uFigAn, uFigAa, uFigAs); }
  vec3 figB() { return vec3(uFigBn, uFigBa, uFigBs); }

  vec3 fromHue(float hue, float l, float c){
    float h = radians(hue); float a = cos(h)*c; float b = sin(h)*c;
    float l_ = l + 0.3963377774*a + 0.2158037573*b;
    float m_ = l - 0.1055613458*a - 0.0638541728*b;
    float s_ = l - 0.0894841775*a - 1.2914855480*b;
    vec3 lms = vec3(l_*l_*l_, m_*m_*m_, s_*s_*s_);
    return clamp(mat3(4.0767416621,-1.2684380046,-0.0041960863,
                     -3.3077115913, 2.6097574011,-0.7034186147,
                      0.2309699292,-0.3413193965, 1.7076147010) * lms, 0.0, 1.0);
  }
  vec3 toSrgb(vec3 c){
    vec3 lo = c*12.92; vec3 hi = 1.055*pow(c, vec3(1.0/2.4)) - 0.055;
    return mix(lo, hi, step(0.0031308, c));
  }
  vec3 tono(int i){
    if (i == 0) return fromHue(uH0, uL0, uC0);
    if (i == 1) return fromHue(uH1, uL1, uC1);
    if (i == 2) return fromHue(uH2, uL2, uC2);
    return fromHue(uH3, uL3, uC3);
  }

  /* Radio de una figura de Material en polares. El numero de puntas SIEMPRE es
     entero: interpolar n daria un contorno que no cierra y se veria una costura
     en el angulo pi. Lo que se mezcla mas abajo son los dos radios completos. */
  float radio(vec3 fig, float th, float lat){
    float n = fig.x, a = fig.y * lat, s = fig.z * lat;
    return 1.0 + a * cos(n * th) + s * cos(2.0 * n * th);
  }

  /* Distancia con signo a la figura morfada, centrada en c y de tamano R. */
  float sdFigura(vec2 p, vec2 c, float R, float rot, float lat){
    vec2 q = p - c;
    q = mat2(cos(rot), -sin(rot), sin(rot), cos(rot)) * q;
    float el = mix(uElongA, uElongB, uMezcla);
    q.x /= el;
    float th = atan(q.y, q.x);
    float r = mix(radio(figA(), th, lat), radio(figB(), th, lat), uMezcla);
    return (length(q) - R * r) / max(R, 0.001);
  }

  /* Relleno con degradado interno entre dos pasteles, en la direccion de la luz
     nominal del sistema (arriba-izquierda). Va en LINEAL, antes de la gamma. */
  vec3 relleno(vec2 p, vec2 c, float R, int t1, int t2){
    float g = clamp(0.5 + dot(p - c, normalize(vec2(-0.55, 0.84))) / (2.0 * R), 0.0, 1.0);
    g = g * g * (3.0 - 2.0 * g);
    return mix(tono(t1), tono(t2), g);
  }

  /* Poner una figura sobre lo que ya hay. Todas las composiciones usan esta
     misma funcion: el estilo no cambia, solo cambia donde y cuantas. */
  vec3 pon(vec3 col, vec2 p, vec2 casa, float R, float velRot, float fase, float t,
           int t1, int t2, vec2 amp, vec2 frq){
    /* La figura no esta quieta en su sitio: ORBITA alrededor de el. Las dos
       frecuencias son distintas y no son multiplos, asi que el recorrido es una
       curva de Lissajous abierta — nunca repite el mismo camino. Es lo que
       separa "se mueve" de "se desliza": una traslacion recta se lee como una
       pegatina arrastrada; una orbita se lee como algo que flota. */
    vec2 c = casa + amp * vec2(sin(t * frq.x + fase), cos(t * frq.y + fase * 1.7));
    float lat = 1.0 + 0.09 * sin(t * 0.85 + fase);   // late con periodo de ~26 s
    float d = sdFigura(p, c, R, t * velRot + fase, lat);
    /* Antialias con un ancho fijo en vez de fwidth(): swiftshader (el
       driver headless del arnes) no trae GL_OES_standard_derivatives, y
       el resto de fondos del proyecto (hyprEmber, viceInk) ya usan un ancho
       constante en espacio normalizado en vez de derivadas de pantalla. */
    float aa = 1.5 * (2.0 / uResolution.y) / max(R, 0.001);
    float a = 1.0 - smoothstep(-aa, aa, d);
    return mix(col, relleno(p, c, R, t1, t2), a);
  }

  void main(){
    vec2 p = (vUv - 0.5) * vec2(uResolution.x/uResolution.y, 1.0);
    /* Dos relojes distintos y a proposito. El MORFADO entre figuras lo manda
       uMezcla, que viene de la hora del visitante: cambia una vez por tramo.
       El AMBIENTE — giro y latido — corre con este t, mucho mas rapido, para
       que se note en los treinta segundos que dura una visita. Con el factor
       de antes (0.045) la figura giraba 2 grados en medio minuto: matematica-
       mente se movia, humanamente estaba quieta. */
    float t = uTime * 0.28;
    vec3 col = tono(0);

    // A3 · Tres en diagonal: tamanos escalonados, la mirada baja de izquierda
    // a derecha. Es la unica que tiene direccion.
    col = pon(col, p, vec2(-0.68, 0.26), 0.44, 0.026, 0.0, t, 1, 2, vec2(0.18, 0.12), vec2(0.41, 0.33));
    col = pon(col, p, vec2(-0.02,-0.02), 0.31, -0.034, 1.3, t, 2, 3, vec2(0.22, 0.15), vec2(0.29, 0.47));
    col = pon(col, p, vec2( 0.58,-0.30), 0.21, 0.042, 2.6, t, 3, 1, vec2(0.16, 0.17), vec2(0.53, 0.37));
    /* Cuatro satelites en los huecos que deja la diagonal. Van fuera de las
       dos zonas ocupadas — el widget arriba a la derecha y el bloque de texto
       abajo a la izquierda — y dos de ellos los corta el canto de la ventana,
       que es lo que impide que se lean como pegatinas sueltas. */
    col = pon(col, p, vec2( 0.12, 0.42), 0.085, -0.058, 0.6, t, 3, 2, vec2(0.26, 0.07), vec2(0.61, 0.51));
    col = pon(col, p, vec2( 0.93, 0.05), 0.075, 0.066, 1.9, t, 2, 1, vec2(0.10, 0.24), vec2(0.44, 0.67));
    col = pon(col, p, vec2(-0.89, 0.47), 0.055, -0.074, 3.1, t, 1, 3, vec2(0.13, 0.09), vec2(0.71, 0.39));
    col = pon(col, p, vec2( 0.40,-0.46), 0.050, 0.081, 4.2, t, 3, 1, vec2(0.22, 0.08), vec2(0.34, 0.59));

    // Tramado: los degradados internos son largos y sin esto hacen bandas.
    col += (hash(vUv * uResolution + uTime * 0.045) - 0.5) * 0.0035;
    gl_FragColor = vec4(toSrgb(clamp(col, 0.0, 1.0)), 1.0);
  }
`;

const REFRESH_MS = 750;

export function mountCaelestiaFiguras(container: HTMLElement): BackgroundHandle {
  const cache = { min: -1, leido: -Infinity };
  let fase: Fase = { a: 0, b: 1, s: 0 };
  let rampa = rampaAt(0);

  function refresh(): void {
    const ahora = performance.now();
    if (ahora - cache.leido < REFRESH_MS) return;
    cache.leido = ahora;
    const d = new Date();
    const min = d.getHours() * 60 + d.getMinutes();
    if (min === cache.min) return;
    cache.min = min;
    fase = faseAt(min);
    rampa = rampaAt(min);
  }

  const leer =
    <T>(f: () => T) =>
    (): T => {
      refresh();
      return f();
    };

  return mountShaderBackground(container, FRAGMENT_SHADER, {
    uMezcla: leer(() => fase.s),
    uFigAn: leer(() => FIGURAS[fase.a][0]),
    uFigAa: leer(() => FIGURAS[fase.a][1]),
    uFigAs: leer(() => FIGURAS[fase.a][2]),
    uFigBn: leer(() => FIGURAS[fase.b][0]),
    uFigBa: leer(() => FIGURAS[fase.b][1]),
    uFigBs: leer(() => FIGURAS[fase.b][2]),
    uElongA: leer(() => FIGURAS[fase.a][3]),
    uElongB: leer(() => FIGURAS[fase.b][3]),
    uL0: leer(() => rampa[0][0]),
    uC0: leer(() => rampa[0][1]),
    uH0: leer(() => rampa[0][2]),
    uL1: leer(() => rampa[1][0]),
    uC1: leer(() => rampa[1][1]),
    uH1: leer(() => rampa[1][2]),
    uL2: leer(() => rampa[2][0]),
    uC2: leer(() => rampa[2][1]),
    uH2: leer(() => rampa[2][2]),
    uL3: leer(() => rampa[3][0]),
    uC3: leer(() => rampa[3][1]),
    uH3: leer(() => rampa[3][2]),
  });
}
