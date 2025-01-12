import pandas as pd
import itertools
import random
import time
from tqdm import tqdm
from math import comb

adv_stats_file = "data/2324_AdvStats.csv"
ratings_file = "data/2324_Ratings.csv"
adv_stats = pd.read_csv(adv_stats_file, skiprows=1)
ratings = pd.read_csv(ratings_file, skiprows=1)

# Keep only teams ending with " NCAA" in adv_stats, then remove the suffix
adv_stats = adv_stats[adv_stats["School"].str.endswith(" NCAA", na=False)]
adv_stats["School"] = adv_stats["School"].str.replace(" NCAA", "", regex=True)

# Merge, specifying suffixes for overlapping columns
merged = pd.merge(adv_stats, ratings, on="School", how="inner", suffixes=("_adv","_rat"))

# Keep columns needed, then rename
merged = merged[["School","Pace","ORtg_adv","DRtg","SOS_rat","ORB%","TOV%"]]

merged.rename(columns={
    "ORtg_adv": "ORtg",
    "SOS_rat":  "SOS"
}, inplace=True)

# Convert e.g. 15.6 → 0.156
merged["ORB%"] = merged["ORB%"] / 100
merged["TOV%"] = merged["TOV%"] / 100

def simulate_game(team1, team2, std_dev=8):
    possessions = int((team1["Pace"] + team2["Pace"]) / 2)
    t1_ortg = team1["ORtg"] * (1 + (team1["ORB%"] - team2["TOV%"])) + team1["SOS"]
    t2_ortg = team2["ORtg"] * (1 + (team2["ORB%"] - team1["TOV%"])) + team2["SOS"]
    score1 = sum(random.gauss(t1_ortg - team2["DRtg"], std_dev) for _ in range(possessions))
    score2 = sum(random.gauss(t2_ortg - team1["DRtg"], std_dev) for _ in range(possessions))
    return score1 > score2

def monte_carlo(team1, team2, num_simulations=10000):
    wins1 = sum(simulate_game(team1, team2) for _ in range(num_simulations))
    return {
        "Team1": team1["School"],
        "Team2": team2["School"],
        "Team1_Win_Percentage": wins1 / num_simulations * 100,
        "Team2_Win_Percentage": 100 - (wins1 / num_simulations * 100)
    }

start_time = time.time()
records = merged.to_dict("records")
total_combos = comb(len(records), 2)
pairs = itertools.combinations(records, 2)
results = []

for t1, t2 in tqdm(pairs, desc="Simulating", total=total_combos, unit="matchup"):
    results.append(monte_carlo(t1, t2))

pd.DataFrame(results).to_csv("march_madness_python_output.csv", index=False)

end_time = time.time()
execution_time_minutes = (end_time - start_time) / 60
print(f"Execution Time: {execution_time_minutes:.2f} minutes")
