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
	currentFleetState: number
	stake: number
}

// Convert data from json in event structure
const parseEvents = (data: any[], planetLocsFleetStates: any[]): Event[] => {
	let events: Event[] = []

	Object.keys(data).forEach((loc) => {
		const locationHex = BigNumber.from(loc).toHexString()
		const { x, y } = locationToXY(locationHex)

		events.push({
			name: data[loc].name,
			locX: x,
			locY: y,
			blockNumber: data[loc].block_number,
			blockTimestamp: data[loc].block_timestamp,
			currentFleetState: planetLocsFleetStates[loc],
			stake: data[loc].stake
		})
	})

	return events
}

// HSL colors
const colors_hsl = {
	FleetArrived: [356, 83, 41],
	FleetSent: [22, 97, 48],
	PlanetTransfer: [220, 70, 70],
	PlanetStake: [50, 100, 52],
	ExitComplete: [134, 75, 72],
	PlanetExit: [181, 49, 43],
	Transfer: [249, 100, 75],
	default: [0, 0, 35]
}

const parseColorHSL = (hsl: number[], saturation: number) => {
	return `hsl(${hsl[0]}, ${Math.round((hsl[1] * saturation) / 100)}%, ${
		hsl[2]
	}%)`
}

export const fleetSizeColor = (quantity: number) => {
	if (quantity < 100000) {
		return "green"
	} else if (quantity >= 100000 && quantity <= 1000000) {
		return "orange"
	} else return "red"
}

// Modify saturation according to timestamp since last event for planet
// 1 day back = 86400
// 3 days back = 259200
// 7 days back = 604800
// 14 days back = 1209600
export const blockTimestampColor = (blockTimestamp: number) => {
	const currentTime = Math.floor(Date.now() / 1000)
	const difference = currentTime - blockTimestamp

	if (difference >= 86400 && difference < 259200) {
		return 80
	} else if (difference >= 259200 && difference < 604800) {
		return 50
	} else if (difference >= 604800 && difference < 1209600) {
		return 20
	} else if (difference >= 1209600) {
		return 1
	} else {
		return 100
	}
}

// Render proper color for exact event according to timestamp and other filters
export const eventTypeColor = (eventName: string, blockTimestamp: number) => {
	if (!colors_hsl[eventName]) {
		return parseColorHSL(
			colors_hsl.default,
			blockTimestampColor(blockTimestamp)
		)
	} else {
		return parseColorHSL(
			colors_hsl[eventName],
			blockTimestampColor(blockTimestamp)
		)
	}
}

export default parseEvents
