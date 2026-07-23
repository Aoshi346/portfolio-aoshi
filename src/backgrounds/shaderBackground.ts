export interface BackgroundHandle {
  destroy: () => void;
}

/**
 * Quad a pantalla completa en WebGL crudo. Se evita Three.js a proposito: el
 * unico uso de WebGL del sitio son fragment shaders fullscreen, y la libreria
 * anadia ~516 kB (129 kB gzip) para dibujar dos triangulos.
 */
const VERTEX_SHADER = /* glsl */ `
  attribute vec2 aPosition;
  varying vec2 vUv;

  void main() {
    vUv = aPosition * 0.5 + 0.5;
    gl_Position = vec4(aPosition, 0.0, 1.0);
  }
`;

/**
 * Ruido de valor + fbm compartido por los shaders de tema. Se antepone al
 * fragment shader de cada fondo para no duplicarlo tres veces.
 */
export const NOISE_CHUNK = /* glsl */ `
  precision highp float;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
      mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x),
      u.y
    );
  }

  float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    for (int i = 0; i < 5; i++) {
      v += a * noise(p);
      p *= 2.0;
      a *= 0.5;
    }
    return v;
  }
`;

/** Instante fijo que se renderiza cuando el usuario pide movimiento reducido. */
const STATIC_FRAME_TIME = 8.0;

/** Fondo inerte: si el navegador no da contexto WebGL queda el degradado CSS. */
const NOOP_HANDLE: BackgroundHandle = { destroy: () => {} };

function compileShader(gl: WebGLRenderingContext, type: number, source: string): WebGLShader | null {
  const shader = gl.createShader(type);
  if (!shader) return null;

  gl.shaderSource(shader, source);
  gl.compileShader(shader);

  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    console.error("Shader compile failed:", gl.getShaderInfoLog(shader));
    gl.deleteShader(shader);
    return null;
  }
  return shader;
}

/**
 * Monta un fondo generativo a pantalla completa a partir de un fragment shader.
 * Mantiene la disciplina de limpieza del proyecto: cancela el RAF, desconecta
 * observers y libera programa, shaders, buffer y contexto al destruir.
 */
export function mountShaderBackground(
  container: HTMLElement,
  fragmentShader: string,
): BackgroundHandle {
  const canvas = document.createElement("canvas");
  const gl = canvas.getContext("webgl", { antialias: false, alpha: false, depth: false });
  if (!gl) return NOOP_HANDLE;

  const vertex = compileShader(gl, gl.VERTEX_SHADER, VERTEX_SHADER);
  const fragment = compileShader(gl, gl.FRAGMENT_SHADER, `${NOISE_CHUNK}\n${fragmentShader}`);
  const program = gl.createProgram();

  if (!vertex || !fragment || !program) return NOOP_HANDLE;

  gl.attachShader(program, vertex);
  gl.attachShader(program, fragment);
  gl.linkProgram(program);

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error("Program link failed:", gl.getProgramInfoLog(program));
    return NOOP_HANDLE;
  }

  gl.useProgram(program);

  // Quad como triangle strip: cuatro vertices, sin index buffer.
  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);

  const positionLocation = gl.getAttribLocation(program, "aPosition");
  gl.enableVertexAttribArray(positionLocation);
  gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

  const timeLocation = gl.getUniformLocation(program, "uTime");
  const resolutionLocation = gl.getUniformLocation(program, "uResolution");

  container.appendChild(canvas);

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function draw(elapsed: number) {
    if (!gl) return;
    gl.uniform1f(timeLocation, elapsed);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  function resize() {
    if (!gl) return;
    const { clientWidth, clientHeight } = container;
    if (clientWidth === 0 || clientHeight === 0) return;

    // Los degradados son suaves: no necesitan DPR alto y el coste sube al cuadrado.
    const ratio = Math.min(window.devicePixelRatio, 1.5);
    canvas.width = Math.floor(clientWidth * ratio);
    canvas.height = Math.floor(clientHeight * ratio);

    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(resolutionLocation, canvas.width, canvas.height);
    if (prefersReducedMotion) draw(STATIC_FRAME_TIME);
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(container);
  resize();

  let isVisible = true;
  const intersectionObserver = new IntersectionObserver(
    ([entry]) => {
      isVisible = entry.isIntersecting;
    },
    { threshold: 0 },
  );
  intersectionObserver.observe(container);

  let frameId = 0;
  const start = performance.now();

  function animate(timestamp: number) {
    frameId = requestAnimationFrame(animate);
    if (!isVisible) return;
    draw((timestamp - start) / 1000);
  }

  if (prefersReducedMotion) {
    // Una sola pasada estatica: el fondo queda compuesto pero inmovil.
    draw(STATIC_FRAME_TIME);
  } else {
    frameId = requestAnimationFrame(animate);
  }

  return {
    destroy() {
      cancelAnimationFrame(frameId);
      resizeObserver.disconnect();
      intersectionObserver.disconnect();

      gl.deleteBuffer(buffer);
      gl.detachShader(program, vertex);
      gl.detachShader(program, fragment);
      gl.deleteShader(vertex);
      gl.deleteShader(fragment);
      gl.deleteProgram(program);
      gl.getExtension("WEBGL_lose_context")?.loseContext();

      if (canvas.parentNode === container) {
        container.removeChild(canvas);
      }
    },
  };
}
