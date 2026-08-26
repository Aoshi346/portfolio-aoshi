import { contactChannels, identity, sceneIndex, type ContactChannel } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";

/**
 * Iconos del dock. Cadenas propias y estaticas, bundleadas — por eso pueden ir
 * por `elFromMarkup` (innerHTML). Nunca metas aqui dato externo.
 * GitHub y LinkedIn son las marcas oficiales (simple-icons, CC0).
 */
const ICONOS: Record<ContactChannel["key"], string> = {
  github:
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>',
  linkedin:
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
  correo:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="m3.5 7.5 8.5 6 8.5-6"/></svg>',
  telefono:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.24 11.4 11.4 0 0 0 3.6.58 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.4 11.4 0 0 0 .58 3.6 1 1 0 0 1-.25 1z"/></svg>',
};

// El tipo se importa para que `ICONOS` no pueda desincronizarse de los canales:
// si manana aparece un quinto `key`, TypeScript exige el icono.

/*
 * No hace falta mapa de etiqueta a icono: `ContactChannel.key` ya es
 * "correo" | "linkedin" | "telefono" | "github", exactamente estas claves.
 */

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

  /*
   * `prepend`, no `append`: la barra esta fija arriba de todo visualmente,
   * pero el orden del DOM regia el orden de tabulacion, y al final del arbol
   * de `#app` hacian falta 37 pulsaciones de Tab para alcanzar la primera
   * pastilla desde una carga limpia (medido). El resto del arbol de `#app`
   * que la precede (`bg-theme`, `noise`) es `aria-hidden` y no contiene nada
   * enfocable, asi que anteponerla la deja como el primer parada real.
   */
  root.prepend(barra);

  // El reloj de la barra es lo que gobierna el tema: tiene que ir al minuto.
  const tic = window.setInterval(() => {
    reloj.textContent = formatoHora(new Date());
  }, 30_000);

  // ------------------------------------------------------------------ dock
  // Centrado y dimensionado a su contenido, NO estirado a todo el ancho: un
  // dock estirado se lee como pie de pagina.
  const accesos = contactChannels.map((canal) => {
    const icono = elFromMarkup("cae-dock-icon", ICONOS[canal.key]);
    const enlace = el("a", "cae-dock-item", [icono]);
    enlace.href = canal.href;
    enlace.setAttribute("aria-label", canal.label);
    // La etiqueta visible es un tooltip decorativo; la accesible es aria-label.
    enlace.dataset.caeLabel = canal.value;
    if (canal.external) {
      enlace.target = "_blank";
      enlace.rel = "noopener noreferrer";
      // Punto de "abierto": el dock marca lo que esta corriendo.
      enlace.dataset.caeLive = "";
    }
    return enlace;
  });

  const dock = el("div", "cae-dock", accesos);
  dock.dataset.caeDock = "";
  /*
   * Se inserta justo tras `<main>`, no al final de `#app`: asi el orden de
   * tabulacion queda barra -> contenido -> dock, en vez de colarse detras del
   * cromo de cine y la navegacion de escenas.
   */
  const mainEl = root.querySelector("main");
  if (mainEl) mainEl.after(dock);
  else root.append(dock);

  const setScene = (index: number): void => {
    pastillas.forEach((boton, i) => {
      boton.setAttribute("aria-current", i === index ? "true" : "false");
    });
  };

  // --------------------------------------------------------- notificaciones
  const avisoTitulo = el("b", "cae-toast-t");
  const avisoDetalle = el("span", "cae-toast-s");
  const avisoPunto = el("i", "cae-dot");
  const aviso = el("aside", "cae-toast", [
    avisoPunto,
    el("span", "cae-toast-body", [avisoTitulo, avisoDetalle]),
  ]);
  aviso.dataset.caeToast = "";
  // `polite`, no `assertive`: informa, no interrumpe. Y nunca toma el foco.
  aviso.setAttribute("aria-live", "polite");
  root.append(aviso);

  let cierre = 0;
  const notificar = (titulo: string, detalle: string): void => {
    avisoTitulo.textContent = titulo;
    avisoDetalle.textContent = detalle;
    aviso.classList.add("is-open");
    window.clearTimeout(cierre);
    cierre = window.setTimeout(() => aviso.classList.remove("is-open"), 4200);
  };

  const alCambiarEsquema = (evento: Event): void => {
    if (!(evento instanceof CustomEvent)) return;
    const detalle: unknown = evento.detail;
    if (typeof detalle !== "object" || detalle === null || !("oscuro" in detalle)) return;
    const oscuro = Boolean((detalle as { oscuro: unknown }).oscuro);
    notificar(
      oscuro ? "El escritorio ha cambiado a modo noche" : "El escritorio ha vuelto a modo día",
      "El esquema se decide con tu reloj",
    );
  };
  document.documentElement.addEventListener("caelestia:esquema", alCambiarEsquema);
  limpiadores.push(() =>
    document.documentElement.removeEventListener("caelestia:esquema", alCambiarEsquema),
  );

  // Primer aviso: el estado, que es lo que un reclutador viene a saber.
  const primerAviso = window.setTimeout(() => {
    notificar(identity.availability, `${identity.now} · ${identity.location}`);
  }, 900);

  return {
    destroy: () => {
      window.clearInterval(tic);
      window.clearTimeout(primerAviso);
      window.clearTimeout(cierre);
      for (const limpiar of limpiadores) limpiar();
      barra.remove();
      dock.remove();
      aviso.remove();
    },
    setScene,
  };
}
