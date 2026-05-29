from dotenv import load_dotenv
from trip_planner.llm import LLMClient
from trip_planner.prompts import build_itinerary_prompt

def main():
    city = input("Enter the city you're visiting: ")
    vibe = input("Enter the vibe you're looking for: ")
    energy_level = input("Enter your energy level (low, medium, high): ").lower().strip()
    
    if energy_level not in ['low', 'medium', 'high']:
        print("Energy level must be one of 'low', 'medium', or 'high'.")
        return
    
    prompt = build_itinerary_prompt(city, vibe, energy_level)
    llm_client = LLMClient()
    itinerary = llm_client.generate_itinerary(prompt)

    print("\n--- Your Itinerary ---\n")
    print(f"{itinerary.city} — {itinerary.vibe} vibe, {itinerary.energy_level} energy")
    print(f"\n{itinerary.summary}\n")

    for section in itinerary.sections:
        print(f"## {section.name}")
        for stop in section.stops:
            print(f"- {stop.time}: {stop.name}")
            print(f"  {stop.description}")
            print(f"  Why it fits: {stop.why_it_fits}")
            print(f"  Duration: {stop.estimated_duration_minutes} minutes")
            print()

    if itinerary.notes:
        print("Notes:")
        for note in itinerary.notes:
            print(f"- {note}")

if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    main()