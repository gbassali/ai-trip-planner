from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import ValidationError

from trip_planner.models import Itinerary

load_dotenv()

# LLMClient is responsible for communicating with the language model to generate itineraries based on user preferences. 
# It uses the Google Gemini API to send prompts and receive responses, which are then validated and parsed into Itinerary objects.
class LLMClient:
    def __init__(self, model_name: str = "gemini-3-flash-preview"):
        self.client = genai.Client() # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        self.model_name = model_name

    def generate_itinerary(self, prompt: str) -> Itinerary:
        response = self.client.models.generate_content(
            model="gemini-3-flash-preview", contents=prompt
        )
        raw_text = response.text

        try:
             itinerary = Itinerary.model_validate_json(raw_text) # Check if response is valid JSON and matches the Itinerary schema
             return itinerary
        except ValidationError as e:
             raise ValueError(f"Failed to parse itinerary from LLM response. Error: {e}\nRaw response: {raw_text}")