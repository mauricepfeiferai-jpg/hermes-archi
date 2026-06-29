#!/bin/zsh
# Loop Agent — self-improve + patch proposal
ROOT=~/ai-empire/projects/hermes-archi/templates/one-person-ai-agent-company
DATE=$(date +%Y-%m-%d)
OUT=$ROOT/loop/outputs
mkdir -p $OUT
python3 $ROOT/ops/cron/run_agent.py loop improve --date $DATE --out $OUT/patch_proposal_$DATE.md
