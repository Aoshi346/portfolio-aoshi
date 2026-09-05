/**
 * Nombre de tecnologia tal y como aparece en `caseStudies[].stack` -> slug de
 * icono (mayoria `simple-icons`, dos de Devicon Plain, ver `icons.ts`). Se
 * mantiene aparte de `icons.ts` porque aquello es el registro de slugs
 * disponibles y esto es la traduccion desde el contenido.
 *
 * Una tecnologia sin marca devuelve `null` y no pinta tile: el nombre ya
 * aparece escrito en la linea de stack, asi que no se pierde nada, y no se
 * inventa un logotipo que no existe. Hoy no hay ningun caso `null`, pero la
 * regla se mantiene para lo que se anada despues.
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
  Zustand: "zustand",
};

export function slugDeStack(nombre: string): string | null {
  return SLUGS[nombre] ?? null;
}
