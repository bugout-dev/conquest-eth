import React, {useState} from "react"

import { getData } from "../api/receiver"
import Layout from "../components/Layout"
import Map from "../components/Map"
import Sidebar from "../components/Sidebar"
import dataFile from "../data.json"
import snapshotInfo from "../snapshotInfo.json"

const Index = ({ data, snapshotInfo }) => {
	const [activeLocation, setActiveLocation] = useState(null)
	const [activeLocationSidebarRef, setActiveLocationSidebarRef] = useState(null)
	return (
		<Layout snapshotInfo={snapshotInfo}>
			<Map data={data} setActiveLocation={setActiveLocation} />
			<Sidebar data={data} activeLocation={activeLocation} />
		</Layout>
	)
}

export default Index
export async function getStaticProps() {
	// const data = await getData()
	const data = dataFile

	return {
		props: { data, snapshotInfo }
	}
}
