import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timezone

# Your full TEAM_TAGS list
TEAM_TAGS = [
    "PR2W", "NTPD1", "SSH", "BEEHVE", "RFTP", "S0RC", "TCHR", "NTO", "P1RE",
    # (shortened here for readability — include your full list)
]
TEAM_TAGS = sorted(list(set(TEAM_TAGS)), key=TEAM_TAGS.index)

def get_team_data(team_tag, retries=3, delay=2):
    url = f"https://www.nitrotype.com/api/v2/teams/{team_tag}"
    for attempt in range(1, retries + 1):
        try:
            print(f"[{team_tag}] Fetching API (attempt {attempt})")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "OK":
                return data["results"].get("season", []), data["results"].get("stats", [])
            print(f"[{team_tag}] Invalid status: {data.get('status')}")
            return [], []
        except Exception as e:
            print(f"[{team_tag}] Error: {e} (retrying in {delay}s)")
            time.sleep(delay)
    return [], []

def get_team_stats(stats):
    for stat in stats:
        if stat.get("board") == "season":
            return {
                "typed": int(stat.get("typed", 0)),
                "secs":   int(stat.get("secs", 0)),
                "played": int(stat.get("played", 0)),
                "errs":   int(stat.get("errs", 0))
            }
    return {"typed": 0, "secs": 0, "played": 0, "errs": 0}

def calculate_wpm(typed, secs):
    return (typed / 5) / (secs / 60) if secs > 0 else 0

def calculate_accuracy(typed, errs):
    return (typed - errs) / typed if typed > 0 else 0

def calculate_points(wpm, accuracy, races):
    return (100 + (wpm / 2)) * accuracy * races

# Write timestamp
utc_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
with open("timestamp.txt", "w") as f:
    f.write(f"Last Updated: {utc_ts}")

# Create output folder
csv_archive_dir = "csv_archive"
os.makedirs(csv_archive_dir, exist_ok=True)

all_players = []
team_summary = {}

for tag in TEAM_TAGS:
    season_data, stats_data = get_team_data(tag)
    if not season_data:
        print(f"[{tag}] No data, skipping.")
        continue

    ts = get_team_stats(stats_data)
    team_wpm = calculate_wpm(ts["typed"], ts["secs"])
    team_acc = calculate_accuracy(ts["typed"], ts["errs"])
    team_pts = calculate_points(team_wpm, team_acc, ts["played"])

    team_summary[tag] = {
        "Team": tag,
        "TotalPoints": team_pts,
        "Racers": sum(1 for m in season_data if m.get("points") is not None),
        "Races": ts["played"]
    }

    for m in season_data:
        if m.get("points") is None:
            continue

        username = m.get("username", "")

        # Anti-bot check
        try:
            resp = requests.get(
                f"https://magmal-official.fly.dev/api/bots/search/{username}",
                timeout=5
            )
            if resp.json().get("is_bot"):
                print(f"[{tag}] Skipping bot user: {username}")
                continue
        except Exception as e:
            print(f"[{tag}] Bot-check failed for {username}: {e}. Including by default.")

        it, isecs, ierrs, iplayed = (
            int(m.get("typed", 0)),
            int(m.get("secs", 0)),
            int(m.get("errs", 0)),
            int(m.get("played", 0))
        )
        acc = calculate_accuracy(it, ierrs)
        wpm = calculate_wpm(it, isecs)
        pts = calculate_points(wpm, acc, iplayed)

        all_players.append({
            "Username":    username,
            "ProfileLink": f"https://www.nitrotype.com/racer/{username}",
            "DisplayName": m.get("displayName", "Unknown"),
            "Title":       m.get("title", "No Title"),
            "CarID":       m.get("carID", 0),
            "CarHueAngle": m.get("carHueAngle", 0),
            "Speed":       wpm,
            "Races":       iplayed,
            "Points":      pts,
            "Accuracy":    acc * 100,
            "Team":        tag
        })

if all_players:
    df = pd.DataFrame(all_players).sort_values("Points", ascending=False)
    date_stamp = datetime.utcnow().strftime("%Y%m%d")
    df.to_csv(os.path.join(csv_archive_dir, f'nitrotype_season_leaderboard_{date_stamp}.csv'), index=False)

    df2 = pd.DataFrame(team_summary.values()).sort_values("TotalPoints", ascending=False)
    df2.to_csv(os.path.join(csv_archive_dir, f'nitrotype_team_leaderboard_{date_stamp}.csv'), index=False)
else:
    print("No valid player data found. Check team tags or API responses.")
