import "./style.css";
import { createNav } from "./components/nav";
import { createFooter } from "./components/footer";
import { createHero } from "./sections/hero";
import { createAbout } from "./sections/about";
import { createCaseStudies } from "./sections/caseStudies";
import { createSkills } from "./sections/skills";
import { createExperience } from "./sections/experience";
import { createContact } from "./sections/contact";
import { el } from "./utils/dom";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) {
  throw new Error("Missing #app root element");
}

const main = el("main", "relative min-h-screen text-paper", [
  createHero(),
  createAbout(),
  createCaseStudies(),
  createSkills(),
  createExperience(),
  createContact(),
]);

const atmosphere = el("div", "bg-atmosphere", []);
atmosphere.setAttribute("aria-hidden", "true");
const noise = el("div", "bg-noise", []);
noise.setAttribute("aria-hidden", "true");

app.append(atmosphere, noise, createNav(), main, createFooter());

void import("./utils/reveal").then(({ initScrollReveal }) => initScrollReveal(main));
