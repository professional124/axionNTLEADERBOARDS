import requests
import pandas as pd
from datetime import datetime
import time

# Team tags you want to track
teams = ["PR2W", "NTPD1", "SSH", "BEEHVE", "RFTP", "S0RC", "TCHR", "NTO", "P1RE"]

# Output file
output_csv = "leaderboard.csv"
timestamp_file = "timestamp.txt"

# Headers to simulate a browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}

all_data = []

for team in teams:
    print(f"[{team}] Fetching API (attempt 1)")
    url = f"https://www.nitrotype.com/api/v2/teams/{team}"
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            members = data['results']['members']
            for member in members:
                all_data.append({
                    'Team': team,
                    'Username': member['name'],
                    'Display Name': member['displayName'],
                    'Races': member['numRaces'],
                    'Points': member['score']
                })
            break  # Success: exit retry loop
        except requests.exceptions.RequestException as e:
            print(f"[{team}] Error: {e} (retrying in 2s)")
            time.sleep(2)
    else:
        print(f"[{team}] No data, skipping.")

# Save to CSV
if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv(output_csv, index=False)
    print(f"✅ Saved {output_csv} with {len(df)} rows")

    # Save timestamp
    with open(timestamp_file, "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"🕒 Timestamp written to {timestamp_file}")
else:
    print("No valid player data found. Check team tags or API responses.")
