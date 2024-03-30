import functools
import supabase
import os

supabase_client = supabase.create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY"),
)
sessions_table = supabase_client.table("sessions")


def create_session() -> str:
    response = sessions_table.insert({}).execute()
    session_id = response.data[0]["id"]
    return session_id


@functools.lru_cache(maxsize=15)
def check_session_id_is_valid(session_id: str) -> bool:
    response = sessions_table.select("id").eq("id", session_id).execute()
    return len(response.data) > 0
