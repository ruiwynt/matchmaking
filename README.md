# Game Scheduling Algorithms - Elo Rating + Matchmaking Algorithm

The scripts in this directory (once finished) will take data from the webserver, calculate Elo ratings, and create a .json file containing matches to be played. Each match contained within the output json file will be passed into separate submission supervisor instances, and the games will be played.

Once the game engine finishes, it passes back the result of the matches in json format. The new matches will be sent to the webserver for handling and storage.

## Usage
Certain packages must be installed before `./schedule_match.sh` will run. To create the environment, these commands should be included in the Dockerfile (adapt apt to whatever package manager alpine uses):
- `sudo apt-get -y upgrade && sudo apt-get -y update`
- `sudo apt-get -y install gcc sshguard pkg-config libssl-dev git`

Once finished, `./schedule_match.sh` will create the .json file.

## Data Required
`schedule_match.sh` requires all historical match data from the webserver to run statelessly.

A player's time in queue is the number of times they weren't placed into a game by the matchmaking algorithm. This can be retrieved using the `./Elo-MMR/cache/coup/all_players.csv` file. Players might not get a match because:
1. There are less than 5 players in total left to be matched.
2. There are less than 5 players within the seed player's elo matching range.

See `matchmaking.py` for an explanation on how the matchmaking algorithm works.

## Script Workflow

1. Load game history data into a Python script which writes it into .json files in the `./Elo-MMR/cache/coup` directory.
2. Read the outputted `./Elo-MMR/cache/coup/all_players.csv` file into the matchmaking script.
3. Matchmaking script matches players into games of five players.
4. Resulting matches are written into `./matches.json`.
5. Call the `../scheduler/scheduler.py` script for each match in `./matches.json`
6. Read output returned by the game engine (not sure how this will work).
7. Send results of matches back to the webserver, along with the new time in queue values for each player.