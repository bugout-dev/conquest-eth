import { useEffect, useRef } from "react"

import { eventTypeColor } from "./events"
import styles from "../styles/Sidebar.module.css"

const SidebarDataRow = ({ event, activeLocation, setActiveSidebarRef }) => {
	const itemRef = useRef(null)

	// Responsible for scrolling to row with information about picked planet
	if (
		activeLocation !== null &&
		event.locX === activeLocation[0] &&
		event.locY === activeLocation[1]
	) {
		setActiveSidebarRef(itemRef)
	}

	return (
		<div
			ref={itemRef}
			className={styles.row}
			style={{
				backgroundColor:
					activeLocation !== null &&
					event.locX === activeLocation[0] &&
					event.locY === activeLocation[1]
						? "#2d3748"
						: "#1a202c"
			}}
			key={`sidebar-${event.locX}-${event.locY}`}
		>
			<span
				className={
					event.locX >= 0
						? styles.locX
						: styles.locXnegative
				}
			>
				{event.locX}
			</span>
			<span
				className={
					event.locX >= 0
						? styles.locY
						: styles.locYnegative
				}
			>
				{event.locY}
			</span>
			<span
				className={styles.event_name}
				style={{
					color: eventTypeColor(event.name, event.blockTimestamp)
				}}
			>
				{event.name}
			</span>
			<span className={styles.fleet_state}>
				{parseInt(event.currentFleetState).toLocaleString()}
			</span>
		</div>
	)
}

export default SidebarDataRow
