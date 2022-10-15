from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
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
SELECTED_ACTIVITY_TYPES = {"Hike"}

# The first tag will be the destination folder
REGEX_TO_TAGS = {
    r"TMB #\d.*": ["tmb", "hiking"],
    r".*#NZ.*": ["teararoa", "hiking"],
}

GOOGLE_KEY = "AIzaSyC1MId7bFpkLXNAaYhBSTb8jLyiSqzbDtM"

SPOTIFY_SHOW = "spotify:show:7kqx8Nc4qKPCAuOdYNwFx1"
