import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Vice: serigrafia de cartel a dos tintas. Dos focos (magenta, ambar) tramados
 * en semitono real sobre gl_FragCoord, con rasqueta y desregistro por tinta.
 * El fondo deja de "representar" (bruma, atmosfera) y pasa a ser la materia
 * sobre la que el cartel estaria impreso.
 *
 * Reacciona al scroll por una sola via: `uScroll` (0..1, progreso del
 * documento) mueve el balance entre tintas — magenta en la apertura, ambar en
 * el cierre — y desplaza los dos focos en diagonal. No usa puntero ni
 * velocidad: el prototipo aprobado (`fondos-vice.html`, composicion `print`)
 * tampoco los usa, y anadirlos aqui seria rediseñar, no portar.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  uniform float uScroll;
  varying vec2 vUv;

  const vec3 INK = vec3(0.082, 0.027, 0.149);
  const vec3 AMBER = vec3(1.0, 0.820, 0.400);
  const vec3 MAGENTA = vec3(1.0, 0.180, 0.533);

  /*
   * El techo que permite que el texto se apoye en el fondo sin scrim.
   *
   * Es un techo de LUMINANCIA, no un min por canal. Un min por canal se
   * calibra mirando un tono concreto (magenta, ambar) y falla en cuanto el
   * fondo recorre un tono distinto: el verde aporta el 71% de la luminancia
   * percibida, asi que un cian tocando el mismo tope por canal sale mucho mas
   * luminoso que un magenta o un ambar en el mismo tope. Escalando por
   * luminancia el techo vale para cualquier tono.
   */
  // 0.235 y no 0.26: el limite real medido sobre el sitio es un p99.5
  // de 62 sobre 255 en la franja del texto, o sea 0.243 en lineal. Con
  // 0.26 los fondos salian a 63-64, justo por encima.
  const float LUMA_MAX = 0.235;
  vec3 ceilingClamp(vec3 c) {
    float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
    return l > LUMA_MAX ? c * (LUMA_MAX / max(l, 1e-4)) : c;
  }

  /*
   * Un paso de trama.
   *
   * Trabaja en gl_FragCoord, NO en vUv, y eso no es un detalle: fija el
   * paso de trama en pixeles de DISPOSITIVO, que es como funciona una
   * lineatura real (constante en el papel, no en la imagen). Con la
   * rejilla atada a uv, el paso cambia con la resolucion y la retina de
   * puntos bate contra la rejilla de pixeles de la pantalla: muare, que
   * hormiguea al hacer scroll. Es el riesgo principal de esta direccion.
   */
  float screenDot(vec2 frag, float ang, float pitch, float cover) {
    float c = cos(ang), s = sin(ang);
    vec2 r = vec2(frag.x * c - frag.y * s, frag.x * s + frag.y * c) / pitch;
    vec2 cell = fract(r) - 0.5;
    // El radio crece con la cobertura, y por encima del 0.5 de la celda
    // los puntos se tocan: ganancia de punto, igual que en imprenta.
    float radius = cover * 0.80;
    return smoothstep(radius, radius - 0.20, length(cell));
  }

  /*
   * Marca de registro: la cruz dentro de un anillo que el impresor pone
   * FUERA del corte para alinear las dos planchas. Aqui va en las cuatro
   * esquinas y en una sola tinta — si estuviera en las dos ya no serviria
   * para registrar nada, que es justo el chiste.
   */
  float regMark(vec2 frag, vec2 c, float size) {
    vec2 d = abs(frag - c);
    float arm = 0.85;
    float cross = max(
      step(d.x, arm) * step(d.y, size),
      step(d.y, arm) * step(d.x, size)
    );
    float rad = length(frag - c);
    float ring = smoothstep(size * 0.66, size * 0.60, rad)
               - smoothstep(size * 0.52, size * 0.46, rad);
    return clamp(cross + ring, 0.0, 1.0);
  }

  void main() {
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    vec2 uv = vUv * vec2(aspect, 1.0);
    vec2 p = (vUv * 2.0 - 1.0) * vec2(aspect, 1.0);
    vec2 frag = gl_FragCoord.xy;

    float t = uTime * 0.03;

    /*
     * LO QUE LA TRAMA DIBUJA. Un semitono que trama ruido lee como una
     * textura pegada encima; en un cartel el semitono SIEMPRE describe una
     * forma. Aqui describe una fuente de luz que cruza el encuadre con el
     * recorrido, asi que los puntos tienen direccion y el pliego tiene
     * sujeto.
     */
    /*
     * Los dos focos van en diagonal y a distinta altura, no cruzando el
     * centro: el ambar es la tinta mas luminosa y pasandolo por el medio
     * caia justo en la franja por la que corre la tipografia (p99.5 de
     * 63 sobre un techo de 62). Abajo a la derecha cumple y ademas la
     * composicion gana una diagonal en vez de dos manchas enfrentadas.
     */
    vec2 lightM = vec2(-0.72 + uScroll * 0.75, 0.50 - uScroll * 0.35);
    vec2 lightA = vec2(0.66 - uScroll * 0.42, -0.58 + uScroll * 0.5);

    float dM = length((p - lightM) * vec2(0.82, 1.30));
    float dA = length((p - lightA) * vec2(1.22, 0.86));

    // Caida cerrada (1.9, no 0.75): con una caida amplia el foco llenaba
    // el encuadre entero y quedaba un unico monticulo centrado, que es
    // justo lo contrario de tener forma.
    float fieldM = exp(-dM * dM * 1.9);
    float fieldA = exp(-dA * dA * 1.7);

    // Diente del papel y malla imperfecta: rompe la perfeccion del foco
    // sin llegar a describir otra cosa.
    float tooth = fbm(uv * 3.4 + vec2(t, -t * 0.6)) - 0.5;

    /*
     * Rasqueta: la cobertura nunca es uniforme en una serigrafia real —
     * carga mas por un lado y la malla se satura por zonas. Muy baja
     * frecuencia y distinta por tinta, porque son dos pasadas distintas.
     */
    float squeegeeM = 0.68 + 0.42 * fbm(uv * 0.85 + vec2(2.7, 0.0));
    float squeegeeA = 0.68 + 0.42 * fbm(uv * 0.75 + vec2(0.0, 5.3));

    /*
     * EL SCROLL MUEVE EL BALANCE DE TINTAS, no el desregistro. El
     * desregistro apenas se veia y ademas era un truco; el balance
     * reengancha el fondo con el arco de color que el tema ya tiene:
     * magenta en la apertura, ambar en el cierre.
     */
    float balM = mix(1.0, 0.30, smoothstep(0.08, 0.92, uScroll));
    float balA = mix(0.26, 1.0, smoothstep(0.08, 0.92, uScroll));

    // Desregistro: pequeno, constante y en pixeles de dispositivo. Es
    // una maquina bien calibrada que aun asi no es perfecta.
    vec2 offM = vec2(1.6, -1.1);
    vec2 offA = vec2(-1.3, 1.5);

    float pitch = 7.0;
    /*
     * CADA PLANCHA LLEVA SU PROPIA IMAGEN, y esto es lo que separa una
     * duotonia de dos capas del mismo dibujo teñidas distinto. Con el
     * mismo campo en las dos tintas, magenta y ambar se suman en las
     * mismas zonas y dan MARRON — el encuadre entero se embarra. Con dos
     * focos separados, cada tinta manda en su lado, se cruzan solo en la
     * franja de en medio y ahi es donde aparece el unico sitio con las
     * dos: que es exactamente como se lee un cartel a dos tintas.
     */
    float coverM = clamp((fieldM * 1.2 + tooth * 0.3) * balM * squeegeeM, 0.0, 1.0);
    float coverA = clamp((fieldA * 1.2 + tooth * 0.3) * balA * squeegeeA, 0.0, 1.0);

    float dotM = screenDot(frag + offM, 0.262, pitch, coverM);
    float dotA = screenDot(frag + offA, 1.309, pitch * 0.94, coverA);

    vec3 col = INK;
    col = mix(col, MAGENTA, dotM * 0.36);
    col = mix(col, AMBER, dotA * 0.27);

    // Donde las dos tintas se solapan queda casi negro: sobreimpresion.
    col *= 1.0 - dotM * dotA * 0.38;

    // Marcas de registro, en magenta, a un margen fijo de cada esquina.
    float m = 26.0;
    float sz = 9.0;
    float reg = max(
      max(regMark(frag, vec2(m, m), sz), regMark(frag, vec2(uResolution.x - m, m), sz)),
      max(
        regMark(frag, vec2(m, uResolution.y - m), sz),
        regMark(frag, vec2(uResolution.x - m, uResolution.y - m), sz)
      )
    );
    col = mix(col, MAGENTA, reg * 0.55);

    col *= smoothstep(2.4, 0.4, length(p));
    col += (hash(vUv * uResolution * 0.5) - 0.5) * 0.028;

    gl_FragColor = vec4(ceilingClamp(col), 1.0);
  }
`;

export function mountViceInk(container: HTMLElement): BackgroundHandle {
  /*
   * El scroll se lee del propio `window`, no de Lenis ni de ScrollTrigger: el
   * fondo no debe depender de que la coreografia haya cargado (es un import
   * dinamico que puede tardar o fallar) ni de que el usuario no tenga
   * `prefers-reduced-motion`, caso en el que Lenis nunca llega a montarse.
   */
  const readProgress = (): number => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollable <= 0) return 0;
    return Math.min(Math.max(window.scrollY / scrollable, 0), 1);
  };

  return mountShaderBackground(container, FRAGMENT_SHADER, {
    uScroll: readProgress,
  });
}
