from collections import defaultdict
import requests
from trip_planner.models import Activity

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# temp bounding box around Ottawa.
# south, west, north, east
OTTAWA_BOUNDING_BOX = "45.395,-75.730,45.445,-75.660"

# Useful OpenStreetMap tags --> expand on this
# This info is saved after a place is fetched to form a Activity object.
# Tag Finder: https://tagfinder.osm.ch/search?query=takeaway&lang=en
OSM_DETAIL_TAG_KEYS = [
    "cuisine",
    "outdoor_seating",
    "wheelchair",
    "internet_access",
    "takeaway",
    "diet:vegetarian",
    "diet:vegan",
]

# Used to build Overpass query. We only retrieve places matching one of the tags. 
OSM_CATEGORY_FILTERS = [
    ("amenity", "cafe"),
    ("amenity", "restaurant"),
    ("amenity", "bar"),
    ("amenity", "pub"),
    ("amenity", "nightclub"),
    ("amenity", "music_venue"),
    ("amenity", "theatre"),
    ("amenity", "cinema"),
    ("tourism", "museum"),
    ("tourism", "gallery"),
    ("tourism", "attraction"),
    ("leisure", "park"),
    ("leisure", "garden"),
    ("leisure", "bowling_alley"),
    ("leisure", "escape_game"),
    ("shop", "books"),
]

PRIMARY_CATEGORY_KEYS = ["amenity", "tourism", "leisure", "shop"]

def build_overpass_query(bounding_box: str) -> str:
    """
    Returns an Overpass query to fetch places from OpenStreetMap in a bounding box
    Query gets all nodes, ways, and relations that match the tag filters in OSM_CATEGORY_FILTERS
    """
    query_parts = []

    for key, value in OSM_CATEGORY_FILTERS:
        query_parts.append(f'nwr["{key}"="{value}"]({bounding_box});') # nwr = node, way, relation

    joined_query_parts = "\n      ".join(query_parts)

    return f"""
    [out:json][timeout:25];

    (
      {joined_query_parts}
    );

    out center;
    """

def fetch_raw_places(bounding_box: str) -> list[dict]:
    """
    Fetch raw OpenStreetMap records from the Overpass API for a given bounding box.
    """
    query = build_overpass_query(bounding_box)
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

def fetch_activities(bounding_box: str = OTTAWA_BOUNDING_BOX) -> list[Activity]:
    """
    Retrieve places from OpenStreetMap and return normalized activities.
    """
    raw_places = fetch_raw_places(bounding_box)
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
    if not center:
        return None, None
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
    """
    Build a list of tags for an Activity object based on OpenStreetMap tags.
    """
    activity_tags = [category.replace("_", " ")]

    # Adds all matching category tags to Activity tags list
    # for key in ["amenity", "tourism", "leisure", "shop"]:
    #     value = osm_tags.get(key)
    #     if value:
    #         activity_tags.append(f"{key}: {value.replace('_', ' ')}")

    for key in OSM_DETAIL_TAG_KEYS:
        value = osm_tags.get(key)

        if value:
            readable_key = key.replace("_", " ")
            activity_tags.append(f"{readable_key}: {value}")

    return activity_tags

# To deal with model limitations
def limit_activities_per_category(activities: list[Activity], max_per_category: int = 15,) -> list[Activity]:
    """
    Limit the number of activities per category due to model limitations.
    Groups activities by category & returns a balanced list of activities with a maximum of `max_per_category` activities per category.
    """
    grouped = defaultdict(list)

    for activity in activities:
        grouped[activity.category].append(activity)

    balanced_activities = []

    for category, category_activities in grouped.items():
        balanced_activities.extend(category_activities[:max_per_category])

    return balanced_activities