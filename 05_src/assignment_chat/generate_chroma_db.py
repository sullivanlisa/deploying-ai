import os
import chromadb
import pandas as pd
from pathlib import Path

# 1. Define paths
SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "suggestions_db"
CSV_PATH = SCRIPT_DIR / "sunrise_sunset_suggestions.csv"  # Replace with your CSV file name

# 2. Initialize Persistent Client (Saves data directly to disk)
os.makedirs(DB_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=DB_PATH)

# 3. Create or get your collection
collection = chroma_client.get_or_create_collection(name="suggestions_collection")

# 4. Load CSV data
df = pd.read_csv(CSV_PATH)

# 5. Extract and format columns for ChromaDB
ids = df["ID"].astype(str).tolist()
documents = df["Suggestion"].astype(str).tolist()

# Combine Sunrise and Sunset into metadata dictionaries for filtering
metadatas = [
    {"sunrise": str(row["Sunrise"]), "sunset": str(row["Sunset"])}
    for _, row in df.iterrows()
]

# 6. Safe Batching Loop
# Dynamically fetch the system's safe max batch size (e.g., 5461)
BATCH_SIZE = 5000

print(f"Total rows to import: {len(ids)}. Processing in batches of {BATCH_SIZE}...")

for i in range(0, len(ids), BATCH_SIZE):
    # Slice the data arrays into safe chunks
    batch_ids = ids[i : i + BATCH_SIZE]
    batch_docs = documents[i : i + BATCH_SIZE]
    batch_meta = metadatas[i : i + BATCH_SIZE]
    
    # Add the current chunk to the database
    collection.add(
        ids=batch_ids, 
        documents=batch_docs, 
        metadatas=batch_meta
    )
    print(f"-> Successfully uploaded rows {i} to {i + len(batch_ids)}")

print("\nAll data successfully imported without errors!")