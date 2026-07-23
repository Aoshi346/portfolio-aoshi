import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Hyprland: el gradiente firma cian -> verde (#33ccff / #00ff99) fluyendo sobre
 * negro. Domain warping para que las bandas se plieguen como cristal liquido.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.05;
    float aspect = uResolution.x / max(uResolution.y, 1.0);

    vec2 p = (uv * 2.0 - 1.0) * vec2(aspect, 1.0);

    // Domain warping: el segundo fbm se muestrea desplazado por el primero.
    float warp = fbm(p * 1.4 + vec2(t, -t * 0.7));
    float flow = fbm(p * 1.9 + vec2(-t * 0.8, t * 1.1) + warp * 1.6);

    vec3 cyan = vec3(0.200, 0.800, 1.000);
    vec3 green = vec3(0.000, 1.000, 0.600);
    vec3 base = vec3(0.020, 0.027, 0.040);

    float band = smoothstep(0.25, 0.85, flow);
    vec3 col = mix(base, mix(cyan, green, warp), band * 0.55);

    // Nucleos brillantes: la sensacion "glass" viene del brillo concentrado.
    float glow = pow(smoothstep(0.55, 1.0, flow), 2.0);
    col += mix(cyan, green, flow) * glow * 0.35;

    // Vinieta: mantiene el centro legible.
    col *= smoothstep(1.85, 0.25, length(p));

    col += (hash(uv * uResolution + t) - 0.5) * 0.022;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountHyprGradient(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
