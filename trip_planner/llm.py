from google import genai
from dotenv import load_dotenv
from pydantic import ValidationError

from trip_planner.models import Itinerary

load_dotenv()

# This file defines a GeminiClient class that wraps the GenAI client and provides methods for generating itineraries and getting embeddings.
class GeminiClient:
    def __init__(self, generation_model: str = "gemini-3-flash-preview", embedding_model: str = "gemini-embedding-2"):
        self.client = genai.Client() # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        self.generation_model = generation_model
        self.embedding_model = embedding_model

    def generate_itinerary(self, prompt: str) -> Itinerary:
        response = self.client.models.generate_content(
            model=self.generation_model, contents=prompt
        )
        raw_text = response.text

        try:
             itinerary = Itinerary.model_validate_json(raw_text) # Check if response is valid JSON and matches the Itinerary schema
             return itinerary
        except ValidationError as e:
             raise ValueError(f"Failed to parse itinerary from LLM response. Error: {e}\nRaw response: {raw_text}")
        
    def get_embedding(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=text,
        )
        # This is a list of embedding objects. We only sent one text, so we take the first embedding.
        return response.embeddings[0].values  