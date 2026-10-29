import type { BackgroundHandle } from "../backgrounds/shaderBackground";
import type { Theme } from "./types";

/** Carga diferida de la tipografia del tema. */
function loadThemeFonts(href: string): void {
  /*
   * defensive: el script inline de index.html ya pide esta hoja antes del
   * primer pintado (ver el comentario alli). Esta funcion queda como red de
   * seguridad para el caso de que esa URL se desincronice del `fontHref` real
   * del tema; si la peticion ya esta hecha, no se duplica.
   */
  const selector = `link[rel="stylesheet"][href="${CSS.escape(href)}"]`;
  if (document.head.querySelector(selector)) return;

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = href;
  document.head.appendChild(link);
}

/**
 * Aplica el tema: marca el `data-theme` (del que cuelgan los tokens CSS),
 * ajusta el color del chrome, pide su tipografia y monta su fondo generativo.
 *
 * `index.html` ya trae `data-theme="caelestia"` escrito en `<html>`, para que
 * los tokens esten puestos en el primer pintado; volver a ponerlo aqui es
 * inocuo.
 */
export async function applyTheme(
  theme: Theme,
  backgroundHost: HTMLElement,
): Promise<BackgroundHandle> {
  document.documentElement.dataset.theme = theme.id;

  const themeColorMeta = document.querySelector('meta[name="theme-color"]');
  if (themeColorMeta) themeColorMeta.setAttribute("content", theme.themeColor);

  loadThemeFonts(theme.fontHref);

  return theme.mountBackground(backgroundHost);
}
