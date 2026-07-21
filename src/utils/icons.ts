/**
 * Iconos de marca vía `simple-icons`, importados como SVG crudo (sin loader
 * JS ni red): cada slug es un import estático que Vite inlinea en el bundle.
 */
import react from "simple-icons/icons/react.svg?raw";
import typescript from "simple-icons/icons/typescript.svg?raw";
import tailwindcss from "simple-icons/icons/tailwindcss.svg?raw";
import vite from "simple-icons/icons/vite.svg?raw";
import python from "simple-icons/icons/python.svg?raw";
import django from "simple-icons/icons/django.svg?raw";
import mysql from "simple-icons/icons/mysql.svg?raw";
import javascript from "simple-icons/icons/javascript.svg?raw";
import html5 from "simple-icons/icons/html5.svg?raw";
import css from "simple-icons/icons/css.svg?raw";
import c from "simple-icons/icons/c.svg?raw";
import cplusplus from "simple-icons/icons/cplusplus.svg?raw";

const icons: Record<string, string> = {
  react,
  typescript,
  tailwindcss,
  vite,
  python,
  django,
  mysql,
  javascript,
  html5,
  css,
  c,
  cplusplus,
};

export function getIconMarkup(slug: string): string {
  const svg = icons[slug];
  if (!svg) {
    throw new Error(`Missing simple-icons SVG for slug "${slug}"`);
  }
  return svg;
}
