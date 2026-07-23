import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Vice City: atardecer de neon. Cielo purpura que cae a magenta y ambar sobre
 * el horizonte, sol difuso bajo, bruma en capas y un remate teal abajo.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.03;
    float aspect = uResolution.x / max(uResolution.y, 1.0);

    vec3 nightTop = vec3(0.055, 0.020, 0.145);
    vec3 magenta = vec3(0.450, 0.055, 0.360);
    vec3 ember = vec3(1.000, 0.360, 0.240);

    // Degradado vertical: brasa abajo (horizonte) -> magenta -> noche arriba.
    vec3 col = mix(ember, magenta, smoothstep(0.0, 0.55, uv.y));
    col = mix(col, nightTop, smoothstep(0.45, 1.0, uv.y));

    // Sol difuso, bajo y descentrado.
    vec2 sunDelta = (uv - vec2(0.5, 0.26)) * vec2(aspect, 1.0);
    float sun = smoothstep(0.38, 0.0, length(sunDelta));
    col += vec3(1.0, 0.58, 0.36) * sun * 0.55;

    // Bruma en capas que deriva lateralmente.
    float haze = fbm(vec2(uv.x * 2.4 + t, uv.y * 3.2 - t * 0.6));
    col += vec3(0.9, 0.22, 0.52) * haze * 0.11 * smoothstep(0.85, 0.15, uv.y);

    // Neon teal lamiendo el borde inferior.
    col = mix(col, vec3(0.0, 0.78, 0.74), smoothstep(0.16, 0.0, uv.y) * 0.32);

    // Vinieta suave para que el texto respire.
    float vig = smoothstep(1.35, 0.30, length((uv - 0.5) * vec2(aspect, 1.0)));
    col *= mix(0.72, 1.0, vig);

    // Grano fino: rompe el banding de los degradados.
    col += (hash(uv * uResolution + t) - 0.5) * 0.028;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountViceSunset(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
