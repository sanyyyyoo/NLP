import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import nlp_engine as engine
from project_info import STUDENT_NAME, ROLL_NO, BATCH, SAMPLE_HEADLINES

DEV_FONT = "Nirmala UI"   # ships with Windows; renders Marathi matras correctly
DEFAULT_UI_LANG = "en"    # "en" = English interface, "mr" = Marathi interface

TONE_COLORS = {
    "Positive": ("#DCFCE7", "#166534"),
    "Negative": ("#FEE2E2", "#991B1B"),
    "Neutral": ("#E2E8F0", "#334155"),
}

# =====================================================================
# 0. INTERFACE TEXT (Marathi / English)
# =====================================================================
UI_TEXT = {
    "en": {
        "subtitle_topic": "Marathi & English Newspaper Section Detection and Tone Analysis",
        "launch": "LAUNCH NEWS ANALYSIS WORKSPACE ➔",
        "back": "⬅ Back to Front Page",
        "viewer_btn": "📖 View Dictionary Dataset",
        "ws_title": "Newspaper Headline Analyser",
        "ws_subtitle": "Marathi & English Headline Classification and Tone Analysis Workspace",
        "sample": "Sample headline:",
        "input": "Paste a Marathi or English headline / article:",
        "lang_label": "Language detected:",
        "analyse": "🔍 Analyse News",
        "load": "📂 Load .txt",
        "clear": "✖ Clear",
        "section": "News Section",
        "tone": "News Tone",
        "confidence": "Category Confidence:",
        "log": "Detailed Analysis Log:",
        "score": "Compound score: {:+.2f}   (range −1 to +1)",
        "tone_Positive": "Positive News",
        "tone_Negative": "Negative News",
        "tone_Neutral": "Neutral News",
        "general": "General / Other",
        "no_keywords": "No category keywords found",
        "warn_title": "Incomplete",
        "warn_empty": "Please enter a news headline or article.",
        "log_tokens": "Tokens",
        "log_cat": "▶ Category keywords:",
        "log_sent": "▶ Sentiment words:",
        "log_none": "   (none)",
        "log_neutral": "   (no opinion words – factual / neutral reporting)",
        "lang_mr": "Marathi", "lang_en": "English", "lang_mixed": "Mixed (Marathi + English)", "lang_none": "—",
        "search": "Search:",
        "viewer_title": "Dictionary Dataset Viewer",
    },
    "mr": {
        "subtitle_topic": "मराठी व इंग्रजी वृत्तपत्र बातमी विभाग ओळख व सूर विश्लेषण",
        "launch": "बातमी विश्लेषण कक्ष उघडा ➔",
        "back": "⬅ मुखपृष्ठावर परत",
        "viewer_btn": "📖 शब्दकोश डेटासेट पहा",
        "ws_title": "मराठी व इंग्रजी वृत्तपत्र बातमी विश्लेषक",
        "ws_subtitle": "बातमी मथळा विभाग ओळख व सूर विश्लेषण कक्ष",
        "sample": "नमुना मथळा:",
        "input": "बातमीचा मथळा / मजकूर येथे टाका (मराठी किंवा इंग्रजी):",
        "lang_label": "ओळखलेली भाषा:",
        "analyse": "🔍 विश्लेषण करा",
        "load": "📂 फाइल उघडा",
        "clear": "✖ पुसा",
        "section": "वृत्त विभाग",
        "tone": "बातमीचा सूर",
        "confidence": "विभाग विश्वासार्हता:",
        "log": "विश्लेषण लॉग:",
        "score": "एकत्रित गुण: {:+.2f}   (−1 ते +1)",
        "tone_Positive": "सकारात्मक बातमी",
        "tone_Negative": "नकारात्मक बातमी",
        "tone_Neutral": "तटस्थ बातमी",
        "general": "सामान्य / इतर",
        "no_keywords": "कोणताही विभाग-शब्द सापडला नाही",
        "warn_title": "अपूर्ण",
        "warn_empty": "कृपया बातमीचा मथळा किंवा मजकूर टाका.",
        "log_tokens": "शब्द",
        "log_cat": "▶ विभाग ओळख शब्द:",
        "log_sent": "▶ सूर दर्शवणारे शब्द:",
        "log_none": "   (काहीही नाही)",
        "log_neutral": "   (मत दर्शवणारे शब्द नाहीत – तटस्थ वृत्तांकन)",
        "lang_mr": "मराठी", "lang_en": "इंग्रजी", "lang_mixed": "मिश्र (मराठी + इंग्रजी)", "lang_none": "—",
        "search": "शोधा:",
        "viewer_title": "शब्दकोश डेटासेट",
    },
}

ui_lang = DEFAULT_UI_LANG
last_result = None
translatable = []          # (widget, key, font_kind) re-labelled on every language switch


def T(key):
    return UI_TEXT[ui_lang][key]


def ui_font(size, weight="normal"):
    """Devanagari-capable font for Marathi UI, Segoe UI for English UI."""
    return (DEV_FONT if ui_lang == "mr" else "Segoe UI", size, weight)


def tr(widget, key, size, weight="normal"):
    """Registers a widget whose text follows the current UI language."""
    translatable.append((widget, key, size, weight))
    widget.config(text=T(key), font=ui_font(size, weight))
    return widget


def category_names(category_mr):
    """(primary, secondary) category label for the current UI language."""
    if category_mr not in engine.CATEGORY_ENGLISH:
        return T("general"), ""
    english = engine.CATEGORY_ENGLISH[category_mr]
    return (english, category_mr) if ui_lang == "en" else (category_mr, english)


def set_ui_language(lang):
    global ui_lang
    ui_lang = lang
    for widget, key, size, weight in translatable:
        widget.config(text=T(key), font=ui_font(size, weight))
    for code, btn in lang_buttons:
        btn.config(bg="#F97316" if code == lang else "#CBD5E1", fg="#FFFFFF" if code == lang else "#1E293B")
    if last_result:
        render_result(last_result)
    else:
        clear_results()

# =====================================================================
# 1. NAVIGATION
# =====================================================================
def show_workspace():
    page_front.pack_forget()
    page_workspace.pack(fill=tk.BOTH, expand=True)


def show_front_page():
    page_workspace.pack_forget()
    page_front.pack(fill=tk.BOTH, expand=True)

# =====================================================================
# 2. ACTIONS
# =====================================================================
def load_sample(_event=None):
    text_input.delete("1.0", tk.END)
    text_input.insert("1.0", combo_samples.get())


def load_text_file():
    path = filedialog.askopenfilename(title="Select a news article",
                                      filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not path:
        return
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        messagebox.showerror("Encoding error", "Please save the article as UTF-8 text.")
        return
    text_input.delete("1.0", tk.END)
    text_input.insert("1.0", content)


def clear_results():
    label_category.config(text="—", font=ui_font(18, "bold"))
    label_category_alt.config(text="")
    label_language.config(text=f"{T('lang_label')} —", font=ui_font(10, "bold"))
    label_tone.config(text="—", bg="#E2E8F0", fg="#334155", font=ui_font(14, "bold"))
    label_score.config(text="", font=ui_font(9))
    canvas_bars.delete("all")
    write_log([])


def clear_all():
    global last_result
    last_result = None
    text_input.delete("1.0", tk.END)
    clear_results()


def draw_confidence_bars(ranking):
    canvas_bars.delete("all")
    if not ranking:
        canvas_bars.create_text(10, 20, anchor=tk.W, text=T("no_keywords"), font=ui_font(10), fill="#64748B")
        return
    canvas_bars.update_idletasks()
    width = canvas_bars.winfo_width() or 400
    label_w, bar_x = 170, 180
    max_bar = max(width - bar_x - 60, 50)
    for i, (cat, pct) in enumerate(list(ranking.items())[:4]):
        y = 8 + i * 26
        canvas_bars.create_text(label_w, y + 9, anchor=tk.E, text=category_names(cat)[0],
                                font=ui_font(10, "bold"), fill="#1E293B")
        canvas_bars.create_rectangle(bar_x, y, bar_x + max_bar, y + 18, fill="#E2E8F0", outline="")
        canvas_bars.create_rectangle(bar_x, y, bar_x + max_bar * pct / 100, y + 18,
                                     fill="#4F46E5" if i == 0 else "#A5B4FC", outline="")
        canvas_bars.create_text(bar_x + max_bar + 8, y + 9, anchor=tk.W, text=f"{pct:.0f}%",
                                font=("Segoe UI", 9, "bold"), fill="#334155")


def write_log(lines):
    text_log.config(state=tk.NORMAL)
    text_log.delete("1.0", tk.END)
    for line, tag in lines:
        text_log.insert(tk.END, line + "\n", tag)
    text_log.config(state=tk.DISABLED)


def render_result(result):
    label_language.config(text=f"{T('lang_label')} {T('lang_' + result['language'])}", font=ui_font(10, "bold"))

    primary, secondary = category_names(result["category"])
    label_category.config(text=primary, font=(DEV_FONT, 18, "bold"))
    label_category_alt.config(text=secondary, font=(DEV_FONT, 10))

    tone_key = result["tone"].split("(")[-1].rstrip(")")
    bg, fg = TONE_COLORS[tone_key]
    label_tone.config(text=T("tone_" + tone_key), bg=bg, fg=fg, font=ui_font(14, "bold"))
    label_score.config(text=T("score").format(result["compound"]), font=ui_font(9))
    draw_confidence_bars(result["ranking"])

    log = [(f"{T('log_tokens')} ({len(result['tokens'])}): " + " | ".join(result["tokens"]), "muted"), ("", None)]
    log.append((T("log_cat"), "head"))
    if result["category_evidence"]:
        for tok, root, how, cat, weight, meaning in result["category_evidence"]:
            via = "" if how == "exact" else f"  [{how} → {root}]"
            log.append((f"   • {tok}{via}  ⇒  {category_names(cat)[0]}  (+{weight:g})  — {meaning}", "cat"))
    else:
        log.append((T("log_none"), "muted"))

    log.append(("", None))
    log.append((T("log_sent"), "head"))
    if result["sentiment_items"]:
        for it in result["sentiment_items"]:
            via = "" if it["how"] == "exact" else f"  [{it['how']} → {it['root']}]"
            mods = []
            if it["boost"] != 1.0:
                mods.append(f"×{it['boost']:g}")
            if it["negated"]:
                mods.append("negated")
            mod_txt = f"  ({', '.join(mods)})" if mods else ""
            tag = "pos" if it["score"] > 0 else "neg"
            log.append((f"   • {it['token']}{via}  base {it['base']:+g}{mod_txt}  ⇒  {it['score']:+.1f}  — {it['meaning']}", tag))
    else:
        log.append((T("log_neutral"), "muted"))
    for note in result["sentiment_notes"]:
        log.append((f"   ↳ {note}", "muted"))

    write_log(log)


def handle_analysis():
    global last_result
    news_text = text_input.get("1.0", tk.END).strip()
    if not news_text:
        messagebox.showwarning(T("warn_title"), T("warn_empty"))
        return
    last_result = engine.analyse_news(news_text)
    render_result(last_result)

# =====================================================================
# 3. DICTIONARY DATASET VIEWER
# =====================================================================
def open_dictionary_viewer():
    win = tk.Toplevel(root)
    win.title(T("viewer_title"))
    win.geometry("760x540")
    win.configure(bg="#F1F5F9")

    search_var = tk.StringVar()
    top = tk.Frame(win, bg="#F1F5F9", padx=10, pady=8)
    top.pack(fill=tk.X)
    tk.Label(top, text=T("search"), font=ui_font(10, "bold"), bg="#F1F5F9").pack(side=tk.LEFT)
    tk.Entry(top, textvariable=search_var, font=(DEV_FONT, 11), width=30).pack(side=tk.LEFT, padx=8)

    notebook = ttk.Notebook(win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def make_tab(title, columns, rows):
        frame = tk.Frame(notebook)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor=tk.W)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        notebook.add(frame, text=f"{title} ({len(rows)})")
        return tree, rows

    tabs = []
    for lang, lang_title, meaning_col in (("mr", "Marathi", "English Meaning"), ("en", "English", "मराठी अर्थ")):
        res = engine.RESOURCES[lang]
        cat_rows = [(w, f"{c} ({engine.CATEGORY_ENGLISH[c]})", f"{wt:g}", m)
                    for w, (c, wt, m) in sorted(res["category"].items(), key=lambda x: x[1][0])]
        sent_rows = (
            [(w, "positive" if s > 0 else "negative", f"{s:+g}", m) for w, (s, m) in res["polarity"].items()]
            + [(w, "intensifier", f"×{s:g}", m) for w, (s, m) in res["intensifier"].items()]
            + [(w, "negation", "flip", m) for w, (s, m) in res["negation"].items()]
        )
        tabs.append(make_tab(f"{lang_title} News Keywords", ("Word", "Category", "Weight", meaning_col), cat_rows))
        tabs.append(make_tab(f"{lang_title} Sentiment", ("Word", "Type", "Score", meaning_col), sent_rows))

    style = ttk.Style(win)
    style.configure("Treeview", font=(DEV_FONT, 10), rowheight=26)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def refresh(*_):
        q = search_var.get().strip().lower()
        for tree, rows in tabs:
            tree.delete(*tree.get_children())
            for row in rows:
                if not q or any(q in str(cell).lower() for cell in row):
                    tree.insert("", tk.END, values=row)

    search_var.trace_add("write", refresh)
    refresh()

# =====================================================================
# 4. WINDOW
# =====================================================================
root = tk.Tk()
root.title("Marathi & English Newspaper Headline Classifier & Sentiment Tagger")
root.geometry("900x800")
root.minsize(760, 720)
root.configure(bg="#0F172A")


def make_lang_switch(parent, bg):
    """मराठी | English toggle shown on both pages."""
    frame = tk.Frame(parent, bg=bg)
    for code, label in (("mr", "मराठी"), ("en", "English")):
        btn = tk.Button(frame, text=label, font=(DEV_FONT, 9, "bold"), relief="flat", padx=10, pady=2,
                        cursor="hand2", command=lambda c=code: set_ui_language(c))
        btn.pack(side=tk.LEFT, padx=(0, 2))
        lang_buttons.append((code, btn))
    return frame


lang_buttons = []          # (lang_code, button) for every toggle on every page

# ---------------------------------------------------------------------
# FRAME 1: ACADEMIC FRONT PAGE
# ---------------------------------------------------------------------
page_front = tk.Frame(root, bg="#0F172A", padx=40, pady=30)
page_front.pack(fill=tk.BOTH, expand=True)

make_lang_switch(page_front, "#0F172A").pack(anchor=tk.E)

tk.Label(page_front, text="Artificial Intelligence and Data Science", font=("Helvetica", 16, "bold"),
         fg="#94A3B8", bg="#0F172A").pack(pady=(4, 5))
tk.Label(page_front, text="Natural Language Processing Mini-Project", font=("Helvetica", 14, "italic"),
         fg="#F59E0B", bg="#0F172A").pack(pady=(0, 20))

frame_topic = tk.Frame(page_front, bg="#3B1D0F", highlightbackground="#F97316", highlightthickness=2, padx=20, pady=20)
frame_topic.pack(fill=tk.X, pady=15)
tk.Label(frame_topic, text="📰 PROJECT TOPIC", font=("Helvetica", 10, "bold"), fg="#FDBA74", bg="#3B1D0F").pack(anchor=tk.W, pady=(0, 5))
tk.Label(frame_topic, text="Dictionary-Based Bilingual (Marathi & English) Newspaper\nHeadline Classifier & Sentiment Tagger",
         font=("Helvetica", 16, "bold"), fg="#FFFFFF", bg="#3B1D0F", justify=tk.LEFT).pack(anchor=tk.W)
tr(tk.Label(frame_topic, fg="#FED7AA", bg="#3B1D0F"), "subtitle_topic", 13, "bold").pack(anchor=tk.W, pady=(6, 0))

frame_credentials = tk.Frame(page_front, bg="#0F172A", pady=25)
frame_credentials.pack(fill=tk.X)

frame_student = tk.Frame(frame_credentials, bg="#1E293B", padx=15, pady=15)
frame_student.pack(side=tk.LEFT, anchor=tk.N, expand=True, fill=tk.BOTH, padx=(0, 10))
tk.Label(frame_student, text="SUBMITTED BY:", font=("Helvetica", 9, "bold"), fg="#F59E0B", bg="#1E293B").pack(anchor=tk.W)
tk.Label(frame_student, text=f"Name: {STUDENT_NAME}", font=("Helvetica", 11, "bold"), fg="#E2E8F0", bg="#1E293B").pack(anchor=tk.W, pady=(8, 2))
tk.Label(frame_student, text=f"Roll No: {ROLL_NO}", font=("Helvetica", 10), fg="#94A3B8", bg="#1E293B").pack(anchor=tk.W, pady=2)
tk.Label(frame_student, text=f"Batch: {BATCH}", font=("Helvetica", 10), fg="#94A3B8", bg="#1E293B").pack(anchor=tk.W, pady=2)

stats = engine.dataset_stats()
frame_data = tk.Frame(frame_credentials, bg="#1E293B", padx=15, pady=15)
frame_data.pack(side=tk.LEFT, anchor=tk.N, expand=True, fill=tk.BOTH, padx=(10, 0))
tk.Label(frame_data, text="DICTIONARY DATASET:", font=("Helvetica", 9, "bold"), fg="#F59E0B", bg="#1E293B").pack(anchor=tk.W)
mr, en = stats["mr"], stats["en"]
for line in (
    f"News sections: {stats['categories']}",
    f"Marathi: {mr['category_words']} keywords, {mr['positive_words']}+ / {mr['negative_words']}− sentiment words",
    f"English: {en['category_words']} keywords, {en['positive_words']}+ / {en['negative_words']}− sentiment words",
    f"Modifiers: {mr['intensifiers'] + en['intensifiers']} intensifiers, {mr['negations'] + en['negations']} negations",
):
    tk.Label(frame_data, text=line, font=("Helvetica", 10), fg="#94A3B8", bg="#1E293B").pack(anchor=tk.W, pady=2)

tr(tk.Button(page_front, bg="#F97316", fg="#FFFFFF", activebackground="#EA580C", activeforeground="#FFFFFF",
             relief="flat", padx=20, pady=12, cursor="hand2", command=show_workspace),
   "launch", 11, "bold").pack(pady=(25, 0))

# ---------------------------------------------------------------------
# FRAME 2: NEWS ANALYSIS WORKSPACE
# ---------------------------------------------------------------------
page_workspace = tk.Frame(root, bg="#F1F5F9", padx=25, pady=15)

bar_top = tk.Frame(page_workspace, bg="#F1F5F9")
bar_top.pack(fill=tk.X)
tr(tk.Button(bar_top, bg="#64748B", fg="#FFFFFF", activebackground="#475569", activeforeground="#FFFFFF",
             relief="flat", padx=10, pady=4, command=show_front_page), "back", 9, "bold").pack(side=tk.LEFT)
tr(tk.Button(bar_top, bg="#0EA5E9", fg="#FFFFFF", activebackground="#0284C7", activeforeground="#FFFFFF",
             relief="flat", padx=10, pady=4, command=open_dictionary_viewer), "viewer_btn", 9, "bold").pack(side=tk.RIGHT)
make_lang_switch(bar_top, "#F1F5F9").pack(side=tk.RIGHT, padx=10)

tr(tk.Label(page_workspace, fg="#9A3412", bg="#F1F5F9"), "ws_title", 18, "bold").pack(pady=(4, 0))
tr(tk.Label(page_workspace, fg="#64748B", bg="#F1F5F9"), "ws_subtitle", 10).pack(pady=(0, 8))

row_sample = tk.Frame(page_workspace, bg="#F1F5F9")
row_sample.pack(fill=tk.X, pady=(0, 4))
tr(tk.Label(row_sample, fg="#475569", bg="#F1F5F9"), "sample", 10, "bold").pack(side=tk.LEFT)
combo_samples = ttk.Combobox(row_sample, values=SAMPLE_HEADLINES, state="readonly", font=(DEV_FONT, 10))
combo_samples.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
combo_samples.bind("<<ComboboxSelected>>", load_sample)

row_label = tk.Frame(page_workspace, bg="#F1F5F9")
row_label.pack(fill=tk.X, pady=(4, 2))
tr(tk.Label(row_label, fg="#475569", bg="#F1F5F9"), "input", 11, "bold").pack(side=tk.LEFT)
label_language = tk.Label(row_label, fg="#0369A1", bg="#F1F5F9")
label_language.pack(side=tk.RIGHT)
text_input = tk.Text(page_workspace, height=3, font=(DEV_FONT, 13), bg="#FFFFFF", fg="#1E293B", relief="solid", bd=1,
                     wrap=tk.WORD, padx=8, pady=6)
text_input.pack(fill=tk.X)
text_input.insert("1.0", SAMPLE_HEADLINES[0])

row_buttons = tk.Frame(page_workspace, bg="#F1F5F9")
row_buttons.pack(fill=tk.X, pady=10)
tr(tk.Button(row_buttons, bg="#F97316", fg="#FFFFFF", activebackground="#EA580C", activeforeground="#FFFFFF",
             relief="flat", pady=6, cursor="hand2", command=handle_analysis),
   "analyse", 12, "bold").pack(side=tk.LEFT, fill=tk.X, expand=True)
tr(tk.Button(row_buttons, bg="#334155", fg="#FFFFFF", relief="flat", padx=12, pady=8, command=load_text_file),
   "load", 10, "bold").pack(side=tk.LEFT, padx=(8, 0))
tr(tk.Button(row_buttons, bg="#94A3B8", fg="#FFFFFF", relief="flat", padx=12, pady=8, command=clear_all),
   "clear", 10, "bold").pack(side=tk.LEFT, padx=(8, 0))

# Result cards
row_cards = tk.Frame(page_workspace, bg="#F1F5F9")
row_cards.pack(fill=tk.X)

card_cat = tk.Frame(row_cards, bg="#EEF2FF", highlightbackground="#6366F1", highlightthickness=1, padx=12, pady=8)
card_cat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
tr(tk.Label(card_cat, fg="#4338CA", bg="#EEF2FF"), "section", 10, "bold").pack(anchor=tk.W)
label_category = tk.Label(card_cat, fg="#312E81", bg="#EEF2FF")
label_category.pack(anchor=tk.W)
label_category_alt = tk.Label(card_cat, fg="#6366F1", bg="#EEF2FF")
label_category_alt.pack(anchor=tk.W)

card_tone = tk.Frame(row_cards, bg="#FFFFFF", highlightbackground="#CBD5E1", highlightthickness=1, padx=12, pady=8)
card_tone.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
tr(tk.Label(card_tone, fg="#475569", bg="#FFFFFF"), "tone", 10, "bold").pack(anchor=tk.W)
label_tone = tk.Label(card_tone, padx=10, pady=4)
label_tone.pack(anchor=tk.W, pady=(2, 2))
label_score = tk.Label(card_tone, fg="#64748B", bg="#FFFFFF")
label_score.pack(anchor=tk.W)

tr(tk.Label(page_workspace, fg="#4338CA", bg="#F1F5F9"), "confidence", 10, "bold").pack(anchor=tk.W, pady=(10, 0))
canvas_bars = tk.Canvas(page_workspace, height=110, bg="#FFFFFF", highlightthickness=1, highlightbackground="#CBD5E1")
canvas_bars.pack(fill=tk.X)

tr(tk.Label(page_workspace, fg="#9A3412", bg="#F1F5F9"), "log", 10, "bold").pack(anchor=tk.W, pady=(10, 0))
text_log = tk.Text(page_workspace, height=9, font=(DEV_FONT, 10), bg="#FFF7ED", fg="#1E293B", state=tk.DISABLED,
                   relief="solid", bd=1, padx=10, pady=6, wrap=tk.WORD)
text_log.pack(fill=tk.BOTH, expand=True)
text_log.tag_configure("head", font=(DEV_FONT, 10, "bold"), foreground="#9A3412")
text_log.tag_configure("cat", foreground="#3730A3")
text_log.tag_configure("pos", foreground="#15803D")
text_log.tag_configure("neg", foreground="#B91C1C")
text_log.tag_configure("muted", foreground="#64748B")

set_ui_language(DEFAULT_UI_LANG)
root.mainloop()
