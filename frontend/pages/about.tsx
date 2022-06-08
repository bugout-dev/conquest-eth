import { useEffect, useState } from "react"

import Layout from "../components/Layout"
import styles from "../styles/About.module.css"

const About = () => {
	const [snapshotInfo, setSnapshotInfo] = useState(undefined)

	useEffect(() => {
		const fetchData = async () => {
			const snapshotInfoRaw = await fetch(
				"https://s3.amazonaws.com/static.simiotics.com/conquest-eth/snapshotInfo.json"
			)
			setSnapshotInfo(await snapshotInfoRaw.json())
		}

		fetchData().catch(() => {})
	}, [])

	return (
		<Layout snapshotInfo={snapshotInfo}>
			<div className={styles.description}>
				<p className={styles.text}>
					Build by <a href="https://moonstream.to">Moonstream</a> as
					plugin for{" "}
					<a href="https://conquest.etherplay.io">
						Conquest-eth game
					</a>
					.
				</p>
			</div>
		</Layout>
	)
}

export default About
