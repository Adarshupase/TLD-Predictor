import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib
from tqdm import tqdm
DATA_PATH = "/domain_to_tld_trainable.csv"
GAME_PATH = "fair_game_play.csv"
MAX_PER_TLD = 10000        # cap per TLD to reduce .com bias
MAX_FEATURES = 400_000     
RANDOM_STATE = 42


print("Loading dataset...")
df = pd.read_csv(DATA_PATH, dtype=str, low_memory=False)
df = df.dropna(subset=["base_name", "tld"])
print(f"Loaded {len(df):,} rows total")

print(f"\nBalancing dataset: limiting each TLD to {MAX_PER_TLD} samples...")
balanced = []
for tld, group in tqdm(df.groupby("tld"), total=df["tld"].nunique()):
    if len(group) > MAX_PER_TLD:
        group = group.sample(MAX_PER_TLD, random_state=RANDOM_STATE)
    balanced.append(group)
df = pd.concat(balanced).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
print(f"Balanced dataset size: {len(df):,}\n")

df["input_text"] = (
    df["base_name"]
    .str.lower()
    .str.replace(r"[^a-z0-9]", " ", regex=True)
    .str.strip() + " website"
)

print("Building TF-IDF features (char n-grams 3–7)...")
vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(3, 7),
    max_features=MAX_FEATURES,
    sublinear_tf=True,
    norm="l2"
)

X = vectorizer.fit_transform(df["input_text"])
y = df["tld"]
print(f"TF-IDF matrix: {X.shape}\n")

print("Creating validation split (10%)...")
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.1, stratify=y, random_state=RANDOM_STATE
)
print(f"Train: {X_train.shape[0]:,} | Validation: {X_val.shape[0]:,}\n")

print("Training Logistic Regression (improved config)...")
model = LogisticRegression(
    solver="saga",
    C=1.5,                # slightly less regularization
    max_iter=800,
    n_jobs=-1,
    verbose=1
)
model.fit(X_train, y_train)

print("\nEvaluating model on validation split...")
y_pred = model.predict(X_val)
val_acc = accuracy_score(y_val, y_pred)
print(f"Validation Accuracy: {val_acc * 100:.2f}%\n")
print(classification_report(y_val, y_pred, zero_division=0))

joblib.dump(model, "tld_base_predictor_v2.pkl")
joblib.dump(vectorizer, "tld_base_vectorizer_v2.pkl")
print("\nSaved model → tld_base_predictor_v2.pkl")
print("Saved vectorizer → tld_base_vectorizer_v2.pkl\n")

print("Evaluating on fair gameplay dataset...")
game_df = pd.read_csv(GAME_PATH, dtype=str, low_memory=False)
game_df = game_df.dropna(subset=["base_name", "tld"])
game_df["input_text"] = (
    game_df["base_name"]
    .str.lower()
    .str.replace(r"[^a-z0-9]", " ", regex=True)
    .str.strip() + " website"
)

X_game = vectorizer.transform(game_df["input_text"])
y_game = game_df["tld"]
y_pred_game = model.predict(X_game)

game_acc = accuracy_score(y_game, y_pred_game)
print(f"\nFair Gameplay Accuracy: {game_acc * 100:.2f}%")
print(classification_report(y_game, y_pred_game, zero_division=0))
