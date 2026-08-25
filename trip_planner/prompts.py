import json
from trip_planner.models import RankedActivity

def format_ranked_activities_for_prompt(ranked_activities: list[RankedActivity], limit) -> str:
    """
    Convert ranked activities (list of python objects) into JSON format for the LLM prompt
    """
    activities_for_prompt = []

    for ranked_activity in ranked_activities[:limit]:
        activity = ranked_activity.activity

        activities_for_prompt.append(
            {
                "name": activity.name,
                "category": activity.category,
                "tags": activity.tags,
                "latitude": activity.latitude,
                "longitude": activity.longitude,
                "similarity_score": round(ranked_activity.similarity_score, 3),
            }
        )

    # Serialize list of activities to json string
    return json.dumps(activities_for_prompt, indent=2)

def build_itinerary_prompt(city: str, country: str, vibe: str, energy_level: str, ranked_activities: list[RankedActivity]) -> str:
    activity_options = format_ranked_activities_for_prompt(ranked_activities, limit=20)
    
    return f"""
You are a helpful AI trip planner.

Create a realistic 1-day itinerary for the user.

User preferences:
- City: {city}
- Country: {country}
- Vibe: {vibe}
- Energy level: {energy_level}

You must build the itinerary using ONLY the provided OpenStreetMap activity options below.

OpenStreetMap activity options:
{activity_options}

Return ONLY valid JSON.
Do not include markdown.
Do not wrap the response in ```json.
Do not add a top-level "itinerary" key.

The JSON must match this exact structure:

{{
  "city": "{city}",
  "country": "{country}",
  "vibe": "{vibe}",
  "energy_level": "{energy_level}",
  "summary": "A short overview of the itinerary.",
  "sections": [
    {{
      "name": "Morning",
      "stops": [
        {{
          "time": "9:00 AM",
          "name": "Exact name of one provided OpenStreetMap activity option",
          "description": "Short description based only on the provided category and tags.",
          "why_it_fits": "Why this stop fits the user's vibe and energy level.",
          "estimated_duration_minutes": 60,
          "estimated_cost": "Free",
          "category": "Exact category from the selected OpenStreetMap activity option",
          "tags": ["Exact tags from the selected OpenStreetMap activity option"]
        }}
      ]
    }},
    {{
      "name": "Afternoon",
      "stops": []
    }},
    {{
      "name": "Evening",
      "stops": []
    }}
  ],
  "notes": ["Check opening hours before going."]
}}

Rules:
- Use exactly three sections: Morning, Afternoon, and Evening.
- Each section should have 1 to 3 stops.
- Do not overpack the day.
- Use the exact energy_level value "{energy_level}" in lowercase.
- Do not use "Low", "Medium", or "High". Use "low", "medium", or "high".
- Every stop must use the exact name, category, and tags from one selected OpenStreetMap activity option.
- Every stop name must exactly match one of the provided OpenStreetMap activity option names.
- Do not invent places that are not in the provided OpenStreetMap activity options.
- Do not invent, rename, simplify, or reinterpret categories.
- Do not convert categories into broad labels like "Food", "Nightlife", or "Activity".
- Do not invent exact opening hours, exact prices, menus, events, or reservation availability.
- Do not invent exact prices. If cost is unknown, use "Varies" or "Check official website".
- Every itinerary stop must come from the provided OpenStreetMap activity options.
- You may give general planning reminders, such as checking opening hours, booking requirements, entry policies, or official websites.
- Do not claim that a specific place requires reservations, has cover charges, age restrictions, or special policies unless that information appears in the provided activity data.
"""