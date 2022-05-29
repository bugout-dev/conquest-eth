import React, { useState, useEffect } from "react"
import { Canvas } from "@react-three/fiber"

import Planet from "./elements/Planet"
import { OrthographicCameraHelper } from "./elements/Camera"
import Controls from "./elements/Controls"
import Light from "./elements/Light"
import { parseEvents, fleetSizeColor } from "./events"
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
const Map = ({ data }) => {
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

	const [fleetSentLocs, setFleetSentLocs] = useState([])
	const [exitCompleteLocs, setExitCompleteLocs] = useState([])

	useEffect(() => {
		setWindowWidth(window.innerWidth)
		setWindowHeight(window.innerHeight)

		const [eventFleetSent, eventExitComplete] = parseEvents(data)

		// Fleet Sent event
		let fleetSentItems = []
		eventFleetSent.forEach((loc) => {
			fleetSentItems.push(
				<Planet
					color={fleetSizeColor(loc.quantity)}
					scale={1}
					eventDetails={{
						name: "Fleet Sent",
						locX: loc.x,
						locY: loc.y,
						quantity: loc.quantity
					}}
					position={[loc.x, loc.y, 0]}
					key={`${loc.x}-${loc.y}`}
					windowWidth={window.innerWidth}
					windowHeight={window.innerWidth}
				/>
			)
		})
		setFleetSentLocs(fleetSentItems)

		// Exit Complete event
		let exitCompleteItems = []
		eventExitComplete.forEach((loc) => {
			exitCompleteItems.push(
				<Planet
					color="white"
					scale={1}
					eventDetails={{
						name: "Exit Complete",
						locX: loc.x,
						locY: loc.y,
						stake: loc.stake
					}}
					position={[loc.x, loc.y, 0]}
					key={`${loc.x}-${loc.y}`}
					eventStake={loc.stake}
				/>
			)
		})
		setExitCompleteLocs(exitCompleteItems)
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
				{fleetSentLocs}
				{exitCompleteLocs}
			</Canvas>
		</div>
	)
}

export default Map
