import { sceneIndex } from "../data/content";
import { el } from "../utils/dom";

/**
 * El shell de Caelestia: barra de workspaces, dock y notificaciones.
 *
 * Los tres viven en un solo modulo a proposito — comparten estado (la hora, la
 * escena activa) y cambian juntos. Separarlos obligaria a exportar ese estado,
 * que es el acoplamiento que se quiere evitar.
 */
export interface CaelestiaShellHandle {
  destroy: () => void;
  setScene: (index: number) => void;
}

function formatoHora(fecha: Date): string {
  const hh = String(fecha.getHours()).padStart(2, "0");
  const mm = String(fecha.getMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
}

export function mountCaelestiaShell(root: HTMLElement): CaelestiaShellHandle {
  const limpiadores: (() => void)[] = [];

  // ---------------------------------------------------------------- la barra
  const pastillas = sceneIndex.map((escena, indice) => {
    const numero = el("i", "cae-ws-n", [String(indice + 1)]);
    const boton = el("button", "cae-ws", [numero, escena.label]);
    boton.type = "button";
    boton.dataset.caeWs = escena.id;
    boton.setAttribute("aria-current", indice === 0 ? "true" : "false");

    const alPulsar = (): void => {
      root.dispatchEvent(
        new CustomEvent("caelestia:workspace", {
          detail: { index: indice, id: escena.id },
          bubbles: true,
        }),
      );
    };
    boton.addEventListener("click", alPulsar);
    limpiadores.push(() => boton.removeEventListener("click", alPulsar));
    return boton;
  });

  const navegacion = el("nav", "cae-ws-list", pastillas);
  navegacion.setAttribute("aria-label", "Escenas");

  const punto = el("i", "cae-dot");
  const disponible = el("span", "cae-avail", [punto, "Disponible"]);

  const reloj = el("span", "cae-clock", [formatoHora(new Date())]);
  reloj.dataset.caeClock = "";

  const bandeja = el("span", "cae-tray", [disponible, reloj]);
  const marca = el("span", "cae-mark", ["caelestia"]);

  const barra = el("header", "cae-bar", [marca, navegacion, bandeja]);
  barra.dataset.caeBar = "";

  root.append(barra);

  // El reloj de la barra es lo que gobierna el tema: tiene que ir al minuto.
  const tic = window.setInterval(() => {
    reloj.textContent = formatoHora(new Date());
  }, 30_000);

  const setScene = (index: number): void => {
    pastillas.forEach((boton, i) => {
      boton.setAttribute("aria-current", i === index ? "true" : "false");
    });
  };

  return {
    destroy: () => {
      window.clearInterval(tic);
      for (const limpiar of limpiadores) limpiar();
      barra.remove();
    },
    setScene,
  };
}
