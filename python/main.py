import datetime
import sys

sys.path.append(".")


import json
import os
from typing import List, Set

from stravalib import Client

from python.config import ALREADY_PROCESSED_ACTIVITIES
from python.strava import StravaActivity, StravaActivityFilter, StravaInterface
from python.strava_post import StravaPost


def update_already_processed_activities(original_activities: Set[int], new_activities: List[StravaActivity]):
    new_activities_ids = {activity.id for activity in new_activities}
    activities_to_exclude = original_activities.union(new_activities_ids)
    with open(ALREADY_PROCESSED_ACTIVITIES, "w") as f:
        json.dump(list(activities_to_exclude), f)


def export_refresh_token_to_github_env_variables(client: Client):
    env_file = os.getenv("GITHUB_ENV")
    with open(env_file, "a") as f:
        f.write(f"STRAVA_REFRESH_TOKEN={client.refresh_token}")


if __name__ == "__main__":
    LOCAL = os.environ.get("Local", False)
    STRAVA_CLIENT_ID = int(os.environ["STRAVA_CLIENT_ID"])
    STRAVA_CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
    STRAVA_ACCESS_TOKEN = os.environ["STRAVA_ACCESS_TOKEN"]
    STRAVA_REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]
    TOKEN_EXPIRES_AT = int(os.environ["TOKEN_EXPIRES_AT"])

    client = Client()
    strava_interface = StravaInterface(
        client,
        strava_client_id=STRAVA_CLIENT_ID,
        strava_client_secret=STRAVA_CLIENT_SECRET,
        strava_access_token=STRAVA_ACCESS_TOKEN,
    )
    strava_interface.refresh_client_access_token(STRAVA_REFRESH_TOKEN, TOKEN_EXPIRES_AT)

    activity_filter = StravaActivityFilter(
        remove_already_processed_activities=True,
        only_selected_activity_types=True,
        only_taggable_activities=True,
    )
    activities = strava_interface.get_activities(
        after=datetime.datetime.today() - datetime.timedelta(days=60),
        activity_filter=activity_filter,
    )
    for activity in activities:
        strava_post = StravaPost(activity)
        strava_post.generate()
    update_already_processed_activities(activity_filter.already_processed_activities, activities)

    if not LOCAL:
        export_refresh_token_to_github_env_variables(client)
