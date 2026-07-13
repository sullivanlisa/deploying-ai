from langchain.tools import tool
from fastmcp import FastMCP
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from pydantic import BaseModel, Field
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import os

load_dotenv()

# 1. Force absolute path lookup
SCRIPT_DIR = Path(__file__).resolve().parent
SECRETS_PATH = SCRIPT_DIR.parent / ".secrets"
load_dotenv(dotenv_path=SECRETS_PATH, override=True)
DB_PATH = SCRIPT_DIR / "chroma_db"

chroma = chromadb.PersistentClient(path=str(DB_PATH))

suggestions = chroma.get_collection(name="activity_recs", 
    embedding_function=OpenAIEmbeddingFunction(
    api_key = os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"))

class Suggestion(BaseModel):
    """Structured suggestion data response."""
    suggestion: str = Field(..., description="The suggestion")
    sunrise: str = Field(..., description="If the suggestion is appropriate for sunrise (Yes/No)")
    sunset: str = Field(..., description="If the suggestion is appropriate for sunset (Yes/No)")


@tool
def recommend_suggestion(query: str, n_results: int = 1) -> list[Suggestion]:
    """Fetches suggestion data based on the query. Returns n_results suggestions."""
    recommendations = get_recs(query, suggestions, n_results)
    return recommendations

def get_recs(query:str, collection:chromadb.api.models.Collection, top_n:int):
    rec_data = collection.query(
        query_texts=[query],
        n_results=top_n
    )
    recommendations = []
    if not rec_data:
        return recommendations
    for rec in rec_data:

        this_rec = Suggestion(
            suggestion=rec.get('suggestion', 'N/A'),
            sunrise=rec.get('sunrise', 'N/A'),
            sunset=rec.get('sunset', 'N/A')
        )
        recommendations.append(this_rec)
    return recommendations

