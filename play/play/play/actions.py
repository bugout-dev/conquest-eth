import ctypes
import os
import json
from hashlib import blake2b
from typing import Any, Dict, Optional

import eth_abi
from brownie.network import web3


def location_to_xy(location: int) -> Dict[str, int]:
    """
    Convert 22118353849861000125119349483064933744601 to -39 64.
    """
    locationHex = hex(location)

    if len(locationHex) <= 34:
        x = ctypes.c_int32(int(locationHex, 0)).value
        y = 0
    else:
        x = ctypes.c_int32(int("0x" + locationHex[len(locationHex) - 32 :], 0)).value
        y = ctypes.c_int32(int(locationHex[0 : len(locationHex) - 32], 0)).value

    return {"x": x, "y": y}


def xy_to_location(x: int, y: int) -> int:
    """
    Convert -39 64 to 22118353849861000125119349483064933744601.
    """
    xHexTC = hex(x & ((1 << 128) - 1))
    yHexTC = hex(y & ((1 << 128) - 1))

    locationHex = f"0x{yHexTC[2:]}{xHexTC[2:]}"
    location = int(locationHex, 0)

    return location


def distance_from_to(from_x: int, from_y: int, to_x: int, to_y: int) -> int:
    """
    Calculate distance between planets.
    Source: https://github.com/conquest-eth/conquest-eth-common/blob/caaaa69405c590536fcfd8ac0661b37464aea257/src/model/SpaceInfo.ts#L306
    """
    # TODO(kompotkot): Fetch genesis from event
    genesis = "0xdefd8666ec077c932b62f77bcfea4badcb3c296fc1f8a8792c9b7ca2ee6c8c4c"

    from_loc = xy_to_location(x=from_x, y=from_y)
    to_loc = xy_to_location(x=to_x, y=to_y)

    from_data = web3.solidityKeccak(["bytes32", "uint256"], [genesis, from_loc])
    to_data = web3.solidityKeccak(["bytes32", "uint256"], [genesis, to_loc])

    def value_8_mod(data: str, least_significant_bit: int, mod: int) -> int:
        return (int(data, 0) >> least_significant_bit) % mod

    sub_from_x = 1 - value_8_mod(from_data.hex(), 0, 3)
    sub_from_y = 1 - value_8_mod(from_data.hex(), 2, 3)
    sub_to_x = 1 - value_8_mod(to_data.hex(), 0, 3)
    sub_to_y = 1 - value_8_mod(to_data.hex(), 2, 3)

    g_from_x = from_x * 4 + sub_from_x
    g_from_y = from_y * 4 + sub_from_y
    g_to_x = to_x * 4 + sub_to_x
    g_to_y = to_y * 4 + sub_to_y

    distance = int(((g_to_x - g_from_x) ** 2 + (g_to_y - g_from_y) ** 2) ** 0.5)

    return distance


def arrival_time(distance: int, speed: int) -> int:
    time_per_distance = 1800
    full_time = distance * ((time_per_distance * 10000) / speed)

    return full_time


def fleet_attack_calc(
    _fleet_size_factor: int,
    num_attack: int,
    attack: int,
    num_defense: int,
    defense: int,
):
    attack_factor = num_attack * (
        (1000000 - _fleet_size_factor) + (_fleet_size_factor * num_attack / num_defense)
    )
    attack_damage = (attack_factor * attack) / defense / 1000000

    if num_defense > attack_damage:
        print(
            f"Attack fails with attacker_loss={num_attack} and defender_loss={attack_damage}"
        )
        return False
    else:
        defense_factor = num_defense * (
            (1000000 - _fleet_size_factor)
            + (_fleet_size_factor * num_defense / num_attack)
        )
        defense_damage = (defense_factor * defense) / attack / 1000000

        if defense_damage >= num_attack:
            defense_damage = num_attack - 1

        print(
            f"Attack succeed with attacker_loss={defense_damage} and defender_loss={num_defense}"
        )
        return True


def encode_data_for_planet_stake(owner_addr: str, location: int) -> str:
    """
    Encode data for stake planet.
    """
    encoded_data_bytes = eth_abi.encode_abi(
        ["address", "uint256"], [owner_addr, location]
    )
    encoded_data_hex = encoded_data_bytes.hex()

    return encoded_data_hex


def get_hash_string(private_key: str) -> str:
    hash_string = web3.solidityKeccak(
        ["bytes32", "bytes32"],
        [
            private_key,
            "0x0000000000000000000000000000000000000000000000000000000000000000",
        ],
    )
    return hash_string.hex()


def get_secret_hash(hash_string: str, from_loc: int, nonce: int) -> str:
    secret_hash = web3.solidityKeccak(
        ["bytes32", "uint256", "uint256"], [hash_string, from_loc, nonce]
    )
    return secret_hash.hex()


def get_to_hash(
    secret_hash: str, to_loc: int, gift: bool, specific: str, arrival_time_wanted: int
) -> str:
    to_hash = web3.solidityKeccak(
        ["bytes32", "uint256", "bool", "address", "uint256"],
        [secret_hash, to_loc, gift, specific, arrival_time_wanted],
    )
    return to_hash.hex()


def get_fleet_id(to_hash: str, from_loc: int, public_key: str) -> int:
    fleet_id = web3.solidityKeccak(
        ["bytes32", "uint256", "address", "address"],
        [to_hash, from_loc, public_key, public_key],
    )
    return int(fleet_id.hex(), 0)


def gen_file_hash_name(start_ts: int, base: int, target: int, as_hash=False) -> str:
    """
    Generate filename where to store state.
    """
    file_name: str
    if as_hash:
        h = blake2b(digest_size=22)
        h.update(f"{start_ts}-{base}-{target}".encode("utf-8"))
        file_name = h.hexdigest()
    else:
        file_name = f"{start_ts}-{target}"

    return file_name


def write_latest_state_to_file(incoming_state: Dict[str, Any], file_path: str) -> None:
    """
    Write and update latest state in file.

    If file does not exist, it creates new one
    If latest state in file action is equal to incoming state action,
    it updates state in file.
    """
    file_exists = os.path.exists(file_path)
    if not file_exists:
        open(file_path, "a").close()

    lines = []
    latest_state: Optional[Dict[str, Any]] = None
    with open(file_path, "r+") as fp:
        for line in fp:
            lines.append(line)
            if line != "":
                latest_state = json.loads(line)
        if (
            latest_state is not None
            and latest_state["action"] == incoming_state["action"]
        ):
            fp.seek(0)
            fp.truncate()
            fp.writelines(lines[:-1])

        json.dump(incoming_state, fp)
        fp.write("\n")


def get_latest_state_from_file(file_path: str):
    """
    Get latest state if exists, else return None
    """
    file_exists = os.path.exists(file_path)
    if not file_exists:
        return None, file_path

    latest_state: Optional[Dict[str, Any]] = None
    with open(file_path, "r") as ifp:
        for line in ifp:
            if line != "":
                latest_state = json.loads(line)

    return latest_state, file_path


def get_state_from_file(index: int, file_path: str):
    """
    Get state from file with exact index.
    """
    file_exists = os.path.exists(file_path)
    if not file_exists:
        return None, file_path

    state: Optional[Dict[str, Any]] = None
    with open(file_path, "r") as ifp:
        for line in ifp:
            if line != "":
                line_dct = json.loads(line)
                if line_dct["action"] == index:
                    state = line_dct

    return state, file_path
