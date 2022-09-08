import logging
import time
import os
from typing import Any, Callable, Dict, List, Optional

from brownie.network import web3
from moonstreamdb.models import XDaiLabel
from moonstreamdb.db import yield_db_read_only_session_ctx
from sqlalchemy.orm.session import Session

from .actions import (
    location_to_xy,
    distance_from_to,
    encode_data_for_planet_stake,
    get_hash_string,
    get_secret_hash,
    get_to_hash,
    get_fleet_id,
    get_latest_state_from_file,
    write_latest_state_to_file,
    get_state_from_file,
)
from .OuterSpace import OuterSpace
from .PlayToken import PlayToken

logger = logging.getLogger(__name__)


class Automator:
    def __init__(
        self,
        ospace_contract: OuterSpace,
        play_contract: PlayToken,
        transaction_config: Dict[str, Any],
        start_ts: int,
        debug: bool,
    ) -> None:
        self.ospace_contract = ospace_contract
        self.play_contract = play_contract
        self.transaction_config = transaction_config

        self.start_ts = start_ts  # Required to avoid resend first fleet

        self._events_map = {
            1: {
                "name": "send_fleet_from_base",
                "action": self.action_send_for,
                "confirmation_event": self.event_fleet_sent,
                "revert": False,
            },
            2: {
                "name": "resolve_fleet_at_target",
                "action": self.action_resolve_fleet,
                "confirmation_event": self.event_fleet_arrived,
                "revert": False,
            },
            3: {
                "name": "stake_target",
                "action": self.action_transfer_and_call,
                "confirmation_event": self.event_planet_stake,
                "revert": False,
            },
            4: {
                "name": "send_fleet_from_target",
                "action": self.action_send_for,
                "confirmation_event": self.event_fleet_sent,
                "revert": True,
            },
            5: {
                "name": "exit_target",
                "action": self.action_exit_for,
                "confirmation_event": self.event_exit_complete,
                "revert": False,
            },
            6: {
                "name": "resolve_fleet_at_base",
                "action": self.action_resolve_fleet,
                "confirmation_event": self.event_fleet_arrived,
                "revert": True,
            },
        }

        self.debug = debug

    @property
    def events_map(self) -> Dict[str, Any]:
        return self._events_map

    def gen_fresh_state(self, action: int = 1):
        fresh_state = {
            "action": action,
            "ts": 0,
            "confirmation_event_ts": 0,
            "nonce": 0,
        }
        return fresh_state

    def event_fleet_sent(self, db_session: Session, **kwargs) -> Optional[XDaiLabel]:
        result = None
        query = (
            db_session.query(XDaiLabel)
            .filter(
                XDaiLabel.address == str(self.ospace_contract.address),
                XDaiLabel.label_data["name"].astext == "FleetSent",
                XDaiLabel.label_data["args"]["from"].astext == str(kwargs["from_loc"]),
                XDaiLabel.block_timestamp >= self.start_ts,
            )
            .order_by(XDaiLabel.block_number.desc())
            .limit(1)
        )
        try:
            result = query.one_or_none()
        except Exception as e:
            logger.error("Unexpected error:", e)
        return result

    def action_send_for(self, **kwargs) -> Optional[int]:
        # TODO(kompotkot): Check if separate tx_conf will fix issue with nonce to low
        transaction_config = self.transaction_config

        nonce = None
        try:
            nonce = web3.eth.get_transaction_count(transaction_config["from"].address)
            secret_hash = get_secret_hash(
                kwargs["hash_string"],
                kwargs["from_loc"],
                nonce,
            )
            to_hash = get_to_hash(
                secret_hash,
                kwargs["to_loc"],
                kwargs["gift"],
                kwargs["specific"],
                kwargs["arrival_time_wanted"],
            )
            launch = [
                kwargs["public_key"],
                kwargs["public_key"],
                kwargs["from_loc"],
                kwargs["quantity"],
                to_hash,
            ]
            transaction_config["nonce"] = nonce
            if self.debug:
                logger.info(f"DEBUG secret_hash: {secret_hash}")
                logger.info(f"DEBUG to_hash: {to_hash}")
                logger.info(f"DEBUG launch: {launch}")
                logger.info(f"DEBUG tx nonce: {nonce}")
            result = self.ospace_contract.send_for(
                launch=launch, transaction_config=transaction_config
            )
            logger.info(f"Action: send-for, tx result: {result}")
        except Exception as e:
            logger.error(e)
            return None

        self.transaction_config = transaction_config
        return nonce

    def event_fleet_arrived(self, db_session: Session, **kwargs) -> Optional[XDaiLabel]:
        result = None
        query = (
            db_session.query(XDaiLabel)
            .filter(
                XDaiLabel.address == str(self.ospace_contract.address),
                XDaiLabel.label_data["name"].astext == "FleetArrived",
                XDaiLabel.label_data["args"]["destination"].astext
                == str(kwargs["to_loc"]),
                XDaiLabel.block_timestamp >= self.start_ts,
            )
            .order_by(XDaiLabel.block_number.desc())
            .limit(1)
        )
        try:
            result = query.one_or_none()
        except Exception as e:
            logger.error("Unexpected error:", e)
            db_session.close_all()
        return result

    def action_resolve_fleet(self, **kwargs) -> Optional[int]:
        # TODO(kompotkot): Check if separate tx_conf will fix issue with nonce to low
        transaction_config = self.transaction_config

        nonce = None
        try:
            nonce = web3.eth.get_transaction_count(transaction_config["from"].address)
            secret_hash = get_secret_hash(
                kwargs["hash_string"], kwargs["from_loc"], kwargs["fleet_send_nonce"]
            )
            to_hash = get_to_hash(
                secret_hash,
                kwargs["to_loc"],
                kwargs["gift"],
                kwargs["specific"],
                kwargs["arrival_time_wanted"],
            )
            fleet_id = get_fleet_id(to_hash, kwargs["from_loc"], kwargs["public_key"])
            resolution = [
                kwargs["from_loc"],
                kwargs["to_loc"],
                kwargs["distance"],
                kwargs["arrival_time_wanted"],
                kwargs["gift"],
                kwargs["specific"],
                secret_hash,
                kwargs["public_key"],
                kwargs["public_key"],
            ]
            transaction_config["nonce"] = nonce
            if self.debug:
                logger.info(f"DEBUG secret_hash: {secret_hash}")
                logger.info(f"DEBUG to_hash: {to_hash}")
                logger.info(f"DEBUG fleet_id: {fleet_id}")
                logger.info(f"DEBUG resolution: {resolution}")
                logger.info(f"DEBUG fleet_send_nonce: {kwargs['fleet_send_nonce']}")
                logger.info(f"DEBUG tx nonce: {nonce}")
            result = self.ospace_contract.resolve_fleet(
                fleet_id=fleet_id,
                resolution=resolution,
                transaction_config=transaction_config,
            )
            logger.info(f"Action: resolve-fleet, tx result: {result}")
        except Exception as e:
            logger.error(e)
            return None

        self.transaction_config = transaction_config
        return nonce

    def event_planet_stake(self, db_session: Session, **kwargs) -> Optional[XDaiLabel]:
        result = None
        query = (
            db_session.query(XDaiLabel)
            .filter(
                XDaiLabel.address == str(self.ospace_contract.address),
                XDaiLabel.label_data["name"].astext == "PlanetStake",
                XDaiLabel.label_data["args"]["location"].astext
                == str(kwargs["to_loc"]),
                XDaiLabel.block_timestamp >= self.start_ts,
            )
            .order_by(XDaiLabel.block_number.desc())
            .limit(1)
        )
        try:
            result = query.one_or_none()
        except Exception as e:
            logger.error("Unexpected error:", e)
        return result

    def action_transfer_and_call(self, **kwargs) -> Optional[int]:
        nonce = None
        try:
            amount = (
                self.ospace_contract.get_planet(location=kwargs["to_loc"])[1][2]
                * 100000000000000
            )
            data = encode_data_for_planet_stake(kwargs["public_key"], kwargs["to_loc"])
            nonce = web3.eth.get_transaction_count(
                self.transaction_config["from"].address
            )
            self.transaction_config["nonce"] = nonce
            if self.debug:
                logger.info(f"DEBUG amount: {amount}")
                logger.info(f"DEBUG data: {data}")
                logger.info(f"DEBUG tx nonce: {nonce}")
            result = self.play_contract.transfer_and_call(
                to=self.ospace_contract.address,
                amount=amount,
                data=data,
                transaction_config=self.transaction_config,
            )
            logger.info(f"Action: transfer-and-call, tx result: {result}")
        except Exception as e:
            logger.error(e)
            return None

        return nonce

    def event_exit_complete(self, db_session: Session, **kwargs) -> Optional[XDaiLabel]:
        result = None
        query = (
            db_session.query(XDaiLabel)
            .filter(
                XDaiLabel.address == str(self.ospace_contract.address),
                XDaiLabel.label_data["name"].astext == "PlanetExit",
                XDaiLabel.label_data["args"]["location"].astext
                == str(kwargs["to_loc"]),
                XDaiLabel.block_timestamp >= self.start_ts,
            )
            .order_by(XDaiLabel.block_number.desc())
            .limit(1)
        )
        try:
            result = query.one_or_none()
        except Exception as e:
            logger.error("Unexpected error:", e)
        return result

    def action_exit_for(self, **kwargs) -> Optional[int]:
        try:
            nonce = web3.eth.get_transaction_count(
                self.transaction_config["from"].address
            )
            self.transaction_config["nonce"] = nonce
            if self.debug:
                logger.info(f"DEBUG tx nonce: {nonce}")
            result = self.ospace_contract.exit_for(
                owner=kwargs["public_key"],
                location=kwargs["to_loc"],
                transaction_config=self.transaction_config,
            )
            logger.info(f"Action: exit-for, tx result: {result}")
            return nonce
        except Exception as e:
            logger.error(e)
            return None

    def get_updated_planet_state(self, location: int) -> Optional[Any]:
        try:
            result = self.ospace_contract.get_updated_planet_state(location=location)
            logger.info(f"Get: updated_planet_state, result: {result}")
            return result
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def loc_reverse(action: Dict[str, Any], from_loc: int, to_loc: int):
        """
        Revert locations when we are moving back to base.
        """
        temp_from_loc = from_loc
        temp_to_loc = to_loc
        if action["revert"]:
            temp_from_loc = to_loc
            temp_to_loc = from_loc

        return temp_from_loc, temp_to_loc


def cultivation(
    ospace_contract: OuterSpace,
    play_contract: PlayToken,
    transaction_config: Dict[str, Any],
    base: int,
    target: int,
    specific: str,
    start_ts: int,
    quantity: int,
    state_file_hash: str,
    state_dir: str,
    debug: bool,
) -> None:
    """
    1. Send fleet to target
    2. Resolve fleet at target
    3. Stake target planet
    4. Send fleet back to base
    5. Exit target planet
    6. Resolve fleet at base
    """
    # Data preparation
    base_xy = location_to_xy(base)
    target_xy = location_to_xy(target)
    distance = distance_from_to(
        base_xy["x"], base_xy["y"], target_xy["x"], target_xy["y"]
    )

    # TODO(kompotkot): Calculate time, 4800 is for my test planets with 1h10m travel time + 20m extra
    # arrival_time_wanted = start_ts + 5400
    arrival_time_wanted = 0

    private_key = transaction_config["from"].private_key
    public_key = transaction_config["from"].address

    hash_string = get_hash_string(private_key)

    file_path = os.path.join(state_dir, f"{state_file_hash}.jsonl")

    at = Automator(
        ospace_contract=ospace_contract,
        play_contract=play_contract,
        transaction_config=transaction_config,
        start_ts=start_ts,
        debug=debug,
    )

    logger.info(
        f"Initialized automation cultivation. Distance equal {distance} between base: {base_xy} and target: {target_xy} planets with start time: {start_ts}"
    )

    latest_state, _ = get_latest_state_from_file(file_path=file_path)
    if latest_state is None:
        logger.info(f"New cultivation, creating new file {file_path} with fresh state")
        write_latest_state_to_file(
            incoming_state=at.gen_fresh_state(), file_path=file_path
        )
    else:
        logger.info(f"Found state file {file_path}")

    if debug:
        logger.info(f"DEBUG latest_state at start: {latest_state}")
        logger.info(f"DEBUG len of events map: {len(at.events_map)}")

    while True:
        latest_state, _ = get_latest_state_from_file(file_path=file_path)
        if latest_state["confirmation_event_ts"] == 0:
            # Check if got event confirmation for latest action
            event_exec: Callable = at.events_map[latest_state["action"]][
                "confirmation_event"
            ]
            temp_from_loc, temp_to_loc = at.loc_reverse(
                at.events_map[latest_state["action"]], from_loc=base, to_loc=target
            )
            with yield_db_read_only_session_ctx() as db_session:
                result = event_exec(
                    db_session=db_session, from_loc=temp_from_loc, to_loc=temp_to_loc
                )
            if result is not None:
                latest_state["confirmation_event_ts"] = result.block_timestamp
                write_latest_state_to_file(
                    incoming_state=latest_state, file_path=file_path
                )

        if (
            latest_state["action"] == len(at.events_map)
            and latest_state["confirmation_event_ts"] != 0
        ):
            logger.info("Planet farm complete")
            return

        time_now = int(time.time())

        # Bot logic
        if latest_state["action"] == 1 and latest_state["ts"] == 0:
            logger.info("Space fleet on the launch pad, start in 15 seconds..")
            time.sleep(15)
            logger.info("Sending first fleet to target")

            action_exec: Callable = at.events_map[latest_state["action"]]["action"]

            action_nonce = action_exec(
                public_key=public_key,
                from_loc=base,
                to_loc=target,
                quantity=quantity,
                arrival_time_wanted=arrival_time_wanted,
                gift=False,
                specific=specific,
                hash_string=hash_string,
            )
            if action_nonce is None:
                logger.info(
                    f"Action {at.events_map[latest_state['action']]['name']} failed"
                )
                return

            latest_state["ts"] = time_now
            latest_state["nonce"] = action_nonce
            write_latest_state_to_file(incoming_state=latest_state, file_path=file_path)

            time.sleep(60)
            continue

        if latest_state["confirmation_event_ts"] == 0:
            sleep_time = 180
            logger.info(
                f"Event {at.events_map[latest_state['action']]['name']} without confirmation with start time: {start_ts}, sleeping {sleep_time} seconds.."
            )
            time.sleep(sleep_time)
            continue
        elif latest_state["confirmation_event_ts"] != 0:
            logger.info(
                f"Latest action was {at.events_map[latest_state['action']]['name']} with confirmation ts: {latest_state['confirmation_event_ts']}"
            )

            next_events_map_action = at.events_map[latest_state["action"] + 1]
            action_exec: Callable = next_events_map_action["action"]
            temp_from_loc, temp_to_loc = at.loc_reverse(
                next_events_map_action, from_loc=base, to_loc=target
            )
            gift = next_events_map_action["revert"]

            # Get nonce of send-for fleet action
            fleet_send_nonce: int = 0
            if latest_state["action"] == 2 - 1:
                temp_state, _ = get_state_from_file(index=1, file_path=file_path)
                fleet_send_nonce = temp_state["nonce"]
            elif latest_state["action"] == 6 - 1:
                temp_state, _ = get_state_from_file(index=4, file_path=file_path)
                fleet_send_nonce = temp_state["nonce"]

            temp_quantity = quantity
            if latest_state["action"] == 4 - 1:
                temp_quantity = at.get_updated_planet_state(temp_from_loc)[3] - 1

            if debug:
                logger.info(f"DEBUG temp_to_loc: {temp_to_loc}")
                logger.info(f"DEBUG latest_state action: {latest_state['action']}")
                logger.info(f"DEBUG fleet_send_nonce: {fleet_send_nonce}")
                logger.info(f"DEBUG temp_quantity: {temp_quantity}")
                logger.info(f"DEBUG gift: {gift}")

            action_nonce = action_exec(
                public_key=public_key,
                from_loc=temp_from_loc,
                to_loc=temp_to_loc,
                quantity=temp_quantity,
                arrival_time_wanted=arrival_time_wanted,
                distance=distance,
                gift=gift,
                specific=specific,
                fleet_send_nonce=fleet_send_nonce,
                hash_string=hash_string,
            )
            if action_nonce is None:
                sleep_time = 300
                logger.info(
                    f"Action {at.events_map[latest_state['action'] + 1]['name']} failed with start time: {start_ts}. Probably action not available yet, sleeping {sleep_time} seconds.."
                )
                time.sleep(sleep_time)
                continue

            latest_state["action"] = latest_state["action"] + 1
            latest_state["ts"] = time_now
            latest_state["confirmation_event_ts"] = 0
            latest_state["nonce"] = action_nonce
            write_latest_state_to_file(incoming_state=latest_state, file_path=file_path)
            continue

        time.sleep(30)
        logger.error(f"Unsupported stage: {latest_state}")
