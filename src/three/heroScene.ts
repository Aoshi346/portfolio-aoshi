import {
  AmbientLight,
  DirectionalLight,
  EdgesGeometry,
  Group,
  IcosahedronGeometry,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  MeshStandardMaterial,
  PerspectiveCamera,
  Scene,
  Timer,
  WebGLRenderer,
} from "three";

export interface HeroSceneHandle {
  destroy: () => void;
}

/**
 * Icosaedro low-poly con wireframe superpuesto: geometria procedural,
 * sin assets GLTF que pesen el bundle inicial.
 */
export function mountHeroScene(container: HTMLElement): HeroSceneHandle {
  const scene = new Scene();

  const camera = new PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0, 5.2);

  const renderer = new WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: "high-performance",
    preserveDrawingBuffer: true,
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const geometry = new IcosahedronGeometry(1.4, 1);
  const material = new MeshStandardMaterial({
    color: 0xff5a3c,
    roughness: 0.25,
    metalness: 0.15,
    flatShading: true,
  });
  const core = new Mesh(geometry, material);

  const edges = new EdgesGeometry(geometry);
  const wireframeMaterial = new LineBasicMaterial({
    color: 0xf4f2ec,
    transparent: true,
    opacity: 0.35,
  });
  const wireframe = new LineSegments(edges, wireframeMaterial);
  wireframe.scale.setScalar(1.01);

  const group = new Group();
  group.add(core, wireframe);
  scene.add(group);

  const ambient = new AmbientLight(0xffffff, 0.6);
  const key = new DirectionalLight(0xffffff, 1.4);
  key.position.set(3, 2, 4);
  scene.add(ambient, key);

  const pointer = { x: 0, y: 0 };
  const targetRotation = { x: 0, y: 0 };

  function onPointerMove(event: PointerEvent) {
    const rect = container.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = ((event.clientY - rect.top) / rect.height) * 2 - 1;
  }
  window.addEventListener("pointermove", onPointerMove, { passive: true });

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function resize() {
    const { clientWidth, clientHeight } = container;
    if (clientWidth === 0 || clientHeight === 0) return;
    camera.aspect = clientWidth / clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(clientWidth, clientHeight);
    if (prefersReducedMotion) renderer.render(scene, camera);
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(container);
  resize();

  let isVisible = true;
  const intersectionObserver = new IntersectionObserver(
    ([entry]) => {
      isVisible = entry.isIntersecting;
    },
    { threshold: 0.05 },
  );
  intersectionObserver.observe(container);

  let frameId = 0;
  const timer = new Timer();

  function animate(timestamp: number) {
    frameId = requestAnimationFrame(animate);
    if (!isVisible) return;

    timer.update(timestamp);
    const delta = timer.getDelta();
    const elapsed = timer.getElapsed();

    targetRotation.x += (pointer.y * 0.3 - targetRotation.x) * 0.04;
    targetRotation.y += (pointer.x * 0.3 - targetRotation.y) * 0.04;

    // Bamboleo senoidal sutil: amplitud baja y frecuencia lenta para que se
    // lea como movimiento controlado (respiración), no como ruido.
    group.rotation.x = targetRotation.x + Math.sin(elapsed * 0.22) * 0.045;
    group.rotation.y += delta * 0.09 + (targetRotation.y - group.rotation.y) * 0.02;

    renderer.render(scene, camera);
  }

  if (prefersReducedMotion) {
    // Una sola pasada estática: nada de rotación continua ni bamboleo.
    renderer.render(scene, camera);
  } else {
    frameId = requestAnimationFrame(animate);
  }

  return {
    destroy() {
      cancelAnimationFrame(frameId);
      window.removeEventListener("pointermove", onPointerMove);
      resizeObserver.disconnect();
      intersectionObserver.disconnect();
      geometry.dispose();
      edges.dispose();
      material.dispose();
      wireframeMaterial.dispose();
      renderer.dispose();
      if (renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
    },
  };
}
