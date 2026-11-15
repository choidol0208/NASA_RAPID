// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
// Records one conversation with the SI assistant on the local install as a series of screenshots, for the
// animation docs/readme/assistant_demo.gif (put together by docs/readme/make_gif.py).
//
//   node docs/readme/record_demo.mjs http://127.0.0.1:<port of the local assistant server>/ <folder for the frames>
//
// The server must be in live mode (python3 -m ai.assistant.server, the language model answering). The script
// plays a visitor: it moves a pointer to the input, types the request letter by letter, clicks "Find evidence",
// waits for the answer, then types and sends one follow-up. The pointer is a small arrow that the script draws
// into the page (a headless browser shows no mouse pointer); the typing and the clicks are the script's. The
// page, the steps and the answers are what the local install showed. Headless Google Chrome over the DevTools
// protocol, no library; Chrome can reach 127.0.0.1 and the two hosts of the page's fonts only.
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
rmSync(OUT, { recursive: true, force: true });
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
async function shot(label, ms, state) {
  const r = await send("Page.captureScreenshot", { format: "png" });
  const name = `frame_${String(frames.length).padStart(3, "0")}.png`;
  writeFileSync(join(OUT, name), Buffer.from(r.data, "base64"));
  frames.push({ file: name, label, ms, state: state || null });
}

// ---- the pointer the script draws into the page, and what it does with it
let cur = { x: 620, y: 420 };
const ENSURE = `if (!document.getElementById("demo-cursor")) { const d = document.createElement("div"); d.id = "demo-cursor";
  d.style.cssText = "position:fixed;left:0;top:0;z-index:2147483647;pointer-events:none;width:26px;height:26px;";
  d.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M4 2l15 9-6.6 1.4 3.9 7.3-2.8 1.5-3.9-7.3L5 19z" fill="#111827" stroke="#ffffff" stroke-width="1.6" stroke-linejoin="round"/></svg>' +
    '<span id="demo-ring" style="position:absolute;left:-11px;top:-11px;width:30px;height:30px;border-radius:50%;border:3px solid #2346c4;opacity:0"></span>';
  document.body.appendChild(d); }`;
const place = (x, y, ring) => ev(`(() => { ${ENSURE} const c = document.getElementById("demo-cursor"); c.style.transform = "translate(" + ${Math.round(x)} + "px, " + ${Math.round(y)} + "px)"; document.getElementById("demo-ring").style.opacity = "${ring ? 0.9 : 0}"; return true; })()`);
const centre = (sel, dx = 0.5, dy = 0.5) => ev(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); const r = e.getBoundingClientRect(); return { x: r.left + r.width * ${dx}, y: r.top + r.height * ${dy} }; })()`);
async function moveTo(sel, label, dx, dy) {
  const to = await centre(sel, dx, dy);
  const n = 7;
  for (let i = 1; i <= n; i++) {
    const k = i / n, e = k * k * (3 - 2 * k);           // ease in and out
    await place(cur.x + (to.x - cur.x) * e, cur.y + (to.y - cur.y) * e, false);
    await shot(label, i === n ? 260 : 55);
  }
  cur = to;
}
async function click(label) { await place(cur.x, cur.y, true); await shot(label, 220); await place(cur.x, cur.y, false); }
async function type(sel, text, label) {
  await ev(`document.querySelector(${JSON.stringify(sel)}).focus()`);
  for (let i = 1; i <= text.length; i++) {
    await ev(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); e.value = ${JSON.stringify(text.slice(0, i))}; e.dispatchEvent(new Event("input", { bubbles: true })); })()`);
    if (i % 2 === 0 || i === text.length) await shot(label, i === text.length ? 650 : 110);
  }
}

// ---- the assistant's last turn: is it still working, what do its steps say
const STATE = `(() => { const A = document.querySelector("#assistant"); const t = A && [...A.querySelectorAll(".as-turn")].pop();
  if (!t) return null; return { working: t.classList.contains("as-working") || !!A.querySelector(".as-run"), text: (t.querySelector(".as-steps") || {}).innerText || "", answer: !!t.querySelector(".as-answer") }; })()`;
const TO_TURN = `(() => { const A = document.querySelector("#assistant"); const t = A && [...A.querySelectorAll(".as-turn")].pop(); const n = t || A; if (n) window.scrollTo(0, Math.max(0, n.getBoundingClientRect().top + window.scrollY - 76)); })()`;
async function follow(label, maxMs) {
  const t0 = Date.now();
  let last = null, n = 0, seen = false;
  while (Date.now() - t0 < maxMs) {
    await sleep(1000);
    const s = await ev(STATE);
    if (!s) continue;
    seen = true;
    await ev(TO_TURN); await place(cur.x, cur.y, false); await sleep(80);
    n++;
    if (!s.working && s.answer) break;
    if (s.text !== last || n % 3 === 0) { await shot(label, s.text !== last ? 700 : 380, s); last = s.text; }   // a step changed, or every third second
  }
  if (!seen) throw new Error("the assistant did not start a turn for: " + label);
  await sleep(700); await ev(TO_TURN); await sleep(150);
  await shot(label + " (done)", 5500, await ev(STATE));
}

await send("Page.navigate", { url: BASE });
for (let i = 0; i < 100; i++) { if (await ev("document.readyState === 'complete' && !!document.querySelector('#q')")) break; await sleep(150); }
await sleep(1500); await ev("document.fonts.ready.then(() => true)");
await ev(`window.scrollTo(0, Math.max(0, document.querySelector("#q").getBoundingClientRect().top + window.scrollY - 330))`);
await place(cur.x, cur.y, false);
await shot("start page", 1300);
await moveTo("#q", "to the input", 0.3, 0.5);
await click("click the input");
await type("#q", QUESTION, "typing the request");
await moveTo("#ask-form button[type=submit]", "to the button");
await click("click Find evidence");
await ev(`document.querySelector("#ask-form").requestSubmit()`);
await follow("first answer", 240000);
await ev(`document.querySelector("#as-input").scrollIntoView({ block: "center" })`);
await place(cur.x, cur.y, false); await sleep(200);
await shot("the answer, lower part", 2200);
await moveTo("#as-input", "to the follow-up box", 0.25, 0.5);
await click("click the follow-up box");
await type("#as-input", FOLLOW_UP, "typing the follow-up");
await moveTo("#assistant .as-form button[type=submit], #assistant .as-form .as-send", "to Send");
await click("click Send");
await ev(`document.querySelector("#assistant .as-form").requestSubmit()`);
await sleep(500);
await follow("follow-up answer", 240000);
writeFileSync(join(OUT, "frames.json"), JSON.stringify({ base: BASE, question: QUESTION, follow_up: FOLLOW_UP, viewport: [W, H], taken_at: new Date().toISOString(),
  note: "The pointer is drawn into the page by this script; typing and clicks are the script's. ms is how long the animation shows a frame.", frames }, null, 1) + "\n");
console.log("frames:", frames.length);
ws.close(); stop(); process.exit(0);
