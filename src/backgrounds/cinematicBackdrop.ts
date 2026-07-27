import type { BackgroundHandle } from "./shaderBackground";

export interface BackdropOptions {
  /** Imagen que se pinta al instante; tambien es el fallback permanente. */
  poster: string;
  video: { webm: string; mp4: string };
}

/** El video es un lujo: solo se descarga si la conexion y el dispositivo lo permiten. */
function shouldLoadVideo(): boolean {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return false;
  if (window.matchMedia("(max-width: 820px)").matches) return false;

  const nav = navigator as Navigator & { connection?: { saveData?: boolean } };
  if (nav.connection?.saveData) return false;

  return true;
}

/**
 * Fondo cinematografico: poster inmediato y, si procede, video en bucle que
 * entra fundido por encima. Las capas de gradacion, scrim y grano viven en CSS
 * (`.bg-theme` en style.css), asi que aqui solo se gestionan poster y video.
 */
export function mountCinematicBackdrop(
  container: HTMLElement,
  options: BackdropOptions,
): BackgroundHandle {
  const poster = document.createElement("img");
  poster.src = options.poster;
  poster.alt = "";
  poster.decoding = "async";
  poster.className = "backdrop-media";
  container.appendChild(poster);

  let video: HTMLVideoElement | null = null;
  let onCanPlay: (() => void) | null = null;

  if (shouldLoadVideo()) {
    video = document.createElement("video");
    video.muted = true;
    video.loop = true;
    video.autoplay = true;
    video.playsInline = true;
    video.preload = "auto";
    video.className = "backdrop-media backdrop-video";

    const webm = document.createElement("source");
    webm.src = options.video.webm;
    webm.type = "video/webm";
    const mp4 = document.createElement("source");
    mp4.src = options.video.mp4;
    mp4.type = "video/mp4";
    video.append(webm, mp4);

    // Solo se revela cuando hay fotogramas: nadie ve una caja negra.
    onCanPlay = () => video?.classList.add("is-ready");
    video.addEventListener("canplay", onCanPlay, { once: true });
    container.appendChild(video);

    // Algunos navegadores rechazan el autoplay; el poster queda como fallback.
    void video.play().catch(() => undefined);
  }

  return {
    destroy() {
      if (video) {
        if (onCanPlay) video.removeEventListener("canplay", onCanPlay);
        video.pause();
        video.removeAttribute("src");
        video.load();
        if (video.parentNode === container) container.removeChild(video);
      }
      if (poster.parentNode === container) container.removeChild(poster);
    },
  };
}
