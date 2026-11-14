// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
// Challenge 2026 hackathon (2026-11-14). Takes the dashboard screenshots and the demo GIF
// for the project page (task U5).
//
// Usage:
//   python3 web/build.py && (cd web/dist && python3 -m http.server 8765 &)
//   node web/capture_media.mjs [http://localhost:8765/]
// Needs Playwright with Chromium (NODE_PATH=$(npm root -g) for a global install) and ffmpeg. Writes into web/media/.
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright"); // require() also honours NODE_PATH
const BASE = process.argv[2] || "http://localhost:8765/";
const OUT = join(dirname(fileURLToPath(import.meta.url)), "media");
const FRAMES = join(OUT, ".frames");
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();

async function shot(name, q, { width = 1280, height = 900, scale = 2, section = null, full = false } = {}) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: scale });
  await page.goto(BASE + "?q=" + encodeURIComponent(q));
  await page.waitForTimeout(1500);
  if (section) {
    const el = await page.$(section);
    await el.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
    await el.screenshot({ path: join(OUT, name) });
  } else {
    await page.screenshot({ path: join(OUT, name), fullPage: full });
  }
  await page.close();
  console.log("wrote", name);
}

// Stills (PNG, well under 10 MB each)
await shot("01_iss_top.png", "ISS");
await shot("02_lunar_top.png", "lunar habitat");
await shot("03_lunar_needs.png", "lunar habitat", { section: "#needs" });
await shot("04_iss_coverage_solid.png", "ISS cotton fabric", { section: "#coverage .cov-block" });
await shot("05_lunar_coverage_solid.png", "lunar habitat cotton fabric", { section: "#coverage .cov-block" });
await shot("06_lunar_phone.png", "lunar habitat", { width: 390, height: 844, scale: 3 });

// GIF of the demo story: ISS, then lunar habitat, ending on the solid-fuel coverage grid.
if (existsSync(FRAMES)) rmSync(FRAMES, { recursive: true });
mkdirSync(FRAMES);
const page = await browser.newPage({ viewport: { width: 1100, height: 720 }, deviceScaleFactor: 1 });
let n = 0;
const frame = async (hold = 1) => { for (let i = 0; i < hold; i++) await page.screenshot({ path: join(FRAMES, `f${String(n++).padStart(4, "0")}.png`) }); };
const typeQuery = async (q) => {
  await page.fill("#q", "");
  for (const ch of q) { await page.type("#q", ch); await frame(1); }
  await page.click("button[type=submit]");
  await page.waitForTimeout(400);
  await frame(8);
};
const scrollTo = async (sel, steps = 8) => {
  const y0 = await page.evaluate(() => window.scrollY);
  const y1 = await page.evaluate((s) => document.querySelector(s).getBoundingClientRect().top + window.scrollY - 20, sel);
  for (let i = 1; i <= steps; i++) { await page.evaluate((y) => window.scrollTo(0, y), y0 + ((y1 - y0) * i) / steps); await frame(1); }
};
await page.goto(BASE);
await page.waitForTimeout(1500);
await frame(4);
await typeQuery("ISS cotton fabric");
await scrollTo("#top"); await frame(10);
await scrollTo("#coverage"); await frame(14);
await page.evaluate(() => window.scrollTo(0, 0)); await frame(3);
await typeQuery("lunar habitat cotton fabric");
await scrollTo("#read"); await frame(10);
await scrollTo("#top"); await frame(10);
await scrollTo("#coverage"); await frame(20);
await page.close();
await browser.close();

const gif = join(OUT, "demo_iss_to_lunar.gif");
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", "6", "-i", join(FRAMES, "f%04d.png"),
  "-vf", "scale=880:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4",
  gif]);
rmSync(FRAMES, { recursive: true });
console.log("wrote", gif);
