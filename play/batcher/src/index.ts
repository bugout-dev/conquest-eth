import * as fs from "fs"
import * as path from "path"

import getStream from "get-stream"
import { parse } from "csv-parse"
import Web3 from "web3"

const WEB3_URI = process.env.WEB3_URI
const CONTRACT_ABI_NAME = process.env.CONTRACT_ABI_NAME
const DATA_FILE_NAME = process.env.DATA_FILE_NAME
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS

class Contract {
	web3: Web3
	contract: any

	constructor(web3Uri: string, abi: any[], address: string) {
		try {
			this.web3 = new Web3(web3Uri)
			this.contract = new this.web3.eth.Contract(abi, address)
		} catch (err) {
			console.error(`Failed to initialize the contract:\n${err}`)
		}
	}

	// Fetch data from contract in batches
	_makeBatchRequest(calls) {
		const batch = new this.web3.BatchRequest()

		const promises = calls.map((call) => {
			return new Promise((res, rej) => {
				const req = call.request({}, (err, data) => {
					if (err) rej(err)
					else res(data)
				})
				batch.add(req)
			})
		})
		batch.execute()

		return Promise.all(promises)
	}

	async crawlUpdatedPlanetStateFromBlockchain(locations: string[], batchSize: number = 200) {
		let result = {}
		let dataFromBlockchain = []

		const total = locations.length
		for (let i = 1; i <= total; i += batchSize) {
			console.log(`Crawling owners batch ${i}`)
			let rawRequests = []
			for (let j = i; j <= Math.min(i + batchSize - 1, total); j++) {
				rawRequests.push(this.contract.methods.getUpdatedPlanetState(locations[j - 1]).call)
			}
			const response = await this._makeBatchRequest(rawRequests)
			dataFromBlockchain.push(...response)
		}

		dataFromBlockchain = await Promise.all(dataFromBlockchain)
		dataFromBlockchain.forEach((data, i) => {
			result[locations[i]] = data[3]
		})
		return result
	}
}

const readCsv = async (dataPath): Promise<any> => {
	let output = []
	const parseStream = parse({ delimiter: "," })
	const data = await getStream.array(fs.createReadStream(dataPath).pipe(parseStream))
	data.forEach(line => {
		const lineClean = line.toString().trim()
		if (lineClean !== "") {
			output.push(lineClean)
		}
	})
	return output
}

async function main() {
	const dataPath = path.join(__dirname, "..", "..", "data", DATA_FILE_NAME)
	const locations = await readCsv(`${dataPath}.csv`)
	console.log(`Prepared ${locations.length} locations`)

	const abiPath = path.join(__dirname, "..", "..", "abi", `${CONTRACT_ABI_NAME}.json`)
	const abiJson = JSON.parse(fs.readFileSync(abiPath, "utf8"))
	const contract = new Contract(WEB3_URI, abiJson, CONTRACT_ADDRESS)

	const result = await contract.crawlUpdatedPlanetStateFromBlockchain(locations, 100)

	const outputDataPath = path.join(__dirname, "..", "..", "data", `${DATA_FILE_NAME}FleetStates.json`)
	fs.writeFileSync(outputDataPath, JSON.stringify(result))
}

main()
	.then(() => process.exit(0))
	.catch((error) => {
		console.log(error)
		process.exit(1)
	})
