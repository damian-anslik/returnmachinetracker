import functools
import supabase
import os

supabase_client = supabase.create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY"),
)
locations_table = supabase_client.table("locations")


@functools.lru_cache(maxsize=1)
def get_locations() -> list[dict]:
    response = locations_table.select("*").execute()
    response_data = response.data
    return response_data


def get_location_details(location_id: str) -> dict:
    location_data = locations_table.select("*").eq("id", location_id).execute().data[0]
    if not location_data:
        raise ValueError(f"Invalid location_id={location_id}")
    return location_data
