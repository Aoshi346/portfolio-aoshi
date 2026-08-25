import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * El wallpaper de Caelestia.
 *
 * PROVISIONAL: el fondo generativo definitivo es una fase propia y aun no esta
 * disenado. Lo que hace esta version es dejar de traer color propio -- los
 * cuatro pasteles fijos que habia contradecian al motor de la hora -- y pasar a
 * ser una version difusa del mismo matiz que gobierna el tema.
 *
 * El matiz llega por `--cae-hue`, que escribe `caelestia.color.ts`.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  uniform float uHue;
  uniform float uDark;
  varying vec2 vUv;

  // OkLCH -> sRGB aproximado, suficiente para un fondo desenfocado.
  vec3 fromHue(float hue, float l, float c) {
    float h = radians(hue);
    float a = cos(h) * c;
    float b = sin(h) * c;
    float l_ = l + 0.3963377774 * a + 0.2158037573 * b;
    float m_ = l - 0.1055613458 * a - 0.0638541728 * b;
    float s_ = l - 0.0894841775 * a - 1.2914855480 * b;
    vec3 lms = vec3(l_ * l_ * l_, m_ * m_ * m_, s_ * s_ * s_);
    return clamp(mat3(
       4.0767416621, -1.2684380046, -0.0041960863,
      -3.3077115913,  2.6097574011, -0.7034186147,
       0.2309699292, -0.3413193965,  1.7076147010
    ) * lms, 0.0, 1.0);
  }

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.05;

    float lBase = mix(0.975, 0.175, uDark);
    float lBlob = mix(0.930, 0.245, uDark);

    vec3 col = fromHue(uHue, lBase, 0.010);

    vec2 c1 = vec2(0.22 + sin(t * 0.85) * 0.10, 0.26 + cos(t * 0.65) * 0.10);
    vec2 c2 = vec2(0.80 + cos(t * 0.55) * 0.11, 0.64 + sin(t * 0.75) * 0.10);
    vec2 c3 = vec2(0.52 + sin(t * 0.45 + 1.7) * 0.14, 0.90 + cos(t * 0.60) * 0.08);

    col = mix(col, fromHue(uHue, lBlob, 0.075), smoothstep(0.46, 0.0, length(uv - c1)) * 0.70);
    col = mix(col, fromHue(mod(uHue + 42.0, 360.0), lBlob, 0.060), smoothstep(0.42, 0.0, length(uv - c2)) * 0.60);
    col = mix(col, fromHue(mod(uHue + 318.0, 360.0), lBlob, 0.050), smoothstep(0.48, 0.0, length(uv - c3)) * 0.52);

    col += (hash(uv * uResolution + t) - 0.5) * 0.010;

    gl_FragColor = vec4(col, 1.0);
  }
`;

/*
 * uHue y uDark son uniforms dinamicos (modelo pull de shaderBackground.ts):
 * la lectora se llama en CADA fotograma. `getComputedStyle` fuerza un
 * recalculo de estilo y el matiz solo avanza 0,25 grados por minuto -- no
 * hace falta leerlo 60 veces por segundo. Se cachea y se refresca como mucho
 * cada REFRESH_MS, comparando contra `performance.now()`. `root.dataset` es
 * barato (no fuerza recalculo de estilo) pero se cachea igual para no llevar
 * dos mecanismos distintos.
 */
const REFRESH_MS = 750;

export function mountCaelestiaBlobs(container: HTMLElement): BackgroundHandle {
  const root = document.documentElement;

  // Respaldo sensato si el fondo monta antes que caelestia.color.ts haya
  // escrito --cae-hue (los dos cargan con import() diferido): nunca NaN.
  let cachedHue = 0;
  let cachedDark = 0;
  let lastRead = -Infinity;

  function refresh(): void {
    const now = performance.now();
    if (now - lastRead < REFRESH_MS) return;
    lastRead = now;

    const parsedHue = parseFloat(getComputedStyle(root).getPropertyValue("--cae-hue"));
    if (Number.isFinite(parsedHue)) cachedHue = parsedHue;

    cachedDark = root.dataset.caeEsquema === "noche" ? 1 : 0;
  }

  const readHue = (): number => {
    refresh();
    return cachedHue;
  };

  const readDark = (): number => {
    refresh();
    return cachedDark;
  };

  return mountShaderBackground(container, FRAGMENT_SHADER, {
    uHue: readHue,
    uDark: readDark,
  });
}
