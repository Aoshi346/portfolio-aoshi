import "./style.css";
import { identity } from "./data/content";
import { createNav } from "./components/nav";
import { createFooter } from "./components/footer";
import { el } from "./utils/dom";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) {
  throw new Error("Missing #app root element");
}

const main = el("main", "relative min-h-screen bg-ink text-paper", [
  el("section", "flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center", [
    el("h1", "font-display text-balance text-5xl font-bold md:text-7xl", [identity.headline]),
    el("p", "max-w-xl text-lg text-paper/70 md:text-xl", [identity.subheadline]),
  ]),
]);

app.append(createNav(), main, createFooter());
