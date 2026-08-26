/*
 * PROTOTIPO APROBADO — el fondo de Caelestia, fase B1 (Titulo).
 * Spec: docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md
 *
 * Este fichero es el artefacto que Aoshi aprobo el 2026-08-26, sacado del
 * companion de brainstorming (que NO esta versionado) para que sobreviva.
 * Es GLSL ES 1.0 tal cual lo pide `shaderBackground.ts`.
 *
 * Lo que hay que cambiar al portarlo a `src/backgrounds/caelestiaFiguras.ts`:
 *   - `uComp` desaparece: la composicion aprobada es la A3 y se deja fija.
 *     Las otras cinco ramas se borran.
 *   - `uDeriva` desaparece: era el mando del companion. Se deja en 1.0.
 *   - `uVel` desaparece: era el mando del companion. Se deja en 1.0.
 *   - `uMezcla`, `uFigA`, `uFigB`, `uElong` y los doce `uL/uC/uH` los tiene que
 *     alimentar el modulo leyendo la hora, igual que `caelestiaBlobs.ts` leia
 *     `--cae-hue` (modelo pull, cache de 750 ms).
 *   - `vUv` y los uniforms `uTime` / `uResolution` los da `shaderBackground.ts`.
 */

#extension GL_OES_standard_derivatives : enable
  precision highp float;
  uniform float uTime; uniform vec2 uResolution; uniform float uVel;
  uniform float uL0, uC0, uH0, uL1, uC1, uH1, uL2, uC2, uH2, uL3, uC3, uH3;
  uniform vec3 uFigA, uFigB;      // (n, a, s)
  uniform vec2 uElong;            // (elongA, elongB)
  uniform float uMezcla, uComp, uDeriva;
  varying vec2 vUv;

  vec3 fromHue(float hue, float l, float c){
    float h = radians(hue); float a = cos(h)*c; float b = sin(h)*c;
    float l_ = l + 0.3963377774*a + 0.2158037573*b;
    float m_ = l - 0.1055613458*a - 0.0638541728*b;
    float s_ = l - 0.0894841775*a - 1.2914855480*b;
    vec3 lms = vec3(l_*l_*l_, m_*m_*m_, s_*s_*s_);
    return clamp(mat3(4.0767416621,-1.2684380046,-0.0041960863,
                     -3.3077115913, 2.6097574011,-0.7034186147,
                      0.2309699292,-0.3413193965, 1.7076147010) * lms, 0.0, 1.0);
  }
  vec3 toSrgb(vec3 c){
    vec3 lo = c*12.92; vec3 hi = 1.055*pow(c, vec3(1.0/2.4)) - 0.055;
    return mix(lo, hi, step(0.0031308, c));
  }
  vec3 tono(int i){
    if (i == 0) return fromHue(uH0, uL0, uC0);
    if (i == 1) return fromHue(uH1, uL1, uC1);
    if (i == 2) return fromHue(uH2, uL2, uC2);
    return fromHue(uH3, uL3, uC3);
  }
  float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

  /* Radio de una figura de Material en polares. El numero de puntas SIEMPRE es
     entero: interpolar n daria un contorno que no cierra y se veria una costura
     en el angulo pi. Lo que se mezcla mas abajo son los dos radios completos. */
  float radio(vec3 fig, float th, float lat){
    float n = fig.x, a = fig.y * lat, s = fig.z * lat;
    return 1.0 + a * cos(n * th) + s * cos(2.0 * n * th);
  }

  /* Distancia con signo a la figura morfada, centrada en c y de tamano R. */
  float sdFigura(vec2 p, vec2 c, float R, float rot, float lat){
    vec2 q = p - c;
    q = mat2(cos(rot), -sin(rot), sin(rot), cos(rot)) * q;
    float el = mix(uElong.x, uElong.y, uMezcla);
    q.x /= el;
    float th = atan(q.y, q.x);
    float r = mix(radio(uFigA, th, lat), radio(uFigB, th, lat), uMezcla);
    return (length(q) - R * r) / max(R, 0.001);
  }

  /* Relleno con degradado interno entre dos pasteles, en la direccion de la luz
     nominal del sistema (arriba-izquierda). Va en LINEAL, antes de la gamma. */
  vec3 relleno(vec2 p, vec2 c, float R, int t1, int t2){
    float g = clamp(0.5 + dot(p - c, normalize(vec2(-0.55, 0.84))) / (2.0 * R), 0.0, 1.0);
    g = g * g * (3.0 - 2.0 * g);
    return mix(tono(t1), tono(t2), g);
  }

  /* Poner una figura sobre lo que ya hay. Todas las composiciones usan esta
     misma funcion: el estilo no cambia, solo cambia donde y cuantas. */
  vec3 pon(vec3 col, vec2 p, vec2 casa, float R, float velRot, float fase, float t,
           int t1, int t2, vec2 amp, vec2 frq){
    /* La figura no esta quieta en su sitio: ORBITA alrededor de el. Las dos
       frecuencias son distintas y no son multiplos, asi que el recorrido es una
       curva de Lissajous abierta — nunca repite el mismo camino. Es lo que
       separa "se mueve" de "se desliza": una traslacion recta se lee como una
       pegatina arrastrada; una orbita se lee como algo que flota. */
    vec2 c = casa + amp * uDeriva * vec2(sin(t * frq.x + fase), cos(t * frq.y + fase * 1.7));
    float lat = 1.0 + 0.09 * sin(t * 0.85 + fase);   // late con periodo de ~26 s
    float d = sdFigura(p, c, R, t * velRot + fase, lat);
    float a = 1.0 - smoothstep(-fwidth(d) * 1.1, fwidth(d) * 1.1, d);
    return mix(col, relleno(p, c, R, t1, t2), a);
  }

  void main(){
    vec2 p = (vUv - 0.5) * vec2(uResolution.x/uResolution.y, 1.0);
    /* Dos relojes distintos y a proposito. El MORFADO entre figuras lo manda
       uMezcla, que viene de la hora del visitante: cambia una vez por tramo.
       El AMBIENTE — giro y latido — corre con este t, mucho mas rapido, para
       que se note en los treinta segundos que dura una visita. Con el factor
       de antes (0.045) la figura giraba 2 grados en medio minuto: matematica-
       mente se movia, humanamente estaba quieta. */
    float t = uTime * 0.28 * uVel;
    vec3 col = tono(0);
    int cmp = int(uComp + 0.5);

    if (cmp == 0) {
      // A1 · Colosal: una sola figura mas grande que la ventana. Solo se ve un
      // trozo de su canto, asi que lo que hay detras del texto es color plano.
      col = pon(col, p, vec2(-0.06, 0.02), 1.16, 0.022, 0.0, t, 1, 2, vec2(0.13, 0.09), vec2(0.31, 0.23));
    } else if (cmp == 1) {
      // A2 · Dos que se solapan: la de delante recorta a la de detras. Es la
      // manera de Material de decir que hay dos superficies, sin sombras.
      col = pon(col, p, vec2(-0.44,-0.12), 0.80, 0.024, 0.0, t, 1, 2, vec2(0.17, 0.11), vec2(0.37, 0.29));
      col = pon(col, p, vec2( 0.34, 0.16), 0.60, -0.031, 2.1, t, 3, 2, vec2(0.19, 0.14), vec2(0.29, 0.43));
    } else if (cmp == 2) {
      // A3 · Tres en diagonal: tamanos escalonados, la mirada baja de izquierda
      // a derecha. Es la unica que tiene direccion.
      col = pon(col, p, vec2(-0.68, 0.26), 0.44, 0.026, 0.0, t, 1, 2, vec2(0.18, 0.12), vec2(0.41, 0.33));
      col = pon(col, p, vec2(-0.02,-0.02), 0.31, -0.034, 1.3, t, 2, 3, vec2(0.22, 0.15), vec2(0.29, 0.47));
      col = pon(col, p, vec2( 0.58,-0.30), 0.21, 0.042, 2.6, t, 3, 1, vec2(0.16, 0.17), vec2(0.53, 0.37));
      /* Cuatro satelites en los huecos que deja la diagonal. Van fuera de las
         dos zonas ocupadas — el widget arriba a la derecha y el bloque de texto
         abajo a la izquierda — y dos de ellos los corta el canto de la ventana,
         que es lo que impide que se lean como pegatinas sueltas. */
      col = pon(col, p, vec2( 0.12, 0.42), 0.085, -0.058, 0.6, t, 3, 2, vec2(0.26, 0.07), vec2(0.61, 0.51));
      col = pon(col, p, vec2( 0.93, 0.05), 0.075, 0.066, 1.9, t, 2, 1, vec2(0.10, 0.24), vec2(0.44, 0.67));
      col = pon(col, p, vec2(-0.89, 0.47), 0.055, -0.074, 3.1, t, 1, 3, vec2(0.13, 0.09), vec2(0.71, 0.39));
      col = pon(col, p, vec2( 0.40,-0.46), 0.050, 0.081, 4.2, t, 3, 1, vec2(0.22, 0.08), vec2(0.34, 0.59));
    } else if (cmp == 3) {
      // A4 · Racimo: cinco apinadas en una esquina, el resto de la ventana
      // vacio. Toda la densidad en un sitio y todo el aire en el otro.
      col = pon(col, p, vec2( 0.52, 0.10), 0.36, 0.021, 0.0, t, 1, 2, vec2(0.15, 0.12), vec2(0.33, 0.27));
      col = pon(col, p, vec2( 0.24, 0.30), 0.25, -0.029, 1.1, t, 2, 3, vec2(0.18, 0.10), vec2(0.47, 0.31));
      col = pon(col, p, vec2( 0.78,-0.16), 0.22, 0.037, 2.2, t, 3, 1, vec2(0.14, 0.16), vec2(0.29, 0.53));
      col = pon(col, p, vec2( 0.30,-0.14), 0.16, -0.044, 3.3, t, 2, 1, vec2(0.20, 0.14), vec2(0.59, 0.41));
      col = pon(col, p, vec2( 0.66, 0.36), 0.12, 0.052, 4.4, t, 3, 2, vec2(0.17, 0.11), vec2(0.43, 0.67));
    } else if (cmp == 4) {
      // A5 · Eco: la misma figura repetida hacia dentro sobre un mismo centro,
      // cada anillo un tono. Es el circulo que se expande de Material, quieto.
      col = pon(col, p, vec2(-0.24,-0.04), 1.02, 0.018, 0.0, t, 1, 2, vec2(0.09, 0.07), vec2(0.27, 0.21));
      col = pon(col, p, vec2(-0.24,-0.04), 0.72, -0.024, 0.9, t, 2, 3, vec2(0.12, 0.09), vec2(0.35, 0.29));
      col = pon(col, p, vec2(-0.24,-0.04), 0.46, 0.032, 1.8, t, 3, 1, vec2(0.15, 0.12), vec2(0.43, 0.37));
      col = pon(col, p, vec2(-0.24,-0.04), 0.24, -0.041, 2.7, t, 1, 2, vec2(0.19, 0.16), vec2(0.51, 0.45));
    } else {
      // A6 · Enmarcado: dos figuras cortadas por cantos opuestos, con el centro
      // libre. Es la que menos pelea con un titular grande.
      col = pon(col, p, vec2(-1.02, 0.30), 0.78, 0.020, 0.0, t, 1, 2, vec2(0.16, 0.13), vec2(0.31, 0.25));
      col = pon(col, p, vec2( 1.06,-0.30), 0.72, -0.027, 2.4, t, 3, 2, vec2(0.18, 0.15), vec2(0.39, 0.33));
    }

    // Tramado: los degradados internos son largos y sin esto hacen bandas.
    col += (hash(vUv * uResolution + uTime * 0.045) - 0.5) * 0.0035;
    gl_FragColor = vec4(toSrgb(clamp(col, 0.0, 1.0)), 1.0);
  }
