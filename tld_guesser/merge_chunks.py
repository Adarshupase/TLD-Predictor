import pandas as pd
import glob

# Path where your chunks are saved
CHUNK_DIR = "processed_chunks"
OUTPUT_FILE = "domain_to_tld_cat.csv"

# Get all chunk files (sorted to maintain order)
files = sorted(glob.glob(f"{CHUNK_DIR}/chunk_*.csv"))

print(f"📂 Found {len(files)} chunk files to merge...")

# Read and concatenate all chunks
df = pd.concat([pd.read_csv(f, dtype=str, low_memory=False) for f in files], ignore_index=True)

# Drop duplicate rows if any
df = df.drop_duplicates()

# Save to single CSV
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Merged all {len(files)} chunks into {OUTPUT_FILE}")
print(f"📊 Final row count: {len(df):,}")
print("\nPreview:")
print(df.head())
