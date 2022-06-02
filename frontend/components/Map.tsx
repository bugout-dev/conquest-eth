import React, { useState, useEffect } from "react"
import { Canvas } from "@react-three/fiber"
import { Edges } from "@react-three/drei"

import Planet from "./elements/Planet"
import { OrthographicCameraHelper } from "./elements/Camera"
import Controls from "./elements/Controls"
import Light from "./elements/Light"
import { eventTypeColor } from "./events"
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

// Docs: https://docs.pmnd.rs/react-three-fiber
const Map = ({
	events,
	setActiveLocation,
	fleetLimitState,
	setFleetLimitState,
	fleetLimitStateHideZero,
	setFleetLimitStateHideZero
}) => {
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

	const [eventLocs, setEventLocs] = useState([])
	const [sectors, setSectors] = useState(<></>)

	useEffect(() => {
		// Grid
		// TODO(kompotkot): Move in component
		const step = 16
		const shift = 8

		let sectorItems = []
		for (let i = 0; i <= step * 2 * shift; i += step) {
			for (let j = 0; j <= step * 2 * shift; j += step) {
				sectorItems.push(
					<mesh position={[i, j, 0]}>
						<boxGeometry args={[16, 16, 0]} />
						<meshBasicMaterial opacity={0.0} transparent={true} />
						<Edges color="#303a4d" />
					</mesh>
				)
			}
		}

		let fullSectorItem = (
			<mesh position={[-step * shift, -step * shift, 0]}>
				{sectorItems}
			</mesh>
		)

		setSectors(fullSectorItem)
	}, [])

	useEffect(() => {
		// Generate planets to render on the scene
		let eventItems = []
		events.forEach((event) => {
			eventItems.push(
				<Planet
					color={eventTypeColor(event.name, event.blockTimestamp)}
					scale={1}
					eventDetails={event}
					position={[event.locX, -1 * event.locY, 0]} // event.locY should be multiplied to -1 because of strange original conquest-eth positioning
					key={`map-${event.locX}-${event.locY}`}
					windowWidth={window.innerWidth}
					windowHeight={window.innerWidth}
					setActiveLocation={setActiveLocation}
				/>
			)
		})
		setEventLocs(eventItems)
	}, [events])

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
				{/* <axesHelper args={[10]} /> */}
				{/* <OrthographicCameraHelper
					left={cameraConfig.left}
					right={cameraConfig.right}
					top={cameraConfig.top}
					bottom={cameraConfig.bottom}
					near={cameraConfig.near}
					far={cameraConfig.far}
					posX={cameraConfig.posX}
					posY={cameraConfig.posY}
					posZ={cameraConfig.posZ}
				/> */}
				<Light />
				<boxGeometry args={[16, 16, 0.5]} />
				<meshBasicMaterial opacity={0.0} transparent={true} />
				<Edges color="#435169" />
				{sectors}
				{eventLocs.filter((el) => {
					// Filtering planets by setting number of fleet value
					if (
						parseInt(el.props.eventDetails.currentFleetState) <=
						fleetLimitState
					) {
						if (
							fleetLimitStateHideZero &&
							parseInt(
								el.props.eventDetails.currentFleetState
							) !== 0
						) {
							return el
						}
						if (!fleetLimitStateHideZero) {
							return el
						}
					}
				})}
			</Canvas>
		</div>
	)
}

export default Map
