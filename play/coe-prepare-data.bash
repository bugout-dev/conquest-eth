#!/usr/bin/env bash

# Colors
C_RESET='\033[0m'
C_RED='\033[1;31m'
C_GREEN='\033[1;32m'
C_YELLOW='\033[1;33m'

# Logs
PREFIX_INFO="${C_GREEN}[INFO]${C_RESET} [$(date +%d-%m\ %T)]"
PREFIX_WARN="${C_YELLOW}[WARN]${C_RESET} [$(date +%d-%m\ %T)]"
PREFIX_CRIT="${C_RED}[CRIT]${C_RESET} [$(date +%d-%m\ %T)]"

SCRIPT_DIR="$(realpath $(dirname $0))"

if [ ! -d "$SCRIPT_DIR/data" ]; then
  echo -e "${PREFIX_INFO} Creating data directory"
  mkdir "$SCRIPT_DIR/data"
fi

echo -e "${PREFIX_INFO} Generate locations"
coe generate --output "$SCRIPT_DIR/data/eventsLocationBased.json" locations --query most-recent-event-per-planet-loc-based.sql

echo -e "${PREFIX_INFO} Generate snapshot-info"
coe generate --output "$SCRIPT_DIR/data/snapshotInfo.json" snapshot-info --query snapshot-info.sql

echo -e "${PREFIX_INFO} Prepare planet locations"
psql $MOONSTREAM_DB_URI_READ_ONLY -f "$SCRIPT_DIR/queries/planet-locs.sql" -t -o "$SCRIPT_DIR/data/planetLocs.csv"

echo -e "${PREFIX_INFO} Generate planet fleet states"
npm --prefix batcher run build
CONTRACT_ABI_NAME="defcon-OuterSpace" CONTRACT_ADDRESS="$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" DATA_FILE_NAME="planetLocs" npm --prefix batcher run batch
