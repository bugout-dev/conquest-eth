import { useRef } from "react"
import * as THREE from "three"

const Light = (props: JSX.IntrinsicElements["mesh"]) => {
	const lightRef = useRef<THREE.Mesh>(null!)

	return (
		<mesh ref={lightRef}>
			{/* <ambientLight /> */}
            <pointLight position={[0, 0, 200]} intensity={1} />
		</mesh>
	)
}

export default Light
