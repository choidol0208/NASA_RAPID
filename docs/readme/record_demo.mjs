// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
// Records one conversation with the SI assistant on the local install as a series of screenshots, for the
// animation docs/readme/assistant_demo.gif (put together by docs/readme/make_gif.py).
//
//   node docs/readme/record_demo.mjs http://127.0.0.1:<port of the local assistant server>/ <folder for the frames>
//
// The server must be in live mode (python3 -m ai.assistant.server, the language model answering). The script types
// the request on the start page, waits for the answer, asks one follow-up and waits again; it takes a screenshot
// every 1.5 seconds. Headless Google Chrome over the DevTools protocol, no library; Chrome can reach 127.0.0.1 and
// the two hosts of the page's fonts only.
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

const BASE = (process.argv[2] || "").replace(/\/?$/, "/");
const OUT = process.argv[3];
if (!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(BASE) || !OUT) { console.error("usage: node record_demo.mjs http://127.0.0.1:<port>/ <out dir>"); process.exit(2); }
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8833, W = 1000, H = 720;
const QUESTION = "lunar habitat cotton fabric", FOLLOW_UP = "and for the ISS?";
const PROFILE = join(tmpdir(), "demo-record-chrome-profile");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

rmSync(PROFILE, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, "--remote-debugging-address=127.0.0.1",
  `--user-data-dir=${PROFILE}`, "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars", "--mute-audio",
  "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1, EXCLUDE fonts.googleapis.com, EXCLUDE fonts.gstatic.com", "about:blank"], { stdio: "ignore" });
const stop = () => { try { chrome.kill(); } catch { /* gone */ } };
process.on("exit", stop);

for (let i = 0; i < 100; i++) { try { if ((await fetch(`http://127.0.0.1:${PORT}/json/version`)).ok) break; } catch { /* not yet */ } await sleep(150); }
const t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })).json();
const ws = new WebSocket(t.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let id = 0; const wait = new Map();
ws.onmessage = (m) => { const msg = JSON.parse(m.data); if (msg.id && wait.has(msg.id)) { const { res, rej } = wait.get(msg.id); wait.delete(msg.id); msg.error ? rej(new Error(JSON.stringify(msg.error))) : res(msg.result); } };
const send = (method, params = {}) => { const i = ++id; ws.send(JSON.stringify({ id: i, method, params })); return new Promise((res, rej) => wait.set(i, { res, rej })); };
const ev = async (expr) => { const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 400)); return r.result.value; };
await send("Page.enable"); await send("Runtime.enable");
await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });

const frames = [];
async function shot(label, state) {
  const r = await send("Page.captureScreenshot", { format: "png" });
  const name = `frame_${String(frames.length).padStart(3, "0")}.png`;
  writeFileSync(join(OUT, name), Buffer.from(r.data, "base64"));
  frames.push({ file: name, label, state });
}
// state of the last turn: how many steps are done, whether it is still working
const STATE = `(() => { const A = document.querySelector("#assistant"); const t = A && [...A.querySelectorAll(".as-turn")].pop();
  if (!t) return null; return { working: t.classList.contains("as-working") || !!A.querySelector(".as-run"), text: (t.querySelector(".as-steps") || {}).innerText || "", answer: !!t.querySelector(".as-answer") }; })()`;
const TO_TURN = `(() => { const A = document.querySelector("#assistant"); const t = A && [...A.querySelectorAll(".as-turn")].pop(); const n = t || A; if (n) window.scrollTo(0, Math.max(0, n.getBoundingClientRect().top + window.scrollY - 76)); })()`;

async function follow(label, maxMs) {
  const t0 = Date.now();
  let seenTurn = false;
  while (Date.now() - t0 < maxMs) {
    await sleep(1500);
    const s = await ev(STATE);
    if (!s) continue;
    seenTurn = true;
    await ev(TO_TURN);
    await sleep(120);
    await shot(label, s);
    if (!s.working && s.answer) break;
  }
  if (!seenTurn) throw new Error("the assistant did not start a turn for: " + label);
  await sleep(800); await ev(TO_TURN); await sleep(150);
  await shot(label + " (done)", await ev(STATE));
}

await send("Page.navigate", { url: BASE });
for (let i = 0; i < 100; i++) { if (await ev("document.readyState === 'complete' && !!document.querySelector('#q')")) break; await sleep(150); }
await sleep(1500); await ev("document.fonts.ready.then(() => true)");
await shot("start page", null);
await ev(`(() => { const q = document.querySelector("#q"); q.focus(); q.value = ${JSON.stringify(QUESTION)}; q.dispatchEvent(new Event("input", { bubbles: true })); window.scrollTo(0, Math.max(0, q.getBoundingClientRect().top + window.scrollY - 330)); })()`);
await sleep(300);
await shot("request typed", null);
await ev(`document.querySelector("#ask-form").requestSubmit()`);
await follow("first answer", 240000);
await ev(`(() => { const i = document.querySelector("#as-input"); i.scrollIntoView({ block: "center" }); i.focus(); i.value = ${JSON.stringify(FOLLOW_UP)}; i.dispatchEvent(new Event("input", { bubbles: true })); })()`);
await sleep(400);
await shot("follow-up typed", null);
await ev(`document.querySelector("#assistant .as-form").requestSubmit()`);
await sleep(600);
await follow("follow-up answer", 240000);
writeFileSync(join(OUT, "frames.json"), JSON.stringify({ base: BASE, question: QUESTION, follow_up: FOLLOW_UP, viewport: [W, H], taken_at: new Date().toISOString(), frames }, null, 1) + "\n");
console.log("frames:", frames.length);
ws.close(); stop(); process.exit(0);
