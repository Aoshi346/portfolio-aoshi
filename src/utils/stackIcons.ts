/**
 * Nombre de tecnologia tal y como aparece en `caseStudies[].stack` -> slug de
 * `simple-icons`. Se mantiene aparte de `icons.ts` porque aquello es el
 * registro de slugs disponibles y esto es la traduccion desde el contenido.
 *
 * Una tecnologia sin marca devuelve `null` y no pinta tile: el nombre ya
 * aparece escrito en la linea de stack, asi que no se pierde nada, y no se
 * inventa un logotipo que no existe. `Zustand` es el unico caso hoy.
 */
const SLUGS: Record<string, string> = {
  Python: "python",
  Django: "django",
  TypeScript: "typescript",
  JavaScript: "javascript",
  React: "react",
  Vite: "vite",
  "Next.js": "nextdotjs",
  RxDB: "rxdb",
  GSAP: "gsap",
  Electron: "electron",
  C: "c",
  GTK4: "gtk",
};

export function slugDeStack(nombre: string): string | null {
  return SLUGS[nombre] ?? null;
}
