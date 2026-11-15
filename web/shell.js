// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
// Page shell (web/SHELL.md): the app bar, the landing state, the tabs, the copy-link control, the build stamp.
// It reads what web/app.js renders and never changes a sentence, a number or a link of a section.
// It computes nothing, calls no service, and requests only data/build.json (a file the page already reads).
// Loaded in <head> without "defer" so that the layout classes are on <html> before the first paint.
(function () {
  "use strict";
  var root = document.documentElement;
  var IS_HOW = root.getAttribute("data-page") === "how";

  // ---- the tab map: section id -> tab. A section can also name its tab itself with data-tab="<name>".
  // A section that is in neither stays visible under every tab (nothing is hidden by accident).
  var TABS = [
    ["closest", "Closest investigations"],
    ["found", "What was found"],
    ["data", "Where the data are"],
    ["stops", "Where the evidence stops"],
    ["all", "All investigations"]
  ];
  var TAB_OF = {
    read: "closest", top: "closest",
    "results-first": "found", results: "found", needs: "found", tests: "found", answers: "found", shown: "found", criteria: "found",
    piles: "data",
    stops: "stops",
    all: "all"
  };

  function query() { return new URL(location.href).searchParams.get("q"); }
  function hasQuery() { var q = query(); return q !== null && q.trim() !== ""; }
  function withQuery(href) {
    // keep the visitor's query on links between the dashboard and the method page
    var u = new URL(href, location.href), q = query();
    if (q !== null && q.trim() !== "") u.searchParams.set("q", q); else u.searchParams.delete("q");
    u.searchParams.delete("tab");
    return (u.pathname.split("/").pop() || "./") + u.search + u.hash;
  }

  root.classList.add("shell-on", "is-loading");
  if (!IS_HOW) {
    // Old links to the two method sections (slides, README) open the method page.
    if (/^#(method|ai-use)$/.test(location.hash)) { location.replace(withQuery("how.html" + location.hash)); return; }
    root.classList.add(hasQuery() ? "is-query" : "is-landing");
  }

  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  function el(tag, attrs, kids) {
    var e = document.createElement(tag), k;
    for (k in attrs || {}) if (attrs[k] !== null && attrs[k] !== undefined) e.setAttribute(k, attrs[k]);
    (kids || []).forEach(function (c) { e.append(c); });
    return e;
  }
  var reduceMotion = function () { return window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches; };
  var narrow = function () { return window.matchMedia && matchMedia("(max-width: 720px)").matches; };
  // Setting "hidden" to the value it has still queues a mutation record, and the shell follows main's mutations:
  // change it only when it differs, or the shell would wake itself up again and again.
  function setHidden(e, v) { if (e.hidden !== v) e.hidden = v; }

  function init() {
    var appbar = $("#appbar"), status = $("#status"), main = $("main");
    if (!main) return;

    // ---- sticky offsets follow the real height of the bars (the app bar wraps on a phone)
    function measure() {
      if (appbar) root.style.setProperty("--appbar-h", appbar.offsetHeight + "px");
      var t = $("#tabs");
      root.style.setProperty("--tabs-h", (t && !t.hidden ? t.offsetHeight : 0) + "px");
    }
    if (window.ResizeObserver && appbar) new ResizeObserver(measure).observe(appbar);
    window.addEventListener("resize", measure);

    // ---- links between the two pages keep the query; the build stamp
    function syncLinks() {
      $$('a[href^="how.html"], a.back-link, a.wordmark').forEach(function (a) {
        var base = a.getAttribute("data-href") || a.getAttribute("href");
        a.setAttribute("data-href", base);
        if (a.classList.contains("wordmark") && !IS_HOW) return; // on the dashboard the name leads back to the start
        a.setAttribute("href", withQuery(base));
      });
    }
    var stamp = $("#build-stamp");
    if (stamp) {
      fetch("data/build.json").then(function (r) { return r.ok ? r.json() : null; }).then(function (b) {
        if (!b || !b.commit) return;
        var when = b.built_at ? " · " + String(b.built_at).slice(0, 16).replace("T", " ") + " UTC" : "";
        stamp.textContent = "Build " + String(b.commit).slice(0, 7) + when;
      }).catch(function () {});
    }

    function isLoading() {
      return Boolean(status) && status.textContent.trim() !== "" && !/\bis-(info|error)\b/.test(status.className);
    }

    if (IS_HOW) {
      // The method page: the folded method text is open (the visitor came to read it).
      var d = $("#method details");
      if (d) d.open = true;
      var doneHow = function () {
        if (isLoading()) return;
        root.classList.remove("is-loading");
        syncLinks();
        var target = location.hash ? document.getElementById(decodeURIComponent(location.hash.slice(1))) : null;
        if (target) target.scrollIntoView();
      };
      if (status) new MutationObserver(doneHow).observe(status, { childList: true, characterData: true, subtree: true, attributes: true });
      // if the data never arrive, the static method text is still shown
      setTimeout(function () { root.classList.remove("is-loading"); }, 8000);
      syncLinks(); measure(); doneHow();
      return;
    }

    var ask = $("main > section.ask"), form = $("#ask-form"), q = $("#q");
    var glance = $("#glance"), jump = $("#jump");
    var search = $("#shell-search"), shellQ = $("#shell-q"), copy = $("#copy-link");
    if (!ask || !form || !q) { root.classList.remove("is-loading", "is-landing", "is-query"); return; }

    // ---- the three verbs of the page as small cards, built from the page's own kickers and headings
    var verbs = el("section", { "class": "verbs", "aria-label": "Find, Compare, Interpret" });
    [["#top"], ["#needs"], ["#stops"]].forEach(function (v) {
      var sec = $(v[0]), k = sec && $(".kicker", sec), h2 = sec && $("h2", sec);
      if (!k || !h2) return;
      // version 2: the verb, the section's heading, then the rest of the kicker as a small line (the page's own words)
      var name = $("b", k), nameText = name ? name.textContent : "";
      var rest = k.textContent.replace(nameText, "").replace(/^[\s·]+/, "");
      verbs.append(el("div", { "class": "verb" }, [el("p", { "class": "verb-name" }, [nameText]),
        el("p", { "class": "verb-title" }, [h2.textContent]), el("p", { "class": "verb-sub" }, [rest])]));
    });
    if (verbs.children.length === 3) ask.insertAdjacentElement("afterend", verbs);

    // ---- the model indicator (SHELL.md, "Model indicator"): which language model answers here, or none, in the
    // manner of a chat application that names its model under the message box. assistant.js reports its mode with
    // the event "fee-model" (and window.feeModel); a page without the assistant shows the rule-based state.
    var chip = el("a", { id: "model-chip", "class": "model-chip", href: "how.html#ai-use", "data-mode": "pending" },
      [el("span", { "class": "mc-main" }, [el("span", { "class": "mc-dot", "aria-hidden": "true" }), el("span", { "class": "mc-name" })]),
        el("span", { "class": "mc-sub" })]);
    // Version 2: on the start page it stands under the input at the right end of the help line (index.html keeps the
    // place, #ask-model); once a query is shown, in the request header next to the reading status.
    var meta = $("#ask-model", form);
    if (meta) meta.append(chip);
    else {
      meta = el("div", { "class": "ask-meta" }, [chip]);
      var row = $(".ask-row", form);
      if (row) row.insertAdjacentElement("afterend", meta); else form.prepend(meta);
    }
    function placeChip(landing) {
      var side = $("#request .request-side");
      if (!landing && side) { if (chip.parentNode !== side) side.prepend(chip); }
      else if (chip.parentNode !== meta) meta.append(chip);
    }
    // the reason the local server gives (ai/llm.py), in plain words; the exact reason is in the title
    function reasonWords(r) {
      if (!r) return "";
      if (/AI_NO_MODEL_CALLS=1/.test(r)) return "model calls switched off for this run";
      if (/not reachable/i.test(r)) return "the model server did not answer";
      if (/not installed/i.test(r)) return "the model is not installed";
      if (/digest/i.test(r)) return "the installed model is not the expected version";
      if (/not an allowed model/i.test(r)) return "the model is not on the team's list";
      return r;
    }
    function showModel(d) {
      d = d || {};
      var mode = d.mode || "none", name, ext = "", sub = "", title, dot = "hollow";
      var more = " Opens: how AI is used here.";
      if (mode === "live") {
        name = d.model || "Local model"; ext = d.model ? " · local model" : ""; dot = "filled";
        sub = "Runs on this computer through Ollama";
        title = (d.model || "The local model") + (d.maker ? " by " + d.maker : "") + (d.license ? ", licence " + d.license : "") +
          ". It runs on this computer through Ollama" + (d.digest ? "; its digest " + d.digest + " is the one the team's code expects" : "") + "." + more;
      } else if (mode === "no_model") {
        var why = reasonWords(d.reason);
        name = "Rule-based"; ext = " mode";
        sub = "Answers put together by team code from the facts" + (why ? " · " + why : "");
        title = "Answers are put together by team code from the facts." + (d.reason ? " The local server says: " + d.reason + "." : "") + more;
      } else if (mode === "mock") {
        name = "Mock"; ext = " mode"; sub = "Fixed test answers";
        title = "Every answer is a fixed test file." + more;
      } else { // the public page or a static copy: recorded, nothing, or no assistant on the page
        name = "Rule-based"; ext = " mode";
        if (mode === "recorded" && d.recordedModel) {
          sub = "Recorded answers of " + d.recordedModel + (d.recordedDate ? ", " + d.recordedDate : "");
          title = "The dashboard is computed by team code. The assistant replays answers recorded with the local model " +
            d.recordedModel + (d.recordedDate ? " on " + d.recordedDate : "") + "." + more;
        } else { sub = "Dashboard computed by team code"; title = "The dashboard is computed by team code from NASA PSI data." + more; }
      }
      var nm = $(".mc-name", chip), sb = $(".mc-sub", chip);
      nm.replaceChildren(name, el("span", { "class": "mc-ext" }, [ext]));
      sb.textContent = sub;
      chip.title = title;
      chip.setAttribute("aria-label", name + ext + (sub ? ". " + sub : "") + "." + more);
      chip.setAttribute("data-mode", mode);
      chip.setAttribute("data-dot", dot);
    }
    document.addEventListener("fee-model", function (e) { showModel(e.detail); });
    if (window.feeModel) showModel(window.feeModel);
    // a page without the assistant (or one whose assistant never reports): the rule-based state
    var noAssistant = function () { if (chip.getAttribute("data-mode") === "pending" && !document.getElementById("assistant")) showModel(null); };
    if (document.readyState === "complete") noAssistant(); else window.addEventListener("load", noAssistant);
    setTimeout(function () { if (chip.getAttribute("data-mode") === "pending") showModel(null); }, 8000);

    // ---- loading placeholder for a page opened with a query (the results take its place)
    var skeleton = el("div", { "class": "skeleton", "aria-hidden": "true" },
      [el("span"), el("span"), el("span"), el("span", { "class": "wide" }), el("span", { "class": "wide" })]);
    if (status) status.insertAdjacentElement("afterend", skeleton);

    // ---- the tab bar (replaces the "On this page" list, which stays in the page for the checks)
    var tabs = el("nav", { id: "tabs", "class": "tabs", "aria-label": "Result sections", hidden: "" });
    var tabsIn = el("div", { "class": "tabs-in" });
    tabs.append(tabsIn);
    var tabLinks = {};
    TABS.forEach(function (t) {
      var a = el("a", { href: "?tab=" + t[0], "data-tab": t[0] }, [t[1]]);
      tabLinks[t[0]] = a;
      tabsIn.append(a);
    });
    (jump || glance || ask).insertAdjacentElement("afterend", tabs);
    // the resting place of the tab bar (the bar itself is sticky, so its own position says where it is stuck)
    var anchor = el("span", { id: "tabs-anchor", "class": "tabs-anchor", "aria-hidden": "true" });
    tabs.insertAdjacentElement("beforebegin", anchor);
    // Version 2: the notices of "How your input was read" (#scenario-warnings) are shown under every tab as ONE
    // neutral band between the summary row and the tab bar, rebuilt whenever app.js renders them. Each notice is cut
    // to its first sentence; "Read the full note" opens the rest in place (the full text is in the band's markup).
    var warnCopy = el("aside", { id: "notes-band", "class": "notes-band", "aria-label": "Notes for this environment", hidden: "" });
    anchor.insertAdjacentElement("beforebegin", warnCopy);
    function firstSentence(t) {
      var m = /^([\s\S]*?[.!?])\s+(?=[A-Z(])([\s\S]+)$/.exec(t);
      return m && m[1].length >= 24 ? [m[1], m[2]] : [t, ""];
    }
    function buildNotes(src) {
      var ul = el("ul", { "class": "notes-list" });
      src.forEach(function (w, i) {
        var parts = firstSentence(w.textContent.trim());
        var li = el("li", { "class": "note" }, [el("span", { "class": "note-first" }, [parts[0]])]);
        if (parts[1]) {
          var more = el("span", { "class": "note-rest", id: "note-rest-" + i, hidden: "" }, [" " + parts[1]]);
          var btn = el("button", { type: "button", "class": "text-btn note-more", "aria-expanded": "false", "aria-controls": "note-rest-" + i }, ["Read the full note"]);
          btn.addEventListener("click", function () {
            var open = more.hidden;
            more.hidden = !open;
            btn.setAttribute("aria-expanded", String(open));
            btn.textContent = open ? "Show less" : "Read the full note";
          });
          li.append(more, " ", btn);
        }
        ul.append(li);
      });
      warnCopy.replaceChildren(el("p", { "class": "notes-title" }, ["Notes for this environment"]), ul);
    }

    // ---- version 2: the request header. A white band under the app bar: what was read as the title (the environment's
    // label, then the material when one is named), the reading chips (#conditions, moved here), the reading status,
    // and the block "How your input was read" (#read, moved into a fold that is closed while the notes band shows
    // its notices). app.js finds both by id, so it renders into them where they now are.
    var read = $("#read"), conds = $("#conditions");
    var request = el("div", { id: "request", "class": "request", hidden: "" });
    var reqTitle = el("h2", { "class": "request-title" });
    var reqStatus = el("span", { id: "reading-status", "class": "reading-status", "data-state": "rule" }, ["Rule-based reading"]);
    var readFold = el("details", { "class": "more read-fold" }, [el("summary", {}, ["How this was read"])]);
    if (read && conds) {
      request.append(el("div", { "class": "request-top" }, [reqTitle, el("div", { "class": "request-side" }, [reqStatus])]), conds, readFold);
      ask.insertAdjacentElement("afterend", request);
      readFold.append(read);
    }
    function chipValue(label) {
      var li = $$("li", conds).filter(function (x) { var b = $("b", x); return b && b.textContent === label; })[0];
      if (!li) return "";
      return $$("b, .src", li).reduce(function (t, n) { return t.replace(n.textContent, ""); }, li.textContent).trim();
    }
    function readingTitle() {
      var env = chipValue("Environment"), mat = chipValue("Material");
      return [env, mat].filter(Boolean).join(" · ") || (q.value.trim() || query() || "").trim();
    }
    // The reading status. Without a model: "Rule-based reading". The assistant sets the other states when a local
    // model has checked the reading (window.feeShell.setReading, called from ai/assistant/static/assistant.js).
    var READING = { rule: "Rule-based reading", checking: "Checking the reading with {m}", checked: "Reading checked by {m}",
      corrected: "Reading corrected by {m}", question: "The assistant has a question" };
    function setReading(st, model, detail) {
      if (!READING[st]) st = "rule";
      reqStatus.setAttribute("data-state", st);
      reqStatus.textContent = READING[st].replace("{m}", model || "the local model");
      if (detail) reqStatus.setAttribute("title", detail); else reqStatus.removeAttribute("title");
    }

    // pending: a tab or a section id asked for by the address, opened as soon as app.js has shown it
    // "All investigations" is a tab of its own: its table is open there (the fold stays for the page without the shell)
    var ranking = $("#all details.fold");
    if (ranking) ranking.open = true;
    var state = { tab: null, resetTab: false, typed: null, booted: false, pending: null, defaultQ: null };
    function tabOf(sec) { return sec.getAttribute("data-tab") || TAB_OF[sec.id] || null; }
    function sections() { return $$(":scope > section[id]", main).filter(function (s) { return tabOf(s); }); }
    function wantedTab() {
      var p = new URL(location.href).searchParams.get("tab");
      return TABS.some(function (t) { return t[0] === p; }) ? p : null;
    }
    function holderOf(node) { // the section of a tab that holds a node
      while (node && node.parentElement !== main) node = node.parentElement;
      return node && node.matches && node.matches("section[id]") && tabOf(node) ? node : null;
    }
    // An id in the address: a section of a tab first (index.html also has a list with the id "results"), then any element.
    function byId(id) {
      if (!id) return null;
      var secs = sections().filter(function (x) { return x.id === id; });
      return secs[0] || document.getElementById(id);
    }
    function barsHeight() { return (appbar ? appbar.offsetHeight : 0) + (tabs.hidden ? 0 : tabs.offsetHeight); }
    function nodeY(node) { return Math.max(0, Math.round(node.getBoundingClientRect().top + window.scrollY - barsHeight() - 12)); }
    function scrollToNode(node, instant) {
      window.scrollTo({ top: nodeY(node), behavior: instant || reduceMotion() ? "auto" : "smooth" });
    }
    // always: also when the page is above the tab bar (on a phone a tab's content would start low on the screen)
    function scrollToTabs(always) {
      var y = Math.round(anchor.getBoundingClientRect().top + window.scrollY + (parseFloat(getComputedStyle(tabs).marginTop) || 0) -
        (appbar ? appbar.offsetHeight : 0));
      if (window.scrollY > y + 1 || (always && Math.abs(window.scrollY - y) > 1)) window.scrollTo({ top: Math.max(0, y), behavior: "auto" });
    }
    // An address that names a section: the page scrolls there at once and keeps it there while app.js renders the
    // content above it (a section that arrives later moves it). It lets go after 1.5 s without a move, after 8 s
    // in all, or as soon as the visitor scrolls, clicks or types.
    var settle = null;
    function settleOn(node) { var now = Date.now(); settle = { node: node, until: now + 1500, stopAt: now + 8000 }; scrollToNode(node, true); }
    function resettle() {
      if (!settle) return;
      var now = Date.now();
      if (now > settle.until || now > settle.stopAt || !settle.node.isConnected) { settle = null; return; }
      var y = nodeY(settle.node);
      if (Math.abs(window.scrollY - y) > 2) {
        window.scrollTo({ top: y, behavior: "auto" });
        settle.until = Math.min(settle.stopAt, now + 1500);
      }
    }
    ["wheel", "touchstart", "mousedown", "keydown"].forEach(function (ev) {
      window.addEventListener(ev, function () { settle = null; }, { passive: true, capture: true });
    });
    if (window.ResizeObserver) new ResizeObserver(function () { resettle(); }).observe(main);

    // ---- one pass that brings the shell in step with what app.js has rendered
    function sync() {
      var loading = isLoading(), landing = !hasQuery();
      root.classList.toggle("is-loading", loading);
      root.classList.toggle("is-landing", landing);
      root.classList.toggle("is-query", !landing);
      if (search) search.hidden = landing;
      placeChip(landing);

      if (!loading && landing && query() === null) {
        // Without a query app.js runs its ISS example; the start page shows the input empty instead.
        if (state.typed !== null) { if (q.value !== state.typed) q.value = state.typed; }
        else if (q.value === "ISS" && document.activeElement !== q) { state.defaultQ = q.value; q.value = ""; }
        if (state.typed === null) $$(".presets button[aria-pressed='true']", ask).forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
      }
      if (shellQ && document.activeElement !== shellQ) shellQ.value = landing ? "" : (q.value || query() || "");

      var ok = !landing && Boolean(glance) && !glance.hidden;
      var secs = sections();
      var open = {};
      secs.forEach(function (s) { if (!s.hidden) open[tabOf(s)] = true; });
      var first = null;
      TABS.forEach(function (t) { if (open[t[0]] && !first) first = t[0]; });
      if (state.resetTab) { state.tab = first; state.resetTab = false; state.pending = null; }
      var arrived = null;
      if (state.pending && ok) {
        var p = state.pending, node = p.id ? byId(p.id) : null, sec = node ? holderOf(node) : null;
        if (sec && !sec.hidden) { state.tab = tabOf(sec); arrived = node; state.pending = null; }
        else if (p.tab && open[p.tab]) { state.tab = p.tab; arrived = p.scroll ? tabs : null; state.pending = null; }
        else if (Date.now() > p.until) state.pending = null;
      }
      if (!state.tab || !open[state.tab]) state.tab = first;
      setHidden(tabs, !ok || !first);

      var sw = $("#scenario-warnings");
      var src = sw ? $$(":scope > .warn", sw) : [];
      var sig = src.map(function (w) { return w.className + "|" + w.textContent; }).join("\n");
      if (sig !== warnCopy.getAttribute("data-sig")) {
        buildNotes(src);
        warnCopy.setAttribute("data-sig", sig);
      }
      setHidden(warnCopy, !ok || !src.length);
      root.classList.toggle("has-notes", ok && src.length > 0); // the band carries them: #read does not repeat them
      if (request.parentNode) {
        var showReq = !landing && !loading && !read.hidden;
        setHidden(request, !showReq);
        var title = showReq ? readingTitle() : "";
        if (reqTitle.textContent !== title) reqTitle.textContent = title;
        // no ranking for this input: the notices are in the block itself, so it opens (once per input)
        if (showReq && !ok && state.readOpened !== q.value) { readFold.open = true; state.readOpened = q.value; }
      }
      TABS.forEach(function (t) {
        var a = tabLinks[t[0]], on = ok && t[0] === state.tab;
        setHidden(a, !open[t[0]]);
        if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
        var u = new URL(location.href);
        u.searchParams.set("tab", t[0]); u.hash = "";
        a.setAttribute("href", u.search);
      });
      secs.forEach(function (s) { s.classList.toggle("tab-off", ok && tabOf(s) !== state.tab); hookScroll(s); });
      document.title = (landing ? "" : (q.value.trim() || query() || "").trim() + " · ") + "Fire Evidence Explorer" +
        (landing ? ": the closest NASA microgravity fire investigations, and where the evidence stops" : "");
      syncLinks();
      measure();
      var cur = tabLinks[state.tab]; // keep the current tab in view when the bar scrolls sideways (narrow screens)
      if (cur && ok && tabsIn.scrollWidth > tabsIn.clientWidth &&
          (cur.offsetLeft < tabsIn.scrollLeft || cur.offsetLeft + cur.offsetWidth > tabsIn.scrollLeft + tabsIn.clientWidth))
        tabsIn.scrollLeft = Math.max(0, cur.offsetLeft - 16);
      if (arrived === tabs) scrollToTabs();
      else if (arrived) {
        for (var d = arrived.closest("details"); d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
        settleOn(arrived);
      } else resettle();
      if (!loading && !state.booted) { state.booted = true; route(false); }
    }
    var queued = false;
    function later() { if (!queued) { queued = true; setTimeout(function () { queued = false; sync(); }, 0); } }

    function setTab(name, opts) {
      opts = opts || {};
      if (!tabLinks[name] || tabLinks[name].hidden) return false;
      state.tab = name; state.pending = null;
      if (opts.push) {
        var u = new URL(location.href);
        u.searchParams.set("tab", name); u.hash = "";
        history.pushState(null, "", u);
      }
      sync();
      if (opts.scroll) scrollToTabs(narrow());
      return true;
    }
    function firstTab() {
      for (var i = 0; i < TABS.length; i++) if (tabLinks[TABS[i][0]] && !tabLinks[TABS[i][0]].hidden) return TABS[i][0];
      return null;
    }
    // On the start page app.js has already run its example in the background: a script that asks for one of its
    // sections (the assistant's "Show on the dashboard") gets that run in view, as the page without the shell showed it.
    function showDefaultRun() {
      var dq = state.defaultQ || "ISS";
      var u = new URL(location.href);
      u.searchParams.set("q", dq); u.searchParams.delete("tab"); u.hash = "";
      history.pushState(null, "", u);
      q.value = dq; state.typed = null;
      $$(".presets button", ask).forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-q") === dq)); });
      sync();
    }
    // Open the tab that holds a node (a selector or an element) and scroll to it.
    function reveal(target, opts) {
      var node = typeof target === "string" ? $(target) : target;
      if (!node) return false;
      var sec = holderOf(node);
      if (sec && !sec.hidden && !hasQuery()) showDefaultRun();
      if (sec && sec.hidden) {
        // a section this query does not show: the first tab, from its top
        var f = firstTab();
        if (f) { setTab(f, {}); scrollToTabs(true); }
        return true;
      }
      if (sec) setTab(tabOf(sec), {});
      for (var d = node.closest ? node.closest("details") : null; d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
      if (!opts || opts.scroll !== false) scrollToNode(node);
      return true;
    }
    // A script that scrolls a section into view (app.js, the assistant) while its tab is closed or the start page is
    // shown: the shell opens that tab instead, so the call does what it did on the page without the shell.
    function hookScroll(s) {
      if (s.__shellHook) return;
      s.__shellHook = true;
      s.scrollIntoView = function () {
        if (root.classList.contains("is-landing") || s.classList.contains("tab-off") || s.hidden) { reveal(s); return; }
        return Element.prototype.scrollIntoView.apply(s, arguments);
      };
    }
    // The address decides: #section-id opens the tab that holds it and scrolls there; ?tab=<name> opens a tab.
    function route(fromHistory) {
      var id = decodeURIComponent(location.hash.slice(1)), t = wantedTab();
      if (id && byId(id) && holderOf(byId(id)))
        state.pending = { id: id, until: Date.now() + 6000 };
      else if (t) state.pending = { tab: t, scroll: fromHistory, until: Date.now() + 6000 };
      else if (fromHistory) state.resetTab = true;
      else return;
      sync();
    }

    tabsIn.addEventListener("click", function (e) {
      var a = e.target.closest("a[data-tab]");
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      e.preventDefault();
      setTab(a.getAttribute("data-tab"), { push: true, scroll: true });
    });
    document.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a[href]");
      if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      var href = a.getAttribute("href");
      if (href === "#method" || href === "#ai-use") { // a link to a section that now lives on the method page
        if (!$(href)) { e.preventDefault(); location.href = withQuery("how.html" + href); }
        return;
      }
      if (href.charAt(0) !== "#" || href.length < 2) return;
      var node = byId(decodeURIComponent(href.slice(1)));
      if (!node || !holderOf(node)) return;
      e.preventDefault();
      var u = new URL(location.href);
      u.searchParams.delete("tab"); u.hash = href;
      history.pushState(null, "", u);
      reveal(node);
    });
    window.addEventListener("popstate", function () { later(); route(true); });
    window.addEventListener("hashchange", function () { route(true); });

    // ---- a new query from the input or an example starts on the first tab, at the top
    function newQuery() {
      // The assistant marks its own submit (the dashboard follows an answer that arrives a minute or two after
      // the question): the visitor's tab and scroll position stay as they are.
      if (form.hasAttribute("data-quiet")) { later(); return; }
      setReading("rule");
      state.resetTab = true;
      var u = new URL(location.href);
      if (u.searchParams.has("tab") || u.hash) { u.searchParams.delete("tab"); u.hash = ""; history.replaceState(null, "", u); }
      if (ask.contains(document.activeElement) || (appbar && appbar.contains(document.activeElement))) window.scrollTo({ top: 0, behavior: "auto" });
      later();
    }
    form.addEventListener("submit", newQuery, true);
    $$(".presets button", ask).forEach(function (b) { b.addEventListener("click", newQuery, true); });
    q.addEventListener("input", function () { state.typed = q.value; });
    if (search) search.addEventListener("submit", function (e) {
      e.preventDefault();
      q.value = shellQ.value;
      if (form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
      shellQ.blur();
    });

    // ---- "/" puts the cursor in the input
    document.addEventListener("keydown", function (e) {
      if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
      var t = e.target;
      if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
      var box = search && !search.hidden ? shellQ : q;
      e.preventDefault();
      box.focus(); box.select();
    });

    // ---- copy the address of the current query (and tab)
    if (copy) copy.addEventListener("click", function () {
      var label = $(".copy-label", copy), url = location.href;
      var done = function (ok) {
        if (!label) return;
        label.textContent = ok ? "Link copied" : "Copy the address bar";
        copy.classList.add("is-done");
        setTimeout(function () { label.textContent = "Copy link"; copy.classList.remove("is-done"); }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { done(true); }, function () { done(false); });
      else done(false);
    });

    // print shows everything: the fold that holds "How your input was read" opens for it
    window.addEventListener("beforeprint", function () { readFold.open = true; });

    // app.js shows and hides sections as its files arrive: follow it.
    new MutationObserver(later).observe(main, { attributes: true, attributeFilter: ["hidden", "class"], subtree: true, childList: true });
    window.feeShell = { reveal: reveal, setTab: setTab, tabOf: TAB_OF, setReading: setReading };
    sync();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
