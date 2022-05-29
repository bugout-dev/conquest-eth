import { Html } from "@react-three/drei"

import styles from "../../styles/Details.module.css"

const Details = ({ eventDetails }) => {
	return (
		<Html>
			<div className={styles.popup}>
				<div className={styles.line_slope}></div>
				<div className={styles.popup_details}>
					<div className={styles.popup_details_header}>
						<p>{eventDetails.name}</p>
					</div>
					<div className={styles.popup_details_main}>
						<p>
							coords: {eventDetails.locX}, {eventDetails.locY}
						</p>
						{eventDetails.quantity && (
							<p>quantity: {eventDetails.quantity.toLocaleString()}</p>
						)}
						{eventDetails.stake && (
							<p>
								stake: {eventDetails.stake / 1000000000000000000}
							</p>
						)}
					</div>
				</div>
			</div>
		</Html>
	)
}

export default Details
