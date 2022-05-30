import { useEffect, useState, useRef } from "react"

import parseEvents, { eventTypeColor } from "./events"
import styles from "../styles/Sidebar.module.css"

const Sidebar = ({ eventsLocationBased, activeLocation }) => {
    const [dataList, setDataList] = useState([])
    const [activeSidebarRef, setActiveSidebarRef] = useState(null)

	useEffect(() => {
		if (activeSidebarRef && activeSidebarRef.current && activeSidebarRef.current.scrollIntoView) {
			activeSidebarRef.current.scrollIntoView()
		}
	}, [activeSidebarRef])

    useEffect(() => {
        console.log("Active location: ", activeLocation)
    }, [activeLocation])

    useEffect(() => {
        const events = parseEvents(eventsLocationBased)

        let eventItems = []
        events.forEach((event) => {
            eventItems.push(
                <SidebarItem
                    event={event}
                    activeLocation={activeLocation}
                    setActiveSidebarRef={setActiveSidebarRef}
                />
            )
        })
        setDataList(eventItems)
    }, [activeLocation])

    return (
        <div className={styles.sidebar}>
            <div className={styles.sidebar_title}>
                <p>Events</p>
            </div>
            <div className={styles.sidebar_data}>{dataList}</div>
        </div>
    )
}

const SidebarItem = ({ event, activeLocation, setActiveSidebarRef }) => {
    const itemRef = useRef(null)

	if (activeLocation !== null && event.locX === activeLocation[0] && event.locY === activeLocation[1]) {
		setActiveSidebarRef(itemRef)
	}

    return (
        <div
			ref={itemRef}
            className={styles.sidebar_data_row}
            style={{
                backgroundColor:
                    activeLocation !== null &&
                    event.locX === activeLocation[0] &&
                    event.locY === activeLocation[1]
                        ? "#2d3748"
                        : "#1a202c",
            }}
            key={`sidebar-${event.locX}-${event.locY}`}
        >
            <span className={styles.sidebar_data_loc}>
                {event.locX}, {event.locY}
            </span>
            <span style={{ color: eventTypeColor(event.name, event.blockTimestamp) }}>
                {event.name}
            </span>
        </div>
    )
}

export default Sidebar
