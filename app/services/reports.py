import datetime
import uuid
import supabase
import os

from .locations import get_location_details

# reports_db = tinydb.TinyDB("reports.json", indent=4)
supbase_client = supabase.create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY"),
)
reports_table = supbase_client.table("reports")


def get_reports(num_days: int) -> list[dict]:
    # Return from midnight of now minus num_days
    if num_days == 1:
        date_filter = datetime.datetime.now(datetime.UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        date_filter = datetime.datetime.now(datetime.UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - datetime.timedelta(days=num_days)
    reports = (
        reports_table.select("*")
        .gte("created_at", date_filter.timestamp())
        .execute()
        .data
    )
    return reports


def get_reports_by_location(location_id: str, num_days: int) -> list[dict]:
    # Return from midnight of now minus num_days
    if num_days == 1:
        date_filter = datetime.datetime.now(datetime.UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        date_filter = datetime.datetime.now(datetime.UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - datetime.timedelta(days=num_days)
    request = (
        reports_table.select("*")
        .eq("location_id", location_id)
        .gte("created_at", date_filter.timestamp())
    )
    reports = request.execute().data
    return reports


def get_user_reports_in_last_24_hours(reporter_id: str) -> list[dict]:
    # Check if the reporter has reported the location in the last 24 hours
    date_filter = datetime.datetime.now(datetime.UTC).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    request = (
        reports_table.select("*")
        .eq("reporter_id", reporter_id)
        .gte("created_at", date_filter.timestamp())
    )
    reports = request.execute().data
    return reports


def create_report(
    location_id: str,
    reporter_id: str,
    report_created_at: datetime.datetime = None,
) -> dict:
    # Check if the reporter has reported the location in the last 24 hours
    MAX_REPORTS_PER_USER_PER_DAY = 2
    user_reports = get_user_reports_in_last_24_hours(reporter_id)
    if len(user_reports) >= MAX_REPORTS_PER_USER_PER_DAY:
        raise Exception("User has reached the maximum number of reports per day")
    # Check if user has already reported the location in the last 24 hours
    for report in user_reports:
        if report["location_id"] == location_id:
            raise Exception(
                "User has already reported this location in the last 24 hours"
            )
    get_location_details(location_id)
    report_id = str(uuid.uuid4())
    if report_created_at is None:
        report_created_at = datetime.datetime.now(datetime.UTC)
    report_details = {
        "id": report_id,
        "location_id": location_id,
        "created_at": report_created_at.timestamp(),
        "reporter_id": reporter_id,
    }
    reports_table.insert(report_details).execute().data[0]
    return report_details
