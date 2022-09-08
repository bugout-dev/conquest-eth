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

echo -e "${PREFIX_INFO} Upload eventsLocationBased.json to static.simiotics.com/conquest-eth AWS S3 bucket"
aws s3 cp "$SCRIPT_DIR/data/eventsLocationBased.json" s3://static.simiotics.com/conquest-eth/eventsLocationBased.json
echo -e "${PREFIX_INFO} Upload planetLocsFleetStates.json to static.simiotics.com/conquest-eth AWS S3 bucket"
aws s3 cp "$SCRIPT_DIR/data/planetLocsFleetStates.json" s3://static.simiotics.com/conquest-eth/planetLocsFleetStates.json
echo -e "${PREFIX_INFO} Upload snapshotInfo.json to static.simiotics.com/conquest-eth AWS S3 bucket"
aws s3 cp "$SCRIPT_DIR/data/snapshotInfo.json" s3://static.simiotics.com/conquest-eth/snapshotInfo.json
