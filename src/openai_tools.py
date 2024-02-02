from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def get_embedding(text, model="text-embedding-3-large"):
   text = text.replace("\n", " ")
   client = OpenAI()
   embed = client.embeddings.create(input = [text], model=model).data[0].embedding
   return np.array(embed).reshape(1, -1)


def add_embedding(df, model="text-embedding-3-large"):
    df["embedding"] = df["entry"].apply(lambda x: get_embedding(x, model=model))
    return df


def search_entries(df, search, n=3, pprint=False):
    embed = get_embedding(search)
    results = get_similar_entries(df, embed, n=n)
    if pprint:
        for r in results.entry.values:
            print(r)
            print()
    return results


def get_similar_entries(df, embed, n=3):
    n = int(n)
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, embed))
    results = df.sort_values("similarity", ascending=False).head(n + 1).iloc[1:]
    return results
