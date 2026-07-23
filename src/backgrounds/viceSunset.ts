import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Vice City: atardecer de neon con sol definido. El cielo va en cuatro tramos
 * (brasa -> magenta -> violeta -> noche) para que haya contraste real y no un
 * degradado plano, y una vinieta suave deja el centro limpio para el nombre.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.03;
    float aspect = uResolution.x / max(uResolution.y, 1.0);

    vec3 deepNight = vec3(0.035, 0.010, 0.090);
    vec3 violet = vec3(0.230, 0.040, 0.260);
    vec3 magenta = vec3(0.720, 0.070, 0.420);
    vec3 ember = vec3(1.000, 0.330, 0.180);

    vec3 col = mix(ember, magenta, smoothstep(0.00, 0.26, uv.y));
    col = mix(col, violet, smoothstep(0.20, 0.54, uv.y));
    col = mix(col, deepNight, smoothstep(0.50, 1.00, uv.y));

    // Sol bajo y descentrado: halo ancho + disco recortado. Va fuera del eje
    // central a proposito — ahi va el nombre y el contacto, y el disco los
    // dejaba ilegibles.
    vec2 sunDelta = (uv - vec2(0.72, 0.20)) * vec2(aspect, 1.0);
    float sunDist = length(sunDelta);
    col += vec3(1.0, 0.52, 0.30) * smoothstep(0.52, 0.0, sunDist) * 0.38;
    col = mix(col, vec3(1.0, 0.87, 0.58), smoothstep(0.150, 0.122, sunDist) * 0.85);

    // Bandas horizontales sobre el sol: el corte retro del horizonte.
    float bands = sin((uv.y + t * 0.6) * 44.0) * 0.5 + 0.5;
    float bandMask = smoothstep(0.34, 0.02, uv.y) * smoothstep(0.0, 0.08, uv.y);
    col += vec3(1.0, 0.45, 0.30) * bands * bandMask * 0.12;

    float haze = fbm(vec2(uv.x * 2.2 + t, uv.y * 3.0 - t * 0.5));
    col += vec3(0.85, 0.20, 0.55) * haze * 0.13 * smoothstep(0.92, 0.20, uv.y);

    // Neon teal lamiendo el borde inferior.
    col = mix(col, vec3(0.0, 0.80, 0.78), smoothstep(0.05, 0.0, uv.y) * 0.30);

    float vig = smoothstep(1.30, 0.28, length((uv - vec2(0.5, 0.55)) * vec2(aspect, 1.0)));
    col *= mix(0.58, 1.0, vig);

    col += (hash(uv * uResolution + t) - 0.5) * 0.030;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountViceSunset(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
