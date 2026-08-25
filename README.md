# AI Trip Planner

A Python command-line application that creates a one-day city itinerary based on a traveler's preferred vibe and energy level. It retrieves real place candidates from OpenStreetMap, ranks them using Gemini embeddings, and asks Gemini to organize the best matches into a structured itinerary.

The project currently focuses on retrieval, semantic ranking, and grounded itinerary generation. Geographic route optimization and detailed scheduling are planned features.

## How It Works

1. The user enters a city, country, preferred vibe, and energy level.
2. Nominatim converts the city and country into coordinates.
3. The application creates an 8 km search area around the city center.
4. The Overpass API retrieves matching cafes, restaurants, bars, museums, parks, and other activities from OpenStreetMap.
5. The results are normalized into consistent `Activity` objects and balanced across categories.
6. Gemini embeddings represent the user preferences and each activity as vectors.
7. Cosine similarity ranks activities by how closely they match the requested trip.
8. The highest-ranked activities are provided to Gemini as the only allowed itinerary options.
9. Pydantic validates the generated JSON before the itinerary is displayed.

This is a retrieval-augmented generation workflow, but it does not currently use a vector database. OpenStreetMap places are retrieved for each request, embedded, and ranked in memory.

## Features

- City and country geocoding with Nominatim
- Place retrieval through the OpenStreetMap Overpass API
- Filtering and normalization of OpenStreetMap data
- Category balancing before embedding generation
- Semantic activity ranking with Gemini embeddings and cosine similarity
- Grounded itinerary generation restricted to retrieved places
- Structured JSON output validated with Pydantic
- Morning, afternoon, and evening itinerary sections
- Basic safeguards against invented places, categories, prices, and policies

## Tech Stack

| Technology | Purpose |
| --- | --- |
| Python | Application and CLI logic |
| Gemini API | Embeddings and itinerary generation |
| Google GenAI SDK | Gemini API client |
| Pydantic | Data models and generated response validation |
| OpenStreetMap Nominatim | City geocoding |
| OpenStreetMap Overpass API | Place and activity retrieval |
| Requests | HTTP requests to OpenStreetMap services |
| python-dotenv | Local environment variable loading |

## Project Structure

| Path | Responsibility |
| --- | --- |
| `trip_planner/main.py` | Collects user input and coordinates the full planning flow |
| `trip_planner/geocoding.py` | Geocodes cities and builds the search bounding box |
| `trip_planner/osm.py` | Queries OpenStreetMap and normalizes place data |
| `trip_planner/ranking.py` | Creates embeddings and ranks activities with cosine similarity |
| `trip_planner/llm.py` | Wraps the Gemini generation and embedding APIs |
| `trip_planner/prompts.py` | Builds the grounded itinerary prompt |
| `trip_planner/models.py` | Defines Pydantic models for locations, activities, rankings, and itineraries |
| `notes/` | Contains implementation plans and learning notes for each development step |

## Setup

### Prerequisites

- Python 3.10 or newer
- A [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/gbassali/ai-trip-planner.git
   cd ai-trip-planner
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment.

   Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

4. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Create a `.env` file in the repository root:

   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

Run the application from the repository root:

```bash
python -m trip_planner.main
```

The CLI will ask for:

- City
- Country
- Desired vibe, such as `historic exploring day with a fun bar at night`
- Energy level: `low`, `medium`, or `high`

The application prints the retrieved activity count, the highest-ranked matches, and the final itinerary.

## Current Limitations

- The Overpass query only retrieves the categories listed in `OSM_CATEGORY_FILTERS`.
- The current CLI keeps a limited number of places per category to reduce embedding requests.
- Activity embeddings are requested sequentially and are not cached.
- API requests may be affected by Gemini, Nominatim, and Overpass usage limits.

## Roadmap

- Batch and cache activity embeddings
- Improve error handling for API timeouts and quota limits
- Add automated tests for retrieval, normalization, ranking, and response validation

## Data Attribution

Place data is provided by [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) under the Open Database License. Geocoding uses Nominatim, and place retrieval uses the Overpass API.
