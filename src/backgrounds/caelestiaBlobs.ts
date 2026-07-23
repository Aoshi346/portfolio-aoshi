import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Caelestia: Material You. Fondo claro con blobs pastel que orbitan y se
 * funden lentamente — el unico tema luminoso, para que el contraste al
 * refrescar sea inmediato.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.08;

    vec3 base = vec3(0.957, 0.941, 0.976);
    vec3 lavender = vec3(0.630, 0.530, 0.900);
    vec3 mint = vec3(0.420, 0.820, 0.720);
    vec3 peach = vec3(0.980, 0.760, 0.580);

    // Centros en espacio uv: se estiran con el viewport, lo que a esta escala
    // de desenfoque se lee como profundidad, no como deformacion.
    vec2 c1 = vec2(0.28 + sin(t * 0.90) * 0.10, 0.32 + cos(t * 0.70) * 0.10);
    vec2 c2 = vec2(0.74 + cos(t * 0.60) * 0.11, 0.60 + sin(t * 0.80) * 0.10);
    vec2 c3 = vec2(0.52 + sin(t * 0.50 + 1.7) * 0.13, 0.88 + cos(t * 0.65) * 0.07);

    vec3 col = base;
    col = mix(col, lavender, smoothstep(0.42, 0.0, length(uv - c1)) * 0.55);
    col = mix(col, mint, smoothstep(0.38, 0.0, length(uv - c2)) * 0.45);
    col = mix(col, peach, smoothstep(0.45, 0.0, length(uv - c3)) * 0.40);

    // Respiracion: devuelve zonas hacia el base para que nada quede plano.
    col = mix(col, base, fbm(uv * 3.0 + t * 0.5) * 0.12);

    col += (hash(uv * uResolution + t) - 0.5) * 0.016;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountCaelestiaBlobs(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
