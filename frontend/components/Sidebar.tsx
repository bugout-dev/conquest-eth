import { useEffect, useState, useRef } from "react"

import SidebarDataRow from "./SidebarDataRow"
import { saturationSteps } from "./events"
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

	const [colorBox, setColorBox] = useState([])

	useEffect(() => {
		let colorBoxDiv = []
		for (const [key, value] of Object.entries(saturationSteps)) {
			const color = `hsl(203, ${Math.round((39 * value[2]) / 100)}%, 44%)`
			colorBoxDiv.push(
				<div
					className={styles.color_box}
					style={{
						backgroundColor: color,
						width: `${100 / Object.keys(saturationSteps).length}%`
					}}
				><p>{key}</p></div>
			)
		}
		setColorBox(colorBoxDiv)
	}, [])

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
				<img
					className={styles.icon}
					src="icon-filter.png"
					alt="Filter icon"
				/>
				<p>Fleet Filters</p>
			</div>
			<div className={styles.options}>
				<span className={styles.fleet_state_text}>
					Fleet state on the planet ≤
				</span>
				<div className={styles.fleet_state}>
					<input
						className={styles.short_input}
						value={fleetLimitState}
						type="number"
						onChange={(e) =>
							setFleetLimitState(parseInt(e.target.value))
						}
					/>
				</div>
			</div>
			<div className={styles.options}>
				<span className={styles.fleet_state_text}>
					Hide empty fleet state
				</span>
				<div className={styles.fleet_state}>
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
				<img
					className={styles.icon}
					src="icon-data.png"
					alt="Data icon"
				/>
				<p>List of events</p>
			</div>
			<div
				className={styles.data}
				style={{
					maxHeight: windowHeight ? windowHeight - 480 : "200px"
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

			<div className={styles.title}>
				<img
					className={styles.icon}
					src="icon-filter.png"
					alt="Filter icon"
				/>
				<p>Time Range Filters</p>
			</div>
			<p>Time since the last event on the planet (days)</p>
			<div className={styles.options}>
				<div className={styles.color_range}>{colorBox}</div>
			</div>
		</div>
	)
}

export default Sidebar
