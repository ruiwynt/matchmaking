#!/bin/bash

cd Elo-MMR/multi-skill
RUST_LOG=debug cargo run --release --bin rate mmr-fast coup
cd ../..
python matchmaking.py Elo-MMR/data/coup/ratings_output.csv
cat matches.json