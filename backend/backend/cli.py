import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

from moonstreamdb.db import yield_db_read_only_session_ctx
from moonstreamdb.models import XDaiLabel

from .providers import event_providers


def generate_handler(args: argparse.Namespace) -> None:
    # TODO(kompotkot): First get current file destination and join with queries folder
    with open("./queries/most-recent-event-per-planet.sql") as ifp:
        raw_query = ifp.read().strip()

    planet_recent_events = []
    parsed_events: Dict[str, Any] = {}
    with yield_db_read_only_session_ctx() as db_session:
        planet_recent_events = db_session.execute(raw_query)

        for event in planet_recent_events:
            parsed_events[event[0]] = (
                event_providers[event[1]]
                .convert(event[-1], event[-2], event[-3])
                .dict()
            )

    with open(args.output, "w") as ofp:
        json.dump(parsed_events, ofp)


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
    parser_generate.add_argument("-o", "--output", help="Output file path")
    parser_generate.set_defaults(func=generate_handler)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
