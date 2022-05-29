import { useEffect, useState } from "react"

import { parseEvents, fleetSizeColor } from "./events"
import styles from "../styles/Sidebar.module.css"

const Sidebar = ({ data }) => {
	const [dataList, setDataList] = useState([])

	useEffect(() => {
		const [eventFleetSent, eventExitComplete] = parseEvents(data)

		let fleetSentList = []
		eventFleetSent.forEach((loc) => {
			fleetSentList.push(
				<div
					className={styles.sidebar_data_row}
					key={`${loc.x}-${loc.y}`}
				>
					<span className={styles.sidebar_data_loc}>
						{loc.x}, {loc.y}
					</span>
					<span style={{ color: fleetSizeColor(loc.quantity) }}>
						Fleet Sent
					</span>
					<span>{loc.quantity.toLocaleString()}</span>
				</div>
			)
		})
		setDataList(fleetSentList)
	}, [])

	return (
		<div className={styles.sidebar}>
			<div className={styles.sidebar_title}>
				<p>Events</p>
			</div>
			<div className={styles.sidebar_data}>{dataList}</div>
		</div>
	)
}

export default Sidebar
