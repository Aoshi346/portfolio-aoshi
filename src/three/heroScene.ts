import * as THREE from "three";

export interface HeroSceneHandle {
  destroy: () => void;
}

/**
 * Icosaedro low-poly con wireframe superpuesto: geometria procedural,
 * sin assets GLTF que pesen el bundle inicial.
 */
export function mountHeroScene(container: HTMLElement): HeroSceneHandle {
  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0, 5.2);

  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: "high-performance",
    preserveDrawingBuffer: true,
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const geometry = new THREE.IcosahedronGeometry(1.4, 1);
  const material = new THREE.MeshStandardMaterial({
    color: 0xff5a3c,
    roughness: 0.25,
    metalness: 0.15,
    flatShading: true,
  });
  const core = new THREE.Mesh(geometry, material);

  const edges = new THREE.EdgesGeometry(geometry);
  const wireframeMaterial = new THREE.LineBasicMaterial({
    color: 0xf4f2ec,
    transparent: true,
    opacity: 0.35,
  });
  const wireframe = new THREE.LineSegments(edges, wireframeMaterial);
  wireframe.scale.setScalar(1.01);

  const group = new THREE.Group();
  group.add(core, wireframe);
  scene.add(group);

  const ambient = new THREE.AmbientLight(0xffffff, 0.6);
  const key = new THREE.DirectionalLight(0xffffff, 1.4);
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

  function resize() {
    const { clientWidth, clientHeight } = container;
    if (clientWidth === 0 || clientHeight === 0) return;
    camera.aspect = clientWidth / clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(clientWidth, clientHeight);
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
  const timer = new THREE.Timer();

  function animate(timestamp: number) {
    frameId = requestAnimationFrame(animate);
    if (!isVisible) return;

    timer.update(timestamp);
    const delta = timer.getDelta();
    const elapsed = timer.getElapsed();

    targetRotation.x += (pointer.y * 0.4 - targetRotation.x) * 0.04;
    targetRotation.y += (pointer.x * 0.4 - targetRotation.y) * 0.04;

    group.rotation.x = targetRotation.x + Math.sin(elapsed * 0.3) * 0.1;
    group.rotation.y += delta * 0.15 + (targetRotation.y - group.rotation.y) * 0.02;

    renderer.render(scene, camera);
  }
  frameId = requestAnimationFrame(animate);

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
