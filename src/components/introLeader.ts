import { identity } from "../data/content";
import { el } from "../utils/dom";

/**
 * Leader de apertura (solo Vice, solo sin `prefers-reduced-motion`): la
 * cabecera de academia que precede a una bobina — reticula de registro, anillo
 * doble, brazo barredor que da una vuelta por numero, cuenta atras y punto de
 * cambio de bobina. Al llegar a uno, el propio circulo se abre como un
 * diafragma y deja ver el hero (ver `sceneIntro` en `vice.choreography.ts`).
 *
 * Es decoracion pura: `aria-hidden` y `pointer-events: none` en todo el arbol,
 * como el resto del cromo de cine. Nunca bloquea el scroll ni los clics,
 * tarde lo que tarde en retirarse.
 *
 * El numero es UN solo nodo cuyo texto cambia, no tres nodos superpuestos: la
 * cuenta la conduce la timeline, que es quien sabe en que tiempo va.
 */
export function createIntroLeader(): HTMLElement {
  const sweep = el("div", "leader-sweep", []);
  sweep.setAttribute("data-leader-sweep", "");

  const num = el("span", "leader-num", ["3"]);
  num.setAttribute("data-leader-num", "");

  const ring = el("div", "leader-ring", [sweep, num]);
  ring.setAttribute("data-leader-ring", "");

  const cue = el("div", "leader-cue", []);
  cue.setAttribute("data-leader-cue", "");

  // Contenido real, no relleno: el mismo nombre que preside el hero.
  const foot = el("p", "leader-foot", [`Rollo 01 · ${identity.name}`]);

  // El iris va el PRIMERO: es la capa que pinta el negro de la pantalla, asi
  // que todo lo demas del leader tiene que quedar por encima de el.
  const iris = el("div", "leader-iris", []);
  iris.setAttribute("data-leader-iris", "");

  const leader = el("div", "intro-leader", [
    iris,
    el("div", "leader-cross", []),
    ring,
    cue,
    foot,
  ]);
  leader.setAttribute("data-intro-leader", "");
  leader.setAttribute("aria-hidden", "true");
  return leader;
}
