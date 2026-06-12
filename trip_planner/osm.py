import requests
from trip_planner.models import Activity

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# temp bounding box around Ottawa.
# south, west, north, east
OTTAWA_BOUNDING_BOX = "45.395,-75.730,45.445,-75.660"

# Useful OpenStreetMap tags --> expand on this
# Tag Finder: https://tagfinder.osm.ch/search?query=takeaway&lang=en
USEFUL_TAG_KEYS = [
    "cuisine",
    "outdoor_seating",
    "wheelchair",
    "internet_access",
    "takeaway",
    "diet:vegetarian",
    "diet:vegan",
]

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

def normalize_place(place: dict) -> Activity | None:
    """
    Convert one raw OpenStreetMap record into an Activity object
    Returns None when the record is missing info that the trip planner needs
    """
    osm_tags = place.get("tags", {})

    name = osm_tags.get("name")
    category = get_category(osm_tags)
    latitude, longitude = get_coordinates(place)

    if not name or not category or latitude is None or longitude is None:
        return None


    readable_category = category.replace("_", " ")
    activity_tags = build_activity_tags(osm_tags, category)

    # Not an optimal description, only gives some context. Expand on this
    # or potentially get embedding system to just look at tags instead of descriptions for better understanding
    description = f"{name} is listed as a {readable_category} in OpenStreetMap."

    return Activity(
        id=f"{place['type']}-{place['id']}",
        name=name,
        description=description,
        category=readable_category,
        tags=activity_tags,
        latitude=latitude,
        longitude=longitude,
    )

def normalize_places(raw_places: list[dict]) -> list[Activity]:
    """
    Convert raw OpenStreetMap records into normalized Activity objects.
    Unusable & duplicate records are skipped. 
    """
    activities = []
    seen_ids = set()

    for place in raw_places:
        activity = normalize_place(place)

        if activity is None or activity.id in seen_ids:
            continue

        seen_ids.add(activity.id)
        activities.append(activity)

    return activities

def fetch_activities() -> list[Activity]:
    """
    Retrieve places from OpenStreetMap and return normalized activities.
    """
    raw_places = fetch_raw_places()
    return normalize_places(raw_places)

# NORMALIZATION HELPERS
def get_coordinates(place: dict) -> tuple[float | None, float | None]:
    """
    Return a single lat & long for an OpenStreetMap record.

    Nodes store coordinates directly.
    Ways and relations store the approximate location inside "center" when the Overpass query uses `out center`.
    """
    if "lat" in place and "lon" in place:
        return place["lat"], place["lon"]

    center = place.get("center")
    return center.get("lat"), center.get("lon")

def get_category(tags: dict) -> str | None:
    """
    Return the main category for a place
    Order matters --> return the first recognized category
    """
    return (
        tags.get("amenity")
        or tags.get("tourism")
        or tags.get("leisure")
        or tags.get("shop")
    )

def build_activity_tags(osm_tags: dict, category: str) -> list[str]:
    activity_tags = [category.replace("_", " ")]

    for key in USEFUL_TAG_KEYS:
        value = osm_tags.get(key)

        if value:
            readable_key = key.replace("_", " ")
            activity_tags.append(f"{readable_key}: {value}")

    return activity_tags
