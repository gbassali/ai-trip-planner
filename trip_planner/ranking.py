import math
from trip_planner.llm import GeminiClient
from trip_planner.models import Activity, RankedActivity
    
# Formula: cosine similarity for 2 vectors = (A . B) / (||A|| * ||B||)
def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Embeddings must have the same number of dimensions.")

    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)

def build_user_query(vibe: str, energy_level: str) -> str:
    return (
        f"The traveler wants a {vibe} experience. "
        f"Their energy level is {energy_level}. " 
        f"Recommend relevant trip activities, attractions, food, nightlife, "
        f"entertainment, parks, museums, bars, cafes, restaurants, and local experiences "
        f"that match the user's preferences."
    )

# Get embedding for a user query
def embed_user_query(client: GeminiClient, query: str) -> list[float]:
    # With gemini-embedding-2 it's recommended to add a task instruction to the prompt
    # https://ai.google.dev/gemini-api/docs/embeddings
    formatted_query = f"task: search result | query: {query}"
    return client.get_embedding(formatted_query)

# Get embedding for an activity
def embed_activity(client: GeminiClient, activity: Activity) -> list[float]:
    text_content = f"Description: {activity.description}, Category: {activity.category}, Tags: {', '.join(activity.tags)}"
    return client.get_embedding(f"title: {activity.name} | content: {text_content}")

# Rank activities based on cosine similarity between user query embedding and activity embeddings
def rank_activities(client: GeminiClient, user_query: str, activities: list[Activity]) -> list[RankedActivity]:
    user_embedding = embed_user_query(client, user_query)
    ranked_activities = []

    for activity in activities:
        activity_embedding = embed_activity(client, activity)
        similarity_score = cosine_similarity(user_embedding, activity_embedding)
        ranked_activities.append(RankedActivity(activity=activity, similarity_score=similarity_score))

    ranked_activities.sort(key=lambda x: x.similarity_score, reverse=True)
    return ranked_activities
