"""Checks for module 00 - onboarding.

Deliberately gentle. The point of module 00 is not the JSON, it is that you have
opened a pull request, watched a robot check it, and had a human approve it. If
you have never done that before, that is the whole week's win.
"""

from __future__ import annotations

from gym.checks import CORE, Check, CheckSuite

REQUIRED = {
    "handle": "your GitHub username, exactly as it appears in your profile URL",
    "name": "what you would like to be called",
    "role": "one short line, e.g. 'PhD researcher, physics' or 'MSc student'",
    "here_for": "one or two sentences: what you want to be able to do by the end",
}

TRACKS = {"data-and-analysis", "ml-and-experiments", "research-ready"}


def profile_is_valid_json(s):
    profile = s.load_json()
    if not isinstance(profile, dict):
        raise AssertionError(f"profile.json should hold one object, got a {type(profile).__name__}")


def profile_has_every_required_field(s):
    profile = s.load_json()
    missing = [key for key in REQUIRED if not str(profile.get(key, "")).strip()]
    if missing:
        detail = "\n".join(f"  {key}: {REQUIRED[key]}" for key in missing)
        raise AssertionError(f"profile.json is missing or blank on:\n{detail}")


def handle_matches_the_folder(s):
    handle = str(s.load_json().get("handle", "")).strip()
    if handle.lower() != s.handle.lower():
        raise AssertionError(
            f'handle is "{handle}" but the folder is submissions/{s.handle}/ - '
            "these have to match, because that is how the site knows the work is yours"
        )


def track_is_one_of_the_three(s):
    track = str(s.load_json().get("track", "")).strip()
    if track not in TRACKS:
        raise AssertionError(
            f'track should be one of {sorted(TRACKS)}, got "{track}". '
            "Pick where you feel you are today - nobody is held to it, and the "
            "stretch checks are there whichever one you choose."
        )


def here_for_is_a_real_sentence(s):
    text = str(s.load_json().get("here_for", "")).strip()
    if len(text) < 30:
        raise AssertionError(
            f'here_for is only {len(text)} characters. Write a bit more - you will be '
            "asked about it at the end, and vague goals are hard to hit."
        )


SUITE = CheckSuite(
    entrypoint="profile.json",
    checks=[
        Check("profile.json is valid JSON", profile_is_valid_json, CORE,
              hint="paste it into a JSON linter if you are stuck - usually a trailing comma"),
        Check("profile.json fills in every required field", profile_has_every_required_field, CORE),
        Check("The handle matches your submissions folder", handle_matches_the_folder, CORE),
        Check("The track is one of the three", track_is_one_of_the_three, CORE),
        Check("here_for says something specific", here_for_is_a_real_sentence, CORE),
    ],
)
