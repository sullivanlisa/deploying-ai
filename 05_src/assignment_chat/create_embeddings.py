import os
import time
import openai  
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
SCRIPT_DIR = Path(__file__).resolve().parent.parent
SECRETS_PATH = SCRIPT_DIR / ".secrets"
load_dotenv(dotenv_path=SECRETS_PATH, override=True)


SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "sunrise_sunset_suggestions.csv"
DB_PATH = SCRIPT_DIR / "chroma_db"

df = pd.read_csv(str(CSV_PATH))

chroma_client = chromadb.PersistentClient(path=str(DB_PATH))

collection = chroma_client.create_collection(
    name = "activity_recs",
    embedding_function = OpenAIEmbeddingFunction(
        model_name="text-embedding-3-small",
        api_key = "any value",
        api_base='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1',
        default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
))

ids = df["ID"].astype(str).tolist()
documents = df["Suggestion"].astype(str).tolist()
metadatas = [
    {"sunrise": row["Sunrise"], "sunset": row["Sunset"]}
    for _, row in df.iterrows()
]

BATCH_SIZE = 50 
MAX_RETRIES = 5  # Maximum times to try a failing batch

print(f"Total rows to process: {len(ids)}.")
print(f"Uploading securely in chunks of {BATCH_SIZE} with retry logic...")

for i in range(0, len(ids), BATCH_SIZE):
    batch_ids = ids[i : i + BATCH_SIZE]
    batch_docs = documents[i : i + BATCH_SIZE]
    batch_meta = metadatas[i : i + BATCH_SIZE]
    
    # Retry management loop for this specific batch
    attempt = 0
    wait_time = 2  # Start with a 2-second delay
    while attempt < MAX_RETRIES:
        try:
            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta
            )
            print(f"-> Successfully embedded and saved rows {i} to {i + len(batch_ids)}")
            break  # Success! Break out of retry loop and move to next batch
            
        except (openai.InternalServerError, openai.APIStatusError) as e:
            attempt += 1
            if attempt == MAX_RETRIES:
                print(f"\n❌ CRITICAL: Batch starting at row {i} failed after {MAX_RETRIES} attempts.")
                raise e  # Stop the program if it keeps failing
                
            print(f"⚠️ OpenAI Server encountered a 502/500 error. Retrying batch in {wait_time}s... (Attempt {attempt}/{MAX_RETRIES})")
            time.sleep(wait_time)
            wait_time *= 2  # Exponential backoff: 2s -> 4s -> 8s -> 16s

print("\n Database creation completely successful!")
