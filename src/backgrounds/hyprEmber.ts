import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Ascua: el campo de brasa y el haz.
 *
 * Dos piezas, y la segunda es la que importa. El campo es emision suave
 * (halo anisotropo, elipse rotada, no un circulo). El HAZ es una cuna de
 * bordes NITIDOS que cruza en diagonal: es el gesto que rompe con lo blando,
 * y lo blando era justo lo que hacia que el tema se leyera como generado.
 *
 * El grano no es decorativo: sin el, un degradado de este tamano hace bandas
 * visibles sobre un campo casi negro.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  /* distancia con signo a una banda diagonal: el canto duro del haz */
  float beam(vec2 p, float ang, float halfWidth) {
    vec2 dir = vec2(cos(ang), sin(ang));
    vec2 n = vec2(-dir.y, dir.x);
    return halfWidth - abs(dot(p, n));
  }

  void main() {
    vec2 uv = vUv;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    vec2 p = (uv * 2.0 - 1.0) * vec2(aspect, 1.0);
    float t = uTime * 0.04;

    vec3 base  = vec3(0.043, 0.016, 0.016);   /* #0b0404 */
    vec3 ember = vec3(1.000, 0.353, 0.204);   /* #ff5a34 */
    vec3 crim  = vec3(0.878, 0.114, 0.235);   /* #e01d3c */
    vec3 amber = vec3(1.000, 0.627, 0.235);   /* #ffa03c */

    /* campo: halo anisotropo que respira, no una mancha centrada */
    vec2 c = vec2(-0.18 + sin(t * 0.7) * 0.12, 0.22 + cos(t * 0.5) * 0.08);
    vec2 q = (p - c) * vec2(0.62, 1.15);
    float glow = exp(-dot(q, q) * 1.25);
    vec3 col = base + mix(crim, ember, 0.5 + 0.5 * sin(t)) * glow * 0.85;

    /* segundo foco, mas frio y bajo, para que el campo no sea simetrico */
    vec2 q2 = (p - vec2(0.55, -0.42)) * vec2(0.9, 1.3);
    col += crim * exp(-dot(q2, q2) * 2.4) * 0.3;

    /* EL HAZ: canto duro. El smoothstep es de ~1,5 pixeles, no un degradado. */
    float px = 2.0 / uResolution.y;
    float ang = 1.28 + sin(t * 0.35) * 0.05;
    float d = beam(p - vec2(-0.45, 0.0), ang, 0.30);
    float edge = smoothstep(0.0, px * 1.5, d);
    float falloff = smoothstep(1.25, -0.35, p.y);
    col += mix(ember, amber, 0.5 + 0.5 * p.y) * edge * falloff * 0.20;

    /* vinetado y grano */
    col *= smoothstep(2.05, 0.30, length(p));
    col += (hash(uv * uResolution + t) - 0.5) * 0.030;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountHyprEmber(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
