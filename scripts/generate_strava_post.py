from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from jinja2 import Environment, PackageLoader, select_autoescape
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_FILE = BASE_DIR / '_templates' / 'strava_hike_template.txt'
POSTS_DIRECTORY = BASE_DIR / '_posts'

MAP_BASE_STRING = '''
{{% leaflet_map {{"zoom" : 13,
                 "divId" : "map_size" }} %}}
    {{% leaflet_marker {{"latitude" : 34.296184,
                       "longitude" : -117.211329,
                       "popupContent": "Arrowhead Pinacles Trail"}} %}} 
    {{% leaflet_geojson {leaflet_geojson} %}}

{{% endleaflet_map %}}
'''


env = Environment(
    loader=PackageLoader("generate_strava_post"),
    autoescape=select_autoescape()
)
map_string = MAP_BASE_STRING.format(leaflet_geojson='"/assets/Afternoon_Hike.geojson"')


@dataclass
class StravaPostVariables:
    title: str
    date: datetime
    assets_folder: str
    tags: List[str]
    visible: int
    leaflet_string: str

    def generate_template(self):
        template = env.get_template("strava_hike_template.txt")
        return template.render(
            title=self.title,
            date=self.date.strftime("%Y-%m-%d %H:%M:%S") + " +0200",
            assets_folder=self.assets_folder,
            tags=' '.join(self.tags),
            visible=self.visible,
            leaflet_string=self.leaflet_string
        )


strava_post_variables = StravaPostVariables(
    title='Prova',
    date=datetime(2022, 8, 12),
    assets_folder='/assets/test_hike/',
    tags=['hiking teararoa'],
    visible=1,
    leaflet_string=map_string
)

file_string = strava_post_variables.generate_template()
with open(POSTS_DIRECTORY / 'teararoa' / '2022-08-12-test-post2.md', 'w') as f:
    f.write(file_string)

