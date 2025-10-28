from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import random
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

class TfidfProgress(TfidfVectorizer):
    pass  

model = joblib.load("tld_predictor.pkl")
vectorizer = joblib.load("tld_vectorizer.pkl")
app = Flask(__name__)
CORS(app)


df = pd.read_csv("fair_game_play.csv", dtype=str, low_memory=False)
df = df.dropna(subset=["base_name", "category", "tld"]).reset_index(drop=True)

@app.route("/api/question")
def get_question():
    row = df.sample(1).iloc[0]
    domain, category, true_tld = row["base_name"], row["category"], row["tld"]

    text = [f"{domain} {category}"]
    X = vectorizer.transform(text)
    probs = model.predict_proba(X)[0]
    classes = model.classes_

    top = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)[:4]
    options = [t[0] for t in top]

    if true_tld not in options:
        options[random.randint(0, 3)] = true_tld
    random.shuffle(options)

    print("\n ====== NEW QUESTION ======")
    print(f" Domain: {domain}")
    print(f" Category: {category}")
    print(" Top 4 Predicted TLDs (with confidence):")
    for tld, score in top:
        print(f"{tld:<10} → {score:.4f}")
    print("=============================\n")

    # Return question to frontend
    return jsonify({
        "domain": domain,
        "category": category,
        "options": options,
        "answer": true_tld
    })

if __name__ == "__main__":
    print(" Starting Flask server at http://localhost:5000")
    print(" Endpoint available: /api/question\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
