import random

def simulate_game(team1, team2, is_tournament_game=False):
    """
    Simulates a single game between two teams using advanced stats directly from Sports-Reference.
    """
    # Average possessions between the two teams
    average_possessions = (team1["Pace"] + team2["Pace"]) / 2

    # Use lower variance for tournament games to reflect tighter play
    std_dev = 8 if is_tournament_game else 10

    # Adjust Offensive Ratings based on possession factors and SOS
    team1_adjusted_ORtg = team1["ORtg"] * (1 + (team1["ORB%"] - team2["TOV%"])) + team1["SOS"]
    team2_adjusted_ORtg = team2["ORtg"] * (1 + (team2["ORB%"] - team1["TOV%"])) + team2["SOS"]

    # Simulate scores
    team1_score = sum(random.gauss(team1_adjusted_ORtg - team2["DRtg"], std_dev) for _ in range(int(average_possessions)))
    team2_score = sum(random.gauss(team2_adjusted_ORtg - team1["DRtg"], std_dev) for _ in range(int(average_possessions)))

    return team1_score > team2_score

def monte_carlo_simulation(team1, team2, num_simulations=10000):
    """
    Runs a Monte Carlo simulation to calculate win percentages for two teams.
    """
    team1_wins = sum(simulate_game(team1, team2) for _ in range(num_simulations))
    team2_wins = num_simulations - team1_wins
    return {
        "Team1_Win_Percentage": team1_wins / num_simulations * 100,
        "Team2_Win_Percentage": team2_wins / num_simulations * 100
    }

# Example team stats directly from Sports-Reference
team1_stats = {
    "ORtg": 112.3,    # Offensive Rating (points per 100 possessions)
    "DRtg": 95.4,     # Defensive Rating (points allowed per 100 possessions)
    "Pace": 70.2,     # Possessions per game
    "SOS": 2.3,       # Strength of Schedule
    "ORB%": 0.315,    # Offensive Rebound Percentage (already a decimal)
    "TOV%": 0.156     # Turnover Percentage (already a decimal)
}

team2_stats = {
    "ORtg": 108.5,
    "DRtg": 97.1,
    "Pace": 72.3,
    "SOS": 1.8,
    "ORB%": 0.289,
    "TOV%": 0.167
}

# Run the simulation
results = monte_carlo_simulation(team1_stats, team2_stats)
print(f"Team 1 Win Percentage: {results['Team1_Win_Percentage']:.2f}%")
print(f"Team 2 Win Percentage: {results['Team2_Win_Percentage']:.2f}%")
