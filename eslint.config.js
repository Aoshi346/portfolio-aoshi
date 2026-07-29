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
   */
  { ignores: ["dist", ".claude/**"] },
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
