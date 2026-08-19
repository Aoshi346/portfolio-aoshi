// Prototipo APROBADO del fondo de Hyprland — "el haz al mando".
//
// Copia literal del shader validado en el companion de brainstorming el
// 2026-08-19, sacada al repo a proposito: el companion vive en `.superpowers/`,
// que esta en .gitignore, asi que sin esto los numeros exactos del diseno
// aprobado no viajarian con la rama.
//
// NO es el fichero de produccion. El de produccion es
// `src/backgrounds/hyprEmber.ts`, y al portarlo hay que:
//
//   1. Quitar los seis uniforms `fAsim`/`fSangre`/`fEje`/`fCorte`/`fDerrame`/
//      `fMateria`: existen solo para poder apagar cada correccion en la maqueta.
//      En produccion las seis van fijas a 1 y los `mix(viejo, nuevo, f*)` se
//      colapsan al lado nuevo.
//   2. Quitar `uTecho` y `uQuieto`: el techo es la constante 46 y el
//      movimiento reducido ya lo resuelve `shaderBackground.ts` congelando
//      `uTime` en STATIC_FRAME_TIME.
//   3. Sustituir el literal 0.735/0.765 de la entrada del segundo haz por el
//      limite REAL de la seccion de creditos. Ver el aviso del spec.
//   4. Usar NOISE_CHUNK de `shaderBackground.ts` en vez de redeclarar
//      hash/noise/fbm.
//
// Spec: docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md

// ---------- cabecera de la maqueta ----------
precision highp float;
    uniform float uTime, uScroll, uTecho, uQuieto, uPixelRatio;
    uniform float fAsim, fSangre, fEje, fCorte, fDerrame, fMateria;
    uniform vec2 uResolution;
    varying vec2 vUv;
    float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453123); }
    float noise(vec2 p){
      vec2 i = floor(p), f = fract(p); vec2 u = f*f*(3.0-2.0*f);
      return mix(mix(hash(i), hash(i+vec2(1,0)), u.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), u.x), u.y);
    }
    float fbm(vec2 p){ float v=0.0,a=0.5; for(int i=0;i<4;i++){ v+=a*noise(p); p*=2.0; a*=0.5; } return v; }
    vec3 techo(vec3 c){
      float lm = uTecho / 255.0;
      float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
      return l > lm ? c * (lm / max(l, 1e-4)) : c;
    }
    vec3 INK = vec3(0.043,0.016,0.016);
    vec3 EMBER = vec3(1.0,0.353,0.204);
    vec3 CRIM = vec3(0.878,0.114,0.235);
    vec3 AMBER = vec3(1.0,0.627,0.235);

// ---------- el shader aprobado ----------
/* Grano de carbon atado a pixeles de DISPOSITIVO, no a uv: con la rejilla
       atada a uv el paso cambia con la resolucion y bate contra la rejilla de
       la pantalla, y eso hormiguea al scrollear. Misma razon por la que Vice
       ata su lineatura al fragmento. */
    float carbon(vec2 frag, float ang){
      /* Se divide por uPixelRatio para trabajar en pixeles CSS. Con el paso
         fijo en pixeles de BUFFER el grano cambia de tamano fisico entre
         pantallas: shaderBackground.ts acota el ratio a 1 en <=820 px y a 1.5
         en escritorio, asi que la misma textura sale ~1.5 veces mas fina en
         retina que sin retina. Es el mismo hallazgo que viceInk.ts dejo
         escrito para su lineatura, y la misma decision. */
      vec2 css = frag / max(uPixelRatio, 1.0);
      float c = cos(ang), s = sin(ang);
      vec2 r = vec2(css.x*c - css.y*s, css.x*s + css.y*c);
      return mix(fbm(r / 34.0), hash(floor(r / 1.4)), 0.30);
    }

    void main(){
      vec2 uv = vUv;
      float aspect = uResolution.x / max(uResolution.y, 1.0);
      vec2 p = (uv * 2.0 - 1.0) * vec2(aspect, 1.0);
      float px = 2.0 / uResolution.y;
      float t = mix(uTime, 8.0, uQuieto);   /* movimiento reducido: fotograma fijo */

      /* MOVIL: no basta con enderezar el angulo.
         Medido a 390x844: con el semiancho fijo, el haz cubre TODA la pantalla
         y su canto duro —lo unico que define esta direccion— queda fuera del
         encuadre. Y con el origen fijo en -0.62 el sitio abre con el fondo
         casi vacio, porque en un encuadre estrecho el haz aun no ha entrado.
         Asi que el aspecto gobierna las cuatro cosas, no solo el angulo. */
      float vertical = smoothstep(1.0, 0.62, aspect);
      float ang = mix(1.36, 1.52, vertical) - uScroll * mix(0.30, 0.14, vertical);

      vec2 dir = vec2(cos(ang), sin(ang));
      vec2 nrm = vec2(-dir.y, dir.x);
      /* entra antes y recorre menos: en vertical hay mucho menos ancho que cruzar */
      vec2 o = vec2(mix(-0.62, -0.30, vertical) + uScroll * mix(0.95, 0.62, vertical),
                    mix(0.0, 0.30, vertical));
      vec2 rel = p - o;

      /* s: distancia CON SIGNO al eje. Sin abs(), que es lo que hacia que los
         dos cantos salieran iguales y el haz se leyera como una cinta. */
      float s = dot(rel, nrm);
      /* el semiancho se estrecha con el encuadre: un haz que no deja franja
         fuera de si mismo no es un haz, es un fondo de color */
      float hw = (0.26 + uScroll * 0.10) * mix(1.0, 0.42, vertical);

      /* 1 · CANTO ASIMETRICO. Un canto duro que define el haz, y el otro lado
         se pierde en el material. Es lo que separa una luz de una banda. */
      float duro  = 1.0 - smoothstep(-px*0.7, px*0.7, s - hw);
      float suave = smoothstep(-hw - 0.42, -hw + 0.02, s);
      float dentroAsim = duro * suave;
      float dentroSim  = 1.0 - smoothstep(0.0, px*1.5, abs(s) - hw);
      float dentro = mix(dentroSim, dentroAsim, fAsim);

      /* 3 · CAIDA POR SU EJE. Antes era un degradado vertical de viewport, asi
         que al girar el haz la caida no giraba con el y la luz se apagaba por
         una razon ajena a la luz. Ahora se mide A LO LARGO del haz. */
      float alo = dot(rel, dir);
      float caidaEje = smoothstep(1.45, -0.15, alo) * smoothstep(-1.6, -0.9, alo);
      float caidaVieja = smoothstep(1.30, -0.45, p.y);
      float caida = mix(caidaVieja, caidaEje, fEje);

      vec3 col = INK;

      /* 5 · DERRAME. El campo deja de tener posicion propia: es la luz que el
         haz suelta sobre el material, calculada desde el mismo eje. Un halo
         suelto no se echaba de menos y pagaba render. */
      float derrame = exp(-abs(s - hw) * 2.6) * caida;
      /* el derrame tambien se contiene en vertical: era lo que acababa de
         inundar la pantalla estrecha */
      col += mix(CRIM, EMBER, uScroll) * derrame * mix(0.30, 0.17, vertical) * fDerrame;

      /* 6 · MATERIA dentro del haz, multiplicativa. Aditiva subiria el suelo
         del cuadro entero. El CANTO se queda liso a proposito: un canto duro
         con textura deja de ser un canto duro. */
      float m = carbon(gl_FragCoord.xy, ang);
      float cuerpo = mix(1.0, 0.55 + m * 0.85, fMateria);

      col += mix(EMBER, AMBER, 0.5 + 0.5*p.y) * dentro * caida * 0.19 * cuerpo;
      col += AMBER * (1.0 - smoothstep(0.0, px*1.15, abs(s - hw))) * caida * 0.62;

      /* 4 · CORTE EN FRONTERA. El segundo haz entra en el limite Obra->
         Creditos (uScroll 0.75), no a mitad de una seccion, y entra con corte
         seco: algo que aparece de la nada dentro de una escena se lee como
         fallo de render, no como decision. */
      float ent = mix(smoothstep(0.45, 0.75, uScroll),
                      smoothstep(0.735, 0.765, uScroll), fCorte);
      vec2 o2 = vec2(0.55, 0.10);
      vec2 d2dir = vec2(cos(-0.95), sin(-0.95));
      float s2 = dot(p - o2, vec2(-d2dir.y, d2dir.x));
      float alo2 = dot(p - o2, d2dir);
      float caida2 = mix(caida, smoothstep(1.3, -0.9, alo2), fEje);
      col += AMBER * (1.0 - smoothstep(0.0, px*1.15, abs(abs(s2) - 0.055))) * caida2 * 0.46 * ent;

      /* 2 · SALE A SANGRE. El vinetado moria justo en las esquinas, que es por
         donde el haz sale del cuadro: reblandecia con una linea lo mismo que
         el canto endurece. Se sustituye por una caida muy leve y solo en el
         vertice contrario al haz. */
      float vieja = smoothstep(2.15, 0.35, length(p));
      float nueva = mix(1.0, 0.86, smoothstep(0.6, 1.9, length(p - vec2(0.9, -0.9))));
      col *= mix(vieja, nueva, fSangre);

      col += (hash(uv*uResolution + t) - 0.5) * 0.026;
      col = techo(col);
      gl_FragColor = vec4(col, 1.0);
    }
