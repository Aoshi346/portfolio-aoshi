import { el } from "../utils/dom";

/**
 * El encendido: equivale a la cortinilla de academia de Vice, en el material
 * de este tema. La pagina arranca a oscuras y la luz prende una vez.
 *
 * No hay cuenta atras ni iris: eso es de Vice. Aqui es un unico corte de
 * 1,1s con la curva dura del tema, y el velo se autodestruye al terminar
 * para no dejar un nodo a pantalla completa capturando eventos.
 */
export interface IgnitionHandle {
  destroy: () => void;
}

export function mountHyprIgnition(host: HTMLElement): IgnitionHandle {
  const veil = el("div", "hypr-ignition", []);
  veil.setAttribute("aria-hidden", "true");
  host.appendChild(veil);

  let done = false;
  const finish = (): void => {
    if (done) return;
    done = true;
    veil.remove();
  };

  veil.addEventListener("animationend", finish, { once: true });
  // Red: si la animacion no llega a disparar (pestana en segundo plano al
  // cargar, por ejemplo), el velo se retira igualmente.
  const fallback = window.setTimeout(finish, 2000);

  return {
    destroy(): void {
      window.clearTimeout(fallback);
      finish();
    },
  };
}
