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
CORS(app,
     resources={r"/api/*": {
         "origins": [
             "http://localhost:5173",
             "https://tld-predictor-1.onrender.com"
         ],
         "methods": ["GET", "POST", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"]
     }})
@app.after_request
def apply_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "https://tld-predictor-1.onrender.com"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response



# load gameplay dataset (fair_game_play) consist of 20 % of the original used for testing
df = pd.read_csv("fair_game_play.csv", dtype=str, low_memory=False)
df = df.dropna(subset=["base_name", "category", "tld"]).reset_index(drop=True)
logging.info("Gameplay dataset loaded (%d rows).", len(df))

@app.route("/api/categories")
def get_categories():
    try:
        categories = sorted(df["category"].dropna().unique().tolist())
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": "Could not load categories"}), 500

@app.route("/api/predict", methods=["POST"])
def predict_tld():
    try:
    text = [f"{base_name} {category}" if category else base_name]
    X = vectorizer.transform(text)
    probs = model.predict_proba(X)[0]
    classes = model.classes_
except Exception as e:
    logging.exception("Prediction failed:")
    return jsonify({"error": str(e)}), 500


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

    if true_tld not in options:
        idx = random.Random(domain + category).randint(0, 3)  # deterministic per domain+category
        options[idx] = true_tld

    random.shuffle(options)  # shuffle for UI

    logging.info("NEW QUESTION: domain=%s category=%s", domain, category)
    logging.info("Top predictions (class -> score): %s", ", ".join([f"{t}:{s:.4f}" for t, s in top4]))
    logging.info("Returned options: %s | true: %s", options, true_tld)

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
    import os
    port = int(os.environ.get("PORT",5000))
    logging.info(f"starting flask server on htpps://0.0.0.0:{port}")
    app.run(host="0.0.0.0",port = port)
