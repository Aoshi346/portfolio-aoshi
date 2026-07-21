import "./style.css";
import { createNav } from "./components/nav";
import { createFooter } from "./components/footer";
import { createHero } from "./sections/hero";
import { el } from "./utils/dom";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) {
  throw new Error("Missing #app root element");
}

const main = el("main", "relative min-h-screen bg-ink text-paper", [createHero()]);

app.append(createNav(), main, createFooter());
