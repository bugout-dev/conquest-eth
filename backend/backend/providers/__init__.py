from typing import Any, Dict

from . import provider

event_providers: Dict[str, Any] = {
    provider.ApprovalForAll.event_type: provider.ApprovalForAll,
    provider.PlanetExit.event_type: provider.PlanetExit,
    provider.ExitComplete.event_type: provider.ExitComplete,
    provider.FleetSent.event_type: provider.FleetSent,
    provider.Transfer.event_type: provider.Transfer,
}
