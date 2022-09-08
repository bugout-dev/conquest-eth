from typing import Any, Dict, List

from pydantic import BaseModel, Field, validator


class EventProvider:
    def __init__(
        self,
        event_type: str,
        description: str,
        base_model: BaseModel,
        conversion_map: Dict[str, List[str]],
    ):
        self.event_type = event_type
        self.description = description
        self.base_model = base_model
        self.conversion_map = conversion_map

    def convert(
        self, block_number: int, block_timestamp: int, label_data: Dict[str, Any]
    ) -> BaseModel:
        temp_dict: Dict[str, Any] = {
            "block_number": block_number,
            "block_timestamp": block_timestamp,
        }
        for k, v in self.conversion_map.items():
            temp_output = label_data
            for i in v:
                temp_output = temp_output[i]
            temp_dict[k] = temp_output
        return self.base_model(**temp_dict)


class EventApprovalForAll(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    owner: str
    approved: bool
    operator: str


ApprovalForAll = EventProvider(
    event_type="ApprovalForAll",
    description="Short desc.",
    base_model=EventApprovalForAll,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "owner": ["args", "owner"],
        "approved": ["args", "approved"],
        "operator": ["args", "operator"],
    },
)


class EventPlanetExit(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    owner: str
    location: str


PlanetExit = EventProvider(
    event_type="PlanetExit",
    description="Short desc.",
    base_model=EventPlanetExit,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "owner": ["args", "owner"],
        "location": ["args", "location"],
    },
)


class EventExitComplete(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    owner: str
    stake: str
    location: str


ExitComplete = EventProvider(
    event_type="ExitComplete",
    description="Short desc.",
    base_model=EventExitComplete,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "owner": ["args", "owner"],
        "stake": ["args", "stake"],
        "location": ["args", "location"],
    },
)


class EventFleetSent(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    from_location: str  # from - take it as location
    fleet: str
    operator: str
    quantity: int
    fleet_owner: str
    fleet_sender: str
    new_overflow: str
    new_num_spaceships: int
    new_traveling_upkeep: int


FleetSent = EventProvider(
    event_type="FleetSent",
    description="Short desc.",
    base_model=EventFleetSent,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "from_location": ["args", "from"],
        "fleet": ["args", "fleet"],
        "operator": ["args", "operator"],
        "quantity": ["args", "quantity"],
        "fleet_owner": ["args", "fleetOwner"],
        "fleet_sender": ["args", "fleetSender"],
        "new_overflow": ["args", "newOverflow"],
        "new_num_spaceships": ["args", "newNumSpaceships"],
        "new_traveling_upkeep": ["args", "newTravelingUpkeep"],
    },
)


class EventTransfer(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    to: str
    from_addr: str  # from
    location: str


Transfer = EventProvider(
    event_type="Transfer",
    description="Short desc.",
    base_model=EventTransfer,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "to": ["args", "to"],
        "from_addr": ["args", "from"],
        "location": ["args", "location"],
    },
)


class EventFleetArrived(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    won: bool
    data: List[int]
    gift: bool
    fleet: str
    fleet_owner: str
    destination: str  # take it as location
    destination_owner: str


FleetArrived = EventProvider(
    event_type="FleetArrived",
    description="Short desc.",
    base_model=EventFleetArrived,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "won": ["args", "won"],
        "data": ["args", "data"],
        "gift": ["args", "gift"],
        "fleet": ["args", "fleet"],
        "fleet_owner": ["args", "fleetOwner"],
        "destination": ["args", "destination"],
        "destination_owner": ["args", "destinationOwner"],
    },
)


class EventPlanetTransfer(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    location: str
    new_owner: str
    new_overflow: int
    previous_owner: str
    new_num_spaceships: int
    new_traveling_upkeep: int


PlanetTransfer = EventProvider(
    event_type="PlanetTransfer",
    description="Short desc.",
    base_model=EventPlanetTransfer,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "location": ["args", "location"],
        "new_owner": ["args", "newOwner"],
        "new_overflow": ["args", "newOverflow"],
        "previous_owner": ["args", "previousOwner"],
        "new_num_spaceships": ["args", "newNumspaceships"],
        "new_traveling_upkeep": ["args", "newTravelingUpkeep"],
    },
)


class EventTravelingUpkeepRefund(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    fleet: str
    origin: str  # take it as location
    new_overflow: int
    new_num_spaceships: int
    new_traveling_upkeep: int


TravelingUpkeepRefund = EventProvider(
    event_type="TravelingUpkeepRefund",
    description="Short desc.",
    base_model=EventTravelingUpkeepRefund,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "fleet": ["args", "fleet"],
        "origin": ["args", "origin"],
        "new_overflow": ["args", "newOverflow"],
        "new_num_spaceships": ["args", "newNumspaceships"],
        "new_traveling_upkeep": ["args", "newTravelingUpkeep"],
    },
)


class EventInitialized(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    genesis: str
    exit_duration: int
    resolve_window: int
    expansion_delta: int
    gift_tax_per_10000: int
    time_per_distance: int
    fleet_size_factor_6: int
    frontrunning_delay: int
    production_speed_up: int
    acquire_num_spaceships: int
    initial_space_expansion: int
    production_cap_as_duration: int
    upkeep_production_decrease_rate_per_10000th: int


Initialized = EventProvider(
    event_type="Initialized",
    description="Short desc.",
    base_model=EventInitialized,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "genesis": ["args", "genesis"],
        "exit_duration": ["args", "exitDuration"],
        "resolve_window": ["args", "resolveWindow"],
        "expansion_delta": ["args", "expansionDelta"],
        "gift_tax_per_10000": ["args", "giftTaxPer10000"],
        "time_per_distance": ["args", "timePerDistance"],
        "fleet_size_factor_6": ["args", "fleetSizeFactor6"],
        "frontrunning_delay": ["args", "frontrunningDelay"],
        "production_speed_up": ["args", "productionSpeedUp"],
        "acquire_num_spaceships": ["args", "acquireNumSpaceships"],
        "initial_space_expansion": ["args", "initialSpaceExpansion"],
        "production_cap_as_duration": ["args", "productionCapAsDuration"],
        "upkeep_production_decrease_rate_per_10000th": [
            "args",
            "upkeepProductionDecreaseRatePer10000th",
        ],
    },
)


class EventPlanetStake(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    stake: str
    acquirer: str
    freegift: bool
    location: str
    overflow: int
    num_spaceships: int
    traveling_upkeep: int


PlanetStake = EventProvider(
    event_type="PlanetStake",
    description="Short desc.",
    base_model=EventPlanetStake,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "stake": ["args", "stake"],
        "acquirer": ["args", "acquirer"],
        "freegift": ["args", "freegift"],
        "location": ["args", "location"],
        "overflow": ["args", "overflow"],
        "num_spaceships": ["args", "numSpaceships"],
        "traveling_upkeep": ["args", "travelingUpkeep"],
    },
)


class EventStakeToWithdraw(BaseModel):
    block_number: int
    block_timestamp: int
    label_type: str
    name: str
    owner: str
    freegift: str
    new_stake: int


StakeToWithdraw = EventProvider(
    event_type="StakeToWithdraw",
    description="Short desc.",
    base_model=EventStakeToWithdraw,
    conversion_map={
        "label_type": ["type"],
        "name": ["name"],
        "owner": ["args", "owner"],
        "freegift": ["args", "freegift"],
        "new_stake": ["args", "newStake"],
    },
)
