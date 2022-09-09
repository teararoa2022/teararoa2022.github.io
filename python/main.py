import argparse
import datetime
import json
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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Pass Strava secrets to Python file")
    parser.add_argument("--strava-client-id", dest="STRAVA_CLIENT_ID")
    parser.add_argument("--strava-client-secret", dest="STRAVA_CLIENT_SECRET")
    parser.add_argument("--strava-access-token", dest="STRAVA_ACCESS_TOKEN")
    parser.add_argument("--strava-refresh-token", dest="STRAVA_REFRESH_TOKEN")
    parser.add_argument("--token-expires-at", dest="TOKEN_EXPIRES_AT", type=int)
    args = parser.parse_args()

    client = Client()
    strava_interface = StravaInterface(
        client,
        strava_client_id=args.STRAVA_CLIENT_ID,
        strava_client_secret=args.STRAVA_CLIENT_SECRET,
        strava_access_token=args.STRAVA_ACCESS_TOKEN,
    )
    strava_interface.refresh_client_access_token(args.STRAVA_REFRESH_TOKEN, args.TOKEN_EXPIRES_AT)

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
