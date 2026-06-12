import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# temp bounding box around Ottawa.
# south, west, north, east
OTTAWA_BOUNDING_BOX = "45.395,-75.730,45.445,-75.660"

def fetch_raw_places() -> list[dict]:
    """
    Retrieve a small set of real places from OpenStreetMap --> intentionally limited to central Ottawa. 
    We will make the location dynamic.
    """

    query = f"""
    [out:json]
    [timeout:25];

    (
      node["amenity"="cafe"]({OTTAWA_BOUNDING_BOX});
      node["amenity"="restaurant"]({OTTAWA_BOUNDING_BOX});
      node["tourism"="museum"]({OTTAWA_BOUNDING_BOX});
      node["leisure"="park"]({OTTAWA_BOUNDING_BOX});
      node["shop"="books"]({OTTAWA_BOUNDING_BOX});
    );

    out center;
    """
    # gets the center point of each node

    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers = {'Accept': 'application/json', 'Content-Type': 'text/plain', 'User-Agent': 'ai-trip-planner/0.1'},
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()
    return data["elements"]

def print_raw_places(places: list[dict]) -> None:
    for place in places:
        tags = place.get("tags", {})

        name = tags.get("name")
        amenity = tags.get("amenity")
        tourism = tags.get("tourism")
        leisure = tags.get("leisure")
        shop = tags.get("shop")

        category = amenity or tourism or leisure or shop

        print(
            f"id={place['id']} | "
            f"name={name} | "
            f"category={category} | "
            f"lat={place.get('lat')} | "
            f"lon={place.get('lon')}"
        )

if __name__ == "__main__":
    places = fetch_raw_places()

    print(f"Retrieved {len(places)} places.\n")
    print_raw_places(places)