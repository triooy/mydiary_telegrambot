import openai
from sklearn.metrics.pairwise import cosine_similarity


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]


def add_embedding(df, model="text-embedding-ada-002"):
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
