import requests
import csv
import time
import json

teams = [
    'PR2W', 'NTPD1', 'SSH', 'BEEHVE', 'RFTP', 'S0RC', 'TCHR',
    'NTO', 'P1RE'
]

all_players = []

for team_tag in teams:
    attempts = 0
    while attempts < 3:
        try:
            print(f"[{team_tag}] Fetching API (attempt {attempts+1})")
            response = requests.get(f'https://www.nitrotype.com/api/v2/teams/{team_tag}')
            response.raise_for_status()
            team_data = response.json()

            # Debug print to see full data structure (comment out after checking)
            # print(json.dumps(team_data, indent=2))

            members = team_data.get('team', {}).get('members', [])
            if not members:
                print(f"[{team_tag}] No members found, skipping.")
                break

            for member in members:
                row = {
                    'Team': team_tag,
                    'Username': member.get('name', 'N/A'),
                    'DisplayName': member.get('displayName', 'N/A'),
                    'Races': member.get('races', 0),
                    'Points': member.get('points', 0),
                }
                all_players.append(row)

            break  # Successfully fetched and processed, break retry loop

        except requests.exceptions.HTTPError as e:
            print(f"[{team_tag}] Error: {e} (retrying in 2s)")
            attempts += 1
            time.sleep(2)
        except Exception as e:
            print(f"[{team_tag}] Unexpected error: {e}")
            break

    else:
        print(f"[{team_tag}] No data, skipping.")

if not all_players:
    print("No valid player data found. Check team tags or API responses.")
else:
    keys = ['Team', 'Username', 'DisplayName', 'Races', 'Points']
    with open('team_members.csv', 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_players)

    print(f"Saved {len(all_players)} players to team_members.csv")
