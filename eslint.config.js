import js from "@eslint/js";
import tseslint from "typescript-eslint";
import globals from "globals";

export default tseslint.config(
  /*
   * `.claude` fuera del barrido, no solo `dist`. El tooling de sesion crea los
   * git worktrees en `.claude/worktrees/<nombre>`, o sea DENTRO del repo: al
   * lintar desde la raiz, ESLint entra ahi, encuentra dos tsconfig candidatos
   * (el del repo y el de la copia) y aborta con "No tsconfigRootDir was set,
   * and multiple candidate TSConfigRootDirs are present" en TODOS los ficheros.
   * Medido: 64 errores de parseo, ninguno de codigo, con un worktree presente.
   * `.gitignore` no vale aqui — la configuracion plana de ESLint no lo lee.
   *
   * `.superpowers/**` va por lo mismo y es el otro directorio de tooling de
   * sesion dentro del repo: el companion de brainstorming copia ahi un
   * `gsap.min.js` para que las maquetas animen de verdad, y ESLint lo lintaba.
   * Medido el 2026-09-03: 219 errores, los 219 de ese unico fichero minificado
   * y ninguno de codigo del proyecto. `npm run lint` es requisito de DONE, y un
   * gate que no puede ponerse verde deja de leerse — el mismo modo de fallo que
   * ya documenta la linea base de `verify.py`.
   */
  { ignores: ["dist", ".claude/**", ".superpowers/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      "no-console": ["warn", { allow: ["warn", "error"] }],
    },
  },
);
