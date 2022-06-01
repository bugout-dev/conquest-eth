import Layout from "../components/Layout"
import snapshotInfo from "../public/snapshotInfo.json"
import styles from "../styles/About.module.css"

const About = () => {
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

export async function getStaticProps() {
	return {
		props: { snapshotInfo }
	}
}
