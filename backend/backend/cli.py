import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from moonstreamdb.db import yield_db_read_only_session_ctx

from .providers import event_providers

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
QUERIES_DIR = os.path.join(THIS_DIR, "..", "queries")


def generate_handler(args: argparse.Namespace) -> None:
    generate_query_file = os.path.join(QUERIES_DIR, args.query)
    with open(generate_query_file, "r") as ifp:
        generate_query = ifp.read().strip()
    assert generate_query != ""

    planet_recent_events = []
    parsed_events: Dict[str, Any] = {}
    with yield_db_read_only_session_ctx() as db_session:
        planet_recent_events = db_session.execute(generate_query)

        for event in planet_recent_events:
            parsed_events[event[0]] = (
                event_providers[event[1]]
                .convert(event[-1], event[-2], event[-3])
                .dict()
            )

    with args.output:
        json.dump(parsed_events, args.output)


def snapshot_info_handler(args: argparse.Namespace) -> None:
    snapshot_query_file = os.path.join(QUERIES_DIR, "snapshot-info.sql")
    snapshot_query = ""
    with open(snapshot_query_file, "r") as ifp:
        snapshot_query = ifp.read().strip()
    assert snapshot_query != ""

    with yield_db_read_only_session_ctx() as db_session:
        snapshot_info_row = db_session.execute(snapshot_query).one()

    snapshot_info = {
        "block_number": snapshot_info_row[0],
        "block_timestamp": snapshot_info_row[1],
    }

    with args.output:
        json.dump(snapshot_info, args.output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Conquest-eth map CLI")
    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers(description="CEH commands")

    time_now = datetime.now(timezone.utc)

    parser_generate = subcommands.add_parser(
        "generate", description="Generate data for conquest-eth map"
    )
    parser_generate.set_defaults(func=lambda _: parser_generate.print_help())

    parser_generate.add_argument(
        "-s",
        "--sample",
        action="store_true",
        help="If provided get 5 sample events of each type",
    )
    parser_generate.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Optional output file in which to write output information",
    )
    parser_generate.add_argument(
        "-q", "--query", required=True, help="Output file path"
    )
    parser_generate.set_defaults(func=generate_handler)

    parser_snapshot_info = subcommands.add_parser(
        "snapshot-info", description="Information about current snapshot"
    )
    parser_snapshot_info.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Optional output file in which to write output information",
    )
    parser_snapshot_info.set_defaults(func=snapshot_info_handler)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
