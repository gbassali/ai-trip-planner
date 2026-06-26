from dotenv import load_dotenv
from trip_planner.llm import GeminiClient
from trip_planner.prompts import build_itinerary_prompt
from trip_planner.ranking import build_user_query, rank_activities
from trip_planner.osm import fetch_activities, limit_activities_per_category
from trip_planner.geocoding import geocode_city_to_bounding_box

def main():
    city = input("Enter the city you're visiting: ")
    country = input("Enter the country of the city: ")
    vibe = input("Enter the vibe you're looking for: ")
    energy_level = input("Enter your energy level (low, medium, high): ").lower().strip()
    
    if energy_level not in ['low', 'medium', 'high']:
        print("Energy level must be one of 'low', 'medium', or 'high'.")
        return
    
    llm_client = GeminiClient()
    
    try:
        bounding_box = geocode_city_to_bounding_box(city, country)
    except ValueError as e:
        print(e)
        return
    
    print(f"\nFound bounding box for {city}, {country}: {bounding_box}")
    
    activities = fetch_activities(bounding_box)
    print(f"\nRetrieved {len(activities)} usable activities from OpenStreetMap.")

    activities = limit_activities_per_category(activities, max_per_category=15)

    print(f"Embedding {len(activities)} balanced activities.")

    user_query = build_user_query(vibe, energy_level)
    ranked_activities = rank_activities(llm_client, user_query, activities)

    print("\n--- Activity Rankings ---\n")

    for ranked_activity in ranked_activities[:10]:
        print(
            f"{ranked_activity.similarity_score:.3f} - "
            f"{ranked_activity.activity.name}"
            f"({ranked_activity.activity.category}) "
            f"({ranked_activity.activity.tags})"
        )

    prompt = build_itinerary_prompt(city, country, vibe, energy_level, ranked_activities)
    itinerary = llm_client.generate_itinerary(prompt)

    print("\n--- Your Itinerary ---\n")
    print(f"{itinerary.city}, {itinerary.country} — {itinerary.vibe} vibe, {itinerary.energy_level} energy")
    print(f"\n{itinerary.summary}\n")

    for section in itinerary.sections:
        print(f"## {section.name}")
        for stop in section.stops:
            print(f"- {stop.time}: {stop.name}")
            print(f"  {stop.description}")
            print(f"  Why it fits: {stop.why_it_fits}")
            print(f"  Duration: {stop.estimated_duration_minutes} minutes")
            print(f"  Cost: {stop.estimated_cost}")
            print(f"  Category: {stop.category}")
            print()

    if itinerary.notes:
        print("Notes:")
        for note in itinerary.notes:
            print(f"- {note}")

if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    main()