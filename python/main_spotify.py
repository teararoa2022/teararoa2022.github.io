import sys

from python.spotify import SpotifyEpisode, SpotifyManager, SpotifyPost

sys.path.append(".")


import json
from typing import List, Set

from python.config import ALREADY_PROCESSED_PODCASTS


def update_already_processed_podcasts(original_podcasts: Set[int], new_podcasts: List[SpotifyEpisode]):
    new_podcast_ids = {podcast.id for podcast in new_podcasts}
    podcasts_to_exclude = original_podcasts.union(new_podcast_ids)
    with open(ALREADY_PROCESSED_PODCASTS, "w") as f:
        json.dump(sorted(list(podcasts_to_exclude)), f)


def get_existing_episodes() -> Set[str]:
    with open(ALREADY_PROCESSED_PODCASTS, "r") as f:
        existing_episodes_ids = set(json.load(f))
    return existing_episodes_ids


if __name__ == "__main__":
    spotify = SpotifyManager()

    existing_episodes_ids = get_existing_episodes()
    new_episodes = spotify.get_new_episodes(existing_episodes_ids)

    posts = [SpotifyPost(episode) for episode in new_episodes]
    for post in posts:
        post.generate()

    update_already_processed_podcasts(existing_episodes_ids, new_episodes)
