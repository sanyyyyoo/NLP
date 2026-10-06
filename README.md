# Dictionary-Based Bilingual (Marathi & English) Newspaper Headline Classifier & Sentiment Tagger

NLP mini-project (Artificial Intelligence and Data Science).

Paste a Marathi or English newspaper headline/article and the app:

1. **Detects the news section** — राजकारण (Politics), क्रीडा (Sports), अर्थकारण (Business), मनोरंजन (Entertainment),
   आरोग्य (Health), शिक्षण (Education), हवामान व कृषी (Weather & Agriculture), गुन्हे (Crime), तंत्रज्ञान (Technology).
2. **Tags the news tone** — Positive / Negative / Neutral, with negation (`आवडला नाही`, `not good`) and
   intensifier (`खूप`, `very`) handling.

The interface can be switched between English and Marathi.

## Run

There are two front-ends over the same NLP engine and dictionaries.

**Web version (Flask)**

```bash
pip install -r requirements.txt
python server.py
```

Open http://127.0.0.1:5000

**Desktop version (Tkinter)**: no extra packages needed.

```bash
python app.py
```

## Deploy the web version

The repo is ready for any Python host that runs `gunicorn server:app`.

- **Render**: New → Blueprint → pick this repo. `render.yaml` sets the build/start commands and the `/health` check.
  (Or New → Web Service with build `pip install -r requirements.txt` and start `gunicorn server:app`.)
- **Railway / Heroku-style hosts**: they read `Procfile` automatically.
- **PythonAnywhere**: point the WSGI file at `from server import app as application`.

Student details shown on the front page live in `project_info.py`.

### API

| Method | Path | Body / result |
|---|---|---|
| `POST` | `/api/analyse` | `{"text": "..."}` → section, tone, compound score, matched words |
| `GET` | `/api/dataset` | All four dictionaries as JSON |
| `GET` | `/health` | `{"status": "ok"}` |

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

- `nlp_engine.py` — NLP pipeline (no GUI; shared by both front-ends)
- `server.py`, `templates/`, `static/` — web version (Flask)
- `app.py` — desktop version (Tkinter)
- `project_info.py` — student details and sample headlines
