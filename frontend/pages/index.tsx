import React, { useEffect, useState } from "react"

import Layout from "../components/Layout"
import Map from "../components/Map"
import Sidebar from "../components/Sidebar"
import parseEvents from "../components/events"

const Index = () => {
	const [activeLocation, setActiveLocation] = useState(null)
	const [fleetLimitState, setFleetLimitState] = useState<number>(8200100)
	const [fleetLimitStateHideZero, setFleetLimitStateHideZero] =
		useState<boolean>(false)
	const [events, setEvents] = useState([])

	const [snapshotInfo, setSnapshotInfo] = useState(undefined)

	useEffect(() => {
		const fetchData = async () => {
			const snapshotInfoRaw = await fetch(
				"https://s3.amazonaws.com/static.simiotics.com/conquest-eth/snapshotInfo.json"
			)
			setSnapshotInfo(await snapshotInfoRaw.json())

			const eventsLocationBasedRaw = await fetch(
				"https://s3.amazonaws.com/static.simiotics.com/conquest-eth/eventsLocationBased.json"
			)
			const planetLocsFleetStatesRaw = await fetch(
				"https://s3.amazonaws.com/static.simiotics.com/conquest-eth/planetLocsFleetStates.json"
			)
			const parsedEvents = parseEvents(
				await eventsLocationBasedRaw.json(),
				await planetLocsFleetStatesRaw.json()
			)
			setEvents(parsedEvents)
		}

		fetchData().catch(() => {})
	}, [])

	return (
		<Layout snapshotInfo={snapshotInfo}>
			<Map
				events={events}
				setActiveLocation={setActiveLocation}
				fleetLimitState={fleetLimitState}
				setFleetLimitState={setFleetLimitState}
				fleetLimitStateHideZero={fleetLimitStateHideZero}
				setFleetLimitStateHideZero={setFleetLimitStateHideZero}
			/>
			<Sidebar
				events={events}
				activeLocation={activeLocation}
				fleetLimitState={fleetLimitState}
				setFleetLimitState={setFleetLimitState}
				fleetLimitStateHideZero={fleetLimitStateHideZero}
				setFleetLimitStateHideZero={setFleetLimitStateHideZero}
			/>
		</Layout>
	)
}

export default Index
