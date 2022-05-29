import { extend, ReactThreeFiber, useThree } from "@react-three/fiber"
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls"

const Controls = () => {
	const {
		camera,
		gl: { domElement }
	} = useThree()

	return <orbitControls args={[camera, domElement]} />
}

// Overwrite global elements
extend({ OrbitControls })

declare global {
	namespace JSX {
		interface IntrinsicElements {
			orbitControls: ReactThreeFiber.Object3DNode<
				OrbitControls,
				typeof OrbitControls
			>
		}
	}
}

export default Controls
