# Dictionary-Based Bilingual (Marathi & English) Newspaper Headline Classifier & Sentiment Tagger

NLP mini-project (Artificial Intelligence and Data Science).

Paste a Marathi or English newspaper headline/article and the app:

1. **Detects the news section** — राजकारण (Politics), क्रीडा (Sports), अर्थकारण (Business), मनोरंजन (Entertainment),
   आरोग्य (Health), शिक्षण (Education), हवामान व कृषी (Weather & Agriculture), गुन्हे (Crime), तंत्रज्ञान (Technology).
2. **Tags the news tone** — Positive / Negative / Neutral, with negation (`आवडला नाही`, `not good`) and
   intensifier (`खूप`, `very`) handling.

The interface can be switched between English and Marathi.

## Run

Requires Python 3.8+ (Tkinter ships with the standard Windows/macOS installer; no extra packages).

```bash
python app.py
```

## How it works

```
text → language ID (per word, by script) → normalisation → tokenisation
     → rule-based stemming (Marathi case suffixes / English inflections)
     → dictionary lookup (exact → stem → fuzzy match)
     → (a) weighted keyword voting  ⇒ news section
     → (b) lexicon scoring + negation + intensifiers ⇒ tone (compound score −1 … +1)
```

## Dictionary datasets

| File | Contents |
|---|---|
| `news_category_dictionary.csv` | Marathi news keywords → section, weight, English meaning |
| `marathi_sentiment_lexicon.csv` | Marathi positive/negative words, intensifiers, negations |
| `english_news_category_dictionary.csv` | English news keywords → section, weight, Marathi meaning |
| `english_sentiment_lexicon.csv` | English positive/negative words, intensifiers, negations |

## Files

- `app.py` — Tkinter GUI (front page + analysis workspace + dataset viewer)
- `nlp_engine.py` — NLP pipeline (no GUI; can be imported and tested on its own)
