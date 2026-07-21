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

const main = el("main", "relative min-h-screen bg-ink text-paper", [
  createHero(),
  createAbout(),
  createCaseStudies(),
  createSkills(),
  createExperience(),
  createContact(),
]);

app.append(createNav(), main, createFooter());

void import("./utils/reveal").then(({ initScrollReveal }) => initScrollReveal(main));
