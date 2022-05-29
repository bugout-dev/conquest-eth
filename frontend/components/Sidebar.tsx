import { useEffect, useState } from "react"

import parseEvents, { eventTypeColor } from "./events"
import styles from "../styles/Sidebar.module.css"

const Sidebar = ({ data }) => {
	const [dataList, setDataList] = useState([])

	useEffect(() => {
		const events = parseEvents(data)

		let eventItems = []
		events.forEach((event) => {
			eventItems.push(
				<div
					className={styles.sidebar_data_row}
					key={`sidebar-${event.locX}-${event.locY}`}
				>
					<span className={styles.sidebar_data_loc}>
						{event.locX}, {event.locY}
					</span>
					<span style={{ color: eventTypeColor(event.name) }}>
						{event.name}
					</span>
				</div>
			)
		})
		setDataList(eventItems)
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
