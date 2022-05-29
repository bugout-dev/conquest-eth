import { OrthographicCamera, PerspectiveCamera } from "three"

export const PerspectiveCameraHelper = (props: {
	fov: number
	aspect: number
	near: number
	far: number
	posX: number
	posY: number
	posZ: number
}) => {
	const camera = new PerspectiveCamera(
		props.fov,
		props.aspect,
		props.near,
		props.far
	)
	return (
		<group position={[props.posX, props.posY, props.posZ]}>
			<cameraHelper args={[camera]} />
		</group>
	)
}

export const OrthographicCameraHelper = (props: {
	left: number
	right: number
	top: number
	bottom: number
	near: number
	far: number
	posX: number
	posY: number
	posZ: number
}) => {
	const camera = new OrthographicCamera(
		props.left,
		props.right,
		props.top,
		props.bottom,
		props.near,
		props.far
	)
	return (
		<group position={[props.posX, props.posY, props.posZ]}>
			<cameraHelper args={[camera]} />
		</group>
	)
}
