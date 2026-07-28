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
    vec3 lavender = vec3(0.560, 0.430, 0.910);
    vec3 mint = vec3(0.290, 0.780, 0.660);
    vec3 peach = vec3(0.990, 0.680, 0.480);
    vec3 sky = vec3(0.450, 0.680, 0.960);

    // Centros en espacio uv: se estiran con el viewport, lo que a esta escala
    // de desenfoque se lee como profundidad, no como deformacion.
    vec2 c1 = vec2(0.24 + sin(t * 0.90) * 0.12, 0.28 + cos(t * 0.70) * 0.12);
    vec2 c2 = vec2(0.78 + cos(t * 0.60) * 0.13, 0.62 + sin(t * 0.80) * 0.12);
    vec2 c3 = vec2(0.50 + sin(t * 0.50 + 1.7) * 0.16, 0.90 + cos(t * 0.65) * 0.09);
    vec2 c4 = vec2(0.88 + sin(t * 0.75 + 0.6) * 0.10, 0.18 + cos(t * 0.55) * 0.10);

    // Saturacion alta a proposito: las superficies tonales van encima con
    // blur, asi que el fondo necesita color de verdad para que se note.
    vec3 col = base;
    col = mix(col, lavender, smoothstep(0.46, 0.0, length(uv - c1)) * 0.72);
    col = mix(col, mint, smoothstep(0.42, 0.0, length(uv - c2)) * 0.62);
    col = mix(col, peach, smoothstep(0.48, 0.0, length(uv - c3)) * 0.55);
    col = mix(col, sky, smoothstep(0.38, 0.0, length(uv - c4)) * 0.50);

    // Respiracion: devuelve zonas hacia el base para que nada quede plano.
    col = mix(col, base, fbm(uv * 3.0 + t * 0.5) * 0.10);

    col += (hash(uv * uResolution + t) - 0.5) * 0.014;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountCaelestiaBlobs(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
