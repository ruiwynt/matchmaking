"""
Matchmaking algorithm for Coup matches, based on an elo rating.

For each player in the queue, give the other players a score based on elo, rank distance from seed, and 
how many times they haven't been put into a game. The formula is:

Score = 1/R^(d*log(n))

Where:
- R = rank
- d = number of standard deviations away from average elo difference from seed

If a player isn't within +- 100*(10*e^(-0.3n)+1)*(t+1) elo of the seed, where t is the time the player spent waiting in queue,
then set their score to 0 so they can't be selected.

Normalise all scores so that they sum to 1, then use those as the probability the player is selected to be in the match.

To select other players after the first, set their probability to zero and rescale their probabilities to sum to 1. Repeat until
there are five people selected.
"""
import sys
import json
import numpy as np

score = lambda R, d, n: 1/R**(np.log(n)*d)
search_adj = lambda n: 10*np.exp(-0.3*n) + 1

ELO_RANGE = 100

def match(players, seed_i, n):
    """Create a single match using players[seed_i] as the seed player, if possible"""
    players = sorted(players, key=lambda x: x[1]) # player[0] = name, player[1] = elo, player[3] = time in queue
    ranks = np.array([abs(i-seed_i) for i in range(len(players))], dtype=np.float32) # absolute rank of player relative to seed

    elo_diffs = np.array([players[i][1] for i in range(len(players))], dtype=np.float32) - players[seed_i][1]
    elo_diffs_std = np.abs(elo_diffs/np.std(elo_diffs)) # Scaling values in terms of the standard deviation

    scores = np.array([score(ranks[i], elo_diffs_std[i], len(players)) for i in range(len(players))])
    scores[seed_i] = 0

    possible_players = 0
    for i in range(len(scores)):
        # If the player's elo is out of the seed player's elo searching range, then set their score to zero
        if np.abs(players[i][1] - players[seed_i][1]) > ELO_RANGE*search_adj(n)*(players[seed_i][2]+1):
            scores[i] = 0
        else:
            possible_players += 1

    if possible_players < 5:
        return

    p = scores/sum(scores)
    match = [players[seed_i]]
    for i in range(4):
        chosen = np.random.choice(np.arange(len(players)), p=p)
        match.append(players[chosen])
        p[chosen] = 0
        if sum(p) > 0:
            p = p/sum(p)
    return match

def select_seed_weighted(players):
    """Randomly select a seed player based on how much time they've spent in queue"""
    queue_time = np.array([player[2] for player in players])
    if sum(queue_time) == 0:
        return np.random.choice(np.arange(len(players)))
    else:
        p = queue_time/sum(queue_time)
        return np.random.choice(np.arange(len(players)), p=p)

def match_all(players):
    """Generate as many fair matches as possible from a given set of players."""
    matches = []
    times_matched = 0
    n = len(players)
    while times_matched < 5 and len(players) > 4:
        players_picked = 0
        while len(players) > 4 and players_picked < len(players):
            seed_i = select_seed_weighted(players)
            new_match = match(players, seed_i, n)
            if new_match:
                players = [player for player in players if player not in new_match]
                matches.append([player[0] for player in new_match])
            players_picked += 1
        players = [(player[0], player[1], player[2]+1) for player in players]
        times_matched += 1
    return matches

def format_data(path):
    """Parse JSON data from Elo csv file into list form"""
    players = []
    queue_times = []
    latest_match_time = 0
    with open(path, "r") as f:
        headers = f.readline()
        for line in f:
            # 1: elo, 7: last_contest_time, 10: handle
            line = line.strip()
            elements = line.split(",")
            players.append((elements[10], int(elements[1])))
            queue_times.append(int(elements[7]))
            latest_match_time = max(latest_match_time, int(elements[7]))
    queue_times = latest_match_time - np.array(queue_times)
    players = [players[i] + (queue_times[i],) for i in range(len(players))]
    return players

def write_matches(matches):
    """Write matches into the match.json file"""
    matches_dict = dict()
    for i in range(len(matches)):
        matches_dict[i] = matches[i]
    with open("matches.json", "w") as f:
        f.write(json.dumps(matches_dict))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please pass name of JSON file as a command line argument.")
        sys.exit(2)
    
    # Read JSON file into program
    players = format_data(sys.argv[1]) # ./Elo-MMR/data/coup/all_players.csv

    np.set_printoptions(precision=6, suppress=True)
    # players = [
    #     ("1", 2800, 0),
    #     ("2", 1500, 0),
    #     ("3", 1700, 0),
    #     ("4", 1600, 0),
    #     ("5", 1000, 3),
    #     ("6", 2828, 0),
    #     ("7", 2812, 0),
    #     ("8", 741, 6),
    #     ("9", 2045, 0),
    #     ("10", 2623, 0),
    #     ("14", 2400, 0),
    #     ("15", 2450, 0),
    #     ("11", 1515, 0),
    #     ("12", 1138, 2),
    #     ("13", 1965, 0),
    # ]

    # players = [
    #     ("1", 1400, 2),
    #     ("2", 1600, 0),
    #     ("3", 1500, 0),
    #     ("4", 1550, 0),
    #     ("5", 1670, 0),
    #     ("6", 1300, 4),
    #     ("7", 1450, 0),
    #     ("8", 1800, 1),
    #     ("9", 700, 4),
    #     ("10", 2500, 4)
    # ]

    matches = match_all(players)

    write_matches(matches)