import { sceneIndex, type SceneEntry } from "../data/content";

export type { SceneEntry };
export const TARGETS: SceneEntry[] = sceneIndex;

/*
 * El carril de obra se recorre en horizontal dentro de un pin. Su borde de
 * inicio deja la primera cartela a medio montar: el fotograma asentado esta en
 * u ~ 0,42 de los 6,25 que dura la timeline maestra. Se lee EN EL MOMENTO del
 * clic y nunca se cachea: el presupuesto del pin cambia con cada refresh de
 * ScrollTrigger.
 *
 * OBRA_TOTAL_U REIMPLEMENTA un dato de `vice.choreography.ts`: sale de
 * 4 * OBRA_TRANSIT + 5 * OBRA_REST. No se importa de alli a proposito — ese
 * modulo carga en diferido y solo en Vice, y traerlo aqui lo metaria en el
 * bundle de arranque de los tres temas. El precio de la copia es que puede
 * derivar, y derivada NO falla: el ancla de obra aterriza mal en silencio.
 * Por eso `scripts/measure-nav.py` recalcula la suma y compara antes de medir
 * nada. Si tocas OBRA_TRANSIT u OBRA_REST, el arnes te lo dira.
 */
export const OBRA_SETTLED_U = 0.42;
export const OBRA_TOTAL_U = 6.25;

export function destinationFor(id: string): number | null {
  const target = document.getElementById(id);
  if (!target) return null;

  const top = target.getBoundingClientRect().top + window.scrollY;

  if (id === "obra") {
    // La altura del envoltorio menos una pantalla es el recorrido que el pin
    // reserva. Si el carril no esta fijado (Hyprland, Caelestia, movil) el
    // termino sale <= 0 y el destino es el borde, que es lo correcto ahi.
    const budget = Math.max(0, target.offsetHeight - window.innerHeight);
    return top + (OBRA_SETTLED_U / OBRA_TOTAL_U) * budget;
  }

  return top;
}
