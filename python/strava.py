import datetime
import json
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import numpy as np
from geojson import LineString
from stravalib import Client
from stravalib.model import Activity

from python.config import (
    ALREADY_PROCESSED_ACTIVITIES,
    REGEX_TO_TAGS,
    SELECTED_ACTIVITY_TYPES,
    STRAVA_ACTIVITY_TYPES,
)


@dataclass
class StravaActivityStatistics:
    distance: float
    elevation_gain: int
    moving_time: datetime.timedelta
    elapsed_time: datetime.timedelta

    @staticmethod
    def from_raw_activity(activity: Activity):
        return StravaActivityStatistics(
            distance=activity.distance.num // 10 / 100,  # keep up to 10m (e.g. 10.34km)
            elevation_gain=int(activity.total_elevation_gain),
            moving_time=activity.moving_time,
            elapsed_time=activity.elapsed_time,
        )

    def format_parameters(self) -> Dict[str, str]:
        return {
            "distance": str(self.distance),
            "elevation_gain": str(self.elevation_gain),
            "moving_time": self.time_to_str(self.moving_time),
            "elapsed_time": self.time_to_str(self.elapsed_time),
        }

    def time_to_str(self, time: datetime.timedelta) -> str:
        seconds = time.seconds
        return f"{seconds // 3600}:{str(seconds % 3600 // 60).zfill(2)}:{str(seconds % 60).zfill(2)}"


@dataclass
class StravaActivity:
    id: int
    title: str
    description: str
    type: str
    start_date: datetime.datetime
    tags: List[str]
    statistics: StravaActivityStatistics
    summary_polyline: str
    photos: Optional[List[str]] = None
    gps_data: Optional[LineString] = None

    def get_center(self):
        data = np.array(self.gps_data["coordinates"])
        center = (np.max(data, axis=0) + np.min(data, axis=0)) / 2
        return center

    @classmethod
    def from_raw_activity(
        cls, activity: Activity, photos: Optional[List[str]] = None, gps_data: Optional[LineString] = None
    ):
        tags = cls.get_activity_tags(activity)
        return StravaActivity(
            id=activity.id,
            title=activity.name,
            description=activity.description,
            type=activity.type,
            start_date=activity.start_date,
            tags=tags,
            statistics=StravaActivityStatistics.from_raw_activity(activity),
            summary_polyline=activity.map.summary_polyline,
            photos=photos,
            gps_data=gps_data,
        )

    @classmethod
    def get_activity_tags(cls, activity: Activity) -> List[str]:
        description = activity.description if activity.description else ""
        for regex, tags in REGEX_TO_TAGS.items():
            try:
                if re.match(regex, activity.name) or re.match(regex, description):
                    return tags
            except Exception as e:
                print(regex, activity.name, activity.description)
                raise e
        return []


class StravaActivityFilter:
    def __init__(
        self,
        remove_already_processed_activities: bool = True,
        only_selected_activity_types: bool = True,
        only_taggable_activities: bool = True,
    ):
        self.already_processed_activities = self._get_already_processed_activities(remove_already_processed_activities)
        self.selected_activity_types = self._get_selected_activity_types(only_selected_activity_types)
        self.regex_to_tags = self._get_regex_to_tags(only_taggable_activities)

    def _get_already_processed_activities(self, remove_already_processed_activities: bool) -> Set[int]:
        if remove_already_processed_activities:
            with open(ALREADY_PROCESSED_ACTIVITIES, "r") as f:
                activities = json.load(f)
            return set(activities)
        else:
            return set()

    def _get_selected_activity_types(self, only_selected_activity_types: bool) -> Set[str]:
        return SELECTED_ACTIVITY_TYPES if only_selected_activity_types else STRAVA_ACTIVITY_TYPES

    def _get_regex_to_tags(self, filter_on_content: bool) -> Dict[str, List[str]]:
        return REGEX_TO_TAGS if filter_on_content else {".*": []}

    def filter(self, activities: List[Activity]) -> List[Activity]:
        activities = self._filter_already_processed_activities(activities)
        activities = self._filter_activity_types(activities)
        activities = self._filter_taggable_activities(activities)
        return activities

    def _filter_already_processed_activities(self, activities: List[Activity]) -> List[Activity]:
        return [activity for activity in activities if activity.id not in self.already_processed_activities]

    def _filter_activity_types(self, activities: List[Activity]) -> List[Activity]:
        return [activity for activity in activities if activity.type in self.selected_activity_types]

    def _filter_taggable_activities(self, activities: List[Activity]) -> List[Activity]:
        return [activity for activity in activities if self._has_tag(activity)]

    def _has_tag(self, activity: Activity) -> bool:
        for pattern, tags in self.regex_to_tags.items():
            name = activity.name if activity.name else ""
            description = activity.description if activity.description else ""
            if re.match(pattern, name) or re.match(pattern, description):
                return True
        return False


class StravaInterface:
    STREAM_TYPES = ["time", "latlng", "altitude", "heartrate"]
    DEFAULT_ACTIVITY_TYPE = {"Hike"}

    def __init__(self, client: Client, strava_client_id: int, strava_client_secret: str, strava_access_token: str):
        self.client = client
        self.strava_client_id = strava_client_id
        self.strava_client_secret = strava_client_secret
        self.strava_access_token = strava_access_token
        self.client.access_token = strava_access_token

    def refresh_client_access_token(self, refresh_token: str, token_expires_at: int):
        if time.time() < token_expires_at:
            return

        refresh_response = self.client.refresh_access_token(
            client_id=self.strava_client_id,
            client_secret=self.strava_client_secret,
            refresh_token=refresh_token,
        )
        self.client.access_token = refresh_response["access_token"]
        self.client.refresh_token = refresh_response["refresh_token"]
        self.client.token_expires_at = refresh_response["expires_at"]

    def get_activities(
        self,
        before: Optional[datetime.datetime] = None,
        after: Optional[datetime.datetime] = None,
        add_photos: bool = True,
        add_gps_data: bool = True,
        activity_filter: StravaActivityFilter = None,
    ):
        raw_activities = self._get_raw_activities(before, after)
        raw_activities = activity_filter.filter(raw_activities)
        activities_photos = self._get_activities_photos(raw_activities, add_photos)
        activities_gps_data = self._get_activities_gps_data(raw_activities, add_gps_data)
        activities = self._to_activities(raw_activities, activities_photos, activities_gps_data)
        return activities

    def _get_raw_activities(self, before: Optional[datetime.datetime], after: Optional[datetime.datetime]):
        return [activity for activity in self.client.get_activities(before=before, after=after)]

    def _get_activities_photos(self, raw_activities, add_photos: bool):
        return [self._get_photos_for_activity(activity.id) if add_photos else None for activity in raw_activities]

    def _get_photos_for_activity(self, activity_id: int) -> List[str]:
        photos = [_ for _ in self.client.get_activity_photos(activity_id, size="800")]
        photos = [photo.urls["800"] for photo in photos if "800" in photo.urls]
        return photos

    def _get_activities_gps_data(self, raw_activities, add_gps_data: bool):
        return [self._get_gps_data_for_activity(activity.id) if add_gps_data else None for activity in raw_activities]

    def _get_gps_data_for_activity(self, activity_id: int) -> LineString:
        gps_data = self.client.get_activity_streams(activity_id, types=self.STREAM_TYPES, resolution="medium")
        gps_data = LineString([(point[1], point[0]) for point in gps_data["latlng"].data])
        return gps_data

    def _to_activities(self, raw_activities, activities_photos, activities_gps_data):
        return [
            StravaActivity.from_raw_activity(activity=activity, photos=photos, gps_data=gps_data)
            for activity, photos, gps_data in zip(raw_activities, activities_photos, activities_gps_data)
        ]

    def _exclude_already_processed_activities(self, raw_activities, already_processed_activities: Set[int]):
        return [activity for activity in raw_activities if activity.id not in already_processed_activities]
