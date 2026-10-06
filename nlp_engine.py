"""
NLP engine for the Bilingual (Marathi + English) Newspaper Headline Classifier & Sentiment Tagger.

Pipeline:
    raw text -> language identification (per token, by script)
             -> normalisation -> tokenisation -> rule-based stemming (language specific)
             -> dictionary lookup (exact / stem / fuzzy)
             -> (a) weighted keyword voting  => news category
             -> (b) lexicon scoring with negation + intensifiers => headline tone
"""
import csv
import difflib
import math
import os
import re
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FUZZY_CUTOFF = 0.88            # category keywords
SENTIMENT_FUZZY_CUTOFF = 0.92  # stricter: a wrong polarity flips the tone
FUZZY_MIN_LEN = {"mr": 4, "en": 5}
NEGATION_WINDOW = 3

CATEGORY_ENGLISH = {
    "राजकारण": "Politics",
    "क्रीडा": "Sports",
    "अर्थकारण": "Business & Economy",
    "मनोरंजन": "Entertainment",
    "आरोग्य": "Health",
    "शिक्षण": "Education",
    "हवामान व कृषी": "Weather & Agriculture",
    "गुन्हे": "Crime & Accidents",
    "तंत्रज्ञान": "Science & Technology",
}
CATEGORY_MARATHI = {en: mr for mr, en in CATEGORY_ENGLISH.items()}

LANG_NAMES = {"mr": "मराठी (Marathi)", "en": "English", "mixed": "मिश्र (Marathi + English)", "none": "—"}

# =====================================================================
# 1. DICTIONARY DATASET LOADING
# =====================================================================
def load_category_dictionary(filename):
    """word -> (marathi_category_key, weight, meaning)"""
    table = {}
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader)                                     # header
        for word, category, weight, meaning in reader:
            category = CATEGORY_MARATHI.get(category.strip(), category.strip())
            table[word.strip().lower()] = (category, float(weight), meaning.strip())
    return table


def load_sentiment_lexicon(filename):
    """Splits a lexicon into polarity words, intensifiers and negations."""
    polarity, intensifiers, negations = {}, {}, {}
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for word, kind, score, meaning in reader:
            word, kind = word.strip().lower(), kind.strip()
            entry = (float(score), meaning.strip())
            if kind == "intensifier":
                intensifiers[word] = entry
            elif kind == "negation":
                negations[word] = entry
            else:
                polarity[word] = entry
    return polarity, intensifiers, negations


def _resources(category_file, sentiment_file):
    polarity, intensifiers, negations = load_sentiment_lexicon(sentiment_file)
    return {"category": load_category_dictionary(category_file), "polarity": polarity,
            "intensifier": intensifiers, "negation": negations}


RESOURCES = {
    "mr": _resources("news_category_dictionary.csv", "marathi_sentiment_lexicon.csv"),
    "en": _resources("english_news_category_dictionary.csv", "english_sentiment_lexicon.csv"),
}

# Backwards-compatible names (Marathi tables)
CATEGORY_DICT = RESOURCES["mr"]["category"]
POLARITY_DICT = RESOURCES["mr"]["polarity"]
INTENSIFIER_DICT = RESOURCES["mr"]["intensifier"]
NEGATION_DICT = RESOURCES["mr"]["negation"]

# =====================================================================
# 2. PRE-PROCESSING: NORMALISATION, TOKENISATION, LANGUAGE ID
# =====================================================================
DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def token_language(token):
    return "mr" if DEVANAGARI.search(token) else "en"


def normalize(text):
    text = text.replace("ऱ्", "र्")                  # eyelash-ra variant -> standard ra
    text = re.sub(r"[।॥]", " ", text)      # danda (।) / double danda (॥)
    text = text.replace("’", "'").replace("`", "'").lower()
    text = re.sub(r"[^ऀ-ॿa-z'\s]", " ", text)  # keep Devanagari + English letters
    return text


def tokenize(text):
    tokens = []
    for tok in normalize(text).split():
        tok = tok.strip("'")
        if tok.endswith("'s"):
            tok = tok[:-2]
        if tok:
            tokens.append(tok)
    return tokens


def merge_english_phrases(tokens):
    """Joins two-word English keywords such as 'world cup' or 'chief minister'."""
    phrases = {w for w in RESOURCES["en"]["category"] if " " in w}
    merged, i = [], 0
    while i < len(tokens):
        if i + 1 < len(tokens) and f"{tokens[i]} {tokens[i + 1]}" in phrases:
            merged.append(f"{tokens[i]} {tokens[i + 1]}")
            i += 2
        else:
            merged.append(tokens[i])
            i += 1
    return merged


def detect_language(tokens):
    langs = {token_language(t) for t in tokens}
    if not langs:
        return "none"
    return langs.pop() if len(langs) == 1 else "mixed"

# =====================================================================
# 3. STEMMING
# =====================================================================
# Marathi attaches case markers / postpositions directly to the noun.
# Each rule is (suffix, list of endings to re-attach to rebuild the dictionary form).
MARATHI_SUFFIX_RULES = [
    ("्यांच्या", ["ा", "ी", ""]), ("्यांमध्ये", ["ा", "ी", ""]), ("्यांना", ["ा", "ी", ""]),
    ("्यांनी", ["ा", "ी", ""]), ("्यांचा", ["ा", "ी", ""]), ("्यांची", ["ा", "ी", ""]),
    ("्यांचे", ["ा", "ी", ""]), ("्याच्या", ["ा", "ी", ""]), ("्याचा", ["ा", "ी", ""]),
    ("्याची", ["ा", "ी", ""]), ("्याचे", ["ा", "ी", ""]), ("्याला", ["ा", "ी", ""]),
    ("्याने", ["ा", "ी", ""]), ("्यात", ["ा", "ी", ""]), ("्यांत", ["ा", "ी", ""]),
    ("्या", ["ा", "ी", ""]),
    ("ेच्या", ["ा", ""]), ("ेतील", ["ा", ""]), ("ेचा", ["ा", ""]), ("ेची", ["ा", ""]),
    ("ेचे", ["ा", ""]), ("ेला", ["ा", ""]), ("ेने", ["ा", ""]), ("ेत", ["ा", ""]),
    ("ांच्या", ["", "ा"]), ("ांमध्ये", ["", "ा"]), ("ांना", ["", "ा"]), ("ांनी", ["", "ा"]),
    ("ांचा", ["", "ा"]), ("ांची", ["", "ा"]), ("ांचे", ["", "ा"]),
    ("ाच्या", ["", "ा"]), ("ामध्ये", ["", "ा"]), ("ातील", ["", "ा"]),
    ("ाचा", ["", "ा"]), ("ाची", ["", "ा"]), ("ाचे", ["", "ा"]), ("ाला", ["", "ा"]),
    ("ाने", ["", "ा"]), ("ात", ["", "ा"]),
    ("ींच्या", ["ी"]), ("ींना", ["ी"]), ("ींनी", ["ी"]), ("ूंना", ["ू"]), ("ूंनी", ["ू"]),
    ("ीमुळे", ["", "ी"]), ("ीच्या", ["", "ी"]), ("ीतील", ["", "ी"]), ("ीचा", ["", "ी"]),
    ("ीची", ["", "ी"]), ("ीचे", ["", "ी"]), ("ीला", ["", "ी"]), ("ीने", ["", "ी"]), ("ीत", ["", "ी"]),
    ("मध्ये", [""]), ("साठी", [""]), ("कडून", [""]), ("पर्यंत", [""]), ("मुळे", [""]),
    ("च्या", [""]), ("तील", [""]), ("वर", [""]), ("चा", [""]), ("ची", [""]), ("चे", [""]),
    ("ला", [""]), ("ना", [""]), ("ने", [""]), ("नी", [""]), ("ही", [""]), ("च", [""]), ("त", [""]),
]

# English inflections (a light Porter-style stemmer).
ENGLISH_SUFFIX_RULES = [
    ("ies", ["y"]), ("ied", ["y"]), ("ing", ["", "e"]), ("ed", ["", "e"]), ("es", ["", "e"]),
    ("ers", ["er"]), ("ly", [""]), ("s", [""]),
]


def stem_candidates(token, lang="mr"):
    """Possible dictionary (root) forms of an inflected token, most likely first."""
    rules = MARATHI_SUFFIX_RULES if lang == "mr" else ENGLISH_SUFFIX_RULES
    candidates = [token]
    for suffix, endings in rules:
        if token.endswith(suffix) and len(token) - len(suffix) >= 2:
            stem = token[: -len(suffix)]
            forms = [stem + e for e in endings]
            if lang == "en" and len(stem) > 2 and stem[-1] == stem[-2]:
                forms.append(stem[:-1])                  # winning -> winn -> win
            for form in forms:
                if form not in candidates:
                    candidates.append(form)
    return candidates


def lookup(token, dictionary, lang="mr", cutoff=FUZZY_CUTOFF):
    """Returns (root_word, match_type) or (None, None). match_type: exact | stem | fuzzy."""
    if token in dictionary:
        return token, "exact"
    candidates = stem_candidates(token, lang)
    for cand in candidates[1:]:
        if cand in dictionary:
            return cand, "stem"
    # Fuzzy fallback handles spelling variants (e.g. ु/ू confusion, "goverment").
    best, best_ratio = None, 0.0
    for cand in candidates:
        if len(cand) < FUZZY_MIN_LEN[lang]:
            continue
        for match in difflib.get_close_matches(cand, dictionary.keys(), n=1, cutoff=cutoff):
            ratio = difflib.SequenceMatcher(None, cand, match).ratio()
            if ratio > best_ratio:
                best, best_ratio = match, ratio
    if best:
        return best, "fuzzy"
    return None, None

# =====================================================================
# 4. TASK A: NEWS CATEGORY CLASSIFICATION (weighted keyword voting)
# =====================================================================
def classify_category(tokens):
    scores = defaultdict(float)
    evidence = []
    for tok in tokens:
        lang = token_language(tok)
        table = RESOURCES[lang]["category"]
        root, how = lookup(tok, table, lang)
        if root:
            category, weight, meaning = table[root]
            scores[category] += weight
            evidence.append((tok, root, how, category, weight, meaning))

    total = sum(scores.values())
    if total == 0:
        return "सामान्य / इतर", {}, evidence
    ranked = dict(sorted(((c, s / total * 100) for c, s in scores.items()), key=lambda x: -x[1]))
    return next(iter(ranked)), ranked, evidence

# =====================================================================
# 5. TASK B: HEADLINE TONE (lexicon scoring + negation + intensifiers)
# =====================================================================
def is_negation(tok, lang):
    return tok in RESOURCES[lang]["negation"] or (lang == "en" and tok.endswith("n't"))


def analyse_sentiment(tokens):
    items = []                 # one dict per polarity word found
    pending_boost = 1.0
    pending_negation = None    # index of a negation waiting for the NEXT sentiment word
    notes = []

    for idx, tok in enumerate(tokens):
        lang = token_language(tok)
        res = RESOURCES[lang]

        if tok in res["intensifier"]:
            pending_boost = res["intensifier"][tok][0]
            notes.append(f"'{tok}' intensifier ×{pending_boost:g}")
            continue

        if is_negation(tok, lang):
            target = None
            # Marathi is SOV: negation normally FOLLOWS the word ("चांगला नाही").
            # English negation PRECEDES the word ("not good"), so it always waits.
            if lang == "mr" and tok != "न":
                for item in reversed(items):
                    if idx - item["pos"] <= NEGATION_WINDOW and not item["negated"]:
                        target = item
                        break
            if target:
                target["negated"] = True
                target["score"] *= -1
                notes.append(f"'{tok}' negates '{target['token']}'")
            else:
                pending_negation = idx
                notes.append(f"'{tok}' negates the next sentiment word")
            continue

        root, how = lookup(tok, res["polarity"], lang, SENTIMENT_FUZZY_CUTOFF)
        if root:
            base, meaning = res["polarity"][root]
            negated = pending_negation is not None and idx - pending_negation <= NEGATION_WINDOW
            score = base * pending_boost * (-1 if negated else 1)
            items.append({"token": tok, "root": root, "how": how, "base": base, "boost": pending_boost,
                          "negated": negated, "score": score, "pos": idx, "meaning": meaning})
            pending_boost, pending_negation = 1.0, None

    raw = sum(i["score"] for i in items)
    compound = raw / math.sqrt(raw * raw + 15) if raw else 0.0   # squash into [-1, 1]
    if compound >= 0.05:
        label = "सकारात्मक बातमी (Positive)"
    elif compound <= -0.05:
        label = "नकारात्मक बातमी (Negative)"
    else:
        label = "तटस्थ बातमी (Neutral)"
    return label, compound, items, notes

# =====================================================================
# 6. FULL PIPELINE
# =====================================================================
def analyse_news(text):
    tokens = merge_english_phrases(tokenize(text))
    language = detect_language(tokens)
    category, ranking, cat_evidence = classify_category(tokens)
    tone, compound, sent_items, sent_notes = analyse_sentiment(tokens)
    return {
        "tokens": tokens,
        "language": language,
        "language_name": LANG_NAMES[language],
        "category": category,
        "category_en": CATEGORY_ENGLISH.get(category, "General / Other"),
        "ranking": ranking,
        "category_evidence": cat_evidence,
        "tone": tone,
        "compound": compound,
        "sentiment_items": sent_items,
        "sentiment_notes": sent_notes,
    }


def dataset_stats():
    stats = {}
    for lang, res in RESOURCES.items():
        stats[lang] = {
            "category_words": len(res["category"]),
            "positive_words": sum(1 for s, _ in res["polarity"].values() if s > 0),
            "negative_words": sum(1 for s, _ in res["polarity"].values() if s < 0),
            "intensifiers": len(res["intensifier"]),
            "negations": len(res["negation"]),
        }
    stats["categories"] = len(CATEGORY_ENGLISH)
    return stats
