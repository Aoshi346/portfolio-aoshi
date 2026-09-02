/**
 * La escena Titulo de Caelestia: lo que no se puede hacer con CSS.
 *
 * Spec: docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md
 */

/**
 * Estira las lineas del titular hasta que todas midan lo mismo.
 *
 * DOS TRAMPAS, las dos pagadas ya:
 *
 * 1. Medir la caja del <span> NO es medir el texto. Los `.cae-ln` son de
 *    bloque: `getBoundingClientRect().width` devuelve el ancho del CONTENEDOR.
 *    Con esa medida las tres lineas salen del MISMO tamano y el bloque solo
 *    PARECE justificado. Hay que usar `Range` + `selectNodeContents`.
 *
 * 2. La medida comun no puede ser fija. Con esta frase las lineas son de 18, 24
 *    y 9 caracteres: forzarlas a una medida ancha dispara el alto de la ultima
 *    y se come el dock (medido: 400 px de bloque, -138 px de aire). Por eso el
 *    bucle estrecha la medida en pasos hasta que cabe.
 *
 * TERCERA TRAMPA, pagada al medir contra el arnes: `Math.round()` en el
 * tamano de fuente. Con lineas de 18/24/9 caracteres los tres tamanos salen
 * MUY distintos entre si (medido: 75 / 56 / 145 px) y el error de redondear a
 * entero es proporcional al tamano — 0.5 px de 56 pesa el triple, en
 * proporcion, que 0.5 px de 145. Sumados los tres, los anchos finales
 * quedaban a 7.9 px entre si (tope del arnes: 4 px). Sin redondear (tamano de
 * fuente fraccionario, que CSS acepta sin problema) el error baja a ~3 px.
 */
export function justificarTitular(root: HTMLElement, medida = 1080, altoMax = 250): void {
  const tit = root.querySelector<HTMLElement>(".cae-tit");
  if (!tit) return;
  const lineas = Array.from(tit.querySelectorAll<HTMLElement>(".cae-ln"));
  if (lineas.length === 0) return;

  const aplicar = (objetivo: number): void => {
    for (const linea of lineas) {
      linea.style.fontSize = "100px";
      const rango = document.createRange();
      rango.selectNodeContents(linea);
      const ancho = rango.getBoundingClientRect().width;
      if (ancho > 0) linea.style.fontSize = `${(objetivo / ancho) * 100}px`;
    }
  };

  let objetivo = medida;
  aplicar(objetivo);
  while (objetivo > 380 && tit.getBoundingClientRect().height > altoMax) {
    objetivo -= 30;
    aplicar(objetivo);
  }
}

export interface TituloHandle {
  destroy: () => void;
}

export function montarTitulo(root: HTMLElement): TituloHandle {
  const rejustificar = (): void => justificarTitular(root);

  // Las fuentes variables cargan despues del primer pintado: justificar antes
  // mide Georgia (el respaldo) y los tamanos salen mal.
  void document.fonts.ready.then(rejustificar);
  rejustificar();
  window.addEventListener("resize", rejustificar);

  return {
    destroy: () => window.removeEventListener("resize", rejustificar),
  };
}
