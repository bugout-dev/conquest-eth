import React, { useState } from "react"

import Layout from "../components/Layout"
import Map from "../components/Map"
import Sidebar from "../components/Sidebar"
import eventsLocationBased from "../public/eventsLocationBased.json"
import snapshotInfo from "../public/snapshotInfo.json"

const Index = ({ eventsLocationBased, snapshotInfo }) => {
	const [activeLocation, setActiveLocation] = useState(null)
	return (
		<Layout snapshotInfo={snapshotInfo}>
			<Map eventsLocationBased={eventsLocationBased} setActiveLocation={setActiveLocation} />
			<Sidebar eventsLocationBased={eventsLocationBased} activeLocation={activeLocation} />
		</Layout>
	)
}

export default Index
export async function getStaticProps() {
	return {
		props: { eventsLocationBased, snapshotInfo }
	}
}
