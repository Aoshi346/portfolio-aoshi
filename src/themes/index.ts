import type { BackgroundHandle } from "../backgrounds/shaderBackground";
import { caelestiaTheme } from "./caelestia";
import { hyprlandTheme } from "./hyprland";
import type { Theme } from "./types";
import { viceTheme } from "./vice";

/** Registro extensible: anadir un tema es anadir una entrada aqui. */
export const themeRegistry: Theme[] = [viceTheme, hyprlandTheme, caelestiaTheme];

/**
 * Elige el tema de la visita. Es aleatorio por diseno (no hay selector), salvo
 * el override `?theme=<id>`, reservado para QA y screenshots reproducibles.
 */
export function pickTheme(): Theme {
  const requested = new URLSearchParams(window.location.search).get("theme");
  const forced = themeRegistry.find((theme) => theme.id === requested);
  if (forced) return forced;

  // El script inline de index.html ya sorteo el tema antes del primer pintado
  // (evita el flash de un tema oscuro a Caelestia, que es claro). Respetarlo.
  const preset = themeRegistry.find((theme) => theme.id === document.documentElement.dataset.theme);
  if (preset) return preset;

  const index = Math.floor(Math.random() * themeRegistry.length);
  // defensive: Math.random() nunca devuelve 1, pero el fallback evita un
  // undefined silencioso si el registro quedara vacio en el futuro.
  return themeRegistry[index] ?? viceTheme;
}

/** Carga diferida de la tipografia del tema activo (las otras nunca se piden). */
function loadThemeFonts(href: string): void {
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = href;
  document.head.appendChild(link);
}

/**
 * Aplica el tema: marca el `data-theme` (del que cuelgan los tokens CSS),
 * ajusta el color del chrome, pide su tipografia y monta su fondo generativo.
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
