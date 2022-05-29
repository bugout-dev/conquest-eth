import React, { useEffect } from "react"
import Head from "next/head"

import styles from "../styles/Layout.module.css"

const Layout = ({ children, title = "map" }) => {
	useEffect(() => {}, [])

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
								<a href="https://moonstream.to">MOONSTREAM</a>
							</li>
							<li className={styles.nav_right}>
								<a href="/">MAP</a>
							</li>
							<li>
								<a href="/">ABOUT</a>
							</li>
						</ul>
					</nav>
				</header>
				<main className={styles.main}>{children}</main>
				<footer className={styles.footer}>
					<p>© 2022 MOONSTREAM</p>
				</footer>
			</div>
		</>
	)
}

export default Layout
