import { useRef } from "react"
import * as THREE from "three"

const Light = (props: JSX.IntrinsicElements["mesh"]) => {
	const lightRef = useRef<THREE.Mesh>(null!)

	return (
		<mesh ref={lightRef}>
			<ambientLight />
            <pointLight position={[0, 0, 5]} intensity={3} />
		</mesh>
	)
}

export default Light
