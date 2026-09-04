/**
 * Las 23 figuras de Material 3 Expressive de la bandeja de Creditos (B4).
 *
 * Todas son la misma curva armonica polar:
 *
 *     r(t) = 1 + a·cos(n·t) + s·cos(2n·t)
 *
 * `n` son los lobulos —lo que distingue una figura de otra— y el signo de `a`
 * decide si son concavos (galleta) o convexos (trebol). UNA sola familia para
 * las 23: con familias de canto recto mezcladas no existe un area comun
 * alcanzable (un hexagono no baja de 3.00 y un cuadrado no baja de 3.147), y el
 * despeje las aplanaba a circulos.
 *
 * Las amplitudes de `AMPLITUDES` salen despejadas por biseccion en
 * `docs/superpowers/specs/2026-09-03-caelestia-creditos-figuras.py`, que ademas
 * lleva los seis gates (23 figuras, 23 unicas, 240 vertices, dispersion de area
 * < 0,5 %, relieve >= 6 %, anisotropia < 1,25). Aqui solo se reconstruye.
 *
 * Se reconstruye en vez de embeber porque el generador emite 167 KB de
 * coordenadas y no hacen falta: medido, dividir por `rmax` es redundante
 * cuando despues se encaja normalizando el VANO de cada eje (desviacion punto
 * a punto 4.4e-16, error de coma flotante).
 */

/** 240 y no menos: dos `polygon()` solo interpolan si tienen el MISMO numero
 *  de puntos. Con distinto, el navegador no morfa — corta de golpe, sin error
 *  y sin aviso. Es la trampa que costo la fase B2. */
const VERTICES = 240;

/** Slug de figura: la clave de `AMPLITUDES`, tal como llega desde `content.ts`. */
export type SlugFigura = string;

interface DefFigura {
  readonly tipo: "galleta" | "trebol";
  readonly n: number;
  readonly a: number;
}

/* Pega aqui la tabla del Paso 1, con esta forma. Concavas en Interfaz y
   Herramientas, convexas en Backend y Lenguajes: el territorio ya lo dicen la
   banda y su rotulo, la figura identifica la PIEZA. Ninguna concava por debajo
   de 5 lobulos — con 3 o 4 la cintura se cierra tanto que la figura se lee
   como un aspa y el icono se sale por los brazos. */
const AMPLITUDES: Readonly<Record<string, DefFigura>> = {
  // Interfaz
  react: { tipo: "galleta", n: 5, a: 0.095138 },
  nextdotjs: { tipo: "galleta", n: 6, a: 0.09705 },
  typescript: { tipo: "galleta", n: 7, a: 0.070599 },
  tailwindcss: { tipo: "galleta", n: 8, a: 0.110285 },
  vite: { tipo: "galleta", n: 9, a: 0.059717 },
  gsap: { tipo: "galleta", n: 10, a: 0.061956 },
  electron: { tipo: "galleta", n: 11, a: 0.05384 },
  gtk: { tipo: "galleta", n: 12, a: 0.072186 },
  // Backend y datos
  python: { tipo: "trebol", n: 3, a: 0.183186 },
  django: { tipo: "trebol", n: 4, a: 0.056827 },
  nodedotjs: { tipo: "trebol", n: 5, a: 0.112974 },
  mysql: { tipo: "trebol", n: 6, a: 0.118822 },
  rxdb: { tipo: "trebol", n: 7, a: 0.089681 },
  // Lenguajes base
  javascript: { tipo: "trebol", n: 8, a: 0.056809 },
  html5: { tipo: "trebol", n: 9, a: 0.078557 },
  css: { tipo: "trebol", n: 10, a: 0.082262 },
  c: { tipo: "trebol", n: 11, a: 0.072448 },
  cplusplus: { tipo: "trebol", n: 12, a: 0.05678 },
  // Herramientas
  git: { tipo: "galleta", n: 13, a: 0.050769 },
  github: { tipo: "galleta", n: 14, a: 0.05196 },
  n8n: { tipo: "galleta", n: 15, a: 0.048537 },
  claude: { tipo: "galleta", n: 16, a: 0.058386 },
  googlegemini: { tipo: "galleta", n: 18, a: 0.048394 },
};

type Punto = readonly [number, number];

function radios({ tipo, n, a }: DefFigura, relieve: number): number[] {
  const amp = (tipo === "galleta" ? -a : a) * relieve;
  const seg = (tipo === "galleta" ? a * 0.18 : -a * 0.14) * relieve;
  const rs: number[] = [];
  for (let i = 0; i < VERTICES; i += 1) {
    const t = (i * 2 * Math.PI) / VERTICES;
    rs.push(1 + amp * Math.cos(n * t) + seg * Math.cos(2 * n * t));
  }
  return rs;
}

/**
 * Encaja el poligono en su caja normalizando el VANO de cada eje, y recentra.
 *
 * No vale dividir por `max(abs(x))`: eso es el RADIO, no la semianchura, y en
 * una figura de lobulos impares la silueta no es simetrica respecto al centro.
 * Medido con la version anterior: el trebol de 3 ocupaba 90,4 px de ancho donde
 * el de 4 ocupaba 102 — un 13,7 % menos con el mismo dato, que es exactamente
 * lo que se veia.
 */
function encaja(rs: readonly number[]): Punto[] {
  const p: Punto[] = rs.map((r, i) => {
    const t = (i * 2 * Math.PI) / VERTICES;
    return [r * Math.cos(t), r * Math.sin(t)] as const;
  });
  const xs = p.map(([x]) => x);
  const ys = p.map(([, y]) => y);
  const cx = (Math.max(...xs) + Math.min(...xs)) / 2;
  const cy = (Math.max(...ys) + Math.min(...ys)) / 2;
  const hx = (Math.max(...xs) - Math.min(...xs)) / 2;
  const hy = (Math.max(...ys) - Math.min(...ys)) / 2;
  return p.map(([x, y]) => [(x - cx) / hx, (y - cy) / hy] as const);
}

function poly(p: readonly Punto[]): string {
  return `polygon(${p
    .map(([x, y]) => `${(50 + 50 * x).toFixed(2)}% ${(50 + 50 * y).toFixed(2)}%`)
    .join(", ")})`;
}

const cache = new Map<string, string>();

function figura(slug: string, relieve: number, clave: string): string {
  const memo = cache.get(clave);
  if (memo !== undefined) return memo;
  const def = AMPLITUDES[slug];
  // defensive: un slug nuevo en content.ts sin figura no debe romper la escena;
  // cae al circulo, que es una figura valida de 240 vertices.
  const salida = def ? poly(encaja(radios(def, relieve))) : FIGURA_CIRCULO;
  cache.set(clave, salida);
  return salida;
}

export function figuraDe(slug: string): string {
  return figura(slug, 1, `f:${slug}`);
}

/** Al rozar, la figura se ablanda sin cambiar de caja: mismo numero de
 *  vertices, asi que interpola. */
export function figuraSuaveDe(slug: string): string {
  return figura(slug, 0.42, `s:${slug}`);
}

export const FIGURA_CIRCULO: string = poly(
  encaja(new Array<number>(VERTICES).fill(1)),
);

/** El icono se acota por el radio INSCRITO, no por la caja: en una figura de
 *  lobulos profundos la cintura queda por dentro del canto y el icono se salia
 *  por los brazos. */
export function radioInscritoDe(slug: string): number {
  const def = AMPLITUDES[slug];
  if (!def) return 1;
  return Math.min(...encaja(radios(def, 1)).map(([x, y]) => Math.hypot(x, y)));
}
