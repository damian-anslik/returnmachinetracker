import tinydb
import dotenv
import json
import os
import supabase

dotenv.load_dotenv()
supabase_client = supabase.create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY"),
)
locations_table = supabase_client.table("locations")


def create_new_location(id: str, name: str, latitude: float, longitude: float) -> dict:
    location_data = {
        "id": id,
        "name": name,
        "lat": latitude,
        "long": longitude,
    }
    locations_table.insert(location_data).execute()
    return location_data


def main():
    with open("raw_locations.json", "r") as f:
        raw_locations = json.load(f)
    for location in raw_locations["locations"]:
        location_name = ", ".join(
            [location["title"], location["city"], location["postal_code"]]
        )
        create_new_location(
            id=location["id"],
            name=location_name,
            latitude=location["lat"],
            longitude=location["lng"],
        )


if __name__ == "__main__":
    main()
