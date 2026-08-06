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
    { clase: "disp", x: 222, y: 340, tam: 96, tono: "#fff4ee", texto: "Aoshi Blanco Sanz" },
    { clase: "bar", x: 570, y: 470, w: 300, h: 6, opac: 0.42 },
    { clase: "rl", x: 267, y: 530, w: 1120, h: 1, tono: "#ff5a34", opac: 0.5 },
    { clase: "bar", x: 267, y: 552, w: 180, h: 5, opac: 0.3 },
    { clase: "bar", x: 1180, y: 552, w: 207, h: 5, opac: 0.3 },
  ],
  "quien-es": [
    { clase: "beam", opac: 0.8 },
    { clase: "bar", x: 100, y: 132, w: 100, h: 5, tono: "#ff5a34" },
    { clase: "box", x: 100, y: 167, w: 1238, h: 280 },
    { clase: "dot", x: 120, y: 187, w: 48, h: 48, tono: "#5a3a34" },
    { clase: "disp", x: 120, y: 246, tam: 62, tono: "#ffd9cc", texto: "Aoshi Blanco Sanz" },
    { clase: "dot", x: 120, y: 321, w: 8, h: 8, tono: "#ff5a34" },
    { clase: "bar", x: 140, y: 321, w: 210, h: 6, tono: "#ff5a34", opac: 0.7 },
    { clase: "bar", x: 120, y: 352, w: 52, h: 5, opac: 0.32 },
    { clase: "bar", x: 196, y: 352, w: 214, h: 5 },
    { clase: "bar", x: 120, y: 378, w: 52, h: 5, opac: 0.32 },
    { clase: "bar", x: 196, y: 378, w: 168, h: 5 },
    { clase: "bar", x: 120, y: 404, w: 52, h: 5, opac: 0.32 },
    { clase: "bar", x: 196, y: 404, w: 132, h: 5 },
    { clase: "bar", x: 100, y: 500, w: 640, h: 9, opac: 0.42 },
    { clase: "rl", x: 100, y: 586, w: 1238, h: 1 },
    { clase: "bar", x: 125, y: 660, w: 270, h: 11, opac: 0.6 },
    { clase: "bar", x: 670, y: 664, w: 230, h: 7, opac: 0.45 },
    { clase: "rl", x: 125, y: 742, w: 1190, h: 1 },
    { clase: "bar", x: 125, y: 790, w: 310, h: 11, opac: 0.6 },
    { clase: "bar", x: 670, y: 794, w: 270, h: 7, opac: 0.45 },
  ],
  obra: [
    { clase: "beam", opac: 0.75 },
    { clase: "rl", x: 287, y: 0, w: 1, h: 900 },
    { clase: "rl", x: 574, y: 0, w: 1, h: 900 },
    { clase: "rl", x: 861, y: 0, w: 1, h: 900 },
    { clase: "rl", x: 1148, y: 0, w: 1, h: 900 },
    { clase: "disp", x: 196, y: 140, tam: 96, tono: "#2c1311", texto: "01" },
    { clase: "disp", x: 483, y: 160, tam: 96, tono: "#2c1311", texto: "02" },
    { clase: "disp", x: 770, y: 150, tam: 96, tono: "#371815", texto: "03" },
    { clase: "disp", x: 1057, y: 130, tam: 96, tono: "#2c1311", texto: "04" },
    { clase: "disp", x: 1344, y: 150, tam: 96, tono: "#2c1311", texto: "05" },
    { clase: "bar", x: 22, y: 70, w: 150, h: 6, tono: "#ff5a34", opac: 0.8 },
    { clase: "disp", x: 22, y: 92, tam: 30, texto: "EchoPlan" },
    { clase: "bar", x: 22, y: 146, w: 200, h: 8, opac: 0.4 },
    { clase: "bar", x: 22, y: 170, w: 150, h: 8, opac: 0.4 },
    { clase: "rl", x: 22, y: 225, w: 240, h: 1 },
    { clase: "bar", x: 22, y: 250, w: 110, h: 5, opac: 0.3 },
    { clase: "bar", x: 22, y: 275, w: 180, h: 5, opac: 0.3 },
    { clase: "bar", x: 310, y: 196, w: 140, h: 6, tono: "#ff5a34", opac: 0.8 },
    { clase: "disp", x: 310, y: 218, tam: 30, texto: "TesisFar" },
    { clase: "bar", x: 310, y: 272, w: 210, h: 8, opac: 0.4 },
    { clase: "bar", x: 310, y: 296, w: 160, h: 8, opac: 0.4 },
    { clase: "rl", x: 310, y: 350, w: 240, h: 1 },
    { clase: "bar", x: 310, y: 375, w: 130, h: 5, opac: 0.3 },
    { clase: "bar", x: 597, y: 36, w: 150, h: 6, tono: "#ff5a34", opac: 0.8 },
    { clase: "disp", x: 597, y: 58, tam: 30, texto: "HyprFinance" },
    { clase: "bar", x: 597, y: 112, w: 200, h: 8, opac: 0.4 },
    { clase: "bar", x: 597, y: 136, w: 140, h: 8, opac: 0.4 },
    { clase: "rl", x: 597, y: 190, w: 240, h: 1 },
    { clase: "bar", x: 597, y: 215, w: 150, h: 5, opac: 0.3 },
    { clase: "bar", x: 597, y: 240, w: 190, h: 5, opac: 0.3 },
    { clase: "bar", x: 884, y: 112, w: 130, h: 6, tono: "#ff5a34", opac: 0.8 },
    { clase: "disp", x: 884, y: 134, tam: 30, texto: "WatchDog" },
    { clase: "bar", x: 884, y: 188, w: 215, h: 8, opac: 0.4 },
    { clase: "bar", x: 884, y: 212, w: 180, h: 8, opac: 0.4 },
    { clase: "rl", x: 884, y: 266, w: 240, h: 1 },
    { clase: "bar", x: 884, y: 291, w: 160, h: 5, opac: 0.3 },
    { clase: "bar", x: 1171, y: 150, w: 190, h: 6, tono: "#ff5a34", opac: 0.8 },
    { clase: "disp", x: 1171, y: 186, tam: 30, texto: "Editor de texto" },
    { clase: "bar", x: 1171, y: 240, w: 200, h: 8, opac: 0.4 },
    { clase: "bar", x: 1171, y: 264, w: 150, h: 8, opac: 0.4 },
    { clase: "rl", x: 1171, y: 318, w: 240, h: 1 },
    { clase: "bar", x: 1171, y: 343, w: 170, h: 5, opac: 0.3 },
  ],
  creditos: [
    { clase: "beam", opac: 0.85 },
    { clase: "bar", x: 100, y: 132, w: 200, h: 5, tono: "#ff5a34" },
    { clase: "box", x: 100, y: 165, w: 1000, h: 332 },
    { clase: "bar", x: 119, y: 190, w: 78, h: 5, opac: 0.32 },
    { clase: "bar", x: 119, y: 216, w: 74, h: 12, opac: 0.85 },
    { clase: "bar", x: 213, y: 216, w: 82, h: 12 },
    { clase: "bar", x: 315, y: 216, w: 118, h: 12 },
    { clase: "bar", x: 453, y: 216, w: 136, h: 12 },
    { clase: "bar", x: 609, y: 216, w: 54, h: 12 },
    { clase: "bar", x: 683, y: 216, w: 70, h: 12 },
    { clase: "bar", x: 119, y: 270, w: 140, h: 5, opac: 0.32 },
    { clase: "bar", x: 119, y: 296, w: 86, h: 12 },
    { clase: "bar", x: 225, y: 296, w: 84, h: 12 },
    { clase: "bar", x: 329, y: 296, w: 88, h: 12 },
    { clase: "bar", x: 437, y: 296, w: 86, h: 12 },
    { clase: "bar", x: 119, y: 350, w: 126, h: 5, opac: 0.32 },
    { clase: "bar", x: 119, y: 376, w: 114, h: 12 },
    { clase: "bar", x: 253, y: 376, w: 74, h: 12 },
    { clase: "bar", x: 347, y: 376, w: 60, h: 12 },
    { clase: "bar", x: 427, y: 376, w: 30, h: 12 },
    { clase: "bar", x: 119, y: 430, w: 106, h: 5, opac: 0.32 },
    { clase: "bar", x: 119, y: 456, w: 48, h: 12 },
    { clase: "bar", x: 187, y: 456, w: 82, h: 12 },
    { clase: "bar", x: 289, y: 456, w: 54, h: 12 },
    { clase: "bar", x: 363, y: 456, w: 134, h: 12 },
    { clase: "box", x: 100, y: 549, w: 1000, h: 286 },
    { clase: "dot", x: 120, y: 572, w: 44, h: 44, tono: "#ff5a34" },
    { clase: "disp", x: 120, y: 624, tam: 64, tono: "#ffd9cc", texto: "React" },
    { clase: "bar", x: 120, y: 712, w: 340, h: 7, opac: 0.4 },
    { clase: "rl", x: 120, y: 752, w: 960, h: 1 },
    { clase: "box", x: 120, y: 790, w: 96, h: 28 },
    { clase: "box", x: 236, y: 790, w: 118, h: 28 },
  ],
  contacto: [
    { clase: "beam", opac: 1 },
    { clase: "bar", x: 124, y: 196, w: 90, h: 5, tono: "#ff5a34" },
    { clase: "disp", x: 124, y: 228, tam: 96, tono: "#ffd9cc", texto: "Hablemos" },
    { clase: "bar", x: 124, y: 352, w: 240, h: 8, opac: 0.42 },
    { clase: "bar", x: 124, y: 422, w: 90, h: 5, opac: 0.3 },
    { clase: "bar", x: 238, y: 422, w: 230, h: 5, opac: 0.45 },
    { clase: "rl", x: 100, y: 468, w: 1240, h: 1 },
    { clase: "bar", x: 200, y: 512, w: 96, h: 5, opac: 0.3 },
    { clase: "rl", x: 876, y: 514, w: 30, h: 2, tono: "#ff5a34" },
    { clase: "bar", x: 930, y: 504, w: 410, h: 16, opac: 0.85 },
    { clase: "rl", x: 100, y: 560, w: 1240, h: 1 },
    { clase: "bar", x: 200, y: 604, w: 110, h: 5, opac: 0.3 },
    { clase: "rl", x: 956, y: 606, w: 30, h: 2, tono: "#ff5a34" },
    { clase: "bar", x: 1010, y: 596, w: 330, h: 16, opac: 0.7 },
    { clase: "rl", x: 100, y: 652, w: 1240, h: 1 },
    { clase: "bar", x: 200, y: 696, w: 104, h: 5, opac: 0.3 },
    { clase: "rl", x: 966, y: 698, w: 30, h: 2, tono: "#ff5a34" },
    { clase: "bar", x: 1020, y: 688, w: 320, h: 16, opac: 0.7 },
    { clase: "rl", x: 100, y: 745, w: 1240, h: 1 },
    { clase: "bar", x: 200, y: 788, w: 88, h: 5, opac: 0.3 },
    { clase: "rl", x: 1066, y: 790, w: 30, h: 2, tono: "#ff5a34" },
    { clase: "bar", x: 1120, y: 780, w: 220, h: 16, opac: 0.7 },
    { clase: "rl", x: 100, y: 838, w: 1240, h: 1 },
  ],
};

export function construirSilueta(id: string): HTMLElement {
  const shot = document.createElement("span");
  shot.className = "scene-shot";
  for (const p of SILUETAS[id] ?? []) {
    const n = document.createElement("span");
    n.className = `scene-shot-${p.clase}`;
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
    shot.append(n);
  }
  return shot;
}
