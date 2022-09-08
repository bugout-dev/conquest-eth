import argparse
import json
import logging
import os
import sys
import time
from typing import Any, Dict

from brownie import network
from web3 import Web3
from moonstreamdb.db import yield_db_read_only_session_ctx

from .actions import (
    location_to_xy,
    xy_to_location,
    distance_from_to,
    encode_data_for_planet_stake,
    fleet_attack_calc,
    get_hash_string,
    get_secret_hash,
    get_to_hash,
    get_fleet_id,
    gen_file_hash_name,
)
from .automation import cultivation
from .OuterSpace import (
    OuterSpace,
    add_default_arguments,
    get_transaction_config,
    boolean_argument_type,
)
from .PlayToken import PlayToken
from .providers import event_providers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
QUERIES_DIR = os.path.join(THIS_DIR, "..", "..", "queries")


def generate_planet_fleet_state_handler(args: argparse.Namespace) -> None:
    # TODO(kompotkot): Finish it
    query_file = os.path.join(QUERIES_DIR, args.query)
    with open(query_file, "r") as ifp:
        get_query = ifp.read().strip()
    assert get_query != ""

    network.connect(args.network)

    with yield_db_read_only_session_ctx() as db_session:
        planet_locs = db_session.execute(get_query).all()

    planet_hangars = []
    contract = OuterSpace(args.address)
    for planet_loc in planet_locs[0:5]:
        result = contract.get_updated_planet_state(planet_loc)
        planet_hangars.append({result[3]: type(result)})

    with args.output:
        json.dump(planet_hangars, args.output)


def generate_locations_handler(args: argparse.Namespace) -> None:
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


def generate_snapshot_info_handler(args: argparse.Namespace) -> None:
    snapshot_query_file = os.path.join(QUERIES_DIR, args.query)
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


def generate_calldata_handler(args: argparse.Namespace) -> None:
    data = encode_data_for_planet_stake(args.owner_addr, args.location)

    print(f"0x{data}")


def calculate_fleet_invasion_handler(args: argparse.Namespace) -> None:
    """
    Return True if attack succeed and False if fails.
    """
    _fleet_size_factor = 500000  # From Initialized event fleetSizeFactor6 arg
    won = fleet_attack_calc(
        _fleet_size_factor=_fleet_size_factor,
        num_attack=args.num_attack,
        attack=args.attack,
        num_defense=args.num_defense,
        defense=args.defense,
    )


def calculate_location_handler(args: argparse.Namespace) -> None:
    if args.location is not None:
        assert args.x is None
        assert args.y is None

        xy = location_to_xy(args.location)
        print(xy)

    elif args.x is not None and args.y is not None:
        assert args.location is None

        location = xy_to_location(args.x, args.y)
        print(location)
    else:
        print("Argument location or x and y should be specified")
        return


def calculate_distance_handler(args: argparse.Namespace) -> None:
    distance = distance_from_to(
        int(args.from_coords[0]),
        int(args.from_coords[1]),
        int(args.to_coords[0]),
        int(args.to_coords[1]),
    )
    print(distance)


def automation_cultivation_handler(args: argparse.Namespace) -> None:
    network.connect(args.network)
    ospace_contract = OuterSpace(args.ospace_address)
    play_contract = PlayToken(args.play_address)
    transaction_config = get_transaction_config(args)

    # Workflow for each target
    # TODO(kompotkot): Re-write to work with multiple targets in threads
    for i, v in enumerate(args.targets):
        args.targets[i] = int(v)
    target = args.targets[0]

    start_ts = args.start_ts
    if start_ts is None:
        start_ts = int(time.time())

    state_file_hash = gen_file_hash_name(
        start_ts=start_ts, base=args.base, target=target
    )
    state_dir = THIS_DIR
    if args.state_dir is not None:
        state_dir = args.state_dir

    cultivation(
        ospace_contract=ospace_contract,
        play_contract=play_contract,
        transaction_config=transaction_config,
        base=args.base,
        target=target,
        specific="0x0000000000000000000000000000000000000001",
        start_ts=start_ts,
        quantity=args.quantity,
        state_file_hash=state_file_hash,
        state_dir=state_dir,
        debug=args.debug,
    )


def calculate_file_hash_handler(args: argparse.Namespace) -> None:
    states_files = os.listdir(args.states_path)
    state_hashes = []
    for f in states_files:
        state = f.strip().split(".")
        if len(state) == 2 and state[1] == "jsonl":
            state_hashes.append(state[0])

    looking_hashes = {}

    time_now = int(time.time())
    for check_hash in state_hashes:
        print(f"Checking hash {check_hash}")
        for check_target in args.targets:
            target_checked = False
            if not target_checked:
                for check_time in range(args.start_ts, time_now):
                    current_hash = gen_file_hash_name(
                        check_time, args.base, check_target
                    )
                    if current_hash == check_hash:
                        looking_hashes[current_hash] = {
                            "time": check_time,
                            "target": check_target,
                        }
                        target_checked = True
                        break
    print(f"\nFound hashes: {json.dumps(looking_hashes)}")


def calculate_secret_hash_handler(args: argparse.Namespace) -> None:
    signer = network.accounts.load(args.sender, args.password)
    if args.verbose:
        print(f"Signer public address: {signer.address}")

    hash_string = get_hash_string(signer.private_key)
    secret_hash = get_secret_hash(hash_string, args.from_loc, args.nonce)
    print(f"Secret hash: {secret_hash}")


def calculate_to_hash_handler(args: argparse.Namespace) -> None:
    if args.secret_hash is None and args.from_loc is None and args.nonce is None:
        print("One of secret-hash or from_loc and nonce required")
        return
    signer = network.accounts.load(args.sender, args.password)
    if args.verbose:
        print(f"Signer public address: {signer.address}")

    if args.secret_hash is None:
        hash_string = get_hash_string(signer.private_key)
        secret_hash = get_secret_hash(hash_string, args.from_loc, args.nonce)
    else:
        secret_hash = args.secret_hash
    if args.verbose:
        print(f"Secret hash: {secret_hash}")

    arrival_time_wanted_lst = args.arrival_time_wanted.strip("").split("-")
    if len(arrival_time_wanted_lst) == 1:
        to_hash = get_to_hash(
            secret_hash,
            args.to_loc,
            args.gift,
            args.specific,
            int(arrival_time_wanted_lst[0]),
        )
        print(f"To hash: {to_hash}")
    else:
        for i in range(
            int(arrival_time_wanted_lst[0]), int(arrival_time_wanted_lst[1])
        ):
            to_hash = get_to_hash(
                secret_hash, args.to_loc, args.gift, args.specific, int(i)
            )
            print(f"To hash: {to_hash}")
            if (
                to_hash
                == "0xbf071dacdc1ad1374ca03ed7058ed7e447e30fc6967d3778960952d4c8a11ba4"
            ):
                print("Found")
                break


def calculate_fleet_id_handler(args: argparse.Namespace) -> None:
    if args.secret_hash is None and args.nonce is None:
        print("One of secret-hash or nonce required")
        return
    signer = network.accounts.load(args.sender, args.password)
    if args.verbose:
        print(f"Signer public address: {signer.address}")

    if args.secret_hash is None:
        hash_string = get_hash_string(signer.private_key)
        secret_hash = get_secret_hash(hash_string, args.from_loc, args.nonce)
    else:
        secret_hash = args.secret_hash
    if args.verbose:
        print(f"Secret hash: {secret_hash}")

    to_hash = get_to_hash(
        secret_hash, args.to_loc, args.gift, args.specific, args.arrival_time_wanted
    )
    if args.verbose:
        print(f"To hash: {to_hash}")

    fleet_id = get_fleet_id(to_hash, args.from_loc, signer.address)
    print(f"Fleet id: {fleet_id}")


# Decode function call (could be copied from metamask or scan transaction) data
def decode_handler(args: argparse.Namespace) -> None:
    network.connect(args.network)
    contract = OuterSpace(args.address)
    contract_instance = Web3().eth.contract(abi=contract.abi)
    decoded_input = contract_instance.decode_function_input(args.string)

    print(decoded_input)


def main() -> None:
    parser = argparse.ArgumentParser(description="Conquest-eth map CLI")
    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers(description="Conquest-eth commands")

    parser_automation = subcommands.add_parser(
        "automation", description="Automate operations conquest-eth"
    )
    parser_automation.set_defaults(func=lambda _: parser_automation.print_help())
    add_default_arguments(parser_automation, True)
    subcommands_automation = parser_automation.add_subparsers(
        description="Automation commands"
    )
    parser_automation_cultivation = subcommands_automation.add_parser(
        "cultivation", description="Start cultivation workflow"
    )
    parser_automation_cultivation.add_argument(
        "-b",
        "--base",
        type=int,
        required=True,
        help="Base planet location, which never be unstaked",
    )
    parser_automation_cultivation.add_argument(
        "-t",
        "--targets",
        nargs="+",
        required=True,
        help="List of planet locations for farming",
    )
    parser_automation_cultivation.add_argument(
        "-s",
        "--start-ts",
        type=int,
        help="When farm started",
    )
    parser_automation_cultivation.add_argument(
        "-q",
        "--quantity",
        type=int,
        required=True,
        help="Quantity of ships to send",
    )
    parser_automation_cultivation.add_argument(
        "--ospace-address",
        required=True,
        help="OuterSpace main contract address",
    )
    parser_automation_cultivation.add_argument(
        "--play-address",
        required=True,
        help="PlayToken token address",
    )
    parser_automation_cultivation.add_argument(
        "--state-dir",
        help="Directory to store state files",
    )
    parser_automation_cultivation.add_argument(
        "--debug", action="store_true", help="Print debug output"
    )
    parser_automation_cultivation.set_defaults(func=automation_cultivation_handler)

    parser_decode = subcommands.add_parser("decode", description="Decode data")
    parser_decode.add_argument(
        "-s",
        "--string",
        required=True,
        help="Raw data string",
    )
    parser_decode.add_argument(
        "--address",
        required=True,
        help="Contract address",
    )
    parser_decode.add_argument(
        "--network", required=True, help="Name of brownie network to connect to"
    )
    parser_decode.set_defaults(func=decode_handler)

    parser_generate = subcommands.add_parser(
        "generate", description="Generate data for conquest-eth"
    )
    parser_generate.set_defaults(func=lambda _: parser_generate.print_help())
    parser_generate.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Optional output file in which to write output information",
    )

    subcommands_generate = parser_generate.add_subparsers(
        description="Generate commands"
    )
    parser_generate_locations = subcommands_generate.add_parser(
        "locations", description="Information about locations from Outer Space"
    )
    parser_generate_locations.add_argument(
        "-q",
        "--query",
        type=str,
        default="most-recent-event-per-planet-loc-based.sql",
        help="Query to apply",
    )
    parser_generate_locations.set_defaults(func=generate_locations_handler)

    parser_generate_snapshot_info = subcommands_generate.add_parser(
        "snapshot-info", description="Information about current snapshot"
    )
    parser_generate_snapshot_info.add_argument(
        "-q", "--query", type=str, default="snapshot-info.sql", help="Query to apply"
    )
    parser_generate_snapshot_info.set_defaults(func=generate_snapshot_info_handler)

    parser_generate_planet_fleet_states = subcommands_generate.add_parser(
        "planet-fleet-states", description="Information about fleet state on planets"
    )
    add_default_arguments(parser_generate_planet_fleet_states, False)
    parser_generate_planet_fleet_states.add_argument(
        "-q", "--query", type=str, default="planet-locs.sql", help="Query file path"
    )
    parser_generate_planet_fleet_states.set_defaults(
        func=generate_planet_fleet_state_handler
    )

    parser_generate_calldata = subcommands_generate.add_parser(
        "calldata", description="Generates calldata for TransferAndCall"
    )
    parser_generate_calldata.add_argument(
        "-o", "--owner_addr", required=True, help="Future owner of planet"
    )
    parser_generate_calldata.add_argument(
        "-l", "--location", type=int, required=True, help="Location of planet"
    )
    parser_generate_calldata.set_defaults(func=generate_calldata_handler)

    parser_calculate = subcommands.add_parser(
        "calculate", description="Calculate data of conquest-eth"
    )
    parser_calculate.set_defaults(func=lambda _: parser_calculate.print_help())
    subcommands_calculate = parser_calculate.add_subparsers(
        description="Calculate commands"
    )

    parser_calculate_file_hash = subcommands_calculate.add_parser(
        "compare-hash", description="Calculate file hashes and compare with time start"
    )
    parser_calculate_file_hash.add_argument(
        "-b",
        "--base",
        type=int,
        required=True,
        help="Base planet location",
    )
    parser_calculate_file_hash.add_argument(
        "-t",
        "--targets",
        nargs="+",
        required=True,
        help="List of planet locations for farming",
    )
    parser_calculate_file_hash.add_argument(
        "-s",
        "--start-ts",
        type=int,
        required=True,
        help="When approximately farm started",
    )
    parser_calculate_file_hash.add_argument(
        "-p", "--states-path", required=True, help="Path to directory with states files"
    )
    parser_calculate_file_hash.set_defaults(func=calculate_file_hash_handler)

    parser_calculate_location = subcommands_calculate.add_parser(
        "location", description="Calculate location"
    )
    parser_calculate_location.add_argument("-x", "--x", type=int, help="X location")
    parser_calculate_location.add_argument("-y", "--y", type=int, help="Y location")
    parser_calculate_location.add_argument(
        "-l", "--location", type=int, help="Full location"
    )
    parser_calculate_location.set_defaults(func=calculate_location_handler)

    parser_calculate_distance = subcommands_calculate.add_parser(
        "distance", description="Calculate distance"
    )
    parser_calculate_distance.add_argument(
        "-f",
        "--from_coords",
        nargs="+",
        required=True,
        help="From coords Tuple(x y)",
    )
    parser_calculate_distance.add_argument(
        "-t", "--to_coords", nargs="+", required=True, help="To coords Tuple(x y)"
    )
    parser_calculate_distance.set_defaults(func=calculate_distance_handler)

    parser_calculate_fleet_invasion = subcommands_calculate.add_parser(
        "fleet-invasion", description="Fleet commands"
    )
    parser_calculate_fleet_invasion.add_argument(
        "--num-attack",
        required=True,
        type=int,
        help="Number of spaceships in the attack fleet",
    )
    parser_calculate_fleet_invasion.add_argument(
        "--attack",
        required=True,
        type=int,
        help="The attack value of the planet the fleet is coming from",
    )
    parser_calculate_fleet_invasion.add_argument(
        "--num-defense",
        required=True,
        type=int,
        help="Number of spaceships on the planet at the time the fleet arrive",
    )
    parser_calculate_fleet_invasion.add_argument(
        "--defense",
        required=True,
        type=int,
        help="The defense value of the planet being attacked",
    )
    parser_calculate_fleet_invasion.set_defaults(func=calculate_fleet_invasion_handler)

    parser_calculate_secret_hash = subcommands_calculate.add_parser(
        "secret-hash", description="Calculates secret hash"
    )
    parser_calculate_secret_hash.add_argument(
        "--from-loc", required=True, type=int, help="From location"
    )
    parser_calculate_secret_hash.add_argument(
        "--nonce", required=True, type=int, help="Transaction nonce"
    )
    parser_calculate_secret_hash.add_argument(
        "--sender", required=True, help="Path to keystore file for transaction sender"
    )
    parser_calculate_secret_hash.add_argument(
        "--password",
        required=False,
        help="Password to keystore file (if you do not provide it, you will be prompted for it)",
    )
    parser_calculate_secret_hash.add_argument(
        "--verbose", action="store_true", help="Print verbose output"
    )
    parser_calculate_secret_hash.set_defaults(func=calculate_secret_hash_handler)

    parser_calculate_to_hash = subcommands_calculate.add_parser(
        "to-hash", description="Calculates to hash"
    )
    parser_calculate_to_hash.add_argument("--secret-hash", help="Secret hash")
    parser_calculate_to_hash.add_argument(
        "--from-loc",
        type=int,
        help="From location (required if secret-hash not specified)",
    )
    parser_calculate_to_hash.add_argument(
        "--nonce",
        type=int,
        help="Transaction nonce (required if secret-hash not specified)",
    )
    parser_calculate_to_hash.add_argument(
        "--to-loc", required=True, type=int, help="To location"
    )
    parser_calculate_to_hash.add_argument(
        "--gift", required=True, type=boolean_argument_type, help="Gift"
    )
    parser_calculate_to_hash.add_argument("--specific", required=True, help="specific")
    parser_calculate_to_hash.add_argument(
        "--arrival-time-wanted", required=True, help="Arrival time wanted"
    )
    parser_calculate_to_hash.add_argument(
        "--sender", required=True, help="Path to keystore file for transaction sender"
    )
    parser_calculate_to_hash.add_argument(
        "--password",
        required=False,
        help="Password to keystore file (if you do not provide it, you will be prompted for it)",
    )
    parser_calculate_to_hash.add_argument(
        "--verbose", action="store_true", help="Print verbose output"
    )
    parser_calculate_to_hash.set_defaults(func=calculate_to_hash_handler)

    parser_calculate_fleet_id = subcommands_calculate.add_parser(
        "fleet-id", description="Calculates fleet id"
    )
    parser_calculate_fleet_id.add_argument("--secret-hash", help="Secret hash")
    parser_calculate_fleet_id.add_argument(
        "--from-loc", required=True, type=int, help="From location"
    )
    parser_calculate_fleet_id.add_argument(
        "--nonce",
        type=int,
        help="Transaction nonce (required if secret-hash not specified)",
    )
    parser_calculate_fleet_id.add_argument(
        "--to-loc", required=True, type=int, help="To location"
    )
    parser_calculate_fleet_id.add_argument(
        "--gift", required=True, type=boolean_argument_type, help="Gift"
    )
    parser_calculate_fleet_id.add_argument("--specific", required=True, help="specific")
    parser_calculate_fleet_id.add_argument(
        "--arrival-time-wanted", required=True, type=int, help="Arrival time wanted"
    )
    parser_calculate_fleet_id.add_argument(
        "--sender", required=True, help="Path to keystore file for transaction sender"
    )
    parser_calculate_fleet_id.add_argument(
        "--password",
        required=False,
        help="Password to keystore file (if you do not provide it, you will be prompted for it)",
    )
    parser_calculate_fleet_id.add_argument(
        "--verbose", action="store_true", help="Print verbose output"
    )
    parser_calculate_fleet_id.set_defaults(func=calculate_fleet_id_handler)

    args = parser.parse_args()
    args.func(args)
