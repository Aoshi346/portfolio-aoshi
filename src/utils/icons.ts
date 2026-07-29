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
import nextdotjs from "simple-icons/icons/nextdotjs.svg?raw";
import nodedotjs from "simple-icons/icons/nodedotjs.svg?raw";
import gsap from "simple-icons/icons/gsap.svg?raw";
import rxdb from "simple-icons/icons/rxdb.svg?raw";
import electron from "simple-icons/icons/electron.svg?raw";
import gtk from "simple-icons/icons/gtk.svg?raw";
import git from "simple-icons/icons/git.svg?raw";
import github from "simple-icons/icons/github.svg?raw";
import n8n from "simple-icons/icons/n8n.svg?raw";
import claude from "simple-icons/icons/claude.svg?raw";
import googlegemini from "simple-icons/icons/googlegemini.svg?raw";

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
  nextdotjs,
  nodedotjs,
  gsap,
  rxdb,
  electron,
  gtk,
  git,
  github,
  n8n,
  claude,
  googlegemini,
};

export function getIconMarkup(slug: string): string {
  const svg = icons[slug];
  if (!svg) {
    throw new Error(`Missing simple-icons SVG for slug "${slug}"`);
  }
  return svg;
}
