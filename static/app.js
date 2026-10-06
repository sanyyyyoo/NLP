(() => {
  "use strict";

  const UI_TEXT = {
    en: {
      subtitle_topic: "Marathi & English Newspaper Section Detection and Tone Analysis",
      launch: "LAUNCH NEWS ANALYSIS WORKSPACE ➔",
      back: "⬅ Back to Front Page",
      viewer_btn: "📖 View Dictionary Dataset",
      ws_title: "Newspaper Headline Analyser",
      ws_subtitle: "Marathi & English Headline Classification and Tone Analysis Workspace",
      sample: "Sample headline:",
      sample_pick: "— pick a sample headline —",
      input: "Paste a Marathi or English headline / article:",
      lang_label: "Language detected:",
      analyse: "🔍 Analyse News",
      analysing: "Analysing…",
      load: "📂 Load .txt",
      clear: "✖ Clear",
      section: "News Section",
      tone: "News Tone",
      confidence: "Category Confidence:",
      log: "Detailed Analysis Log:",
      score: "Compound score: {s}   (range −1 to +1)",
      tone_Positive: "Positive News", tone_Negative: "Negative News", tone_Neutral: "Neutral News",
      general: "General / Other",
      no_keywords: "No category keywords found",
      warn_empty: "Please enter a news headline or article.",
      net_error: "Could not reach the server. Check your connection and try again.",
      file_error: "Could not read that file. Save the article as UTF-8 text and try again.",
      log_tokens: "Tokens",
      log_cat: "▶ Category keywords:",
      log_sent: "▶ Sentiment words:",
      log_none: "(none)",
      log_neutral: "(no opinion words – factual / neutral reporting)",
      log_empty: "Analyse a headline to see the matched dictionary words here.",
      lang_mr: "Marathi", lang_en: "English", lang_mixed: "Mixed (Marathi + English)", lang_none: "—",
      search: "Search:",
      viewer_title: "Dictionary Dataset Viewer",
      loading: "Loading…",
    },
    mr: {
      subtitle_topic: "मराठी व इंग्रजी वृत्तपत्र बातमी विभाग ओळख व सूर विश्लेषण",
      launch: "बातमी विश्लेषण कक्ष उघडा ➔",
      back: "⬅ मुखपृष्ठावर परत",
      viewer_btn: "📖 शब्दकोश डेटासेट पहा",
      ws_title: "मराठी व इंग्रजी वृत्तपत्र बातमी विश्लेषक",
      ws_subtitle: "बातमी मथळा विभाग ओळख व सूर विश्लेषण कक्ष",
      sample: "नमुना मथळा:",
      sample_pick: "— नमुना मथळा निवडा —",
      input: "बातमीचा मथळा / मजकूर येथे टाका (मराठी किंवा इंग्रजी):",
      lang_label: "ओळखलेली भाषा:",
      analyse: "🔍 विश्लेषण करा",
      analysing: "विश्लेषण सुरू…",
      load: "📂 फाइल उघडा",
      clear: "✖ पुसा",
      section: "वृत्त विभाग",
      tone: "बातमीचा सूर",
      confidence: "विभाग विश्वासार्हता:",
      log: "विश्लेषण लॉग:",
      score: "एकत्रित गुण: {s}   (−1 ते +1)",
      tone_Positive: "सकारात्मक बातमी", tone_Negative: "नकारात्मक बातमी", tone_Neutral: "तटस्थ बातमी",
      general: "सामान्य / इतर",
      no_keywords: "कोणताही विभाग-शब्द सापडला नाही",
      warn_empty: "कृपया बातमीचा मथळा किंवा मजकूर टाका.",
      net_error: "सर्व्हरशी संपर्क झाला नाही. इंटरनेट तपासा आणि पुन्हा प्रयत्न करा.",
      file_error: "फाइल वाचता आली नाही. बातमी UTF-8 मजकूर म्हणून सेव्ह करून पुन्हा प्रयत्न करा.",
      log_tokens: "शब्द",
      log_cat: "▶ विभाग ओळख शब्द:",
      log_sent: "▶ सूर दर्शवणारे शब्द:",
      log_none: "(काहीही नाही)",
      log_neutral: "(मत दर्शवणारे शब्द नाहीत – तटस्थ वृत्तांकन)",
      log_empty: "जुळलेले शब्दकोश शब्द पाहण्यासाठी मथळ्याचे विश्लेषण करा.",
      lang_mr: "मराठी", lang_en: "इंग्रजी", lang_mixed: "मिश्र (मराठी + इंग्रजी)", lang_none: "—",
      search: "शोधा:",
      viewer_title: "शब्दकोश डेटासेट",
      loading: "लोड होत आहे…",
    },
  };

  const boot = JSON.parse(document.getElementById("boot-data").textContent);
  const CATEGORY_EN = boot.categories;                     // Marathi key -> English name
  const $ = (id) => document.getElementById(id);

  let uiLang = "en";
  try { uiLang = localStorage.getItem("ui-lang") || "en"; } catch (_) { /* storage blocked */ }
  let lastResult = null;

  const T = (key) => UI_TEXT[uiLang][key];

  function categoryNames(catMr) {
    if (!(catMr in CATEGORY_EN)) return [T("general"), ""];
    return uiLang === "en" ? [CATEGORY_EN[catMr], catMr] : [catMr, CATEGORY_EN[catMr]];
  }

  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // ---------------- Language toggle ----------------
  function setUiLang(lang) {
    uiLang = lang;
    try { localStorage.setItem("ui-lang", lang); } catch (_) { /* ignore */ }
    document.documentElement.dataset.ui = lang;
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach((n) => { n.textContent = T(n.dataset.i18n); });
    document.querySelectorAll("[data-ui-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.uiLang === lang)));
    $("dataset-search").placeholder = uiLang === "en" ? "word, category or meaning" : "शब्द, विभाग किंवा अर्थ";
    if (lastResult) render(lastResult); else renderEmpty();
    if (dialog.open) renderDatasetTabs();
  }
  document.querySelectorAll("[data-ui-lang]").forEach((b) => b.addEventListener("click", () => setUiLang(b.dataset.uiLang)));

  // ---------------- Navigation ----------------
  function showWorkspace() { $("page-front").hidden = true; $("page-workspace").hidden = false; window.scrollTo(0, 0); }
  function showFront() { $("page-workspace").hidden = true; $("page-front").hidden = false; window.scrollTo(0, 0); }
  $("btn-launch").addEventListener("click", showWorkspace);
  $("btn-back").addEventListener("click", showFront);

  // ---------------- Rendering ----------------
  function renderEmpty() {
    $("category").textContent = "—";
    $("category-alt").textContent = "";
    $("tone").textContent = "—";
    $("tone").className = "tone-pill tone-Neutral";
    $("score").textContent = "";
    $("lang-detected").textContent = `${T("lang_label")} —`;
    $("bars").replaceChildren(el("p", "bars-empty", "—"));
    $("log").replaceChildren(el("p", "muted", T("log_empty")));
  }

  function renderBars(ranking) {
    const bars = $("bars");
    if (!ranking.length) { bars.replaceChildren(el("p", "bars-empty", T("no_keywords"))); return; }
    bars.replaceChildren(...ranking.slice(0, 4).map(([cat, pct]) => {
      const row = el("div", "bar-row");
      const track = el("div", "bar-track");
      const fill = el("div", "bar-fill");
      fill.style.width = `${pct}%`;
      track.append(fill);
      row.append(el("span", "bar-name", categoryNames(cat)[0]), track, el("span", "bar-pct", `${Math.round(pct)}%`));
      return row;
    }));
  }

  function logItem(cls, main, via, rest) {
    const p = el("p", `item ${cls}`, `• ${main}`);
    if (via) p.append(el("span", "via", `  [${via}]`));
    p.append(document.createTextNode(rest));
    return p;
  }

  function renderLog(r) {
    const out = [el("p", "muted", `${T("log_tokens")} (${r.tokens.length}): ${r.tokens.join(" | ")}`)];

    out.push(el("p", "head", T("log_cat")));
    if (r.category_evidence.length) {
      r.category_evidence.forEach((e) => {
        const via = e.how === "exact" ? "" : `${e.how} → ${e.root}`;
        out.push(logItem("cat", e.token, via, `  ⇒  ${categoryNames(e.category)[0]}  (+${e.weight})  — ${e.meaning}`));
      });
    } else out.push(el("p", "item muted", T("log_none")));

    out.push(el("p", "head", T("log_sent")));
    if (r.sentiment_items.length) {
      r.sentiment_items.forEach((it) => {
        const via = it.how === "exact" ? "" : `${it.how} → ${it.root}`;
        const mods = [];
        if (it.boost !== 1) mods.push(`×${it.boost}`);
        if (it.negated) mods.push("negated");
        const base = `${it.base > 0 ? "+" : ""}${it.base}`;
        const score = `${it.score > 0 ? "+" : ""}${it.score.toFixed(1)}`;
        out.push(logItem(it.score > 0 ? "pos" : "neg", it.token, via,
          `  base ${base}${mods.length ? `  (${mods.join(", ")})` : ""}  ⇒  ${score}  — ${it.meaning}`));
      });
    } else out.push(el("p", "item muted", T("log_neutral")));
    r.sentiment_notes.forEach((n) => out.push(el("p", "item muted", `↳ ${n}`)));

    $("log").replaceChildren(...out);
  }

  function render(r) {
    $("lang-detected").textContent = `${T("lang_label")} ${T("lang_" + r.language)}`;
    const [primary, secondary] = categoryNames(r.category);
    $("category").textContent = primary;
    $("category-alt").textContent = secondary;
    $("tone").textContent = T("tone_" + r.tone_key);
    $("tone").className = `tone-pill tone-${r.tone_key}`;
    const s = `${r.compound >= 0 ? "+" : ""}${r.compound.toFixed(2)}`;
    $("score").textContent = T("score").replace("{s}", s);
    renderBars(r.ranking);
    renderLog(r);
  }

  // ---------------- Actions ----------------
  function showError(msg) { const e = $("form-error"); e.textContent = msg; e.hidden = !msg; }

  async function analyse() {
    const text = $("news-text").value.trim();
    if (!text) { showError(T("warn_empty")); $("news-text").focus(); return; }
    showError("");
    const btn = $("btn-analyse");
    btn.disabled = true;
    btn.textContent = T("analysing");
    try {
      const res = await fetch("api/analyse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!res.ok) { showError(data.error || T("net_error")); return; }
      lastResult = data;
      render(data);
    } catch (_) {
      showError(T("net_error"));
    } finally {
      btn.disabled = false;
      btn.textContent = T("analyse");
    }
  }

  $("analyse-form").addEventListener("submit", (ev) => { ev.preventDefault(); analyse(); });
  $("news-text").addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && (ev.ctrlKey || ev.metaKey)) { ev.preventDefault(); analyse(); }
  });
  $("sample").addEventListener("change", (ev) => {
    if (ev.target.value) { $("news-text").value = ev.target.value; analyse(); }
  });
  $("btn-clear").addEventListener("click", () => {
    $("news-text").value = ""; $("sample").value = ""; lastResult = null; showError(""); renderEmpty(); $("news-text").focus();
  });
  $("file-input").addEventListener("change", (ev) => {
    const file = ev.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => { $("news-text").value = String(reader.result).slice(0, 5000); ev.target.value = ""; analyse(); };
    reader.onerror = () => showError(T("file_error"));
    reader.readAsText(file, "utf-8");
  });

  // ---------------- Dataset viewer ----------------
  const dialog = $("dataset-dialog");
  let dataset = null;
  let activeTab = "mr-keywords";

  const TABS = [
    ["mr-keywords", "Marathi News Keywords"], ["mr-sentiment", "Marathi Sentiment"],
    ["en-keywords", "English News Keywords"], ["en-sentiment", "English Sentiment"],
  ];

  function tabRows(key) {
    const [lang, kind] = key.split("-");
    const meaningCol = lang === "mr" ? "English Meaning" : "मराठी अर्थ";
    if (kind === "keywords") {
      return {
        cols: ["Word", "Category", "Weight", meaningCol],
        rows: dataset[lang].keywords.map((r) => [r.word, `${r.category} (${r.category_en})`, String(r.weight), r.meaning]),
      };
    }
    return {
      cols: ["Word", "Type", "Score", meaningCol],
      rows: dataset[lang].sentiment.map((r) => [r.word, r.type, r.score, r.meaning]),
    };
  }

  function renderDatasetTabs() {
    if (!dataset) return;
    $("dataset-tabs").replaceChildren(...TABS.map(([key, label]) => {
      const b = el("button", "", `${label} (${tabRows(key).rows.length})`);
      b.type = "button";
      b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", String(key === activeTab));
      b.addEventListener("click", () => { activeTab = key; renderDatasetTabs(); });
      return b;
    }));
    renderDatasetTable();
  }

  function renderDatasetTable() {
    const { cols, rows } = tabRows(activeTab);
    const q = $("dataset-search").value.trim().toLowerCase();
    const table = $("dataset-table");
    const head = el("tr");
    cols.forEach((c) => head.append(el("th", "", c)));
    table.tHead.replaceChildren(head);
    const body = rows
      .filter((r) => !q || r.some((cell) => cell.toLowerCase().includes(q)))
      .map((r) => { const tr = el("tr"); r.forEach((cell) => tr.append(el("td", "", cell))); return tr; });
    table.tBodies[0].replaceChildren(...body);
  }

  function tableMessage(msg) {
    const td = el("td", "", msg);
    td.colSpan = 4;
    const tr = el("tr");
    tr.append(td);
    $("dataset-table").tBodies[0].replaceChildren(tr);
  }

  $("btn-dataset").addEventListener("click", async () => {
    dialog.showModal();
    if (!dataset) {
      tableMessage(T("loading"));
      try { dataset = await (await fetch("api/dataset")).json(); }
      catch (_) { tableMessage(T("net_error")); return; }
    }
    renderDatasetTabs();
  });
  $("btn-close-dataset").addEventListener("click", () => dialog.close());
  $("dataset-search").addEventListener("input", renderDatasetTable);

  // ---------------- Start ----------------
  setUiLang(uiLang === "mr" ? "mr" : "en");
  analyse();   // open with the first sample already analysed
})();
