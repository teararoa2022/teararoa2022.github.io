import datetime
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

import spotipy
from jinja2 import Environment, PackageLoader, select_autoescape
from spotipy import SpotifyClientCredentials

from python.config import SPOTIFY_SHOW

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_FILE = BASE_DIR / "_templates" / "spotify_episode_template.txt"
POSTS_DIRECTORY = BASE_DIR / "_posts"

env = Environment(loader=PackageLoader("strava_post"), autoescape=select_autoescape())


@dataclass
class SpotifyEpisode:
    id: int
    description: str
    title: str
    date: datetime.datetime
    uri: str
    photo_url: Optional[str]

    @staticmethod
    def from_episode_dict(episode: Dict):
        return SpotifyEpisode(
            id=episode["id"],
            description=episode["description"],
            title=episode["name"],
            date=datetime.datetime.strptime(episode["release_date"], "%Y-%m-%d"),
            uri=episode["uri"],
            photo_url=episode["images"][0]["url"] if "images" in episode and len(episode["images"]) else None,
        )

    def get_embed_code(self):
        EMBED_CODE = f"""
<iframe style="border-radius:12px"
src="https://open.spotify.com/embed/episode/{self.id}?utm_source=generator"
width="100%" height="232" frameBorder="0" allowfullscreen=""
allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>
"""
        return EMBED_CODE


class SpotifyManager:
    def __init__(self):
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    def get_new_episodes(self, existing_episodes_ids: Set[str]) -> List[SpotifyEpisode]:
        episodes = self.get_all_episodes()
        new_episodes = [
            SpotifyEpisode.from_episode_dict(episode)
            for episode in episodes
            if episode["id"] not in existing_episodes_ids
        ]
        return new_episodes

    def get_all_episodes(self) -> Dict:
        show = self.spotify.show(SPOTIFY_SHOW, market="GB")
        episodes = show["episodes"]["items"]
        return episodes


@dataclass
class SpotifyPostPaths:
    file_name_no_suffix: str
    subfolder_name: str
    abs_post_path: Path

    @classmethod
    def from_episode(cls, episode: SpotifyEpisode, create_paths=True):
        date = episode.date
        file_name_no_suffix = cls.remove_symbols(
            f"{date.year}-{date.month}-{date.day}-" f'{episode.title.lower().replace(" ", "-")}'
        )
        subfolder_name = "podcast"
        spotify_post_paths = SpotifyPostPaths(
            file_name_no_suffix=file_name_no_suffix,
            subfolder_name=subfolder_name,
            abs_post_path=POSTS_DIRECTORY / subfolder_name / (file_name_no_suffix + ".md"),
        )
        if create_paths:
            spotify_post_paths.create_paths()
        return spotify_post_paths

    @classmethod
    def remove_symbols(cls, string: str) -> str:
        return re.sub("[^A-Za-z0-9-]+", "", string)

    def create_paths(self):
        self.abs_post_path.parent.mkdir(parents=True, exist_ok=True)


class SpotifyPost:
    def __init__(self, episode: SpotifyEpisode):
        self.episode = episode
        self.post_paths = SpotifyPostPaths.from_episode(episode)

    def generate(self):
        post_content = self.generate_string_from_template()
        with open(self.post_paths.abs_post_path, "w") as f:
            f.write(post_content)

    def generate_string_from_template(self):
        template = env.get_template("spotify_episode_template.txt")
        template_parameters = {
            "title": f'"{self.episode.title}"',
            "date": self.episode.date.strftime("%Y-%m-%d %H:%M:%S") + " +0200",
            "tags": "podcast",
            "thumbnail": self.episode.photo_url if self.episode.photo_url else "/assets/thumbnail.jpg",
            "visible": "1",
            "embed": self.episode.get_embed_code(),
        }
        return template.render(**template_parameters)
