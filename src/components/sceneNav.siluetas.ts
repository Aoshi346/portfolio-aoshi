/**
 * Siluetas del indice de escenas: cada escena reducida a su estructura, en
 * coordenadas del plano real de 1440x900. El CSS las escala al fotograma.
 *
 * Son una COPIA a mano de la maqueta de cada escena, no se leen del DOM: el
 * indice se pinta con la cortinilla cerrada y las escenas ni siquiera estan
 * montadas del todo. El precio es que pueden envejecer — si una escena cambia
 * de dispositivo y su silueta no, la hoja miente en silencio. Vigilado por
 * `scripts/measure-cortinilla.py`, que comprueba que hay cinco y ninguna vacia.
 */

/** Una pieza de la silueta. `x`/`y`/`w`/`h` en pixeles del plano de 1440x900. */
export interface Pieza {
  /** `rl` filete, `bar` bloque de texto abstraido, `box` caja, `dot` circulo,
   *  `disp` texto real en la cara de display, `beam` el haz. */
  readonly clase: "rl" | "bar" | "box" | "dot" | "disp" | "beam";
  readonly x?: number;
  readonly y?: number;
  readonly w?: number;
  readonly h?: number;
  readonly texto?: string;
  readonly tam?: number;
  readonly tono?: string;
  readonly opac?: number;
}

export const SILUETAS: Readonly<Record<string, readonly Pieza[]>> = {
  hero: [
    { clase: "beam", opac: 1 },
    { clase: "rl", x: 190, y: 300, w: 1, h: 280 },
    { clase: "disp", x: 222, y: 340, tam: 96, tono: "var(--color-paper)", texto: "Aoshi Blanco Sanz" },
    { clase: "bar", x: 570, y: 470, w: 300, h: 6, opac: 0.42 },
    { clase: "rl", x: 267, y: 530, w: 1120, h: 1, tono: "var(--l1)", opac: 0.5 },
    { clase: "bar", x: 267, y: 552, w: 180, h: 5, opac: 0.3 },
    { clase: "bar", x: 1180, y: 552, w: 207, h: 5, opac: 0.3 },
  ],
  "quien-es": [
    { clase: "beam", opac: 0.8 },
    { clase: "bar", x: 101, y: 205, w: 150, h: 5, tono: "var(--l1)" },
    { clase: "box", x: 101, y: 239, w: 1238, h: 437 },
    { clase: "rl", x: 101, y: 383, w: 1238, h: 1 },
    { clase: "rl", x: 101, y: 529, w: 1238, h: 1 },
    { clase: "rl", x: 720, y: 239, w: 1, h: 437 },
    { clase: "box", x: 733, y: 252, w: 118, h: 118 },
    { clase: "bar", x: 118, y: 252, w: 52, h: 5, opac: 0.32 },
    { clase: "disp", x: 118, y: 270, tam: 39, tono: "var(--color-paper)", texto: "Aoshi Blanco Sanz" },
    { clase: "bar", x: 118, y: 319, w: 480, h: 6, opac: 0.4 },
    { clase: "bar", x: 943, y: 252, w: 52, h: 5, opac: 0.32 },
    { clase: "disp", x: 943, y: 270, tam: 32, tono: "var(--catch)", texto: "Disponible para proyectos" },
    { clase: "bar", x: 118, y: 419, w: 360, h: 9, opac: 0.55 },
    { clase: "bar", x: 737, y: 419, w: 180, h: 9, opac: 0.55 },
    { clase: "bar", x: 118, y: 564, w: 300, h: 9, opac: 0.55 },
    { clase: "bar", x: 737, y: 564, w: 300, h: 9, opac: 0.55 },
  ],
  obra: [
    { clase: "beam", opac: 0.75 },
    { clase: "rl", x: 0, y: 396, w: 1440, h: 1 },
    { clase: "rl", x: 0, y: 506, w: 1440, h: 1 },
    { clase: "rl", x: 0, y: 615, w: 1440, h: 1 },
    { clase: "rl", x: 0, y: 725, w: 1440, h: 1 },
    { clase: "rl", x: 0, y: 834, w: 1440, h: 1 },
    { clase: "disp", x: 114, y: 402, tam: 90, tono: "var(--color-paper)", texto: "EchoPlan" },
    { clase: "box", x: 1279, y: 402, w: 161, h: 101 },
    { clase: "bar", x: 114, y: 522, w: 300, h: 90, opac: 0.5 },
    { clase: "box", x: 1279, y: 512, w: 161, h: 101 },
    { clase: "bar", x: 114, y: 631, w: 450, h: 90, opac: 0.5 },
    { clase: "box", x: 1279, y: 621, w: 161, h: 101 },
    { clase: "bar", x: 114, y: 741, w: 385, h: 90, opac: 0.5 },
    { clase: "box", x: 1279, y: 731, w: 161, h: 101 },
    { clase: "bar", x: 114, y: 850, w: 540, h: 90, opac: 0.5 },
    { clase: "box", x: 1279, y: 840, w: 161, h: 101 },
  ],
  creditos: [
    { clase: "beam", opac: 0.85 },
    { clase: "bar", x: 101, y: 152, w: 220, h: 5, tono: "var(--l1)" },
    { clase: "bar", x: 101, y: 210, w: 90, h: 5, opac: 0.35 },
    { clase: "bar", x: 133, y: 249, w: 73, h: 12, opac: 0.85 },
    { clase: "bar", x: 133, y: 291, w: 139, h: 12, opac: 0.7 },
    { clase: "bar", x: 133, y: 333, w: 161, h: 12, opac: 0.7 },
    { clase: "bar", x: 133, y: 375, w: 71, h: 12, opac: 0.6 },
    { clase: "box", x: 651, y: 210, w: 344, h: 242 },
    { clase: "bar", x: 684, y: 210, w: 150, h: 5, opac: 0.35 },
    { clase: "bar", x: 716, y: 249, w: 92, h: 12, opac: 0.85 },
    { clase: "bar", x: 716, y: 291, w: 94, h: 12, opac: 0.7 },
    { clase: "bar", x: 716, y: 333, w: 90, h: 12, opac: 0.7 },
    { clase: "box", x: 995, y: 210, w: 344, h: 242 },
    { clase: "bar", x: 1028, y: 210, w: 140, h: 5, opac: 0.35 },
    { clase: "bar", x: 1060, y: 249, w: 35, h: 12, opac: 0.85 },
    { clase: "bar", x: 1060, y: 291, w: 160, h: 12, opac: 0.7 },
    { clase: "bar", x: 1060, y: 333, w: 132, h: 12, opac: 0.7 },
    { clase: "rl", x: 101, y: 626, w: 1238, h: 2, tono: "var(--l1)", opac: 1 },
    { clase: "bar", x: 101, y: 650, w: 150, h: 5, opac: 0.35 },
    { clase: "disp", x: 133, y: 674, tam: 38, tono: "var(--color-paper)", texto: "JavaScript" },
    { clase: "bar", x: 354, y: 682, w: 95, h: 34, opac: 0.6 },
    { clase: "bar", x: 502, y: 682, w: 69, h: 34, opac: 0.6 },
    { clase: "bar", x: 624, y: 682, w: 24, h: 34, opac: 0.6 },
    { clase: "bar", x: 700, y: 682, w: 57, h: 34, opac: 0.6 },
  ],
  contacto: [
    { clase: "beam", opac: 1 },
    { clase: "bar", x: 125, y: 199, w: 90, h: 5, tono: "var(--l1)" },
    { clase: "disp", x: 125, y: 228, tam: 96, tono: "var(--catch)", texto: "Hablemos" },
    { clase: "bar", x: 125, y: 352, w: 240, h: 8, opac: 0.42 },
    { clase: "rl", x: 0, y: 733, w: 1440, h: 1, tono: "var(--l1)", opac: 0.5 },
    { clase: "bar", x: 930, y: 737, w: 250, h: 9, opac: 0.5, tono: "var(--catch)" },
    { clase: "bar", x: 101, y: 787, w: 65, h: 5, opac: 0.32 },
    { clase: "bar", x: 101, y: 821, w: 315, h: 16, opac: 0.7 },
    { clase: "rl", x: 101, y: 873, w: 315, h: 1, tono: "var(--l1)", opac: 0.42 },
    { clase: "bar", x: 529, y: 787, w: 75, h: 5, opac: 0.32 },
    { clase: "bar", x: 529, y: 821, w: 236, h: 16, opac: 0.7 },
    { clase: "rl", x: 529, y: 873, w: 236, h: 1, tono: "var(--l1)", opac: 0.42 },
    { clase: "bar", x: 880, y: 787, w: 84, h: 5, opac: 0.32 },
    { clase: "bar", x: 880, y: 821, w: 222, h: 16, opac: 0.7 },
    { clase: "rl", x: 880, y: 873, w: 222, h: 1, tono: "var(--l1)", opac: 0.42 },
    { clase: "bar", x: 1216, y: 787, w: 60, h: 5, opac: 0.32 },
    { clase: "bar", x: 1216, y: 821, w: 123, h: 16, opac: 0.7 },
    { clase: "rl", x: 1216, y: 873, w: 123, h: 1, tono: "var(--l1)", opac: 0.42 },
  ],
};

/*
 * Grosor minimo, en pixeles del plano, para que una pieza siga siendo un trazo
 * y no un manchon en movil.
 *
 * A 390 el encuadre mide 170,5 y el plano se escala a 0,1184, asi que hace
 * falta 1 / 0,1184 = 8,45 px de plano para renderizar 1 px. Todo lo que quede
 * por debajo lo pinta el navegador como una mancha gris translucida. Medido en
 * el estado anterior: hero 5 de 6 piezas por debajo de 1 px, quien-es 13 de 19,
 * obra 31 de 41 (con los nombres de proyecto a 3,6 px), creditos 7 de 31.
 * Es el hallazgo P1 de `lidia-naive-tester`: las siluetas de movil obligaban a
 * leer el rotulo en vez de ayudar a decidir, 2,5-3 s hasta la primera pulsacion
 * correcta sobre un umbral de 2 s.
 *
 * No se corrige subiendo la escala — el encuadre lo fija la rejilla — sino
 * dejando de dibujar lo que ya no se ve. Lo que sobrevive queda mas limpio.
 */
const GROSOR_MINIMO = 9;

/** Cuerpo minimo de un texto de la silueta para que en movil se lea como
 *  palabra y no como raya: a 0,1184 un `tam` de 40 renderiza a 4,7 px. */
const CUERPO_MINIMO = 40;

/*
 * Tonos de acento: emiten. Por debajo de un pixel el navegador funde el color
 * en el pixel, asi que un trazo de `--l1` a plena opacidad sigue leyendose como
 * marca aunque mida 0,7 px, mientras que el mismo trazo en `--haze` al 30% se
 * disuelve en el fondo. Por eso el criterio no puede ser solo el grosor: si lo
 * fuera, el carril de obra se quedaba en movil con sus cinco ordinales de marca
 * de agua y nada mas — comprobado en captura, el fotograma quedaba vacio.
 */
const ACENTOS = ["--l1", "--l2", "--l3", "--catch"];
const OPACIDAD_QUE_AGUANTA = 0.6;

function emite(p: Pieza): boolean {
  return (
    p.tono !== undefined &&
    ACENTOS.some((t) => p.tono?.includes(t)) &&
    (p.opac ?? 1) >= OPACIDAD_QUE_AGUANTA
  );
}

function esFino(p: Pieza): boolean {
  if (p.clase === "beam") return false;
  if (emite(p)) return false;
  // Una `box` solo aporta su borde de 1px: en movil nunca sobrevive.
  if (p.clase === "box") return true;
  if (p.texto !== undefined) return (p.tam ?? 0) < CUERPO_MINIMO;
  const lados = [p.w, p.h].filter((v): v is number => v !== undefined);
  return lados.length > 0 && Math.min(...lados) < GROSOR_MINIMO;
}

export function construirSilueta(id: string): HTMLElement {
  const shot = document.createElement("span");
  shot.className = "scene-shot";
  /*
   * Las piezas van dentro de un PLANO de 1440x900 que se escala entero, no
   * sueltas dentro del encuadre. `transform: scale()` escala la caja de un
   * elemento pero no su `left`/`top`: con las piezas como hijas directas, una
   * en `top: 340px` seguia a 340px de un encuadre de 166px de alto y la
   * recortaba el `overflow: hidden`. Medido: de las seis piezas de la silueta
   * del hero, CERO caian dentro del encuadre — el fotograma era el haz y nada
   * mas.
   *
   * El haz no entra en el plano: se dibuja sobre el encuadre, a su tamano.
   */
  const plano = document.createElement("span");
  plano.className = "scene-shot-plano";
  shot.append(plano);
  for (const p of SILUETAS[id] ?? []) {
    const n = document.createElement("span");
    n.className = esFino(p) ? `scene-shot-${p.clase} scene-shot-fino` : `scene-shot-${p.clase}`;
    if (p.x !== undefined) n.style.left = `${p.x}px`;
    if (p.y !== undefined) n.style.top = `${p.y}px`;
    if (p.w !== undefined) n.style.width = `${p.w}px`;
    if (p.h !== undefined) n.style.height = `${p.h}px`;
    if (p.tam !== undefined) n.style.fontSize = `${p.tam}px`;
    if (p.tono !== undefined) n.style.background = p.tono;
    if (p.opac !== undefined) n.style.opacity = String(p.opac);
    // `textContent`, nunca `innerHTML`: es contenido propio y estatico, pero la
    // regla del proyecto es construir DOM a mano y no abrir la puerta.
    if (p.texto !== undefined) {
      n.textContent = p.texto;
      n.style.background = "";
      if (p.tono !== undefined) n.style.color = p.tono;
    }
    (p.clase === "beam" ? shot : plano).append(n);
  }
  return shot;
}
