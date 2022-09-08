from typing import Any, Dict

from . import provider

event_providers: Dict[str, Any] = {
    provider.ApprovalForAll.event_type: provider.ApprovalForAll,
    provider.PlanetExit.event_type: provider.PlanetExit,
    provider.ExitComplete.event_type: provider.ExitComplete,
    provider.FleetSent.event_type: provider.FleetSent,
    provider.Transfer.event_type: provider.Transfer,
    provider.FleetArrived.event_type: provider.FleetArrived,
    provider.PlanetTransfer.event_type: provider.PlanetTransfer,
    provider.TravelingUpkeepRefund.event_type: provider.TravelingUpkeepRefund,
    provider.Initialized.event_type: provider.Initialized,
    provider.PlanetStake.event_type: provider.PlanetStake,
}
