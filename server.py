"""
Web version of the Marathi & English Newspaper Headline Classifier.

Local:      python server.py          -> http://127.0.0.1:5000
Production: gunicorn server:app       (see Procfile / render.yaml)
"""
import os

from flask import Flask, jsonify, render_template, request

import nlp_engine as engine
from project_info import BATCH, PROJECT_TITLE, ROLL_NO, SAMPLE_HEADLINES, STUDENT_NAME

MAX_TEXT_CHARS = 5000

app = Flask(__name__)
app.json.ensure_ascii = False      # send Devanagari as-is, not \u escapes


@app.get("/")
def index():
    return render_template(
        "index.html",
        title=PROJECT_TITLE,
        student={"name": STUDENT_NAME, "roll": ROLL_NO, "batch": BATCH},
        stats=engine.dataset_stats(),
        samples=SAMPLE_HEADLINES,
        categories=engine.CATEGORY_ENGLISH,
    )


@app.post("/api/analyse")
def analyse():
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    if not text:
        return jsonify(error="Please enter a news headline or article."), 400
    if len(text) > MAX_TEXT_CHARS:
        return jsonify(error=f"Text is too long (max {MAX_TEXT_CHARS} characters)."), 413

    result = engine.analyse_news(text)
    result["tone_key"] = result["tone"].split("(")[-1].rstrip(")")
    result["ranking"] = [[cat, pct] for cat, pct in result["ranking"].items()]
    result["category_evidence"] = [
        {"token": t, "root": r, "how": h, "category": c, "weight": w, "meaning": m}
        for t, r, h, c, w, m in result["category_evidence"]
    ]
    return jsonify(result)


@app.get("/api/dataset")
def dataset():
    out = {}
    for lang, res in engine.RESOURCES.items():
        out[lang] = {
            "keywords": [
                {"word": w, "category": c, "category_en": engine.CATEGORY_ENGLISH[c], "weight": wt, "meaning": m}
                for w, (c, wt, m) in sorted(res["category"].items(), key=lambda x: x[1][0])
            ],
            "sentiment": (
                [{"word": w, "type": "positive" if s > 0 else "negative", "score": f"{s:+g}", "meaning": m}
                 for w, (s, m) in res["polarity"].items()]
                + [{"word": w, "type": "intensifier", "score": f"×{s:g}", "meaning": m}
                   for w, (s, m) in res["intensifier"].items()]
                + [{"word": w, "type": "negation", "score": "flip", "meaning": m}
                   for w, (s, m) in res["negation"].items()]
            ),
        }
    return jsonify(out)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
