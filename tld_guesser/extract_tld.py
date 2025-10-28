import pandas as pd
import tldextract
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os

INPUT_FILE = "URL_Classification.csv"
OUTPUT_DIR = "processed_chunks"
CHUNK_SIZE = 100_000     
NUM_CORES = cpu_count()  # use all available CPU cores

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_parts(url):
    try:
        if not isinstance(url, str) or not url.startswith("http"):
            return None, None
        ext = tldextract.extract(url)
        return ext.domain.lower(), ext.suffix.lower()
    except Exception:
        return None, None

def process_chunk(chunk_df, chunk_idx):
    print(f"\n Processing chunk {chunk_idx} with {len(chunk_df)} rows...")

    chunk_df["url"] = chunk_df["url"].astype(str).str.strip()
    chunk_df = chunk_df[chunk_df["url"].str.startswith("http", na=False)]

    urls = chunk_df["url"].tolist()
    with Pool(NUM_CORES) as pool:
        results = list(tqdm(pool.imap(extract_parts, urls), total=len(urls), desc=f"Chunk {chunk_idx}"))

    chunk_df[["base_name", "tld"]] = pd.DataFrame(results, index=chunk_df.index)

    chunk_df["category"] = chunk_df["category"].astype(str).str.strip().str.lower()
    chunk_df = chunk_df.dropna(subset=["base_name", "tld"])
    chunk_df = chunk_df[["id", "url", "base_name", "tld", "category"]]

    out_file = os.path.join(OUTPUT_DIR, f"chunk_{chunk_idx}.csv")
    chunk_df.to_csv(out_file, index=False)
    print(f" Saved {out_file} ({len(chunk_df)} valid rows)")

if __name__ == "__main__":
    print(f" Reading large CSV in chunks from {INPUT_FILE} ...")

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

    
