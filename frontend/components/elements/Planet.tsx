import { useLayoutEffect, useRef, useState } from "react"
import * as THREE from "three"
import { useFrame } from "@react-three/fiber"

import Details from "./Details"

const Planet = (props: JSX.IntrinsicElements["mesh"]) => {
    const planetRef = useRef<THREE.Mesh>(null!)
    const ringRef = useRef<THREE.Mesh>(null!)
    const canvasRef = useRef(document.createElement("canvas"))

    const [hoveredElement, setHoverElement] = useState(false)
    const [activeElement, setActiveElement] = useState(false)

    // useLayoutEffect(() => {
    // 	const canvas = canvasRef.current

    // 	canvas.width = props.windowWidth
    // 	canvas.height = props.windowHeight

    // 	const ctx = canvas.getContext("2d")
    // 	if (ctx) {
    // 		ctx.fillStyle = "#ffffff"
    // 		ctx.fillRect(0, 0, 64, 32)

    // 		ctx.fillStyle = "#666666"
    // 		ctx.fillRect(8, 8, 48, 24)
    // 	}
    // }, [])

    useFrame((state, delta) => {
        // const canvas = canvasRef.current
        // canvas.width = window.innerWidth
        // canvas.height = window.innerHeight

        // const ctx = canvas.getContext("2d")
        // if (ctx) {
        // 	ctx.fillStyle = "purple"
        // 	ctx.fillRect(0, 0, 20, 20)
        // }
        // if (ringRef) {
        // 	ringRef.current.rotation += 0.01;
        // }
        // if (ringRef !== null) {
        // 	console.log(ringRef)
        // }
        if (hoveredElement) {
            ringRef.current.rotation.z += 0.01
        }
    })

    return (
        <mesh
            {...props}
            ref={planetRef}
            onPointerOver={() => setHoverElement(true)}
            onPointerOut={() => setHoverElement(false)}
            onClick={() => {
                setActiveElement(!activeElement)
                props.setActiveLocation([
                    props.eventDetails.locX,
                    props.eventDetails.locY,
                ])
            }}
        >
            <sphereBufferGeometry args={[0.5, 20, 20]} />
            <meshStandardMaterial color={props.color} />

            {hoveredElement && (
                <>
                    <mesh ref={ringRef}>
                        <ringGeometry
                            args={[1, 1.2, 40, 1, 0, 0.5 * Math.PI]}
                        />
                        <meshBasicMaterial
                            color="white"
                            // transparent={true}
                            // opacity={0.5}
                            // side={THREE.DoubleSide}
                        />
                    </mesh>
                    <mesh>
                        <ringGeometry args={[2, 2.2, 40]} />
                        <meshBasicMaterial
                            color="white"
                            // transparent={true}
                            // opacity={0.5}
                            // side={THREE.DoubleSide}
                        />
                    </mesh>
                    <Details eventDetails={props.eventDetails} />
                </>
            )}
        </mesh>
    )
}

export default Planet
