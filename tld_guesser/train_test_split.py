import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("domain_to_tld_cat.csv", dtype=str, low_memory=False)
df = df.dropna(subset=["base_name", "category", "tld"])

tld_counts = df["tld"].value_counts()
valid_tlds = tld_counts[tld_counts >= 100].index
df = df[df["tld"].isin(valid_tlds)]

print(f" Total usable rows: {len(df):,}")
print(f" Unique TLDs: {len(valid_tlds)}")

train_df, test_df = train_test_split(df, test_size=0.2, stratify=df["tld"], random_state=42)

max_per_tld = 3000 
balanced_game = []

for tld, group in test_df.groupby("tld"):
    if len(group) > max_per_tld:
        group = group.sample(max_per_tld, random_state=42)
    balanced_game.append(group)

balanced_game_df = pd.concat(balanced_game)

train_df = train_df[~train_df.index.isin(balanced_game_df.index)]

train_df.to_csv("tld_train.csv", index=False)
balanced_game_df.to_csv("tld_game_balanced.csv", index=False)

print(f"🎓 Training set: {len(train_df):,}")
print(f"🎮 Balanced gameplay set: {len(balanced_game_df):,}")
print(f"🎯 TLDs in gameplay: {balanced_game_df['tld'].nunique()} unique TLDs")

# Verify balance
print("\nTop 15 TLDs in gameplay data:")
print(balanced_game_df['tld'].value_counts().head(15))
