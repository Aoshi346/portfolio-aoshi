import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Vice City: atardecer sobre la costa. La escena se compone por capas — noche
 * estrellada arriba, nubes encendidas por debajo, sol con corte retro, skyline
 * en silueta y el reflejo temblando en el agua. Todo procedural: cero assets.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  /** Silueta de ciudad: bloques de altura pseudoaleatoria sobre una base. */
  float skyline(vec2 uv, float base, float seed, float density, float maxHeight) {
    float block = floor(uv.x * density + seed);
    float height = base + maxHeight * (0.20 + 0.80 * hash(vec2(block, seed * 7.3)));
    return step(uv.y, height);
  }

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.03;
    float aspect = uResolution.x / max(uResolution.y, 1.0);

    vec3 deepNight = vec3(0.030, 0.008, 0.080);
    vec3 violet = vec3(0.230, 0.040, 0.260);
    vec3 magenta = vec3(0.760, 0.070, 0.420);
    vec3 ember = vec3(1.000, 0.360, 0.170);

    vec3 col = mix(ember, magenta, smoothstep(0.14, 0.34, uv.y));
    col = mix(col, violet, smoothstep(0.30, 0.60, uv.y));
    col = mix(col, deepNight, smoothstep(0.55, 1.00, uv.y));

    // Estrellas: solo en la mitad alta, con parpadeo desfasado por celda.
    vec2 starCell = floor(uv * vec2(360.0, 260.0));
    float star = step(0.9975, hash(starCell));
    float twinkle = 0.55 + 0.45 * sin(uTime * 2.0 + hash(starCell) * 30.0);
    col += vec3(1.0, 0.92, 0.85) * star * twinkle * smoothstep(0.48, 0.95, uv.y) * 0.9;

    // Nubes: fbm estirado en horizontal, tenido de brasa donde el sol pega.
    float cloud = fbm(vec2(uv.x * 2.6 + t * 1.4, uv.y * 6.0 - t * 0.2));
    float cloudBand = smoothstep(0.30, 0.52, uv.y) * smoothstep(0.88, 0.55, uv.y);
    col = mix(col, mix(vec3(0.45, 0.10, 0.35), vec3(1.0, 0.55, 0.35), cloud), cloud * cloudBand * 0.42);

    // Sol descentrado (el eje central es del nombre). La mitad baja va cortada
    // en bandas: es el gesto retro que firma el atardecer.
    vec2 sunDelta = (uv - vec2(0.72, 0.235)) * vec2(aspect, 1.0);
    float sunDist = length(sunDelta);
    col += vec3(1.0, 0.52, 0.28) * smoothstep(0.55, 0.0, sunDist) * 0.40;
    float disc = smoothstep(0.150, 0.128, sunDist);
    float slices = step(0.45, fract((uv.y - 0.235) * 90.0 + t * 2.0));
    col = mix(col, vec3(1.0, 0.88, 0.60), disc * max(slices, smoothstep(0.28, 0.36, uv.y)) * 0.9);

    // Skyline en dos planos: el lejano se lee mas claro por la bruma.
    col = mix(col, vec3(0.145, 0.030, 0.150), skyline(uv, 0.115, 3.0, 26.0, 0.075) * 0.85);
    col = mix(col, vec3(0.055, 0.012, 0.075), skyline(uv, 0.085, 11.0, 15.0, 0.060));

    // Agua: columna de sol temblando bajo la linea de costa.
    float waterMask = smoothstep(0.090, 0.075, uv.y);
    float sunColumn = smoothstep(0.16, 0.0, abs(uv.x - 0.72) * aspect);
    float ripple = 0.5 + 0.5 * sin(uv.y * 160.0 + uTime * 1.6 + sin(uv.x * 18.0) * 2.0);
    col = mix(col, mix(vec3(0.08, 0.015, 0.10), vec3(1.0, 0.55, 0.30), sunColumn * ripple * 0.75), waterMask);

    float vig = smoothstep(1.35, 0.30, length((uv - vec2(0.5, 0.55)) * vec2(aspect, 1.0)));
    col *= mix(0.55, 1.0, vig);

    col += (hash(uv * uResolution + t) - 0.5) * 0.032;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountViceSunset(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
