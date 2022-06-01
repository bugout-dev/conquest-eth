import React, { useEffect, useState } from "react"
import Head from "next/head"

import styles from "../styles/Layout.module.css"

const Layout = ({ children, title = "map", snapshotInfo }) => {
	const [snapshotBlockNumber, setSnapshotBlockNumber] = useState(0)
	useEffect(() => {
		if (snapshotInfo && snapshotInfo.block_number) {
			setSnapshotBlockNumber(snapshotInfo.block_number)
		}
	}, [snapshotInfo])

	return (
		<>
			<Head>
				<title>{title}</title>
				<link
					rel="icon"
					href="https://s3.amazonaws.com/static.simiotics.com/moonstream/assets/favicon.png"
				/>
				<meta name="description" content="Map" />
			</Head>
			<div className={styles.container}>
				<header className={styles.header}>
					<nav>
						<ul className={styles.site_nav}>
							<li>
								<a href="/"><b>conquest-eth map</b></a>
							</li>
							<li className={styles.nav_right}>
								<a href="/about">About</a>
							</li>
							<li>
								<a
									href={`https://blockscout.com/xdai/mainnet/block/${snapshotBlockNumber}`}
									target="#"
								>
									Block Number:{" "}
									{snapshotBlockNumber.toLocaleString()}
								</a>
							</li>
						</ul>
					</nav>
				</header>
				<main className={styles.main}>{children}</main>
				<footer className={styles.footer}>
					<p>© 2022 moonstream</p>
				</footer>
			</div>
		</>
	)
}

export default Layout
