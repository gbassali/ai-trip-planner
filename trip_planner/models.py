from typing import Literal
from pydantic import BaseModel, Field

class ItineraryStop(BaseModel):
    time: str = Field(description="Approximate time of the stop, for example, '9:00 AM'")
    name: str = Field(description="Name of the activity or place")
    description: str = Field(description="Short description of what the user will do or experience at this stop")
    why_it_fits: str = Field(description="A brief explanation of why this stop fits the user's preferences (vibe and energy level)")
    estimated_duration_minutes: int = Field(description="Estimated duration of the stop in minutes")
    estimated_cost: str = Field(description="Estimated cost of the stop, if applicable. For example, 'Free', '$20 per person')")
    category: str = Field(description="Category of the stop, such as 'Activity', 'Food', 'Museum', etc.")
    tags: list[str] = Field(default_factory=list, description="List of tags that describe the stop, such as ['outdoor', 'family-friendly', 'adventurous']")

class ItinerarySection(BaseModel):
    name: str = Field(description="Name of the section, typically 'Morning', 'Afternoon', or 'Evening', 'Lunch', or other time-based sections")
    stops: list[ItineraryStop] = Field(description="List of stops planned for this section of the day")

class Itinerary(BaseModel):
    city: str = Field(description="The city for which the itinerary is planned")
    country: str = Field(description="The country for which the itinerary is planned")
    vibe: str = Field(description="The vibe or atmosphere the user is looking for, such as 'romantic', 'adventurous', 'family-friendly'")
    energy_level: Literal['low', 'medium', 'high'] = Field(description="The user's energy level, which can be 'low', 'medium', or 'high'")
    sections: list[ItinerarySection] = Field(description="List of itinerary sections, typically Morning, Afternoon, and Evening")
    notes: list[str] = Field(default_factory=list, description="Additional notes or tips for the user, such as transportation suggestions, best times to visit certain stops, or any special considerations")
    summary: str = Field(description="A brief summary of the itinerary, highlighting the overall theme and key activities planned for the day")

class Activity(BaseModel):
    id: str = Field(description="Unique identifier for the activity")
    name: str = Field(description="Name of the activity or place")
    description: str = Field(description="Description of the activity or place")
    category: str = Field(description="Category such as cafe, museum, park, or nightlife")
    tags: list[str] = Field(default_factory=list, description="Tags describing the activity and its vibe")
    latitude: float = Field(description="Latitude of the activity")
    longitude: float = Field(description="Longitude of the activity")

class RankedActivity(BaseModel):
    activity: Activity
    similarity_score: float = Field(description="Embedding similarity score between the activity and user preferences")