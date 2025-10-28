import pandas as pd
import tldextract
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os

# --- CONFIG ---
INPUT_FILE = "URL_Classification.csv"
OUTPUT_DIR = "processed_chunks"
CHUNK_SIZE = 100_000     # adjust if memory is low (e.g., 50_000)
NUM_CORES = cpu_count()  # use all available CPU cores

# --- ensure output directory exists ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- function to extract base_name and tld safely ---
def extract_parts(url):
    try:
        if not isinstance(url, str) or not url.startswith("http"):
            return None, None
        ext = tldextract.extract(url)
        return ext.domain.lower(), ext.suffix.lower()
    except Exception:
        return None, None

# --- process one chunk ---
def process_chunk(chunk_df, chunk_idx):
    print(f"\n⚙️ Processing chunk {chunk_idx} with {len(chunk_df)} rows...")

    # Clean the URL column
    chunk_df["url"] = chunk_df["url"].astype(str).str.strip()
    chunk_df = chunk_df[chunk_df["url"].str.startswith("http", na=False)]

    # Parallel extraction
    urls = chunk_df["url"].tolist()
    with Pool(NUM_CORES) as pool:
        results = list(tqdm(pool.imap(extract_parts, urls), total=len(urls), desc=f"Chunk {chunk_idx}"))

    # Assign results back
    chunk_df[["base_name", "tld"]] = pd.DataFrame(results, index=chunk_df.index)

    # Clean and reorder
    chunk_df["category"] = chunk_df["category"].astype(str).str.strip().str.lower()
    chunk_df = chunk_df.dropna(subset=["base_name", "tld"])
    chunk_df = chunk_df[["id", "url", "base_name", "tld", "category"]]

    # Save this chunk
    out_file = os.path.join(OUTPUT_DIR, f"chunk_{chunk_idx}.csv")
    chunk_df.to_csv(out_file, index=False)
    print(f"✅ Saved {out_file} ({len(chunk_df)} valid rows)")

# --- main pipeline ---
if __name__ == "__main__":
    print(f"📂 Reading large CSV in chunks from {INPUT_FILE} ...")

    # Read in chunks
    reader = pd.read_csv(
        INPUT_FILE,
        header=0,
        names=["id", "url", "category"],
        dtype=str,
        chunksize=CHUNK_SIZE,
        low_memory=False
    )

    for idx, chunk in enumerate(reader, start=1):
        process_chunk(chunk, idx)

    print("\n🎉 All chunks processed! Combine them later if needed:")
    print(f"   cat {OUTPUT_DIR}/chunk_*.csv > domain_to_tld_cat.csv  (Linux/Mac)")
    print(f"   or use pandas.concat in Python.")
