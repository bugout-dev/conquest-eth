import React, { useEffect, useState } from "react"

import Layout from "../components/Layout"
import Map from "../components/Map"
import Sidebar from "../components/Sidebar"
import eventsLocationBased from "../public/eventsLocationBased.json"
import snapshotInfo from "../public/snapshotInfo.json"
import planetLocsStates from "../public/planetLocsStates.json"
import parseEvents from "../components/events"

const Index = ({ eventsLocationBased, snapshotInfo, planetLocsStates }) => {
	const [activeLocation, setActiveLocation] = useState(null)
	const [fleetLimitState, setFleetLimitState] = useState<number>(3200100)
	const [fleetLimitStateHideZero, setFleetLimitStateHideZero] =
		useState<boolean>(false)
	const [events, setEvents] = useState([])

	useEffect(() => {
		const events = parseEvents(eventsLocationBased, planetLocsStates)
		setEvents(events)
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

export async function getStaticProps() {
	return {
		props: { eventsLocationBased, snapshotInfo, planetLocsStates }
	}
}
