import datetime
import sys

import geojson
from geojson import MultiLineString

sys.path.append(".")


import json
import os
from typing import List, Set

from stravalib import Client

from python.config import ALREADY_PROCESSED_ACTIVITIES, ASSETS_DIR, REGEX_TO_TAGS
from python.strava import StravaActivity, StravaActivityFilter, StravaInterface
from python.strava_post import StravaPost


def update_already_processed_activities(original_activities: Set[int], new_activities: List[StravaActivity]):
    new_activities_ids = {activity.id for activity in new_activities}
    activities_to_exclude = original_activities.union(new_activities_ids)
    with open(ALREADY_PROCESSED_ACTIVITIES, "w") as f:
        json.dump(sorted(list(activities_to_exclude)), f)


def export_refresh_token_to_github_env_variables(client: Client):
    env_file = os.getenv("GITHUB_ENV")
    with open(env_file, "a") as f:
        f.write(f"STRAVA_REFRESH_TOKEN={client.refresh_token}")


def generate_posts(strava_interface: StravaInterface) -> List[StravaPost]:
    activity_filter = StravaActivityFilter(
        remove_already_processed_activities=True,
        only_selected_activity_types=True,
        only_taggable_activities=True,
    )
    activities = strava_interface.get_activities(
        after=datetime.datetime.today() - datetime.timedelta(days=180),
        activity_filter=activity_filter,
    )
    strava_posts = [StravaPost(activity) for activity in activities]
    for post in strava_posts:
        post.generate()
    update_already_processed_activities(activity_filter.already_processed_activities, activities)
    return strava_posts


def _compute_data_for_tag(tag_dir):
    data = []
    for folder in sorted(tag_dir.glob("*")):
        if folder.is_dir():
            geojson_file = folder / "gps_data.geojson"
            with open(geojson_file, "r") as f:
                data.append(geojson.load(f)["coordinates"][::10])
    return data


def _export_data_to_geojson(data, tag_dir, tag):
    mls = MultiLineString(data)
    with open(tag_dir / f"{tag}.geojson", "w") as f:
        geojson.dump(mls, f)


def _add_tag_recap_geojson(tag):
    tag_dir = ASSETS_DIR / tag
    if tag_dir.exists() and tag_dir.is_dir():
        data = _compute_data_for_tag(tag_dir)
        _export_data_to_geojson(data, tag_dir, tag)


def add_tags_recap_geojson():
    tags = set.union(*(set(tags) for tags in REGEX_TO_TAGS.values()))
    for tag in tags:
        _add_tag_recap_geojson(tag)


if __name__ == "__main__":
    LOCAL = os.environ.get("LOCAL", False)
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

    strava_posts = generate_posts(strava_interface)
    add_tags_recap_geojson()

    if not LOCAL:
        export_refresh_token_to_github_env_variables(client)
