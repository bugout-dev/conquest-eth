import { BigNumber } from "@ethersproject/bignumber"
import {
	xyToLocation,
	locationToXY,
	coordFromLocation
} from "conquest-eth/lib/cjs/src/util/location"

interface Event {
	name: string
	locX: number
	locY: number
	blockNumber: number
	blockTimestamp: number
}

const parseEvents = (data: any[]) => {
	let events: Event[] = []

	Object.keys(data).forEach((loc) => {
		const locationHex = BigNumber.from(loc).toHexString()
		const { x, y } = locationToXY(locationHex)

		events.push({
			name: data[loc].name,
			locX: x,
			locY: y,
			blockNumber: data[loc].block_number,
			blockTimestamp: data[loc].block_timestamp
		})
	})

	return events
}

export const fleetSizeColor = (quantity: number) => {
	if (quantity < 100000) {
		return "green"
	} else if (quantity >= 100000 && quantity <= 1000000) {
		return "orange"
	} else return "red"
}

export const blockTimestampColor = (blockTimestamp: number) => {
	const currentTime = Date.now()
	// if (currentTime - blockTimestamp > )
}

export const eventTypeColor = (eventName: string) => {
	const colors = {
		ExitComplete: "#8bbdd8",
		FleetSent: "#df1f54",
		Transfer: "#7c789c",
		PlanetExit: "#876089",
		default: "#808080"
	}

	if (!colors[eventName]) {
		return colors.default
	} else {
		return colors[eventName]
	}
}

export default parseEvents
