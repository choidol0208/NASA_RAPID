/* AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon. */
/* The chat assistant on top of the Fire Evidence Explorer dashboard (contract: ai/assistant/DESIGN.md, section 12).
   Plain JavaScript, one IIFE, no framework, no request to another site. Every number, sentence and source shown
   here comes from the response of the local assistant server, from a recorded response file, or from a mock file;
   this script computes no fact.
   One input (15 November, 16:26 decision): the page's own input (#q in #ask-form) is the only question box a visitor
   meets first. A real submit of it also starts a turn here where a server answers (live, no-model, mock); this
   section shows no text box of its own until an answer is on screen, and then only a follow-up box. */
(function () {
  "use strict";

  // ------------------------------------------------------------------ fixed texts (section 12.5, word for word)
  // Step labels for events that carry none (a turn answered from cache; added after the clean-clone check).
  var STEP_LABELS = { understand: "Reading your request", plan: "Choosing what to look up", lookup: "Looking up the team's files",
    write: "Writing from the facts", check: "Checking every sentence", deliver: "Done" };
  var L = {
    // Titles of the section (one input: the section no longer says "Ask the assistant" above a second box).
    titleIdle: "The SI assistant",
    titleAnswer: "The assistant's answer",
    titleRecorded: "Recorded answers of the SI assistant",
    sub: "Ask in your own words, in any language. Answers are in English, built only from the team's files, with a source for every sentence.",
    followUp: "Ask a follow-up",
    send: "Ask",
    questions: "Questions",
    idleHow: "Type what you are building, or a question, in the box at the top of the page. The written answer appears here.",
    waitLive: "The written answer takes about 1 to 2 minutes on this computer. The dashboard below already shows this request.",
    offer: "Ask the assistant about this",
    offerBusy: "This can be asked when the current answer is done.",
    // The page's input invites a question only where a local server answers it (setInputWords).
    inputLabel: "What are you building, and where? Or ask a question.",
    inputHint: "e.g. moon cotton fabric, 30% O2 at 10.2 psi, or: where are the raw data for the ISS?",
    recordedMark: "Recorded on {date} with the local language model (gpt-oss:20b) and replayed here; no model runs on this page.",
    labelModel: "Written by a local language model (gpt-oss:20b) from the facts shown; every sentence shown passed the code checks and a second model check. A research exploration tool built on NASA PSI data.",
    labelTemplate: "Put together by team code from the facts shown; no language model wrote it. A research exploration tool built on NASA PSI data.",
    sentByCode: "This sentence was put in by team code from its fact, not written by the model.",
    sentByCodeTag: "team code",
    labelRecorded: "Recorded on {date} with the local language model (gpt-oss:20b) and replayed here; no model runs on this page. Every model sentence shown passed the code checks and a second model check when it was recorded. A research exploration tool built on NASA PSI data.",
    modeLive: "Running on this computer with the local model gpt-oss:20b. Each answer: the model reads your request twice and a rule parser once; code looks up the facts; the model writes; code checks and a second model pass check every sentence, and what fails is removed and shown. About 1 to 2 minutes per question on this computer.",
    modeNoModel: "The local model is not available ({reason}), so answers are put together by team code from the facts.",
    modeRecorded: "This public page runs no language model. It replays conversations recorded with the local model, where code checks and a second model pass checked every sentence. To ask your own questions, install the project and run ./run.sh (see the README).",
    modeNothing: "The assistant needs its local server (./run.sh). The dashboard below works without it.",
    recordedList: "Recorded conversations",
    clarify: "One question before I look this up:",
    read: "How your request was read",
    readHint: "Each value is a button. Click one to change it, and the assistant answers again.",
    assumed: "Assumed: ",
    gates: "{written} sentences written, {removed} removed by the checks, {repaired} repaired.",
    removedFold: "What the checks removed",
    factsFold: "Facts this answer rests on ({n})",
    otherFacts: "Also looked up",
    follow: "You could ask next",
    dashboard: "Show this on the dashboard below",
    panels: "Panels for this answer",
    download: "Download as CSV",
    evalFold: "How the assistant was checked",
    error: "Something went wrong on the assistant server. The dashboard below still works.",
    waiting: "Working...",
    recordedFollowNone: "This follow-up was not recorded. Run the project locally to ask it.",
    // Texts this page adds (not in the contract's table; reported to the pm session).
    modeMock: "Mock mode: every answer is a fixed test file from assistant/mock/, not an answer to your words.",
    readRecorded: "How the request was read",
    recordedNotEditable: "Recorded: not editable",
    uncertain: "The readings differed",
    traceFold: "How this answer was made",
    openSource: "Open the source",
    source: "Source: ",
    showOnDashboard: "Show on the dashboard",
    showTable: "Show the table ({n})",
    showPanels: "Show the panels of this answer",
    checkerSkipped: "Model checker: not run ({reason}), so no model sentence is shown.",
    emptyPanels: "Panels appear here with each answer: rankings, counts, tables with a download, quoted NASA sentences and file lists, each with its source.",
    apply: "Apply",
    cancel: "Cancel",
    changed: "Changed: ",
    notGiven: "not given",
    noDashboardPanel: "This part of the dashboard is not shown for this input.",
    recordedPlay: "Play",
    evalNone: "No measurement file was found.",
    // The assistant seen working, as a conversation (15 November, 18:40; web/SHELL.md, "The assistant at work").
    who: "SI assistant",
    workLive: "The figures and cards below are computed at once by rules. The assistant is now reading your request with the language model, looking up the facts, writing an answer and checking every sentence; this takes about 1 to 2 minutes on this computer.",
    workCode: "The figures and cards below are computed at once by rules. The assistant is now looking up the facts and putting its answer together with team code.",
    answered: "Answered in {n} s with {m} model call{s}.",
    answeredRecorded: "Recorded: answered in {n} s with {m} model call{s}.",
    dataFold: "Data for this answer ({n})",
    newConv: "New conversation",
    boxHint: "Ask a follow-up, for example: and for the ISS?",
    boxBusy: "The assistant is answering; the box opens again when the answer is here.",
    sendMsg: "Send",
    mockEval: "Mock file: the values are placeholders for testing the page, not measurements."
  };

  var INTENTS = ["find_investigations", "compare_environments", "question_evidence", "where_data", "modelling_data",
    "equipment_research", "earth_applications", "explain", "help", "out_of_scope"];
  var INTENT_LABEL = {
    find_investigations: "closest investigations", compare_environments: "a comparison of environments",
    question_evidence: "what the recorded tests say", where_data: "where the data are", modelling_data: "data for modelling",
    equipment_research: "research behind equipment", earth_applications: "applications on Earth", explain: "an explanation",
    help: "help", out_of_scope: "outside this tool"
  };
  var EQUIP_LABEL = {
    detection: "Smoke and gas detection", suppression: "Extinguishing agents and suppression",
    material_selection: "Material selection", ventilation: "Ventilation and flow control"
  };
  var QIDS = ["P1", "P2", "P3", "S1", "D1", "D2"];
  var STEP_ORDER = ["understand", "plan", "lookup", "write", "check", "deliver"];
  // Who answers, in the words of the health reply or of the recorded file (no model name is typed here).
  function byWords() {
    var m = S.health && S.health.model && S.health.model.name, rec = S.recorded || {};
    if (S.mode === "live") return m ? m + " · local model" : "local model";
    if (S.mode === "recorded") {
      var rm = rec.model ? String(rec.model).replace(/\s*\(.*\)\s*$/, "") : "";
      return "recorded" + (rm ? " with " + rm : "") + (S.recordedDate ? " on " + S.recordedDate : "");
    }
    if (S.mode === "mock") return "mock mode";
    return "rule-based mode";
  }
  var READER = { M1: "model reading 1", M2: "model reading 2", R: "rule parser" };
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
    "November", "December"];

  var S = {
    mode: null, reason: null, state: null, busy: false, recorded: null, recordedDate: null, vocab: null,
    turns: [], els: {}, mockPrefix: "assistant/mock/", seq: 0,
    handled: [],      // the dashboard queries this conversation already covers (no "Ask the assistant about this" for them)
    pending: null,    // an example that was put into the page's input and is being submitted
    hasList: false    // examples (or the recorded list) are loaded
  };

  // ------------------------------------------------------------------ small helpers
  function h(tag, attrs) {
    var e = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === "class") e.className = v;
        else if (k === "text") e.textContent = v;
        else if (k.slice(0, 2) === "on") e.addEventListener(k.slice(2), v);
        else e.setAttribute(k, v === true ? "" : String(v));
      });
    }
    for (var i = 2; i < arguments.length; i++) add(e, arguments[i]);
    return e;
  }
  function add(e, c) {
    if (c === null || c === undefined || c === false) return;
    if (Array.isArray(c)) { c.forEach(function (x) { add(e, x); }); return; }
    e.appendChild(typeof c === "string" || typeof c === "number" ? document.createTextNode(String(c)) : c);
  }
  var SVGNS = "http://www.w3.org/2000/svg";
  function s(tag, attrs) {
    var e = document.createElementNS(SVGNS, tag);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, String(attrs[k])); });
    for (var i = 2; i < arguments.length; i++) if (arguments[i]) e.appendChild(arguments[i]);
    return e;
  }
  function fill(t, o) { return t.replace(/\{(\w+)\}/g, function (m, k) { return o[k] === undefined ? m : String(o[k]); }); }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function isNum(v) { return typeof v === "number" && isFinite(v); }
  function norm(t) { return String(t || "").trim().toLowerCase(); }
  function answers() { return S.mode === "live" || S.mode === "no_model" || S.mode === "mock"; } // a server (or the mock) answers
  // The query the dashboard shows now: app.js writes it to the address on every run of a visitor's request.
  function currentQ() { return (new URLSearchParams(location.search).get("q") || "").trim(); }
  function fmtNum(v) { return isNum(v) ? String(Number(v.toFixed(3))) : String(v); }
  function link(href, text, cls) {
    if (!href) return h("span", { class: cls }, text);
    return h("a", { href: href, target: "_blank", rel: "noopener", class: cls }, text);
  }

  function fetchJSON(url, opts, timeout) {
    var ctl = typeof AbortController === "function" ? new AbortController() : null;
    var o = opts || {};
    if (ctl) o.signal = ctl.signal;
    var timer = timeout && ctl ? setTimeout(function () { ctl.abort(); }, timeout) : null;
    return fetch(url, o).then(function (r) {
      if (timer) clearTimeout(timer);
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    }, function (e) { if (timer) clearTimeout(timer); throw e; });
  }
  function fetchText(url) { return fetch(url).then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.text(); }); }

  function dateWords(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || "");
    return m ? (Number(m[3]) + " " + MONTHS[Number(m[2]) - 1] + " " + m[1]) : (iso || "");
  }

  // ------------------------------------------------------------------ layout (section 12.2)
  function build() {
    var main = document.querySelector("main");
    if (!main) return false;
    var root = h("section", { id: "assistant", class: "as", "aria-labelledby": "as-title" });
    var els = S.els;
    els.title = h("h2", { id: "as-title" }, L.titleIdle);
    els.sub = h("p", { class: "as-sub" }, h("span", { class: "as-how" }, L.idleHow), " ", L.sub);
    els.mode = h("div", { class: "as-mode", role: "status" });
    els.offer = h("p", { class: "as-offer", hidden: true });
    els.chat = h("div", { class: "as-chat", role: "log", "aria-live": "polite", "aria-label": "Conversation" });
    els.newConv = h("button", { type: "button", class: "as-link as-act", hidden: true,
      onclick: function () { if (!S.busy) { newConversation(); refresh(); } } }, L.newConv);
    els.head = h("div", { class: "as-head" }, els.title, els.newConv);
    // The follow-up box: part of the conversation, shown only once an answer is on screen.
    els.input = h("textarea", { id: "as-input", rows: 1, maxlength: 1000, placeholder: L.boxHint, autocomplete: "off" });
    els.send = h("button", { type: "submit", class: "as-send" }, L.sendMsg);
    els.form = h("form", { class: "as-form", autocomplete: "off", hidden: true },
      h("label", { for: "as-input", class: "as-vh" }, L.followUp), els.input, els.send);
    // One thread: the turns, then the message box with the model indicator under it at the right.
    els.grid = h("div", { class: "as-thread", hidden: true }, els.chat);
    els.byline = h("p", { class: "as-byline", hidden: true });
    els.examples = h("div", { class: "as-examples", hidden: true });
    els.evalBody = h("div", { class: "as-eval-body" });
    els.evalFold = h("details", { class: "as-eval", hidden: true }, h("summary", {}, L.evalFold), els.evalBody);
    add(root, [els.head, els.sub, els.mode, els.offer, els.examples, els.grid, els.form, els.byline, els.evalFold]);
    var ask = main.querySelector(":scope > section.ask");
    if (ask) ask.insertAdjacentElement("afterend", root); else main.appendChild(root);
    S.root = root;
    root.setAttribute("data-state", "idle");

    els.input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229) { e.preventDefault(); submitForm(); }
    });
    els.form.addEventListener("submit", function (e) { e.preventDefault(); submitForm(); });
    wireInput();
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closePopovers(); });
    return true;
  }

  function setMode(mode, reason) {
    S.mode = mode; S.reason = reason || null;
    var t = { live: L.modeLive, no_model: fill(L.modeNoModel, { reason: reason || "unknown reason" }), recorded: L.modeRecorded,
      nothing: L.modeNothing, mock: L.modeMock }[mode];
    S.els.mode.textContent = t || "";
    S.els.mode.className = "as-mode as-mode-" + mode;
    S.root.setAttribute("data-mode", mode);
    S.root.hidden = mode === "nothing"; // no server and no recording: the card is not shown
    S.els.byline.textContent = byWords();
    if (answers()) setInputWords();
    refresh();
    announceModel();
  }

  // The page shell's model indicator (web/SHELL.md, "Model indicator") names the model that answers here, or none.
  // Everything it shows comes from the health reply of the local server or from the recorded file.
  function announceModel() {
    var hl = S.health || {}, m = hl.model || {}, rec = S.recorded || {};
    var d = { mode: S.mode, reason: S.reason, model: m.name || null, maker: m.maker || null, license: m.license || null,
      digest: m.digest_ok ? (m.digest_prefix || null) : null,
      recordedModel: rec.model ? String(rec.model).replace(/\s*\(.*\)\s*$/, "") : null, recordedDate: S.recordedDate || null };
    window.feeModel = d;
    try { document.dispatchEvent(new CustomEvent("fee-model", { detail: d })); } catch (e) { /* no CustomEvent: the shell keeps its default */ }
  }

  // The local server's mode can change while the page is open (the model server stops or starts): health is read
  // again when the page comes back into view, after each answer, and once a minute while the page is in view.
  var lastHealth = 0;
  function recheckHealth() {
    if (S.mode !== "live" && S.mode !== "no_model") return;
    if (Date.now() - lastHealth < 15000) return;
    lastHealth = Date.now();
    fetchJSON("/api/health", { cache: "no-store" }, 3000).then(function (hl) {
      if (!hl || !hl.ok) return;
      S.health = hl;
      var mode = hl.mode === "live" ? "live" : "no_model";
      if (mode !== S.mode || (hl.reason || null) !== S.reason) setMode(mode, hl.reason);
      else announceModel();
    }).catch(function () { /* the server did not answer this time: the mode stays as it was */ });
  }

  // Where a server answers (live, no-model, mock), the page's one input also invites a question. On the public
  // page and without a server it keeps the dashboard's own words (index.html): only the dashboard reads it there.
  function setInputWords() {
    var lab = document.querySelector('#ask-form label[for="q"]'), q = document.getElementById("q");
    var bar = document.getElementById("shell-q"), barLab = document.querySelector('label[for="shell-q"]');
    if (lab) lab.textContent = L.inputLabel;
    if (q) q.setAttribute("placeholder", L.inputHint);
    if (barLab) barLab.textContent = L.inputLabel;
    if (bar) bar.setAttribute("placeholder", L.inputLabel);
  }

  function setBusy(b) {
    S.busy = b;
    S.els.send.disabled = b;
    S.els.send.textContent = b ? L.waiting : L.sendMsg;
    S.els.input.disabled = b;
    S.els.input.setAttribute("placeholder", b ? L.boxBusy : L.boxHint);
    // the example questions next to the page's input are outside this section
    document.querySelectorAll("#assistant .as-act, .as-qgroup .as-act").forEach(function (x) { x.disabled = b; });
    syncOffer();
  }

  // The section in step with the conversation: short before a first question, the answer and its follow-up box after.
  function refresh() {
    if (!S.root) return;
    var els = S.els, talk = S.turns.length > 0, rec = S.mode === "recorded", can = answers();
    S.root.setAttribute("data-state", talk ? "talk" : "idle");
    var shown = !!currentQ();
    els.title.textContent = rec ? L.titleRecorded : (shown && can ? L.who : L.titleIdle);
    els.sub.hidden = !can || talk || shown;
    els.mode.hidden = can && talk; // in a thread each answer names who wrote it
    els.grid.hidden = !talk;
    // the message box: with a thread, and on a page that shows a request (a conversation can start there)
    els.form.hidden = !can || !(talk || shown);
    els.byline.hidden = els.form.hidden;
    els.newConv.hidden = !can || !talk;
    els.examples.hidden = !S.hasList || (!rec && (talk || shown)); // a page that shows a request keeps the card short
    syncOffer();
  }

  // A request shown on the dashboard that this conversation does not cover (a shared link, an example
  // environment, a comparison button): one button, never a model turn nobody asked for.
  function syncOffer() {
    var box = S.els.offer;
    if (!box) return;
    var q = currentQ();
    if (!answers() || !q || S.handled.indexOf(norm(q)) >= 0) { box.hidden = true; return; }
    // While a turn runs, a new request on the dashboard is shown with the button off and one line saying why.
    if (box.hidden || box.getAttribute("data-q") !== q || box.getAttribute("data-busy") !== String(S.busy)) {
      box.setAttribute("data-q", q);
      box.setAttribute("data-busy", String(S.busy));
      box.replaceChildren(h("span", { class: "as-offer-q" }, q), h("button", { type: "button", class: "as-btn as-btn-primary as-act",
        disabled: S.busy, onclick: function () { if (!S.busy) { newConversation(); ask({ message: q }, q, { dashQ: q }); } } }, L.offer));
      if (S.busy) box.appendChild(h("span", { class: "as-small as-offer-wait" }, L.offerBusy));
    }
    box.hidden = false;
  }

  function newConversation() {
    S.turns.forEach(stopWork);
    S.state = null; S.turns = []; S.handled = [];
    S.els.chat.replaceChildren();
    S.els.input.value = "";
  }

  // ------------------------------------------------------------------ the page's one input
  // A turn starts on a real submit of #ask-form (the large input, or the app bar's, which submits the same form).
  // The example environments, a tab, the back button and a page opened with ?q= do not submit the form, so they
  // start no turn; the dashboard's query they show is offered as a button (syncOffer).
  function wireInput() {
    var form = document.getElementById("ask-form"), q = document.getElementById("q");
    if (form && q) {
      form.addEventListener("submit", function () {
        if (S.driving) return; // this section's own drive of the dashboard (driveDashboard)
        var text = (q.value || "").trim();
        if (text) fromInput(text);
      });
    }
    var cond = document.getElementById("conditions"); // app.js fills it again on every run
    var soon = function () { setTimeout(refresh, 0); };
    if (cond && typeof MutationObserver === "function") new MutationObserver(soon).observe(cond, { childList: true });
    window.addEventListener("popstate", soon);
  }

  function fromInput(text) {
    var ex = S.pending && S.pending.text === text ? S.pending : null;
    S.pending = null;
    if (S.busy) return; // the turn in progress finishes first; the new request is then offered as a button
    if (S.mode === "recorded") { // no model on this page: a recorded question shows its recording, anything else the dashboard only
      var rec = findRecorded(text);
      if (!rec) return;
      newConversation(); S.handled.push(norm(text));
      setBusy(true);
      playRecordedTurn(rec, text).then(function () { setBusy(false); }, function () { setBusy(false); });
      return;
    }
    if (!answers()) return;
    newConversation();
    if (ex && ex.request) ask({ request: ex.request, answer_mode: ex.answer_mode }, text, { dashQ: text });
    else ask({ message: text, answer_mode: ex ? ex.answer_mode : null }, text, { dashQ: text });
  }

  // An example question: its text goes into the page's input, which is submitted (the dashboard and this section).
  function askExample(x) {
    if (S.busy) return;
    var text = x.message || x.label;
    S.pending = { text: text, request: x.request || null, answer_mode: x.answer_mode || null };
    var go = function () {
      var input = document.getElementById("q"), form = document.getElementById("ask-form");
      if (!input || !form || !dashboardReady()) { fromInput(text); return; }
      input.value = text;
      if (typeof form.requestSubmit === "function") form.requestSubmit();
      else form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
    };
    whenReady(go, 0, go);
  }

  // ------------------------------------------------------------------ modes (section 12.7)
  function init() {
    if (!build()) return;
    var p = new URLSearchParams(location.search);
    var am = p.get("assistant");
    if (am === "mock") {
      setMode("mock");
      loadExamples(S.mockPrefix + "examples.json");
      loadEval(S.mockPrefix + "eval.json");
      return;
    }
    if (am === "recorded-mock") { startRecorded(S.mockPrefix + "recorded.json", S.mockPrefix + "eval.json"); return; }
    var local = location.hostname === "127.0.0.1" || location.hostname === "localhost";
    if (!local) { startRecorded("assistant/recorded.json", "assistant/eval.json"); return; }
    fetchJSON("/api/health", { cache: "no-store" }, 1500).then(function (hl) {
      if (!hl || !hl.ok) throw new Error("health");
      S.health = hl; lastHealth = Date.now();
      setMode(hl.mode === "live" ? "live" : "no_model", hl.reason);
      document.addEventListener("visibilitychange", function () { if (!document.hidden) recheckHealth(); });
      setInterval(function () { if (!document.hidden && !S.busy) recheckHealth(); }, 60000);
      loadExamples("/api/examples");
      loadEval("assistant/eval.json");
    }).catch(function () { startRecorded("assistant/recorded.json", "assistant/eval.json"); });
  }

  function startRecorded(url, evalUrl) {
    fetchJSON(url, { cache: "no-cache" }).then(function (rec) {
      if (!rec || !Array.isArray(rec.conversations) || !rec.conversations.length) throw new Error("empty");
      S.recorded = rec;
      S.recordedDate = dateWords(rec.recorded_at);
      setMode("recorded");
      renderRecordedList();
      loadEval(evalUrl);
    }).catch(function () { setMode("nothing"); loadEval(evalUrl); });
  }

  function loadExamples(url) {
    fetchJSON(url, { cache: "no-store" }).then(function (d) {
      var ex = (d && d.examples) || [];
      if (!ex.length) return;
      var buttons = function (cls) {
        return ex.map(function (x) {
          return h("button", { type: "button", class: cls + " as-act", onclick: function () { askExample(x); } }, x.message || x.label);
        });
      };
      var box = S.els.examples;
      box.replaceChildren(h("h3", { class: "as-h" }, L.questions), h("div", { class: "as-btns" }, buttons("as-btn")));
      // With the page shell, the same questions also sit next to the page's own examples, as one set
      // ("Environments", "Questions"); the shell shows that group on the start page and this one after it.
      var host = document.querySelector("#ask-form .ask-examples");
      if (host && document.documentElement.classList.contains("shell-on") && !host.querySelector(".as-qgroup")) {
        // Page design v2: at most three questions as text links; the others open under "More examples".
        var qb = buttons("ex-q");
        var qlist = h("div", { class: "ex-list ex-links", role: "group", "aria-labelledby": "as-qlabel" }, qb.slice(0, 3));
        if (qb.length > 3) qlist.appendChild(h("details", { class: "more ex-more" }, h("summary", {}, "More examples"),
          h("div", { class: "ex-list ex-links" }, qb.slice(3))));
        host.appendChild(h("div", { class: "ex-group as-qgroup" }, h("span", { class: "ex-label", id: "as-qlabel" }, L.questions), qlist));
        box.classList.add("as-twin");
      }
      S.hasList = true;
      refresh();
    }).catch(function () { /* no examples: the input still works */ });
  }

  function renderRecordedList() {
    var box = S.els.examples;
    box.replaceChildren(h("h3", { class: "as-h" }, L.recordedList),
      h("p", { class: "as-small as-recmark" }, fill(L.recordedMark, { date: S.recordedDate || "" })),
      h("div", { class: "as-btns" }, S.recorded.conversations.map(function (c) {
        return h("button", { type: "button", class: "as-btn as-act", onclick: function () { playConversation(c); } },
          c.title || c.id);
      })));
    S.hasList = true;
    refresh();
  }

  // ------------------------------------------------------------------ sending a turn
  // The follow-up box: the same conversation goes on (the carried state).
  function submitForm() {
    var msg = (S.els.input.value || "").trim();
    if (!msg || S.busy) return;
    S.els.input.value = "";
    if (S.mode === "recorded") { // not shown in this mode; a recorded question still plays its recording
      var rec = findRecorded(msg);
      if (rec) { setBusy(true); playRecordedTurn(rec).then(function () { setBusy(false); }, function () { setBusy(false); }); }
      return;
    }
    if (!answers()) return;
    ask({ message: msg }, msg);
  }

  // opts.dashQ: the request the dashboard shows when the turn starts. The answer drives the dashboard to its own
  // request only while the dashboard still shows that one (a visitor who moved on is not pulled back).
  function ask(body, shownText, opts) {
    if (S.busy) return;
    var turn = newTurn(shownText);
    turn.dashQ = opts && opts.dashQ !== undefined ? opts.dashQ : currentQ();
    turn.fromInput = !!(opts && opts.dashQ !== undefined); // the dashboard already shows the visitor's own text
    S.handled.push(norm(turn.dashQ));
    if (!opts || opts.dashQ === undefined) showTurn(turn); // asked from inside the conversation
    setBusy(true);
    if (S.mode === "live") readingStatus("checking");
    var payload = {
      message: body.message || null, request: body.request || null, state: S.state,
      answer_mode: body.answer_mode || null
    };
    if (payload.request) payload.message = null;
    var p = S.mode === "mock" ? mockAnswer(payload, turn) : liveAnswer(payload, turn);
    p.then(function (resp) {
      renderResponse(turn, resp, { streamed: turn.streamed });
    }).catch(function (e) {
      renderError(turn, e && e.response);
      if (S.mode === "live") readingStatus("rule");
    }).then(function () { setBusy(false); recheckHealth(); });
  }

  // ---- Page design v2, "Model-checked reading" (web/SHELL.md). With the local model connected, the dashboard is
  // brought to the reading the assistant agreed on (resp.dashboard.q, which arrives with the answer), and the request
  // header of the page says whether that reading is the one the rule parser showed at once or a corrected one.
  function readingStatus(st, detail) {
    var sh = window.feeShell;
    if (sh && typeof sh.setReading === "function") sh.setReading(st, (S.health && S.health.model && S.health.model.name) || null, detail || null);
  }
  // a reading chip without its origin words ("(you)", "(from the preset)"): the check compares what was read
  function chipText(li) {
    var src = li.querySelector(".src"), t = li.textContent;
    if (src) t = t.replace(src.textContent, "");
    return t.replace(/\s+/g, " ").trim();
  }
  function chipTexts() { return Array.prototype.map.call(document.querySelectorAll("#conditions li"), chipText); }
  function checkReading(turn, dq) {
    // only while the dashboard still shows what it showed when the turn began (or already shows the agreed request)
    var cur = norm(currentQ());
    if (cur !== norm(turn.dashQ) && cur !== norm(dq)) { S.handled.push(norm(dq)); readingStatus("rule"); return; }
    var before = chipTexts();
    var compare = function () {
      var after = chipTexts();
      var changed = after.filter(function (t) { return before.indexOf(t) < 0; });
      var gone = before.filter(function (t) { return after.indexOf(t) < 0; });
      if (!changed.length && !gone.length) { readingStatus("checked"); return; }
      readingStatus("corrected", "Changed by the check: " + changed.concat(gone.map(function (t) { return "no longer read: " + t; })).join("; "));
      Array.prototype.forEach.call(document.querySelectorAll("#conditions li"), function (li) {
        if (changed.indexOf(chipText(li)) < 0) return;
        li.classList.add("is-changed");
        setTimeout(function () { li.classList.remove("is-changed"); }, 6000);
      });
    };
    S.handled.push(norm(dq));
    if (cur === norm(dq)) { compare(); return; }
    driveDashboard(dq, null, false);
    setTimeout(compare, 900); // after app.js has rendered the new reading
  }

  function liveAnswer(payload, turn) {
    var opts = { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) };
    return fetch("/api/answer?stream=1", opts).then(function (r) {
      if (!r.ok) return r.json().catch(function () { return {}; }).then(function (j) {
        var err = new Error("HTTP " + r.status); err.response = j; throw err;
      });
      if (!r.body || !r.body.getReader) return r.text().then(function (t) { return readEvents(t.split("\n"), turn); });
      return readStream(r.body.getReader(), turn);
    });
  }

  function readStream(reader, turn) {
    var dec = new TextDecoder(), buf = "", result = null, failure = null;
    function handle(line) {
      if (!line.trim()) return;
      var ev; try { ev = JSON.parse(line); } catch (e) { return; }
      if (ev.event === "step") { turn.streamed = true; onStepEvent(turn, ev); }
      else if (ev.event === "result") result = ev.response;
      else if (ev.event === "error") failure = ev;
    }
    function pump() {
      return reader.read().then(function (x) {
        if (x.done) { handle(buf); buf = ""; return; }
        buf += dec.decode(x.value, { stream: true });
        var lines = buf.split("\n"); buf = lines.pop();
        lines.forEach(handle);
        return pump();
      });
    }
    return pump().then(function () {
      if (result) return result;
      var err = new Error((failure && failure.message) || "no result"); err.response = failure; throw err;
    });
  }
  function readEvents(lines, turn) {
    var result = null;
    lines.forEach(function (line) {
      if (!line.trim()) return;
      var ev; try { ev = JSON.parse(line); } catch (e) { return; }
      if (ev.event === "step") { turn.streamed = true; onStepEvent(turn, ev); }
      if (ev.event === "result") result = ev.response;
    });
    if (!result) throw new Error("no result");
    return result;
  }

  // Mock (section 12.8): fixed files; streaming simulated at 300 ms per line.
  function mockFile(payload) {
    if (payload.message) {
      var m = payload.message.toLowerCase().trim();
      if (m.indexOf("no model") >= 0) return "answer_no_model.json";
      if (m.indexOf("safe") >= 0) return "answer_verdict.json";
      if (m === "rover") return "answer_clarify.json";
      if (m.indexOf("raw") >= 0) return "answer_no_model.json";
      return "answer_lunar_cotton.json";
    }
    var r = payload.request || {};
    if (r.intent === "where_data") return "answer_no_model.json";
    if (r.asks_verdict) return "answer_verdict.json";
    return "answer_lunar_cotton.json";
  }
  function mockAnswer(payload, turn) {
    var file = mockFile(payload);
    if (file === "answer_lunar_cotton.json") {
      return fetchText(S.mockPrefix + "stream_lunar_cotton.ndjson").then(function (t) {
        var lines = t.split("\n").filter(function (x) { return x.trim(); });
        var result = null, chain = Promise.resolve();
        lines.forEach(function (line) {
          chain = chain.then(function () { return sleep(300); }).then(function () {
            var ev = JSON.parse(line);
            if (ev.event === "step") { turn.streamed = true; onStepEvent(turn, ev); }
            if (ev.event === "result") result = ev.response;
          });
        });
        return chain.then(function () { return result; });
      });
    }
    return fetchJSON(S.mockPrefix + file).then(function (resp) {
      var chain = Promise.resolve();
      ((resp.trace && resp.trace.steps) || []).forEach(function (st) {
        chain = chain.then(function () { onStepEvent(turn, { step: st.step, status: "start", label: st.label }); return sleep(300); })
          .then(function () { onStepEvent(turn, { step: st.step, status: "done", summary: st.summary, ms: st.ms, model_calls: st.model_calls }); });
      });
      return chain.then(function () { turn.streamed = true; return resp; });
    });
  }

  // ------------------------------------------------------------------ recorded mode
  function playConversation(c) {
    if (S.busy) return;
    newConversation();
    setBusy(true);
    var chain = Promise.resolve();
    (c.turns || []).forEach(function (t, i) {
      chain = chain.then(function () { return i ? sleep(500) : null; }).then(function () { return playRecordedTurn(t); });
    });
    chain.then(function () { setBusy(false); }, function () { setBusy(false); });
  }

  function playRecordedTurn(t, dashQ) {
    var resp = t.response;
    var turn = newTurn(t.message || (resp && resp.request && resp.request.english) || "");
    turn.dashQ = dashQ !== undefined ? dashQ : currentQ();
    turn.fromInput = dashQ !== undefined;
    if (dashQ === undefined && S.turns.length === 1) showTurn(turn); // opened from the list
    // A recording is shown at once, with its steps as they were recorded: no step runs on this page.
    renderResponse(turn, resp, { streamed: false });
    return Promise.resolve();
  }

  function findRecorded(text) {
    var want = (text || "").trim().toLowerCase();
    var hit = null;
    (S.recorded ? S.recorded.conversations : []).forEach(function (c) {
      (c.turns || []).forEach(function (t) { if (!hit && (t.message || "").trim().toLowerCase() === want) hit = t; });
    });
    return hit;
  }

  // ------------------------------------------------------------------ one turn in the chat (section 12.3)
  function newTurn(text) {
    var chat = S.els.chat;
    var idx = S.turns.length;
    var running = S.mode !== "recorded";
    var steps = h("ol", { class: "as-steps", "aria-label": "Steps" });
    var body = h("div", { class: "as-body" });
    // While the turn runs: who answers, the seconds, the steps, one sentence that sets the rules' figures apart
    // from the assistant's work, and three grey lines where the answer will stand.
    var clock = h("span", { class: "as-clock", role: "timer" }, running ? "0 s" : "");
    var who = h("div", { class: "as-who" }, h("span", { class: "as-avatar", "aria-hidden": "true" }), h("b", {}, L.who),
      h("span", { class: "as-by" }, byWords()), clock);
    var wait = running ? h("p", { class: "as-wait" }, S.mode === "live" ? L.workLive : L.workCode) : null;
    var skel = running ? h("div", { class: "as-skel", "aria-hidden": "true" }, h("span"), h("span"), h("span")) : null;
    var user = h("div", { class: "as-user" }, h("span", { class: "as-vh" }, "You: "), text);
    var first = h("p", { class: "as-firstline" });
    var el = h("article", { class: "as-turn" + (running ? " as-working" : ""), "data-turn": idx }, user, first, who, steps, wait, skel, body);
    // The latest answer is shown in full; the earlier turns fold to their question and the answer's first line.
    S.turns.forEach(function (t) { foldTurn(t, true); });
    chat.appendChild(el);
    var turn = { el: el, user: user, first: first, steps: steps, clock: clock, skel: skel, body: body, idx: idx, streamed: false,
      stepEls: {}, resp: null, wait: wait, dashQ: "", t0: Date.now(), timer: null };
    STEP_ORDER.forEach(function (k) { stepEl(turn, k, null); });
    if (running) turn.timer = setInterval(function () { clock.textContent = Math.round((Date.now() - turn.t0) / 1000) + " s"; }, 1000);
    var toggle = function () { if (el.classList.contains("as-old")) foldTurn(turn, !el.classList.contains("as-folded")); };
    user.addEventListener("click", toggle);
    first.addEventListener("click", toggle);
    user.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } });
    S.turns.push(turn);
    refresh();
    scrollChatTo(el);
    return turn;
  }

  // The turn is over (an answer or an error): the clock stops, the sentence and the grey lines give way.
  function stopWork(turn) {
    if (turn.timer) { clearInterval(turn.timer); turn.timer = null; }
    if (turn.wait) { turn.wait.remove(); turn.wait = null; }
    if (turn.skel) { turn.skel.remove(); turn.skel = null; }
    turn.clock.textContent = "";
    turn.el.classList.remove("as-working");
    Object.keys(turn.stepEls).forEach(function (k) { turn.stepEls[k].classList.remove("as-run"); });
  }

  function foldTurn(turn, fold) {
    turn.el.classList.add("as-old");
    turn.el.classList.toggle("as-folded", fold);
    turn.user.setAttribute("role", "button");
    turn.user.setAttribute("tabindex", "0");
    turn.user.setAttribute("aria-expanded", String(!fold));
  }

  // A turn that starts outside the window (after a follow-up, or a recording opened from the list) is brought into view.
  function showTurn(turn) {
    var bar = document.getElementById("appbar");
    var top = (bar ? bar.offsetHeight : 0) + 16, r = turn.el.getBoundingClientRect();
    if (r.top < top || r.top > window.innerHeight * 0.6) window.scrollBy(0, r.top - top);
  }

  function scrollChatTo(el) {
    var chat = S.els.chat;
    if (chat.scrollHeight > chat.clientHeight + 4) chat.scrollTop = el.offsetTop - chat.offsetTop - 8;
  }

  // The steps are one row of labelled steps: waiting (a ring), running (blue, moving), done (a check mark and the
  // one-line summary the stream gives).
  function stepEl(turn, key, label) {
    var li = turn.stepEls[key];
    if (!li) {
      li = h("li", { class: "as-step as-todo", "data-step": key },
        h("span", { class: "as-mark", "aria-hidden": "true" }),
        h("span", { class: "as-step-label" }, label || STEP_LABELS[key] || key),
        h("span", { class: "as-step-sum" }, ""));
      turn.stepEls[key] = li;
      turn.steps.appendChild(li);
    } else if (label) li.querySelector(".as-step-label").textContent = label;
    return li;
  }

  function onStepEvent(turn, ev) {
    var li = stepEl(turn, ev.step, ev.label);
    var sum = li.querySelector(".as-step-sum");
    if (ev.status === "start") {
      li.className = "as-step as-run";
      sum.textContent = "";
    } else {
      li.className = "as-step as-done";
      var meta = [];
      if (isNum(ev.ms) && ev.step !== "deliver") meta.push(ev.ms >= 1000 ? (Number((ev.ms / 1000).toFixed(1)) + " s") : (ev.ms + " ms"));
      sum.replaceChildren(document.createTextNode(ev.summary || ""));
      if (ev.summary) li.setAttribute("title", ev.summary);
      if (meta.length) sum.appendChild(h("span", { class: "as-ms" }, " " + meta.join(", ")));
    }
    scrollChatTo(turn.el);
  }

  function renderError(turn, j) {
    stopWork(turn);
    add(turn.body, h("p", { class: "as-notice as-notice-error", role: "alert" }, L.error));
    if (j && j.trace) add(turn.body, traceFold(j.trace));
  }

  function renderResponse(turn, resp, opt) {
    turn.resp = resp;
    var measured = Date.now() - turn.t0;
    stopWork(turn);
    if (!resp || typeof resp !== "object") { renderError(turn, null); return; }
    if (!opt.streamed) {
      ((resp.trace && resp.trace.steps) || []).forEach(function (st) {
        onStepEvent(turn, { step: st.step, status: "start", label: st.label });
        onStepEvent(turn, { step: st.step, status: "done", summary: st.summary, ms: st.ms, model_calls: st.model_calls });
      });
    }
    var b = turn.body;
    if (resp.kind === "error") { renderError(turn, resp); return; }
    if (resp.state) S.state = resp.state;
    var recorded = S.mode === "recorded";
    var facts = resp.facts || [];
    var byId = {};
    facts.forEach(function (f) { byId[f.id] = f; });

    if (resp.request) add(b, readChips(resp, recorded));
    (resp.notices || []).forEach(function (n) {
      add(b, h("p", { class: "as-notice", "data-id": n.id }, n.text));
    });
    if (resp.kind === "clarify" && resp.clarify) add(b, clarifyBlock(resp, recorded));

    var nums = {}, order = [];
    var ans = resp.answer;
    turn.first.textContent = (ans && ans.sentences && ans.sentences[0] && ans.sentences[0].text) ||
      (resp.clarify && resp.clarify.question) || ((resp.notices || [])[0] || {}).text || "";
    if (ans && ans.sentences && ans.sentences.length) {
      ans.sentences.forEach(function (st) {
        (st.facts || []).forEach(function (id) { if (!(id in nums) && byId[id]) { order.push(id); nums[id] = order.length; } });
      });
      var pop = h("div", { class: "as-pop", hidden: true, role: "region", "aria-label": "Source of this sentence" });
      var box = h("div", { class: "as-answer " + (ans.origin === "model" ? "as-by-model" : "as-by-code") });
      var para = h("p", {});
      ans.sentences.forEach(function (st, i) {
        if (i) para.appendChild(document.createTextNode(" "));
        // In a model answer, a sentence that team code put in (the lead fact) is marked and titled as such.
        var byCode = ans.origin === "model" && st.origin === "template";
        var span = h("span", { class: "as-sent" + (st.status === "repaired" ? " as-repaired" : "") + (byCode ? " as-sent-code" : ""),
          title: byCode ? L.sentByCode : null }, st.text);
        para.appendChild(span);
        if (byCode) para.appendChild(h("span", { class: "as-code-tag", title: L.sentByCode }, L.sentByCodeTag));
        (st.facts || []).forEach(function (id) {
          var f = byId[id]; if (!f) return;
          para.appendChild(citeButton(f, nums[id], pop));
        });
      });
      add(box, [para, pop]);
      add(b, box);
      // Disclosure line under every answer.
      var lab = h("p", { class: "as-label" }, answerLabel(resp));
      add(b, lab);
      var gr = resp.trace && resp.trace.gate_report;
      if (ans.origin === "model" && gr) {
        add(b, h("p", { class: "as-gates" }, fill(L.gates, { written: gr.written, removed: gr.removed, repaired: gr.repaired })));
      }
      if (ans.removed && ans.removed.length) {
        add(b, h("details", { class: "as-fold as-removed" }, h("summary", {}, L.removedFold),
          h("ul", {}, ans.removed.map(function (r) {
            return h("li", {}, h("s", {}, r.text), " ", h("span", { class: "as-why" }, "removed by " + r.by + ": " + r.reason));
          }))));
      }
    }
    if (facts.length) add(b, factsFold(facts, order, nums));
    // The tool panels of this answer: a fold of the turn, not a second column.
    if ((resp.panels || []).length) {
      add(b, h("details", { class: "as-fold as-data" }, h("summary", {}, fill(L.dataFold, { n: resp.panels.length })),
        h("div", { class: "as-panel-list" }, resp.panels.map(function (p) { return panelView(p, byId, resp); }))));
    }
    if (resp.trace) add(b, traceFold(resp.trace));
    var tr = resp.trace || {}, ms = isNum(tr.total_ms) ? tr.total_ms : (recorded ? null : measured);
    if (ms !== null && isNum(tr.model_calls)) {
      add(b, h("p", { class: "as-answered" }, fill(recorded ? L.answeredRecorded : L.answered,
        { n: ms >= 10000 ? Math.round(ms / 1000) : (ms < 1000 ? "less than 1" : Number((ms / 1000).toFixed(1))), m: tr.model_calls, s: tr.model_calls === 1 ? "" : "s" })));
    }

    var dq = resp.dashboard && resp.dashboard.q;
    var row = h("p", { class: "as-row" });
    if (dq) {
      add(row, h("button", { type: "button", class: "as-btn as-btn-ghost", onclick: function () {
        driveDashboard(dq, resp.dashboard.section, true);
      } }, L.dashboard));
    }
    if (row.childNodes.length) add(b, row);
    // The follow-up suggestions come last in the turn, right above the follow-up box.
    var fu = resp.followups || [];
    if (fu.length) {
      add(b, h("div", { class: "as-follow" }, h("h4", { class: "as-h4" }, L.follow), h("div", { class: "as-btns" },
        fu.map(function (f) {
          return h("button", { type: "button", class: "as-btn as-act", onclick: function () { followUp(f, turn); } }, f.text);
        }))));
    }
    if (dq) {
      // A turn asked from the page's input leaves the dashboard (and the input) on the visitor's own words; the
      // button above offers the answer's request. A follow-up or a recording opened from the list drives the
      // dashboard as before, unless the visitor has moved the dashboard on since.
      if (S.mode === "live" && resp.kind !== "clarify") checkReading(turn, dq); // page design v2: the model-checked reading
      else if (!turn.fromInput && norm(currentQ()) === norm(turn.dashQ)) { S.handled.push(norm(dq)); driveDashboard(dq, null, false); }
      else if (turn.fromInput) S.handled.push(norm(dq));
    } else if (S.mode === "live" && resp.kind !== "clarify") readingStatus("rule");
    if (S.mode === "live" && resp.kind === "clarify") readingStatus("question");
    refresh();
    scrollChatTo(turn.el);
  }

  function answerLabel(resp) {
    var origin = resp.answer && resp.answer.origin;
    if (S.mode === "recorded") return origin === "model" ? fill(L.labelRecorded, { date: S.recordedDate || "" }) : L.labelTemplate;
    if (resp.label) return resp.label;
    return origin === "model" ? L.labelModel : L.labelTemplate;
  }

  function citeButton(f, n, pop) {
    var tip = (f.context ? f.context + ": " : "") + f.text;
    var btn = h("button", { type: "button", class: "as-cite", "aria-expanded": "false", title: tip,
      "aria-label": "Source " + n + ": " + tip }, String(n));
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      pop.parentNode.querySelectorAll(".as-cite[aria-expanded=true]").forEach(function (x) { x.setAttribute("aria-expanded", "false"); });
      if (open) { pop.hidden = true; return; }
      btn.setAttribute("aria-expanded", "true");
      pop.replaceChildren(factView(f, n, true));
      pop.hidden = false;
    });
    return btn;
  }

  function closePopovers() {
    if (!S.root) return;
    S.root.querySelectorAll(".as-pop").forEach(function (p) { p.hidden = true; });
    S.root.querySelectorAll(".as-cite[aria-expanded=true]").forEach(function (x) { x.setAttribute("aria-expanded", "false"); });
  }

  function sourceWords(f) {
    var src = f.source || {};
    var t = src.file || "";
    if (src.line) t += ", line " + src.line;
    else if (src.key) t += " (" + src.key + ")";
    return t;
  }

  function factView(f, n, withLink) {
    var txt = h(f.quote ? "q" : "span", { class: "as-fact-text" }, f.text);
    return h("div", { class: "as-fact" + (f.limit ? " as-fact-limit" : "") },
      n ? h("span", { class: "as-fact-n" }, "[" + n + "]") : null,
      f.context ? h("span", { class: "as-ctx" }, f.context + ". ") : null, txt,
      h("span", { class: "as-src" }, " ", L.source, link(f.link, sourceWords(f) || L.openSource)),
      withLink && f.link ? h("span", { class: "as-open" }, " ", link(f.link, L.openSource + " ↗")) : null);
  }

  function factsFold(facts, order, nums) {
    var cited = order.map(function (id) { return facts.filter(function (f) { return f.id === id; })[0]; }).filter(Boolean);
    var others = facts.filter(function (f) { return !(f.id in nums); });
    var d = h("details", { class: "as-fold as-facts" }, h("summary", {}, fill(L.factsFold, { n: cited.length })));
    if (cited.length) add(d, h("ol", { class: "as-fact-list" }, cited.map(function (f) { return h("li", {}, factView(f, nums[f.id])); })));
    if (others.length) {
      add(d, h("h5", { class: "as-h5" }, L.otherFacts));
      add(d, h("ul", { class: "as-fact-list" }, others.map(function (f) { return h("li", {}, factView(f, null)); })));
    }
    return d;
  }

  // "How this answer was made": the trace of the turn.
  function traceFold(tr) {
    var d = h("details", { class: "as-fold as-trace" }, h("summary", {}, L.traceFold));
    var ol = h("ol", { class: "as-trace-steps" });
    (tr.steps || []).forEach(function (st) {
      var li = h("li", {}, h("b", {}, st.label || STEP_LABELS[st.step] || st.step), " ", st.summary,
        h("span", { class: "as-ms" }, " (" + st.ms + " ms, " + st.model_calls + " model call" + (st.model_calls === 1 ? "" : "s") + ")"));
      var det = st.detail;
      if (det && typeof det === "object") add(li, traceDetail(st.step, det));
      ol.appendChild(li);
    });
    add(d, ol);
    var total = [];
    if (isNum(tr.model_calls)) total.push("Model calls: " + tr.model_calls + " (at most 4 per turn)");
    if (isNum(tr.total_ms)) total.push("time: " + Number((tr.total_ms / 1000).toFixed(1)) + " s");
    if (tr.cache) total.push("cache: " + tr.cache);
    if (tr.data_version) total.push("data version: " + tr.data_version);
    if (tr.commit) total.push("commit: " + tr.commit);
    add(d, h("p", { class: "as-small" }, total.join("; ") + "."));
    if (tr.gate_report) add(d, kv("Gate report", tr.gate_report));
    return d;
  }

  function traceDetail(step, det) {
    var out = h("div", { class: "as-detail" });
    if (det.readings) {
      add(out, h("p", {}, "Readers: " + det.readings.map(function (r) {
        return (READER[r.reader] || r.reader) + (r.valid ? "" : " (invalid, dropped)") + (isNum(r.ms) ? " " + r.ms + " ms" : "");
      }).join("; ") + "."));
    }
    if (det.agreement) {
      add(out, h("p", {}, "Agreement by field: " + Object.keys(det.agreement).map(function (k) { return k + " " + det.agreement[k]; }).join("; ") + "."));
    }
    if (det.removed_ungrounded && det.removed_ungrounded.length) {
      add(out, h("p", {}, "Left out because the message does not state them: " + det.removed_ungrounded.map(function (r) { return r.field + " " + r.value; }).join("; ") + "."));
    }
    if (det.tools && step === "plan") {
      add(out, h("ul", {}, det.tools.map(function (t) { return h("li", {}, h("code", {}, t.tool), " " + JSON.stringify(t.args || {}) + (t.why ? " (" + t.why + ")" : "")); })));
    }
    if (det.tools && step === "lookup") {
      add(out, h("ul", {}, det.tools.map(function (t) { return h("li", {}, h("code", {}, t.tool), " " + t.facts + " facts, " + t.panels + " panels, " + t.ms + " ms"); })));
    }
    if (det.dashboard_mismatch && det.dashboard_mismatch.length) add(out, h("p", {}, "Dashboard read-back differs: " + JSON.stringify(det.dashboard_mismatch)));
    if (det.gate_failures) {
      add(out, h("p", {}, det.gate_failures.length ? "Gate failures: " + det.gate_failures.map(function (g) {
        return "sentence " + g.n + ", " + g.gate + ": " + g.reason;
      }).join("; ") + "." : "No gate failure."));
      if ("repair" in det) add(out, h("p", {}, det.repair ? "One repair call was made with the failures as feedback." : "No repair call."));
      if (det.checker && det.checker.skipped) add(out, h("p", {}, fill(L.checkerSkipped, { reason: det.checker.skipped })));
      else if (det.checker) add(out, h("p", {}, "Model checker: " + det.checker.yes + " supported, " + det.checker.no + " not supported."));
    }
    return out.childNodes.length ? out : null;
  }

  function kv(title, o) {
    return h("p", { class: "as-small" }, title + ": " + Object.keys(o).map(function (k) {
      var v = o[k]; return k + " " + (v !== null && typeof v === "object" ? JSON.stringify(v) : String(v));
    }).join("; ") + ".");
  }

  // ------------------------------------------------------------------ chips (section 12.4)
  function chipList(req) {
    var env = req.environment || {}, item = req.item || {}, unknown = req.unknown || [];
    var envNeeded = unknown.some(function (u) { return u.indexOf("environment") === 0; }) ||
      (req.clarify && String(req.clarify.field).indexOf("environment") === 0);
    var c = [];
    c.push({ key: "intent", path: "intent", text: "Looking for: " + (INTENT_LABEL[req.intent] || req.intent) });
    if (env.label || env.preset || envNeeded) c.push({ key: "environment", path: "environment.preset", text: "Environment: " + (env.label || env.preset || L.notGiven) });
    if (isNum(env.o2_pct)) c.push({ key: "o2", path: "environment.o2_pct", text: "Oxygen: " + fmtNum(env.o2_pct) + "%" });
    if (isNum(env.pressure_kpa)) c.push({ key: "pressure", path: "environment.pressure_kpa", text: "Pressure: " + fmtNum(env.pressure_kpa) + " kPa" });
    if (item.label || item.material) c.push({ key: "material", path: "item.material", text: "Material: " + (item.label || item.material) });
    if ((req.questions || []).length) c.push({ key: "questions", path: "questions", text: "Questions: " + req.questions.join(", ") });
    if (req.equipment) c.push({ key: "equipment", path: "equipment", text: "Equipment: " + (EQUIP_LABEL[req.equipment] || req.equipment) });
    if ((req.investigations || []).length) c.push({ key: "investigations", path: "investigations", text: "Investigations: " + req.investigations.join(", ") });
    return c;
  }

  function readChips(resp, recorded) {
    var req = resp.request;
    var wrap = h("div", { class: "as-read" + (recorded ? "" : " as-read-live") }, h("h4", { class: "as-h4" }, recorded ? L.readRecorded : L.read));
    // the values can be changed: say so in words, next to the title (15 November: the feature was not seen at once)
    if (!recorded) wrap.appendChild(h("p", { class: "as-read-hint" }, L.readHint));
    var editor = h("div", { class: "as-editor", hidden: true });
    var list = h("div", { class: "as-chips", role: "group", "aria-label": L.readRecorded });
    chipList(req).forEach(function (c) {
      var ag = (req.agreement || {})[c.path];
      var src = (req.sources || {})[c.path];
      var unc = ag === "conflict";
      var editable = !recorded && c.key !== "investigations";
      var cls = "as-chip" + (unc ? " as-chip-uncertain" : "") + (src === "preset" || src === "assumed" || src === "default" ? " as-chip-assumed" : "");
      var title = recorded ? L.recordedNotEditable : (unc ? L.uncertain : (src ? "From: " + src : null));
      // "Material: cotton" as a label and a value, so that the value reads as the thing to change
      var cut = c.text.indexOf(": ");
      var inner = cut > 0 ? [h("span", { class: "as-chip-k" }, c.text.slice(0, cut + 2)), h("b", { class: "as-chip-v" }, c.text.slice(cut + 2))] : c.text;
      var chip = h("button", { type: "button", class: cls + (editable ? " as-act as-chip-edit" : ""), title: title || (editable ? "Click to change" : null),
        "aria-expanded": editable ? "false" : null, disabled: editable ? null : true }, inner);
      if (editable) chip.addEventListener("click", function () { openEditor(c, req, editor, chip, list); });
      list.appendChild(chip);
    });
    add(wrap, [list, editor]);
    var asm = req.assumptions || [];
    if (asm.length) add(wrap, h("ul", { class: "as-assume" }, asm.map(function (a) { return h("li", {}, L.assumed + a.text); })));
    return wrap;
  }

  function loadVocab() {
    if (S.vocab) return Promise.resolve(S.vocab);
    var opt = function (u) { return fetchJSON(u).catch(function () { return null; }); };
    return Promise.all([opt("data/scenario_spec.json"), opt("data/scoring_config.json"), opt("data/needs.json")]).then(function (r) {
      var envs = [], seen = {};
      ((r[0] && r[0].scenarios) || []).forEach(function (x) { if (!seen[x.id]) { seen[x.id] = 1; envs.push({ id: x.id, label: x.label }); } });
      var pres = (r[1] && r[1].presets) || {};
      Object.keys(pres).forEach(function (k) { if (!seen[k]) { seen[k] = 1; envs.push({ id: k, label: pres[k].label_en || k }); } });
      var mats = [], ms = {};
      (((r[1] && r[1].keywords) || {}).materials || []).forEach(function (m) {
        var id = m.fuel_material || (m.fuel_class ? "class:" + m.fuel_class : (m.fuel_phase ? "phase:" + m.fuel_phase : null));
        if (!id || ms[id]) return;
        ms[id] = 1;
        var word = (m.keys || []).filter(function (k) { return /^[\x20-\x7e]+$/.test(k); })[0] || id;
        mats.push({ id: id, label: word.trim() });
      });
      var needs = {};
      (((r[2] && r[2].needs) || [])).forEach(function (n) { needs[n.id] = n.name; });
      S.vocab = { envs: envs, mats: mats, needs: needs };
      return S.vocab;
    });
  }

  function openEditor(c, req, editor, chip, list) {
    if (S.busy) return;
    var wasOpen = chip.getAttribute("aria-expanded") === "true";
    list.querySelectorAll("[aria-expanded=true]").forEach(function (x) { x.setAttribute("aria-expanded", "false"); });
    if (wasOpen) { editor.hidden = true; return; }
    chip.setAttribute("aria-expanded", "true");
    loadVocab().then(function (v) {
      var field, get;
      var id = "as-ed-" + (++S.seq);
      var env = req.environment || {};
      if (c.key === "intent") {
        field = select(id, INTENTS.map(function (k) { return { id: k, label: INTENT_LABEL[k] }; }), req.intent);
        get = function () { return { path: "intent", value: field.value, words: "Looking for: " + INTENT_LABEL[field.value] }; };
      } else if (c.key === "environment") {
        field = select(id, v.envs, env.preset);
        get = function () { var o = field.options[field.selectedIndex]; return { path: "environment.preset", value: field.value, words: "Environment: " + o.text }; };
      } else if (c.key === "o2" || c.key === "pressure") {
        var cur = c.key === "o2" ? env.o2_pct : env.pressure_kpa;
        field = h("input", { id: id, type: "number", step: "0.1", min: "0", max: c.key === "o2" ? "100" : null, value: isNum(cur) ? cur : "", inputmode: "decimal" });
        get = function () {
          var x = parseFloat(field.value); if (!isFinite(x)) return null;
          return c.key === "o2" ? { path: "environment.o2_pct", value: x, words: "Oxygen: " + x + "%" }
            : { path: "environment.pressure_kpa", value: x, words: "Pressure: " + x + " kPa" };
        };
      } else if (c.key === "material") {
        field = select(id, v.mats, (req.item || {}).material);
        get = function () { var o = field.options[field.selectedIndex]; return { path: "item.material", value: field.value, words: "Material: " + o.text }; };
      } else if (c.key === "equipment") {
        field = select(id, Object.keys(EQUIP_LABEL).map(function (k) { return { id: k, label: EQUIP_LABEL[k] }; }), req.equipment);
        get = function () { return { path: "equipment", value: field.value, words: "Equipment: " + EQUIP_LABEL[field.value] }; };
      } else if (c.key === "questions") {
        var have = req.questions || [];
        field = h("fieldset", { class: "as-checks", id: id }, h("legend", { class: "as-vh" }, "Questions"), QIDS.map(function (q) {
          return h("label", {}, h("input", { type: "checkbox", value: q, checked: have.indexOf(q) >= 0 }), " " + q + (v.needs[q] ? " " + v.needs[q] : ""));
        }));
        get = function () {
          var qs = Array.prototype.slice.call(field.querySelectorAll("input:checked")).map(function (x) { return x.value; });
          return qs.length ? { path: "questions", value: qs, words: "Questions: " + qs.join(", ") } : null;
        };
      } else return;
      var apply = h("button", { type: "button", class: "as-btn as-act" }, L.apply);
      var cancel = h("button", { type: "button", class: "as-btn as-btn-ghost" }, L.cancel);
      apply.addEventListener("click", function () {
        var g = get(); if (!g) { field.focus(); return; }
        editor.hidden = true; chip.setAttribute("aria-expanded", "false");
        ask({ request: patchRequest(req, g.path, g.value) }, L.changed + g.words);
      });
      cancel.addEventListener("click", function () { editor.hidden = true; chip.setAttribute("aria-expanded", "false"); chip.focus(); });
      editor.replaceChildren(h("label", { for: id, class: "as-vh" }, c.text), field, apply, cancel);
      editor.hidden = false;
      field.focus();
    });
  }

  function select(id, opts, cur) {
    var sel = h("select", { id: id });
    opts.forEach(function (o) { sel.appendChild(h("option", { value: o.id, selected: o.id === cur }, o.label)); });
    return sel;
  }

  // A chip edit or a clarify option: the field is set, its source becomes "chip", and the values that code
  // derives from it are cleared so that the server builds them again (section 4.5).
  function patchRequest(req, path, value) {
    var r = clone(req);
    r.sources = r.sources || {}; r.agreement = r.agreement || {};
    var parts = path.split(".");
    var o = r;
    for (var i = 0; i < parts.length - 1; i++) { o[parts[i]] = o[parts[i]] || {}; o = o[parts[i]]; }
    o[parts[parts.length - 1]] = value;
    if (path === "environment.preset") {
      ["label", "o2_pct", "pressure_kpa", "gravity", "flow", "scenario_id", "cell"].forEach(function (k) {
        r.environment[k] = null; delete r.sources["environment." + k]; delete r.agreement["environment." + k];
      });
    }
    if (path === "environment.o2_pct" || path === "environment.pressure_kpa") { r.environment.cell = null; }
    if (path === "item.material") { r.item.label = null; r.item.query_word = null; r.item.fuel_phase = null; }
    r.sources[path] = "chip"; r.agreement[path] = "chip";
    r.clarify = null;
    r.unknown = (r.unknown || []).filter(function (u) { return u !== path && path.indexOf(u) !== 0; });
    r.assumptions = (r.assumptions || []).filter(function (a) { return a.field !== path; });
    return r;
  }

  function applyPatch(req, patch) {
    var r = clone(req);
    var paths = [];
    (function walk(o, pre) {
      Object.keys(o).forEach(function (k) {
        var v = o[k], p = pre ? pre + "." + k : k;
        if (v && typeof v === "object" && !Array.isArray(v)) walk(v, p); else paths.push([p, v]);
      });
    })(patch, "");
    paths.forEach(function (pv) { r = patchRequest(r, pv[0], pv[1]); });
    return r;
  }

  function clarifyBlock(resp, recorded) {
    var cl = resp.clarify;
    return h("div", { class: "as-clarify" }, h("p", { class: "as-h4" }, L.clarify), h("p", { class: "as-q" }, cl.question),
      h("div", { class: "as-btns" }, (cl.options || []).map(function (o) {
        return h("button", { type: "button", class: "as-btn" + (recorded ? "" : " as-act"), disabled: recorded ? true : null,
          title: recorded ? L.recordedNotEditable : null, onclick: function () {
            if (!o.patch) { S.els.input.focus(); return; }
            ask({ request: applyPatch(resp.request, o.patch) }, o.label);
          } }, o.label);
      })));
  }

  function followUp(f, turn) {
    if (S.busy) return;
    if (S.mode === "recorded") {
      var rec = findRecorded(f.text);
      if (rec) { setBusy(true); playRecordedTurn(rec).then(function () { setBusy(false); }); }
      else add(turn.body, h("p", { class: "as-notice as-notice-info" }, L.recordedFollowNone));
      return;
    }
    if (f.request) ask({ request: f.request }, f.text); else ask({ message: f.text }, f.text);
  }

  // ------------------------------------------------------------------ driving the dashboard (section 12.6)
  function dashboardReady() { var r = document.getElementById("read"); return !!(r && !r.hidden); }
  function whenReady(fn, tries, giveUp) {
    if (dashboardReady()) { fn(); return; }
    if ((tries || 0) > 100) { if (giveUp) giveUp(); return; }
    setTimeout(function () { whenReady(fn, (tries || 0) + 1, giveUp); }, 150);
  }
  function driveDashboard(q, section, scroll) {
    whenReady(function () {
      var input = document.getElementById("q"), form = document.getElementById("ask-form");
      if (!input || !form) return;
      if (q && input.value !== q) {
        input.value = q;
        // S.driving: this submit starts no turn here. data-quiet: the page shell keeps the visitor's tab and
        // scroll position when the dashboard follows an answer (web/shell.js, newQuery).
        S.driving = true;
        if (!scroll) form.setAttribute("data-quiet", "");
        try {
          if (typeof form.requestSubmit === "function") form.requestSubmit();
          else form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
        } finally { S.driving = false; form.removeAttribute("data-quiet"); }
      }
      if (scroll) scrollToSection(section || "#top");
    });
  }
  function scrollToSection(sel, tries) {
    var el = document.querySelector(sel);
    if (el && !el.hidden) {
      // with the page shell the section can be under another tab: the shell opens that tab and scrolls there
      if (window.feeShell && typeof window.feeShell.reveal === "function" && window.feeShell.reveal(el)) return;
      el.scrollIntoView({ behavior: "smooth", block: "start" }); return;
    }
    if ((tries || 0) < 15) { setTimeout(function () { scrollToSection(sel, (tries || 0) + 1); }, 120); return; }
    var top = document.querySelector("#top");
    if (top && !top.hidden) top.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // ------------------------------------------------------------------ panels
  function colOf(p, names) {
    var cs = p.columns || [];
    for (var i = 0; i < names.length; i++) {
      var n = names[i].toLowerCase();
      for (var j = 0; j < cs.length; j++) if (cs[j].key.toLowerCase() === n || cs[j].label.toLowerCase() === n) return cs[j];
    }
    return null;
  }
  function cellText(v) {
    if (v === null || v === undefined) return "";
    if (Array.isArray(v)) return v.join("; ");
    if (typeof v === "object") return v.text || v.href || "";
    return isNum(v) ? fmtNum(v) : String(v);
  }
  function cellNode(v) {
    if (v && typeof v === "object" && !Array.isArray(v)) return link(v.href, v.text || v.href);
    if (Array.isArray(v)) return v.length ? h("ul", { class: "as-cell-list" }, v.map(function (x) { return h("li", {}, cellText(x)); })) : "";
    return cellText(v);
  }

  function panelView(p, facts, resp) {
    var sec = h("section", { class: "as-panel as-panel-" + p.type, "aria-label": p.title });
    add(sec, h("h4", { class: "as-panel-title" }, p.title));
    var vis = null, tableFirst = false;
    if (p.type === "ranking") vis = rankingVis(p);
    else if (p.type === "counts") vis = countsVis(p);
    else if (p.type === "range") vis = rangeVis(p);
    else if (p.type === "piles") vis = pilesVis(p);
    else if (p.type === "quotes") vis = quotesVis(p);
    else if (p.type === "criteria") vis = criteriaVis(p);
    else if (p.type === "card") vis = cardVis(p);
    else tableFirst = true;
    if (vis) add(sec, vis);
    var rows = p.rows || [];
    if (rows.length) {
      if (tableFirst) add(sec, tableView(p));
      else if (p.type !== "card") add(sec, h("details", { class: "as-fold as-table-fold" }, h("summary", {}, fill(L.showTable, { n: rows.length + (rows.length === 1 ? " row" : " rows") })), tableView(p)));
    }
    if (p.note) add(sec, h("p", { class: "as-note" }, p.note));
    var files = {}, fl = [];
    (p.fact_ids || []).forEach(function (id) {
      var f = facts[id]; if (!f || !f.source || !f.source.file) return;
      if (!files[f.source.file]) { files[f.source.file] = 1; fl.push(f); }
    });
    if (fl.length) {
      var srcLine = h("p", { class: "as-src-line" }, L.source);
      fl.forEach(function (f, i) {
        if (i) srcLine.appendChild(document.createTextNode(", "));
        srcLine.appendChild(link(f.link ? f.link.replace(/\?plain=1#L\d+$/, "") : null, f.source.file));
      });
      add(sec, srcLine);
    }
    var acts = h("div", { class: "as-panel-acts" });
    if (p.download && rows.length) {
      add(acts, h("button", { type: "button", class: "as-btn as-btn-ghost", onclick: function () { downloadCSV(p); } },
        L.download + " (" + rows.length + (p.download.total_rows > rows.length ? " of " + p.download.total_rows : "") + " rows)"));
    }
    if (p.dashboard_section) {
      add(acts, h("button", { type: "button", class: "as-btn as-btn-ghost", onclick: function () {
        driveDashboard((resp.dashboard && resp.dashboard.q) || "", p.dashboard_section, true);
      } }, L.showOnDashboard));
    }
    if (acts.childNodes.length) add(sec, acts);
    return sec;
  }

  function tableView(p) {
    var cols = p.columns || [];
    var t = h("table", { class: "as-table" },
      h("thead", {}, h("tr", {}, cols.map(function (c) { return h("th", { scope: "col", class: c.kind === "number" ? "as-num" : null }, c.label); }))),
      h("tbody", {}, (p.rows || []).map(function (r) {
        return h("tr", {}, cols.map(function (c) { return h("td", { class: c.kind === "number" ? "as-num" : null }, cellNode(r[c.key])); }));
      })));
    return h("div", { class: "as-scroll", tabindex: "0", role: "region", "aria-label": p.title }, t);
  }

  function downloadCSV(p) {
    var cols = p.columns || [];
    var esc = function (v) { var x = cellText(v); return /[",\n\r]/.test(x) ? '"' + x.replace(/"/g, '""') + '"' : x; };
    var lines = [cols.map(function (c) { return esc(c.label); }).join(",")];
    (p.rows || []).forEach(function (r) { lines.push(cols.map(function (c) { return esc(r[c.key]); }).join(",")); });
    var blob = new Blob(["﻿" + lines.join("\r\n") + "\r\n"], { type: "text/csv;charset=utf-8" });
    var a = h("a", { href: URL.createObjectURL(blob), download: (p.download && p.download.filename) || "table.csv" });
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  // A bar of width fraction w (0 to 1) in an SVG that scales to its box.
  function barSvg(parts, label) {
    var svg = s("svg", { viewBox: "0 0 100 10", preserveAspectRatio: "none", class: "as-bar", role: "img", "aria-label": label });
    svg.appendChild(s("rect", { x: 0, y: 0, width: 100, height: 10, class: "as-bar-bg" }));
    var x = 0;
    parts.forEach(function (pt) {
      var w = Math.max(0, Math.min(100 - x, pt.w * 100));
      if (w > 0) svg.appendChild(s("rect", { x: x, y: 0, width: w, height: 10, class: pt.cls }));
      x += w;
    });
    return svg;
  }

  function rankingVis(p) {
    var sc = colOf(p, ["score", "team score (0 to 100)"]), inv = colOf(p, ["investigation"]), acc = colOf(p, ["accession"]);
    var conf = colOf(p, ["configuration"]);
    if (!sc) return null;
    return h("ol", { class: "as-bars" }, (p.rows || []).map(function (r) {
      var v = r[sc.key];
      return h("li", {},
        h("div", { class: "as-bar-head" }, h("b", {}, cellText(inv ? r[inv.key] : "") + (acc ? " (" + cellText(r[acc.key]) + ")" : "")),
          h("span", { class: "as-bar-val" }, isNum(v) ? fmtNum(v) + " / 100" : "")),
        isNum(v) ? barSvg([{ w: v / 100, cls: "as-fill-blue" }], sc.label + " " + fmtNum(v)) : null,
        conf && r[conf.key] ? h("div", { class: "as-bar-sub" }, cellText(r[conf.key])) : null);
    }));
  }

  function countsVis(p) {
    var q = colOf(p, ["question"]), nm = colOf(p, ["name"]), n = colOf(p, ["counted"]), a = colOf(p, ["both_inside", "both inside"]);
    var o = colOf(p, ["oxygen_only", "oxygen only"]), pr = colOf(p, ["pressure_only", "pressure only"]), e = colOf(p, ["elsewhere"]);
    if (!n || !a) return null;
    var legend = h("p", { class: "as-legend" },
      h("span", { class: "as-key as-fill-blue" }), a.label + " ",
      o ? [h("span", { class: "as-key as-fill-blue2" }), o.label + " "] : null,
      pr ? [h("span", { class: "as-key as-fill-blue3" }), pr.label + " "] : null,
      e ? [h("span", { class: "as-key as-fill-grey" }), e.label] : null);
    var list = h("ol", { class: "as-bars" }, (p.rows || []).map(function (r) {
      var tot = r[n.key];
      var head = h("div", { class: "as-bar-head" }, h("b", {}, cellText(q ? r[q.key] : "") + (nm ? " " + cellText(r[nm.key]) : "")),
        h("span", { class: "as-bar-val" }, isNum(tot) ? n.label + " " + tot : ""));
      if (!isNum(tot) || tot <= 0) return h("li", {}, head, barSvg([], n.label + " 0"));
      var parts = [{ w: (r[a.key] || 0) / tot, cls: "as-fill-blue" }];
      if (o) parts.push({ w: (r[o.key] || 0) / tot, cls: "as-fill-blue2" });
      if (pr) parts.push({ w: (r[pr.key] || 0) / tot, cls: "as-fill-blue3" });
      if (e) parts.push({ w: (r[e.key] || 0) / tot, cls: "as-fill-grey" });
      var words = [a.label + " " + cellText(r[a.key])];
      if (o) words.push(o.label + " " + cellText(r[o.key]));
      if (pr) words.push(pr.label + " " + cellText(r[pr.key]));
      if (e) words.push(e.label + " " + cellText(r[e.key]));
      return h("li", {}, head, barSvg(parts, words.join(", ")), h("div", { class: "as-bar-sub" }, words.join(" · ")));
    }));
    return h("div", {}, legend, list);
  }

  function spanOf(v) {
    var m = /(-?\d+(?:\.\d+)?)\D+?(-?\d+(?:\.\d+)?)/.exec(String(v || ""));
    return m ? [parseFloat(m[1]), parseFloat(m[2])] : null;
  }
  function rangeVis(p) {
    var ph = colOf(p, ["phase", "fuel phase"]);
    var dims = [
      { span: colOf(p, ["o2_span", "oxygen span (%)"]), you: colOf(p, ["your_o2", "your oxygen"]), rec: colOf(p, ["o2_recorded", "oxygen recorded"]), unit: "%", name: "Oxygen" },
      { span: colOf(p, ["p_span", "pressure span (kpa)"]), you: colOf(p, ["your_p", "your pressure"]), rec: colOf(p, ["p_recorded", "pressure recorded"]), unit: " kPa", name: "Pressure" }
    ];
    var tests = colOf(p, ["tests"]);
    var out = h("div", { class: "as-ranges" });
    (p.rows || []).forEach(function (r) {
      add(out, h("p", { class: "as-range-head" }, h("b", {}, cellText(ph ? r[ph.key] : "")), tests ? " (" + tests.label + " " + cellText(r[tests.key]) + ")" : ""));
      dims.forEach(function (d) {
        if (!d.span) return;
        var sp = spanOf(r[d.span.key]), you = d.you ? r[d.you.key] : null;
        var rec = d.rec ? d.rec.label + " " + cellText(r[d.rec.key]) : "";
        if (!sp) {
          add(out, h("p", { class: "as-range-none" }, d.name + ": " + rec + (isNum(you) ? "; " + d.you.label + " " + fmtNum(you) + d.unit : "") + "."));
          return;
        }
        var hi = Math.max(sp[1], isNum(you) ? you : 0); var top = hi * 1.15 || 1;
        var svg = s("svg", { viewBox: "0 0 100 16", preserveAspectRatio: "none", class: "as-range", role: "img",
          "aria-label": d.span.label + " " + cellText(r[d.span.key]) + (isNum(you) ? ", " + d.you.label + " " + fmtNum(you) : "") });
        svg.appendChild(s("rect", { x: 0, y: 6, width: 100, height: 4, class: "as-bar-bg" }));
        svg.appendChild(s("rect", { x: sp[0] / top * 100, y: 3, width: Math.max(0.8, (sp[1] - sp[0]) / top * 100), height: 10, class: "as-fill-blue" }));
        if (isNum(you)) svg.appendChild(s("rect", { x: Math.min(99.2, you / top * 100), y: 0, width: 0.8, height: 16, class: "as-fill-amber" }));
        add(out, h("div", { class: "as-range-row" },
          h("div", { class: "as-bar-head" }, h("span", {}, d.name + " recorded: " + cellText(r[d.span.key]) + d.unit),
            isNum(you) ? h("span", { class: "as-you" }, d.you.label + " " + fmtNum(you) + d.unit) : null),
          svg, h("div", { class: "as-bar-sub" }, rec)));
      });
    });
    return out;
  }

  function pilesVis(p) {
    var q = colOf(p, ["question"]), bar = colOf(p, ["bar"]);
    var lists = (p.columns || []).filter(function (c) { return c.kind === "list"; });
    return h("div", { class: "as-piles" }, (p.rows || []).map(function (r) {
      return h("div", { class: "as-pile" }, h("h5", { class: "as-h5" }, cellText(q ? r[q.key] : "")),
        bar ? h("p", { class: "as-small" }, cellText(r[bar.key])) : null,
        h("div", { class: "as-pile-cols" }, lists.map(function (c) {
          var v = r[c.key] || [];
          return h("div", { class: "as-pile-col" }, h("p", { class: "as-pile-h" }, c.label + " (" + v.length + ")"), cellNode(v));
        })));
    }));
  }

  function quotesVis(p) {
    var sen = colOf(p, ["sentence", "text"]), inv = colOf(p, ["investigation"]), fld = colOf(p, ["field"]);
    var rec = colOf(p, ["record"]), doi = colOf(p, ["doi", "dataset doi"]);
    if (!sen) return null;
    return h("div", { class: "as-quotes" }, (p.rows || []).map(function (r) {
      var d = doi ? cellText(r[doi.key]) : "";
      return h("figure", { class: "as-quote" }, h("blockquote", {}, cellText(r[sen.key])),
        h("figcaption", {}, cellText(inv ? r[inv.key] : ""), fld ? ", " + cellText(r[fld.key]) : "",
          rec && r[rec.key] ? [" · ", cellNode(r[rec.key])] : null,
          d ? [" · ", link("https://doi.org/" + d.replace(/^https?:\/\/doi\.org\//, ""), "DOI " + d.replace(/^https?:\/\/doi\.org\//, ""))] : null));
    }));
  }

  function criteriaVis(p) {
    var tx = colOf(p, ["text"]), doc = colOf(p, ["document"]), sec = colOf(p, ["section"]), lk = colOf(p, ["link"]);
    if (!tx) return null;
    return h("div", { class: "as-quotes" }, (p.rows || []).map(function (r) {
      return h("figure", { class: "as-quote" }, h("blockquote", {}, cellText(r[tx.key])),
        h("figcaption", {}, cellText(doc ? r[doc.key] : ""), sec ? ", " + cellText(r[sec.key]) : "",
          lk && r[lk.key] ? [" · ", cellNode(r[lk.key])] : null));
    }));
  }

  function cardVis(p) {
    var nm = colOf(p, ["name"]), vl = colOf(p, ["value"]);
    if (!nm || !vl) return tableView(p);
    return h("dl", { class: "as-card" }, (p.rows || []).map(function (r) {
      return h("div", {}, h("dt", {}, cellText(r[nm.key])), h("dd", {}, cellNode(r[vl.key])));
    }));
  }

  // ------------------------------------------------------------------ evaluation fold (section 12.7, point 4)
  function metric(m, key) {
    var v = m[key];
    if (v === undefined || v === null) return "";
    if (isNum(v)) return fmtNum(v);
    if (typeof v === "object") {
      if (isNum(v.correct) && isNum(v.required)) return v.correct + " of " + v.required;
      var k = ["overall", "rate", "mean", "value", "count"].filter(function (x) { return isNum(v[x]); })[0];
      return k ? fmtNum(v[k]) : "";
    }
    return String(v);
  }
  function loadEval(url) {
    // A built page lists the measurement file in data/build.json only when the build has it: no request for a file
    // that is not there (it showed as an error in the console). The mock files are always present.
    var listed = url.indexOf(S.mockPrefix) === 0 ? Promise.resolve(true) :
      fetchJSON("data/build.json", { cache: "no-cache" }).then(function (bj) {
        return !bj || !Array.isArray(bj.optional) || bj.optional.indexOf("assistant/eval.json") >= 0;
      }, function () { return false; });
    listed.then(function (ok) {
      if (!ok) throw new Error("not in this build");
      return fetchJSON(url, { cache: "no-cache" });
    }).then(function (ev) {
      if (!ev || !ev.arms) throw new Error("no arms");
      var cols = [["reading_accuracy", "reading accuracy"], ["citation_valid", "sentences with a valid citation"],
        ["numbers_unsupported", "numbers not in the cited facts"], ["forbidden_wording", "forbidden wording"],
        ["refusals_correct", "correct refusals"], ["fallback_rate", "fallbacks"], ["seconds_per_turn", "seconds per turn"],
        ["model_calls_per_turn", "model calls per turn"]];
      var t = h("table", { class: "as-table" },
        h("thead", {}, h("tr", {}, h("th", { scope: "col" }, "arm"), cols.map(function (c) { return h("th", { scope: "col", class: "as-num" }, c[1]); }))),
        h("tbody", {}, Object.keys(ev.arms).map(function (a) {
          var m = ev.arms[a].metrics || {};
          return h("tr", {}, h("th", { scope: "row" }, a.replace(/_/g, " ")), cols.map(function (c) { return h("td", { class: "as-num" }, metric(m, c[0])); }));
        })));
      var b = S.els.evalBody;
      b.replaceChildren();
      if (ev.mock) add(b, h("p", { class: "as-notice" }, L.mockEval));
      add(b, h("div", { class: "as-scroll", tabindex: "0", role: "region", "aria-label": L.evalFold }, t));
      var when = [];
      if (ev.n_questions) when.push(ev.n_questions + " questions");
      if (ev.model) when.push("model " + ev.model);
      if (ev.started_at) when.push("run of " + dateWords(ev.started_at));
      if (when.length) add(b, h("p", { class: "as-small" }, when.join("; ") + "."));
      if (ev.summary_text) add(b, h("p", {}, ev.summary_text));
      if (Array.isArray(ev.limits) && ev.limits.length) add(b, h("ul", { class: "as-small" }, ev.limits.map(function (x) { return h("li", {}, x); })));
      S.els.evalFold.hidden = false;
    }).catch(function () { S.els.evalFold.hidden = true; });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
