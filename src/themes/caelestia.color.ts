/**
 * El motor de color de Caelestia: la hora del visitante decide el matiz y el
 * esquema. Puro salvo `mountCaelestiaColor`, que es lo unico que toca el DOM.
 *
 * Por que OkLCH y no HSL: en OkLCH la claridad es perceptual e independiente
 * del matiz. Con L y C fijas por rol, el contraste es INVARIANTE al matiz por
 * construccion — se mide una vez y vale para las 1.440 posiciones del reloj.
 * En HSL eso es falso y este gesto seria temerario.
 */

/** L y C por rol. El matiz es lo unico que se mueve. */
type Rol = readonly [l: number, c: number];

const CLARO: Record<string, Rol> = {
  "surface": [0.98, 0.012],
  "surface-container": [0.955, 0.02],
  "surface-container-high": [0.925, 0.026],
  "on-surface": [0.245, 0.035],
  "on-surface-variant": [0.47, 0.032],
  "outline": [0.7, 0.022],
  /*
   * `primary` bajo de 0.505 a 0.450 de claridad. La calibracion original se
   * hizo contra `surface` (L 0.980), donde 0.505 da 4.87:1 en el peor matiz —
   * pero la marca y el reloj de la barra NO se pintan sobre `surface`, sino
   * sobre `elev-2` (= `surface-container-high`, L 0.925), y ahi el mismo par
   * caia a 4.16:1. Barriendo el dia cada 5 minutos, 55 de 288 muestras por
   * debajo de AA, todas entre las 07:00 y las 11:35. Con L 0.450 el peor caso
   * del barrido sube a 5.19:1.
   *
   * Bajar esta L solo puede MEJORAR el otro par que la usa (la pastilla
   * activa, que lleva `primary` de fondo y `on-primary` de texto): medido,
   * 5.01:1 -> 6.27:1. El esquema OSCURO no se toca, ahi el par ya daba
   * 6.32:1 en el peor caso.
   */
  "primary": [0.45, 0.13],
  "on-primary": [0.99, 0.01],
  "primary-container": [0.895, 0.062],
  "on-primary-container": [0.31, 0.1],
};

const OSCURO: Record<string, Rol> = {
  /*
   * La rampa de superficie se abrio de 0.05 a 0.08 de claridad por escalon
   * (Tarea 2, arnes measure-caelestia-hora.py). Con 0.05 la luminancia
   * relativa sRGB — que es la que compara el arnes, no la claridad OkLCH —
   * se comprime cerca del negro: medido 0.0062/0.0104 de paso en el peor
   * matiz (315 grados, croma minimo), por debajo del umbral de 0.008. Con
   * 0.08 el peor caso del barrido (24 matices x 5 escalas de croma) da
   * 0.0118, con margen.
   */
  "surface": [0.185, 0.016],
  "surface-container": [0.265, 0.022],
  "surface-container-high": [0.345, 0.026],
  "on-surface": [0.925, 0.016],
  "on-surface-variant": [0.795, 0.024],
  "outline": [0.42, 0.02],
  "primary": [0.815, 0.115],
  "on-primary": [0.27, 0.095],
  "primary-container": [0.395, 0.105],
  "on-primary-container": [0.9, 0.062],
};

/** Origen de la rueda: "mediodia frio". Ver el spec para por que no es 270. */
const ORIGEN = 60;

/** El ancla no gira nunca: es lo unico constante del tema. */
const AZUFRE = { l: 0.855, lOscuro: 0.905, c: 0.152, h: 96 } as const;

/*
 * El color del cromo del navegador, uno por esquema. `themes/index.ts` pone el
 * `themeColor` estatico del tema ANTES de que este modulo monte (es la semilla
 * previa a JS), y aqui se corrige a la hora real: sin esto la barra del
 * navegador se quedaba clara a las tres de la madrugada.
 *
 * Van en hexadecimal y no en `oklch()` a proposito: el soporte de espacios de
 * color modernos en `meta[name="theme-color"]` no es uniforme entre
 * navegadores, y un valor que el navegador no entienda no degrada — se ignora
 * entero. Son el promedio de la superficie sobre los 24 matices; con croma
 * 0.012/0.016 la superficie es casi neutra, asi que el matiz no se echa de
 * menos a este tamano.
 */
const CROMO_DIA = "#f8f8f8";
const CROMO_NOCHE = "#121212";

const MINUTOS_DIA = 1440;
const AMANECE = 7 * 60;
const ANOCHECE = 20 * 60;

function ok(l: number, c: number, h: number): string {
  return `oklch(${l.toFixed(3)} ${c.toFixed(3)} ${h.toFixed(1)})`;
}

/** Los 360 grados de la rueda repartidos sobre 24 horas. */
export function hueAt(minutes: number): number {
  return (((minutes / MINUTOS_DIA) * 360 + ORIGEN) % 360 + 360) % 360;
}

/**
 * Marea de croma: pleno en la mitad fria, a un tercio en el naranja y el
 * magenta. No recorta el arco — baja la voz cuando pasa por el territorio de
 * Hyprland y de Vice, para que no se confundan con ellos.
 */
export function chromaScaleAt(hue: number): number {
  const d = Math.abs((((hue - 240) % 360) + 540) % 360 - 180);
  if (d <= 70) return 1;
  return Math.max(0.32, 1 - (d - 70) / 115);
}

/** Claro de 07:00 a 20:00. Sin banda de transicion: ver `mountCaelestiaColor`. */
export function isDarkAt(minutes: number): boolean {
  return minutes < AMANECE || minutes >= ANOCHECE;
}

export function caelestiaTokens(minutes: number): Record<string, string> {
  const hue = hueAt(minutes);
  const escala = chromaScaleAt(hue);
  const oscuro = isDarkAt(minutes);
  const roles = oscuro ? OSCURO : CLARO;

  const tokens: Record<string, string> = {};
  for (const [nombre, [l, c]] of Object.entries(roles)) {
    tokens[`--cae-${nombre}`] = ok(l, c * escala, hue);
  }

  tokens["--cae-anchor"] = ok(oscuro ? AZUFRE.lOscuro : AZUFRE.l, AZUFRE.c, AZUFRE.h);
  tokens["--cae-on-anchor"] = ok(0.215, 0.05, AZUFRE.h);
  tokens["--cae-wall-1"] = ok(oscuro ? 0.24 : 0.93, 0.09 * escala, hue);
  tokens["--cae-wall-2"] = ok(oscuro ? 0.21 : 0.95, 0.07 * escala, (hue + 42) % 360);
  tokens["--cae-wall-3"] = ok(oscuro ? 0.2 : 0.96, 0.06 * escala, (hue + 318) % 360);
  tokens["--cae-hue"] = hue.toFixed(1);

  return tokens;
}

export interface CaelestiaColorHandle {
  destroy: () => void;
}

/**
 * Aplica los tokens y los mantiene al dia.
 *
 * EL ESQUEMA NO SE INTERPOLA. La superficie va de L 0.980 a 0.185 y el texto
 * de 0.245 a 0.925: intercambian el orden, asi que cualquier recorrido
 * continuo entre los dos esquemas cruza por el punto en que ambos tienen la
 * misma claridad — contraste 1:1. Medido: 1.38:1 a las 19:55 con una banda de
 * 45 min. No hay easing que lo salve. Por eso el cambio de esquema apaga las
 * transiciones durante un fotograma en vez de suavizarse.
 */
export function mountCaelestiaColor(root: HTMLElement): CaelestiaColorHandle {
  let oscuroActual: boolean | null = null;
  let temporizador = 0;
  // Ventana de 60ms del corte de esquema (`cae-corte`). Guardado para poder
  // cancelarlo en `destroy()`: sin esto, un desmontaje que cae dentro de esa
  // ventana deja el temporizador vivo y toca `root.classList` despues de
  // que el modulo ya se dio por desmontado.
  let corteTimeout = 0;

  const aplicar = (): void => {
    const ahora = new Date();
    const minutos = ahora.getHours() * 60 + ahora.getMinutes();
    const oscuro = isDarkAt(minutos);

    if (oscuroActual !== null && oscuroActual !== oscuro) {
      root.classList.add("cae-corte");
      window.clearTimeout(corteTimeout);
      corteTimeout = window.setTimeout(() => root.classList.remove("cae-corte"), 60);
      root.dispatchEvent(
        new CustomEvent("caelestia:esquema", { detail: { oscuro }, bubbles: true }),
      );
    }
    oscuroActual = oscuro;
    root.dataset.caeEsquema = oscuro ? "noche" : "dia";

    const cromo = document.querySelector('meta[name="theme-color"]');
    if (cromo) cromo.setAttribute("content", oscuro ? CROMO_NOCHE : CROMO_DIA);

    for (const [nombre, valor] of Object.entries(caelestiaTokens(minutos))) {
      root.style.setProperty(nombre, valor);
    }
  };

  aplicar();
  // Un minuto es la resolucion del reloj de la barra; el matiz avanza 0,25
  // grados por minuto, que es imperceptible entre pasos.
  temporizador = window.setInterval(aplicar, 60_000);

  return {
    destroy: () => {
      window.clearInterval(temporizador);
      window.clearTimeout(corteTimeout);
    },
  };
}
