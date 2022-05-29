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
    from_location: str  # from
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
