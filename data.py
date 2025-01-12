import pandas as pd
import itertools
import random

# Load and clean the data
adv_stats_file = "data/2324_AdvStats.csv"
ratings_file = "data/2324_Ratings.csv"

adv_stats = pd.read_csv(adv_stats_file, skiprows=1)
ratings = pd.read_csv(ratings_file, skiprows=1)

# Merge the datasets and handle overlapping columns
data = pd.merge(adv_stats, ratings, on="School", how="inner", suffixes=("_adv", "_rating"))

# Select relevant columns explicitly
data = data[["School", "Pace", "ORtg_adv", "DRtg", "SOS_rating", "ORB%", "TOV%"]]
data.rename(columns={"ORtg_adv": "ORtg", "SOS_rating": "SOS"}, inplace=True)

# Convert ORB% and TOV% to decimal format
data["ORB%"] = data["ORB%"] / 100
data["TOV%"] = data["TOV%"] / 100

def simulate_game(team1, team2, is_tournament_game=False):
    average_possessions = (team1["Pace"] + team2["Pace"]) / 2
    std_dev = 8
    team1_adjusted_ORtg = team1["ORtg"] * (1 + (team1["ORB%"] - team2["TOV%"])) + team1["SOS"]
    team2_adjusted_ORtg = team2["ORtg"] * (1 + (team2["ORB%"] - team1["TOV%"])) + team2["SOS"]
    team1_score = sum(random.gauss(team1_adjusted_ORtg - team2["DRtg"], std_dev) for _ in range(int(average_possessions)))
    team2_score = sum(random.gauss(team2_adjusted_ORtg - team1["DRtg"], std_dev) for _ in range(int(average_possessions)))
    return team1_score > team2_score

def monte_carlo_simulation(team1, team2, num_simulations=10000):
    team1_wins = sum(simulate_game(team1, team2) for _ in range(num_simulations))
    team2_wins = num_simulations - team1_wins
    """
    if team1_wins > team2_wins:
        print(team1["School"] + " over " + team2["School"] + ": "+str(round(team1_wins / num_simulations * 100,2))+"% Likely")
    else:
        print(team2["School"] + " over " + team1["School"] + ": "+str(round(team2_wins / num_simulations * 100,2))+"% Likely")
    """
    return {
        "Team1": team1["School"],
        "Team2": team2["School"],
        "Team1_Win_Percentage": team1_wins / num_simulations * 100,
        "Team2_Win_Percentage": team2_wins / num_simulations * 100
    }

team_combinations = itertools.combinations(data.to_dict("records"), 2)
results = [monte_carlo_simulation(team1, team2) for team1, team2 in team_combinations]
results_df = pd.DataFrame(results)
results_df.to_csv("data/simulation_results.csv", index=False)
