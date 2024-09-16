from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
INCLUDE_DIR = BASE_DIR / "_includes"
ALREADY_PROCESSED_ACTIVITIES = ASSETS_DIR / "already_processed_activities.json"
ALREADY_PROCESSED_PODCASTS = ASSETS_DIR / "already_processed_podcasts.json"

STRAVA_ACTIVITY_TYPES = {
    "AlpineSki",
    "BackcountrySki",
    "Canoeing",
    "Crossfit",
    "EBikeRide",
    "Elliptical",
    "Golf",
    "Handcycle",
    "Hike",
    "IceSkate",
    "InlineSkate",
    "Kayaking",
    "Kitesurf",
    "NordicSki",
    "Ride",
    "RockClimbing",
    "RollerSki",
    "Rowing",
    "Run",
    "Sail",
    "Skateboard",
    "Snowboard",
    "Snowshoe",
    "Soccer",
    "StairStepper",
    "StandUpPaddling",
    "Surfing",
    "Swim",
    "Velomobile",
    "VirtualRide",
    "VirtualRun",
    "Walk",
    "WeightTraining",
    "Wheelchair",
    "Windsurf",
    "Workout",
    "Yoga",
}
SELECTED_ACTIVITY_TYPES = {"Hike", "Ride", "Kayaking", "Canoeing"}

# The first tag will be the destination folder
REGEX_TO_TAGS = {
    r"Tour du Mont Blanc.*": ["tmb", "hiking"],
    r"Alta Via 9.*": ["altavia9", "hiking"],
    r"Te Araroa.*": ["teararoa", "hiking"],
    r"AT:.*": ["austria", "hiking"],
    r"R:.*": ["reunion", "hiking"],
    r"CH:.*": ["switzerland", "hiking"],
}

GOOGLE_KEY = "AIzaSyC1MId7bFpkLXNAaYhBSTb8jLyiSqzbDtM"

SPOTIFY_SHOW = "spotify:show:1dXhQ0ucwq7zykrM9r5Fbb"
