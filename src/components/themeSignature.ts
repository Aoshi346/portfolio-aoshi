import { el } from "../utils/dom";

/**
 * Firma discreta del tema activo. No es un selector — no hay control de tema
 * por diseno — solo deja constancia de en que mundo has caido esta visita.
 */
export function createThemeSignature(label: string): HTMLElement {
  const signature = el(
    "div",
    "theme-signature pointer-events-none fixed bottom-5 right-5 z-40 flex items-center gap-2 font-mono text-[0.6rem] uppercase tracking-[0.3em] text-paper/40",
    [el("span", "block h-1.5 w-1.5 rounded-full bg-accent", []), label],
  );
  signature.setAttribute("aria-hidden", "true");
  return signature;
}
