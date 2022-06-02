import { useEffect, useState, useRef } from "react"

import SidebarDataRow from "./SidebarDataRow"
import styles from "../styles/Sidebar.module.css"

const Sidebar = ({
	events,
	activeLocation,
	fleetLimitState,
	setFleetLimitState,
	fleetLimitStateHideZero,
	setFleetLimitStateHideZero
}) => {
	const [dataList, setDataList] = useState([])
	const [activeSidebarRef, setActiveSidebarRef] = useState(null)
	const [windowHeight, setWindowHeight] = useState<number>(undefined)

	useEffect(() => {
		setWindowHeight(window.innerHeight)

		if (
			activeSidebarRef &&
			activeSidebarRef.current &&
			activeSidebarRef.current.scrollIntoView
		) {
			activeSidebarRef.current.scrollIntoView()
		}
	}, [activeSidebarRef])

	useEffect(() => {
		// Generate row with data about each planet
		let eventItems = []
		events.forEach((event) => {
			eventItems.push(
				<SidebarDataRow
					event={event}
					activeLocation={activeLocation}
					setActiveSidebarRef={setActiveSidebarRef}
				/>
			)
		})
		setDataList(eventItems)
	}, [events, activeLocation])

	return (
		<div className={styles.sidebar}>
			<div className={styles.title}>
				<p>Options</p>
			</div>
			<div className={styles.options}>
				<div className={styles.fleet_state}>
					<input
						className={styles.short_input}
						value={fleetLimitState}
						type="number"
						onChange={(e) =>
							setFleetLimitState(parseInt(e.target.value))
						}
					/>
					<span className={styles.fleet_state_text}>fleet state</span>
					<input
						className={styles.checkbox}
						type="checkbox"
						onChange={(e) =>
							setFleetLimitStateHideZero(!fleetLimitStateHideZero)
						}
					/>
				</div>
			</div>
			<div className={styles.title}>
				<p>Events</p>
			</div>
			<div
				className={styles.data}
				style={{
					maxHeight: windowHeight ? windowHeight - 240 : "200px"
				}}
			>
				{dataList.filter((el) => {
					// Filtering data rows about planets by setting number of fleet value
					if (
						parseInt(el.props.event.currentFleetState) <=
						fleetLimitState
					) {
						if (
							fleetLimitStateHideZero &&
							parseInt(el.props.event.currentFleetState) !== 0
						) {
							return el
						}
						if (!fleetLimitStateHideZero) {
							return el
						}
					}
				})}
			</div>
		</div>
	)
}

export default Sidebar
