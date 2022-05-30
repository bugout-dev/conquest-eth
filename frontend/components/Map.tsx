import React, { useState, useEffect } from "react"
import { Canvas } from "@react-three/fiber"

import Planet from "./elements/Planet"
import { OrthographicCameraHelper } from "./elements/Camera"
import Controls from "./elements/Controls"
import Light from "./elements/Light"
import parseEvents, {eventTypeColor} from "./events"
import styles from "../styles/Map.module.css"

export interface CameraConfig {
	posX: number
	posY: number
	posZ: number
	left: number
	right: number
	top: number
	bottom: number
	near: number
	far: number
	zoom: number
}

export interface Event {
	name: string
	locX: number
	locY: number
	quantity: number
	stake: number
}

// Docs: https://docs.pmnd.rs/react-three-fiber
const Map = ({ eventsLocationBased, setActiveLocation }) => {
	const cameraConfig: CameraConfig = {
		posX: 0,
		posY: 0,
		posZ: 10,
		left: -200,
		right: 200,
		top: 200,
		bottom: -200,
		near: 0,
		far: 20,
		zoom: 5
	}

	const [windowWidth, setWindowWidth] = useState<number>(undefined)
	const [windowHeight, setWindowHeight] = useState<number>(undefined)

	const [eventLocs, setEventLocs] = useState([])

	useEffect(() => {
		setWindowWidth(window.innerWidth)
		setWindowHeight(window.innerHeight)

		const events = parseEvents(eventsLocationBased)

		// Fleet Sent event
		let eventItems = []
		events.forEach((event) => {
			eventItems.push(
				<Planet
					color={eventTypeColor(event.name, event.blockTimestamp)}
					scale={1}
					eventDetails={event}
					position={[event.locX, event.locY, 0]}
					key={`map-${event.locX}-${event.locY}`}
					windowWidth={window.innerWidth}
					windowHeight={window.innerWidth}
					setActiveLocation={setActiveLocation}
				/>
			)
		})
		setEventLocs(eventItems)
	}, [])

	return (
		<div id={styles.map}>
			<Canvas
				id={styles.canvas}
				orthographic
				camera={{
					position: [
						cameraConfig.posX,
						cameraConfig.posY,
						cameraConfig.posZ
					],
					left: cameraConfig.left,
					right: cameraConfig.right,
					top: cameraConfig.top,
					bottom: cameraConfig.bottom,
					zoom: cameraConfig.zoom
				}}
			>
				<Controls />
				<axesHelper args={[10]} />
				<OrthographicCameraHelper
					left={cameraConfig.left}
					right={cameraConfig.right}
					top={cameraConfig.top}
					bottom={cameraConfig.bottom}
					near={cameraConfig.near}
					far={cameraConfig.far}
					posX={cameraConfig.posX}
					posY={cameraConfig.posY}
					posZ={cameraConfig.posZ}
				/>
				<Light />
				{eventLocs}
			</Canvas>
		</div>
	)
}

export default Map
