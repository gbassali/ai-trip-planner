def build_itinerary_prompt(city: str, vibe: str, energy_level: str) -> str:
    return f"""
You are a helpful AI trip planner.

Create a realistic 1-day itinerary for the user.

User preferences:
- City: {city}
- Vibe: {vibe}
- Energy level: {energy_level}

Return ONLY valid JSON.
Do not include markdown.
Do not wrap the response in ```json.
Do not add a top-level "itinerary" key.

The JSON must match this exact structure:

{{
  "city": "{city}",
  "vibe": "{vibe}",
  "energy_level": "{energy_level}",
  "summary": "A short overview of the itinerary.",
  "sections": [
    {{
      "name": "Morning",
      "stops": [
        {{
          "time": "9:00 AM",
          "name": "Name of the stop",
          "description": "Short description of what the user will do.",
          "why_it_fits": "Why this stop fits the user's vibe and energy level.",
          "estimated_duration_minutes": 60,
          "estimated_cost": "Free",
          "category": "Activity",
          "tags": ["low-energy", "relaxed"]
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
- Do not create keys named "morning", "afternoon", "evening", "activities", or "food".
- Put all activities and food options inside the "sections" list as stops.
- Include food stops as normal stops with category "Food".
- Do not invent exact prices. Use values like "Free", "Varies", "$10-20 per person", or "Reservation recommended".
"""