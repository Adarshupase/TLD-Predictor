from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import random
import joblib
import logging
from sklearn.feature_extraction.text import TfidfVectorizer

# If vectorizer was pickled as a subclass, define the same name so unpickling succeeds.
# If not needed, you can remove this class.
class TfidfProgress(TfidfVectorizer):
    pass

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load model and vectorizer once at startup
logging.info("Loading model and vectorizer...")
model = joblib.load("tld_predictor.pkl")
vectorizer = joblib.load("tld_vectorizer.pkl")
logging.info("Model and vectorizer loaded.")

app = Flask(__name__)
CORS(app)

# load gameplay dataset (balanced)
df = pd.read_csv("fair_game_play.csv", dtype=str, low_memory=False)
df = df.dropna(subset=["base_name", "category", "tld"]).reset_index(drop=True)
logging.info("Gameplay dataset loaded (%d rows).", len(df))

@app.route("/api/question")
def get_question():
    # choose a random row
    row = df.sample(1).iloc[0]
    domain, category, true_tld = row["base_name"], row["category"], row["tld"]

    text = [f"{domain} {category}"]
    try:
        X = vectorizer.transform(text)
        probs = model.predict_proba(X)[0]
        classes = model.classes_
    except Exception as e:
        logging.exception("Prediction failed")
        return jsonify({"error": "prediction failed"}), 500

    # top-4 predicted classes with scores
    scored = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
    top4 = scored[:4]
    options = [t for t, _ in top4]

    # ensure true answer present (deterministic choice if reproducible required)
    if true_tld not in options:
        idx = random.Random(domain + category).randint(0, 3)  # deterministic per domain+category
        options[idx] = true_tld

    random.shuffle(options)  # shuffle for UI

    # log predictions and actual
    logging.info("NEW QUESTION: domain=%s category=%s", domain, category)
    logging.info("Top predictions (class -> score): %s", ", ".join([f"{t}:{s:.4f}" for t, s in top4]))
    logging.info("Returned options: %s | true: %s", options, true_tld)

    # return options and optionally the scores for each option
    # build a dict mapping option -> score (score 0 if not in predicted classes)
    score_map = {t: float(s) for t, s in scored}
    options_with_scores = [{"tld": opt, "score": score_map.get(opt, 0.0)} for opt in options]

    return jsonify({
        "domain": domain,
        "category": category,
        "options": options,                    # list of tld strings (shuffled)
        "options_with_scores": options_with_scores,  # optional detailed
        "answer": true_tld
    })

if __name__ == "__main__":
    logging.info("Starting Flask server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)  # set debug=False for production
