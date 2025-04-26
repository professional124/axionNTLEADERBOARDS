import os
import json
import time
import pandas as pd
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# Your full TEAM_TAGS list here…
TEAM_TAGS = [
    "PR2W", "NTPD1", "SSH", "BEEHVE", "RFTP", "S0RC", "TCHR", "NTO", "P1RE",
    "CAM0", "NCT", "PSR", "N8TE", "FASZ", "SER", "T0WER", "ZH", "LOVGOD", "DLX",
    "RVNT", "RIV4L", "FAM3", "RZ", "EXOTIC", "RI5E", "VFU", "SNTL", "SAIL", "HONT",
    "NTRS34", "NTT", "T3X5", "ST0RM", "DUAL", "AMPX", "TNGN", "ZSH", "VLN",
    "CATPLT", "4CU", "BRAVE", "NS7", "WTRMN", "AL0N3D", "NI1TRO", "LOFH", "DIV1",
    "NTW", "LLJ4R", "UNREST", "NGREEN", "TRUST", "GSGMWO", "LSH", "HZE", "BAYLOR",
    "OVCR", "LTC", "SG1MAS", "XWX", "FERARI", "DCPTCN", "RL1", "RL", "AL3", "HELIUM",
    "NTP444", "SSNAKS", "NHS", "DOGGIS", "2S", "ESTER", "ASPN", "50I", "MED13L",
    "FLAGZ", "W2V", "WPMWPM", "SZM", "4EP", "TGNM", "ZTAGZ", "PIGFLY", "KR0W",
    "TOTUF7", "F0J", "D4RKER", "TALK", "VXL", "LE4GUE", "TWO", "FUZHOU", "SK4P", "VTI",
    "GLZ", "B0MBA", "KAPOK", "ERC", "SPRME", "BMW", "NT20", "NT", "CYCV", "PTB", "XS9",
    "KBSM", "190IQ", "FRLB", "ZER0SE", "PR2WX", "CZBZ", "M1NE", "NTM", "MEYBO",
    "LXW", "ZH", "SPRINT", "EMZ", "BMW", "TVX", "YE1LOW", "B4HL", "LEDIHH", "1BESTW", "ALFJ",
    "GOATOG", "BEES", "A3", "BR34K", "792231", "IQ200", "FOX109", "REB3LS", "LDZ",
    "OER", "1STRED", "EXTRME", "SEDYKO", "BRICS", "P1RE", "LEGNDS", "170MPH",
    "FORKS", "VKS", "YADLRS", "JEDI1", "FG4", "WAMDOO", "201030",
    "HAC33R", "SPDLM", "UNSCF", "CHONT", "VG", "F1ERCE", "TYZ", "EMP1R3", "WP", "TMW",
    "XMVP", "HFE", "TVM", "IR", "AV", "XBTP", "42712", "TDTY",
    "FERAL", "MEYBO", "LZNT", "XIII", "KNTT", "FTHM", "L3JENS", "C0NQUE", "BAR0NS",
    "WERTQY", "TFV", "WP", "QC", "IR", "PIRC", "FTHM", "1STRED", "FFS", "RR", "VIELLE", "VS",
    "SWF", "CAT4", "NTY", "CS", "TMW", "ZL", "SBD2", "TXT", "EMPERR", "LWRK", "NCNT",
    "ECS", "L3JENS", "NTA", "NTA3", "NTA4", "BKYS", "DANCE2", "WPJR", "GLXM", "BPR",
    "USP", "T2V", "J2W", "ENMP", "NXC", "ULZ", "F1F2F3", "CR7LEG", "DANATK", "VRSN", 
    "PAWS", "AGNCY", "100DEV", "M4NTA", "CR0WN5", "DYN", "QX", "P20W", "WD5", "HYP3Z", 
    "SPRIT3", "EL1TE", "SEMI", "DKC", "DASDAE", "HFCASH", "EXCEDE", "OWLS99", "0CE8N", 
    "COMP5", "FZH", "BEGO0D", "MMM0", "DIRTH", "LE9ND", "NTGX", "SNOOPY", "SHIBA", "EG", 
    "CR1", "VTU", "MTC2", "NWH", "PAND96", "EOP", "FTINT", "DSNT", "WUPS", "DOG", "DOGEE", 
    "DTR", "GRZ", "LERS", "M0AN", "I9", "ZEEK", "USAAT", "LR7", "NTWA", "GODM", "GZRS", "DUCCK", 
    "4J", "PALICE", "IBM", "QWST", "DYZ", "DB35T", "TEZLA", "FIAMES", "IMT", "NVSEAL", "NTPTS", 
    "BE3ST1", "NZV", "DDFR", "3X0T15", "XLUVX", "PRETZE", "H0LY", "FS1", "SSME", "GENRAC", 
    "HDIK96", "WBMS12", "UFOUFO", "AURA80", "ON", "FVRSMR", "911000", "DRICE", "DAGRUP", 
    "THEIBD", "R1F", "FAM3", "CZBZ", "TOPGOD", "ENTE", "NBX"

]
TEAM_TAGS = sorted(list(set(TEAM_TAGS)), key=TEAM_TAGS.index)

# --- Selenium Setup (optimized + explicit binary) ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2
})
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)
chrome_options.set_capability("pageLoadStrategy", "eager")

# Explicitly point to system-installed Chrome and ChromeDriver
chrome_options.binary_location = os.getenv(
    "CHROME_BINARY",
    "/usr/bin/google-chrome-stable"
)
driver_service = Service(executable_path=os.getenv(
    "CHROMEDRIVER_PATH",
    "/usr/bin/chromedriver"
))
driver = webdriver.Chrome(service=driver_service, options=chrome_options)
driver.set_page_load_timeout(10)

def get_team_data(driver, team_tag, retries=3, delay=2):
    url = f"https://www.nitrotype.com/api/v2/teams/{team_tag}"
    for attempt in range(1, retries + 1):
        try:
            print(f"[{team_tag}] navigating to API (attempt {attempt})")
            driver.get(url)
            print(f"[{team_tag}] page loaded, extracting JSON…")
            time.sleep(0.5)
            try:
                raw = driver.find_element(By.TAG_NAME, "pre").text
            except:
                raw = driver.find_element(By.TAG_NAME, "body").text
            data = json.loads(raw)
            if data.get("status") == "OK":
                return data["results"].get("season", []), data["results"].get("stats", [])
            print(f"[{team_tag}] API returned status: {data.get('status')}")
            return [], []
        except TimeoutException:
            print(f"[{team_tag}] page load timed out")
            return [], []
        except Exception as e:
            print(f"[{team_tag}] error: {e} (retrying in {delay}s)")
            time.sleep(delay)
    return [], []

def get_team_stats(stats):
    for stat in stats:
        if stat.get("board") == "season":
            return {
                "typed": int(stat.get("typed", 0)),
                "secs":   int(stat.get("secs",   0)),
                "played": int(stat.get("played", 0)),
                "errs":   int(stat.get("errs",   0))
            }
    return {"typed":0,"secs":0,"played":0,"errs":0}

def calculate_wpm(typed, secs):
    return (typed/5)/(secs/60) if secs > 0 else 0

def calculate_accuracy(typed, errs):
    return (typed-errs)/typed if typed > 0 else 0

def calculate_points(wpm, accuracy, races):
    return (100 + (wpm/2)) * accuracy * races

# Write timestamp
utc_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
with open("timestamp.txt", "w") as f:
    f.write(f"Last Updated: {utc_ts}")

# Ensure output folder exists
csv_archive_dir = "csv_archive"
os.makedirs(csv_archive_dir, exist_ok=True)

all_players = []
team_summary = {}

for tag in TEAM_TAGS:
    season_data, stats_data = get_team_data(driver, tag)
    if not season_data:
        print(f"[{tag}] no data, skipping.")
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
        it, isecs, ierrs, iplayed = (
            int(m.get("typed", 0)),
            int(m.get("secs",   0)),
            int(m.get("errs",   0)),
            int(m.get("played", 0))
        )
        acc = calculate_accuracy(it, ierrs)
        wpm = calculate_wpm(it, isecs)
        pts = calculate_points(wpm, acc, iplayed)

        all_players.append({
            "Username":    m.get("username", "N/A"),
            "ProfileLink": f"https://www.nitrotype.com/racer/{m.get('username','')}",
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
    print("No valid player data found. Please verify team tags and API responses.")

driver.quit()
