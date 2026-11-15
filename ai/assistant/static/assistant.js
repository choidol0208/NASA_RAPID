/* AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon. */
/* The chat assistant on top of the Fire Evidence Explorer dashboard (contract: ai/assistant/DESIGN.md, section 12).
   Plain JavaScript, one IIFE, no framework, no request to another site. Every number, sentence and source shown
   here comes from the response of the local assistant server, from a recorded response file, or from a mock file;
   this script computes no fact. */
(function () {
  "use strict";

  // ------------------------------------------------------------------ fixed texts (section 12.5, word for word)
  var L = {
    title: "Ask the assistant",
    sub: "Ask in your own words, in any language. Answers are in English, built only from the team's files, with a source for every sentence.",
    placeholder: "e.g. Which NASA tests are closest to a cotton fabric fire in a lunar habitat?",
    inputLabel: "Your question",
    send: "Ask",
    examples: "Try one of these",
    labelModel: "Written by a local language model (gpt-oss:20b) from the facts shown, and checked by code. A research exploration tool, not safety guidance.",
    labelTemplate: "Put together by team code from the facts shown; no language model wrote it. A research exploration tool, not safety guidance.",
    sentByCode: "This sentence was put in by team code from its fact, not written by the model.",
    labelRecorded: "Recorded on {date} with the local language model (gpt-oss:20b) and replayed here; no model runs on this page. A research exploration tool, not safety guidance.",
    modeLive: "Running on this computer with the local model gpt-oss:20b.",
    modeNoModel: "The local model is not available ({reason}), so answers are put together by team code from the facts.",
    modeRecorded: "This public page runs no language model. It replays conversations recorded with the local model. To ask your own questions, install the project and run ./run.sh (see the README).",
    modeNothing: "The assistant needs its local server (./run.sh). The dashboard below works without it.",
    recordedList: "Recorded conversations",
    clarify: "One question before I look this up:",
    read: "How your request was read (click to change)",
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
    emptyChat: "Ask a question below, or try one of the examples.",
    emptyPanels: "Panels appear here with each answer: rankings, counts, tables with a download, quoted NASA sentences and file lists, each with its source.",
    apply: "Apply",
    cancel: "Cancel",
    changed: "Changed: ",
    notGiven: "not given",
    noDashboardPanel: "This part of the dashboard is not shown for this input.",
    typedToDashboard: "No language model runs on this page, so your words went to the dashboard's own rule-based search below. To ask the assistant, install the project and run ./run.sh (see the README).",
    recordedPlay: "Play",
    evalNone: "No measurement file was found.",
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
  var READER = { M1: "model reading 1", M2: "model reading 2", R: "rule parser" };
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
    "November", "December"];

  var S = {
    mode: null, reason: null, state: null, busy: false, recorded: null, recordedDate: null, vocab: null,
    turns: [], els: {}, mockPrefix: "assistant/mock/", seq: 0
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
  function fmtNum(v) { return isNum(v) ? String(Number(v.toFixed(3))) : String(v); }
  function link(href, text, cls) {
    if (!href) return h("span", { class: cls }, text);
    return h("a", { href: href, target: "_blank", rel: "noopener", class: cls }, text);
  }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } return null; }

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
    els.mode = h("div", { class: "as-mode", role: "status" });
    els.chat = h("div", { class: "as-chat", role: "log", "aria-live": "polite", "aria-label": "Conversation" },
      h("p", { class: "as-empty" }, L.emptyChat));
    els.panelList = h("div", { class: "as-panel-list" }, h("p", { class: "as-empty" }, L.emptyPanels));
    els.panels = h("aside", { class: "as-panels", "aria-label": L.panels }, h("h3", { class: "as-h" }, L.panels), els.panelList);
    els.input = h("textarea", { id: "as-input", rows: 2, maxlength: 1000, placeholder: L.placeholder, autocomplete: "off" });
    els.send = h("button", { type: "submit", class: "as-send" }, L.send);
    els.form = h("form", { class: "as-form", autocomplete: "off" },
      h("label", { for: "as-input", class: "as-vh" }, L.inputLabel), els.input, els.send);
    els.examples = h("div", { class: "as-examples", hidden: true });
    els.evalBody = h("div", { class: "as-eval-body" });
    els.evalFold = h("details", { class: "as-eval", hidden: true }, h("summary", {}, L.evalFold), els.evalBody);
    add(root, [h("h2", { id: "as-title" }, L.title), h("p", { class: "as-sub" }, L.sub), els.mode,
      h("div", { class: "as-grid" }, els.chat, els.panels), els.form, els.examples, els.evalFold]);
    var ask = main.querySelector(":scope > section.ask");
    if (ask) ask.insertAdjacentElement("afterend", root); else main.appendChild(root);
    S.root = root;

    var draft = store("as-draft");
    if (draft) els.input.value = draft;
    els.input.addEventListener("input", function () { store("as-draft", els.input.value || null); });
    els.input.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229) { e.preventDefault(); submitForm(); }
    });
    els.form.addEventListener("submit", function (e) { e.preventDefault(); submitForm(); });
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
  }

  function setBusy(b) {
    S.busy = b;
    S.els.send.disabled = b;
    S.els.send.textContent = b ? L.waiting : L.send;
    S.root.querySelectorAll(".as-act").forEach(function (x) { x.disabled = b; });
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
      setMode(hl.mode === "live" ? "live" : "no_model", hl.reason);
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
      var box = S.els.examples;
      box.replaceChildren(h("h3", { class: "as-h" }, L.examples), h("div", { class: "as-btns" }, ex.map(function (x) {
        return h("button", { type: "button", class: "as-btn as-act", title: x.message || null, onclick: function () {
          if (S.busy) return;
          if (x.request) ask({ request: x.request, answer_mode: x.answer_mode || null }, x.label || x.message);
          else ask({ message: x.message, answer_mode: x.answer_mode || null }, x.message);
        } }, x.label || x.message);
      })));
      box.hidden = false;
    }).catch(function () { /* no examples: the input still works */ });
  }

  function renderRecordedList() {
    var box = S.els.examples;
    box.replaceChildren(h("h3", { class: "as-h" }, L.recordedList), h("div", { class: "as-btns" },
      S.recorded.conversations.map(function (c) {
        return h("button", { type: "button", class: "as-btn as-act", onclick: function () { playConversation(c); } },
          c.title || c.id);
      })));
    box.hidden = false;
  }

  // ------------------------------------------------------------------ sending a turn
  function submitForm() {
    var msg = (S.els.input.value || "").trim();
    if (!msg || S.busy) return;
    S.els.input.value = "";
    store("as-draft", null);
    if (S.mode === "recorded" || S.mode === "nothing") { typedWithoutServer(msg); return; }
    ask({ message: msg }, msg);
  }

  function ask(body, shownText) {
    if (S.busy) return;
    var turn = newTurn(shownText);
    setBusy(true);
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
    }).then(function () { setBusy(false); });
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
    setBusy(true);
    S.state = null;
    var chain = Promise.resolve();
    (c.turns || []).forEach(function (t, i) {
      chain = chain.then(function () { return i ? sleep(500) : null; }).then(function () { return playRecordedTurn(t); });
    });
    chain.then(function () { setBusy(false); }, function () { setBusy(false); });
  }

  function playRecordedTurn(t) {
    var resp = t.response;
    var turn = newTurn(t.message || (resp && resp.request && resp.request.english) || "");
    var chain = Promise.resolve();
    ((resp.trace && resp.trace.steps) || []).forEach(function (st) {
      var wait = Math.min(600, Math.max(60, Math.round((st.ms || 0) / 10)));
      chain = chain.then(function () { onStepEvent(turn, { step: st.step, status: "start", label: st.label }); return sleep(wait); })
        .then(function () { onStepEvent(turn, { step: st.step, status: "done", summary: st.summary, ms: st.ms, model_calls: st.model_calls }); });
    });
    return chain.then(function () { turn.streamed = true; renderResponse(turn, resp, { streamed: true }); });
  }

  function findRecorded(text) {
    var want = (text || "").trim().toLowerCase();
    var hit = null;
    (S.recorded ? S.recorded.conversations : []).forEach(function (c) {
      (c.turns || []).forEach(function (t) { if (!hit && (t.message || "").trim().toLowerCase() === want) hit = t; });
    });
    return hit;
  }

  function typedWithoutServer(msg) {
    var rec = S.mode === "recorded" ? findRecorded(msg) : null;
    if (rec) { setBusy(true); playRecordedTurn(rec).then(function () { setBusy(false); }); return; }
    var turn = newTurn(msg);
    add(turn.body, h("p", { class: "as-notice as-notice-info" }, L.typedToDashboard));
    add(turn.body, h("p", { class: "as-row" }, h("button", { type: "button", class: "as-btn", onclick: function () {
      driveDashboard(msg, "#top", true);
    } }, L.dashboard)));
    driveDashboard(msg, null, false);
  }

  // ------------------------------------------------------------------ one turn in the chat (section 12.3)
  function newTurn(text) {
    var chat = S.els.chat;
    var empty = chat.querySelector(".as-empty");
    if (empty) empty.remove();
    var idx = S.turns.length;
    var steps = h("ol", { class: "as-steps", "aria-label": "Steps" });
    var body = h("div", { class: "as-body" });
    var el = h("article", { class: "as-turn", "data-turn": idx },
      h("div", { class: "as-user" }, h("span", { class: "as-vh" }, "You: "), text), steps, body);
    chat.appendChild(el);
    var turn = { el: el, steps: steps, body: body, idx: idx, streamed: false, stepEls: {}, resp: null };
    S.turns.push(turn);
    scrollChatTo(el);
    return turn;
  }

  function scrollChatTo(el) {
    var chat = S.els.chat;
    if (chat.scrollHeight > chat.clientHeight + 4) chat.scrollTop = el.offsetTop - chat.offsetTop - 8;
  }

  function onStepEvent(turn, ev) {
    var li = turn.stepEls[ev.step];
    if (!li) {
      li = h("li", { class: "as-step as-run", "data-step": ev.step },
        h("span", { class: "as-dot", "aria-hidden": "true" }),
        h("span", { class: "as-step-label" }, ev.label || ev.step),
        h("span", { class: "as-step-sum" }, ""));
      turn.stepEls[ev.step] = li;
      turn.steps.appendChild(li);
    }
    if (ev.status === "start") {
      li.className = "as-step as-run";
      li.querySelector(".as-step-sum").textContent = "...";
    } else {
      li.className = "as-step as-done";
      var meta = [];
      if (isNum(ev.ms) && ev.step !== "deliver") meta.push(ev.ms >= 1000 ? (Number((ev.ms / 1000).toFixed(1)) + " s") : (ev.ms + " ms"));
      var sum = li.querySelector(".as-step-sum");
      sum.replaceChildren(document.createTextNode(ev.summary || ""));
      if (meta.length) sum.appendChild(h("span", { class: "as-ms" }, " " + meta.join(", ")));
    }
    scrollChatTo(turn.el);
  }

  function renderError(turn, j) {
    Object.keys(turn.stepEls).forEach(function (k) { turn.stepEls[k].classList.remove("as-run"); });
    add(turn.body, h("p", { class: "as-notice as-notice-error", role: "alert" }, L.error));
    if (j && j.trace) add(turn.body, traceFold(j.trace));
  }

  function renderResponse(turn, resp, opt) {
    turn.resp = resp;
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
    if (resp.trace) add(b, traceFold(resp.trace));

    var fu = resp.followups || [];
    if (fu.length) {
      add(b, h("div", { class: "as-follow" }, h("h4", { class: "as-h4" }, L.follow), h("div", { class: "as-btns" },
        fu.map(function (f) {
          return h("button", { type: "button", class: "as-btn as-act", onclick: function () { followUp(f, turn); } }, f.text);
        }))));
    }
    var dq = resp.dashboard && resp.dashboard.q;
    var row = h("p", { class: "as-row" });
    if (dq) {
      add(row, h("button", { type: "button", class: "as-btn as-btn-ghost", onclick: function () {
        driveDashboard(dq, resp.dashboard.section, true);
      } }, L.dashboard));
    }
    if ((resp.panels || []).length) {
      add(row, h("button", { type: "button", class: "as-btn as-btn-ghost as-showpanels", onclick: function () {
        renderPanels(turn); S.els.panels.scrollIntoView({ behavior: "smooth", block: "nearest" });
      } }, L.showPanels));
    }
    if (row.childNodes.length) add(b, row);
    renderPanels(turn);
    if (dq) driveDashboard(dq, null, false);
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
      var li = h("li", {}, h("b", {}, st.label), " ", st.summary,
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
      if (det.checker) add(out, h("p", {}, "Model checker: " + det.checker.yes + " supported, " + det.checker.no + " not supported."));
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
    var wrap = h("div", { class: "as-read" }, h("h4", { class: "as-h4" }, recorded ? L.readRecorded : L.read));
    var editor = h("div", { class: "as-editor", hidden: true });
    var list = h("div", { class: "as-chips", role: "group", "aria-label": L.readRecorded });
    chipList(req).forEach(function (c) {
      var ag = (req.agreement || {})[c.path];
      var src = (req.sources || {})[c.path];
      var unc = ag === "conflict";
      var editable = !recorded && c.key !== "investigations";
      var cls = "as-chip" + (unc ? " as-chip-uncertain" : "") + (src === "preset" || src === "assumed" || src === "default" ? " as-chip-assumed" : "");
      var title = recorded ? L.recordedNotEditable : (unc ? L.uncertain : (src ? "From: " + src : null));
      var chip = h("button", { type: "button", class: cls + (editable ? " as-act" : ""), title: title,
        "aria-expanded": editable ? "false" : null, disabled: editable ? null : true }, c.text);
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
  function whenReady(fn, tries) {
    if (dashboardReady()) { fn(); return; }
    if ((tries || 0) > 100) return;
    setTimeout(function () { whenReady(fn, (tries || 0) + 1); }, 150);
  }
  function driveDashboard(q, section, scroll) {
    whenReady(function () {
      var input = document.getElementById("q"), form = document.getElementById("ask-form");
      if (!input || !form) return;
      if (q && input.value !== q) {
        input.value = q;
        if (typeof form.requestSubmit === "function") form.requestSubmit();
        else form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
      }
      if (scroll) scrollToSection(section || "#top");
    });
  }
  function scrollToSection(sel, tries) {
    var el = document.querySelector(sel);
    if (el && !el.hidden) { el.scrollIntoView({ behavior: "smooth", block: "start" }); return; }
    if ((tries || 0) < 15) { setTimeout(function () { scrollToSection(sel, (tries || 0) + 1); }, 120); return; }
    var top = document.querySelector("#top");
    if (top && !top.hidden) top.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // ------------------------------------------------------------------ panels
  function renderPanels(turn) {
    var resp = turn.resp, list = S.els.panelList;
    var panels = (resp && resp.panels) || [];
    S.root.querySelectorAll(".as-turn.as-current").forEach(function (x) { x.classList.remove("as-current"); });
    if (!panels.length) return;
    turn.el.classList.add("as-current");
    var facts = {};
    (resp.facts || []).forEach(function (f) { facts[f.id] = f; });
    list.replaceChildren(h("p", { class: "as-panels-for" }, "For: " + (turn.el.querySelector(".as-user").textContent.replace(/^You: /, ""))));
    panels.forEach(function (p) { list.appendChild(panelView(p, facts, resp)); });
  }

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
    fetchJSON(url, { cache: "no-cache" }).then(function (ev) {
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
