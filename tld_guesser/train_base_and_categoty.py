
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib


df = pd.read_csv("tld_train.csv", dtype=str, low_memory=False)
df = df.dropna(subset=["base_name", "category", "tld"])

df["input_text"] = df["base_name"].str.lower() + " " + df["category"].str.lower()

print(f" Training on {len(df):,} samples...")


vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2,5), max_features=500_000)
X = vectorizer.fit_transform(df["input_text"])
y = df["tld"]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(" Training model...")
model = LogisticRegression(max_iter=1000, n_jobs=-1, verbose=1)
model.fit(X_train, y_train)


y_pred = model.predict(X_test)
print("\n Evaluation:")
print(classification_report(y_test, y_pred, zero_division=0))
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")

joblib.dump(model, "tld_predictor.pkl")
joblib.dump(vectorizer, "tld_vectorizer.pkl")
print("\n Model saved -> tld_predictor.pkl")
print(" Vectorizer saved -> tld_vectorizer.pkl")
