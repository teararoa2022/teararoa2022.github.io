import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import geojson
from jinja2 import Environment, PackageLoader, select_autoescape

from python.strava import StravaActivity

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_FILE = BASE_DIR / "_templates" / "strava_hike_template.txt"
POSTS_DIRECTORY = BASE_DIR / "_posts"


env = Environment(loader=PackageLoader("strava_post"), autoescape=select_autoescape())


@dataclass
class StravaPostPaths:
    file_name_no_suffix: str
    subfolder_name: str
    assets_folder: Path
    geojson_path: Path

    abs_post_path: Path
    abs_assets_folder: Path
    abs_geojson_path: Path

    @classmethod
    def from_activity(cls, activity: StravaActivity, create_paths=True):
        start_date = activity.start_date
        file_name_no_suffix = cls.remove_symbols(
            f"{start_date.year}-{start_date.month}-{start_date.day}-" f'{activity.title.lower().replace(" ", "-")}'
        )
        subfolder_name = cls.remove_symbols(activity.tags[0]) if len(activity.tags) else "general"
        assets_folder = Path("/assets/") / subfolder_name / file_name_no_suffix
        abs_assets_folder = BASE_DIR / "assets/" / subfolder_name / file_name_no_suffix
        strava_post_paths = StravaPostPaths(
            file_name_no_suffix=file_name_no_suffix,
            subfolder_name=subfolder_name,
            assets_folder=assets_folder,
            geojson_path=assets_folder / "gps_data.geojson",
            abs_post_path=POSTS_DIRECTORY / subfolder_name / (file_name_no_suffix + ".md"),
            abs_assets_folder=abs_assets_folder,
            abs_geojson_path=abs_assets_folder / "gps_data.geojson",
        )
        if create_paths:
            strava_post_paths.create_paths()
        return strava_post_paths

    @classmethod
    def remove_symbols(cls, string: str) -> str:
        return re.sub("[^A-Za-z0-9-]+", "", string)

    def create_paths(self):
        self.abs_assets_folder.mkdir(parents=True, exist_ok=True)
        self.abs_post_path.parent.mkdir(parents=True, exist_ok=True)
        self.abs_geojson_path.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class StravaPostStrings:
    MAP_BASE_STRING = """
{{% leaflet_map {{"zoom" : 13,
                  "center": {leaflet_center},
                 "divId" : "map_size" }} %}}
    {{% leaflet_geojson "{leaflet_geojson}" %}}

{{% endleaflet_map %}}
"""
    PHOTO_BASE_STRING = """
<br />

![]({url})
"""
    title: str
    description: str
    map_string: str
    photo_string: str

    @classmethod
    def from_activity_and_post_paths(cls, activity: StravaActivity, strava_post_paths: StravaPostPaths):
        map_center = activity.get_center()
        map_string = cls.MAP_BASE_STRING.format(
            leaflet_geojson=str(strava_post_paths.geojson_path),
            leaflet_center=f"[{map_center[1]}, {map_center[0]}]",
        )
        photo_string = "\n".join([cls.PHOTO_BASE_STRING.format(url=url) for url in activity.photos])
        return cls(
            title=activity.title,
            description=activity.description if activity.description else "",
            map_string=map_string,
            photo_string=photo_string,
        )


@dataclass
class StravaPostVariables:
    strava_post_strings: StravaPostStrings
    start_date: datetime
    assets_folder: str
    tags: List[str]
    visible: int

    def generate_post(self):
        template = env.get_template("strava_hike_template.txt")
        return template.render(
            title=f'"{self.strava_post_strings.title}"',
            start_date=self.start_date.strftime("%Y-%m-%d %H:%M:%S") + " +0200",
            assets_folder=self.assets_folder,
            tags=" ".join(self.tags),
            visible=self.visible,
            leaflet_string=self.strava_post_strings.map_string,
            description=self.strava_post_strings.description,
            photo_string=self.strava_post_strings.photo_string,
        )


class StravaPost:
    def __init__(self, activity: StravaActivity):
        self.activity = activity

    def generate(self):
        strava_post_paths = StravaPostPaths.from_activity(self.activity, create_paths=True)
        strava_post_strings = StravaPostStrings.from_activity_and_post_paths(self.activity, strava_post_paths)

        strava_post_variables = StravaPostVariables(
            strava_post_strings=strava_post_strings,
            start_date=self.activity.start_date,
            assets_folder=str(strava_post_paths.assets_folder),
            tags=self.activity.tags,
            visible=1,
        )
        post_content = strava_post_variables.generate_post()

        with open(strava_post_paths.abs_geojson_path, "w") as f:
            geojson.dump(self.activity.gps_data, f)
        with open(strava_post_paths.abs_post_path, "w") as f:
            f.write(post_content)
