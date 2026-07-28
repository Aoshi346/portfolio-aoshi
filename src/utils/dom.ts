export function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  children?: (Node | string)[],
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  for (const child of children ?? []) {
    node.append(child);
  }
  return node;
}

/**
 * Envuelve markup SVG de confianza (bundleado, no input externo) en un
 * contenedor con la clase dada.
 */
export function elFromMarkup(className: string, markup: string): HTMLDivElement {
  const wrapper = document.createElement("div");
  wrapper.className = className;
  wrapper.innerHTML = markup;
  return wrapper;
}
