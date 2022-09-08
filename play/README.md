# conquest-eth

## Data preparation

### Script automation

Fetch data

```bash
./coe-prepare-data.bash
```

Upload to static AWS S3 bucket

```bash
./coe-upload-s3-data.bash
```

### Manually

Fetch all events and generate data for frontend

```bash
coe generate --output data/eventsLocationBased.json locations --query most-recent-event-per-planet-loc-based.sql
```

Make snapshot

```bash
coe generate --output data/snapshotInfo.json snapshot-info --query snapshot-info.sql
```

Fetch planet locations

```bash
psql $MOONSTREAM_DB_URI_READ_ONLY -f queries/planet-locs.sql -t -o data/planetLocs.csv
```

Fetch fleet size for each location with `batcher`

```bash
CONTRACT_ABI_NAME="defcon-OuterSpace" CONTRACT_ADDRESS="$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" DATA_FILE_NAME="planetLocs" npm run batch
```

## Config

Add moonstream moonstream xdai rpc endpoint in brownie networks list

```bash
brownie networks add XDai xdai-moonstream host="<JSON_RPC_URI>" chainid=100
```

## Address book

```bash
export CONQUEST_ETH_MAIN_CONTRACT_ADDRESS="0x7ed5118E042F22DA546C9aaA9540D515A6F776E9"
export CONQUEST_ETH_PLAY_TOKEN_ADDRESS="0x1874F6326eEbcCe664410a93a5217741a977D14A"
export USER_PUBLIC_ADDRESS="<your_ingame_address>"
```

## Play ERC20 token

Mint `0.1 PLAY` **NOT WORKING**

```bash
python play/play/PlayToken.py mint --network "xdai-moonstream" --address "$CONQUEST_ETH_PLAY_TOKEN_ADDRESS" --sender "../.secrets/keyfile" --to "$USER_PUBLIC_ADDRESS" --amount 1000000000000000 --gas-price "2 gwei" --value 1000000000000000
```

Stake the planet

```bash
python play/play/PlayToken.py transfer-and-call --network "xdai-moonstream" --address "$CONQUEST_ETH_PLAY_TOKEN_ADDRESS" --sender .secrets/keyfile --gas-price "2 gwei" \
    --to "$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" \
    --amount 1300000000000000000 \
    --data "0x000000000000000000000000536828c36a82a9054a18d8962660664b889dd00f0000000000000000000000000000004cffffffffffffffffffffffffffffffb2"
```

Prepare data for planet stake

```bash
coe generate calldata -o "$USER_PUBLIC_ADDRESS" -l 26201742252912261686679844772246152282034
```

## Main contract

-   `get-planet`
-   `get-updated-planet-state` - shows number of current spaceships on planet and owner of planet

### Example of calls

Get planet initial info with current owner

```bash
python play/play/OuterSpace.py get-planet --network "xdai-moonstream" --address "$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" --location 22458636216781938588582724090496701956057
```

Get planet updated state

```bash
python play/play/OuterSpace.py get-updated-planet-state --network "xdai-moonstream" --address "$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" --location 22458636216781938588582724090496701956057
```

Send fleet

```bash
python play/play/OuterSpace.py send --network "xdai-moonstream" --address "$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" --sender .secrets/keyfile --gas-price "2 gwei" --from-arg 22118353849861000125119349483064933744601 --to-hash "0x94a847bfa749dca51a0ad9d9d2686006f3e7739125ccb573afd93511b516de6e" --quantity 13
```

Send-for fleet (fleetSender,fleetOwner,from,quantity,toHash)

```bash
python play/play/OuterSpace.py send-for --network "xdai-moonstream" --address "$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" --sender .secrets/keyfile --gas-price "2 gwei" \
    --launch "$USER_PUBLIC_ADDRESS" "$USER_PUBLIC_ADDRESS" 22118353849861000125119349483064933744601 20000 '0xd36157863297ecafd6f021c4fe9f753094c0df57930b2a305d2fbfe24e40f0d4' \
    --nonce 42
```

Resolve fleet

```bash
python play/play/OuterSpace.py resolve-fleet --network "xdai-moonstream" --address "$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" --sender ".secrets/keyfile" --gas-price "2 gwei" \
 --fleet-id 72832651760500237141355142819238817597582057266177857304604040019537869861473 \
 --fromPlanet 22118353849861000125119349483064933744601 \
 --toPlanet 21778071482940061661655974875633165533145 \
 --distance 4 \
 --arrivalTimeWanted 1654737900 \
 --gift True \
 --specific "0x0000000000000000000000000000000000000001" \
 --secret "0xe8b24b213b8ac6b92bc88685da782c8920fbd160f8060374af1e9d00eae35f60" \
 --fleetSender "$USER_PUBLIC_ADDRESS" \
 --operator "$USER_PUBLIC_ADDRESS"
```

Exit planet

```bash
python play/play/OuterSpace.py exit-for --network "xdai-moonstream" --address "$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" --sender .secrets/keyfile --gas-price "2 gwei" \
    --owner "$USER_PUBLIC_ADDRESS" --location 21778071482940061661655974875633165533145
```

## Alliance contract

Get alliance info

```bash
ALLIANCE_CONTRACT_ADDRESS="0x842D1b525Ee81Cd51fc8375E67eCA8E3870c5366"

python play/play/AllianceRegistry.py get-alliance-data --network "xdai-moonstream" --address "$ALLIANCE_CONTRACT_ADDRESS" --alliance 0xd57befb0b45e894e2188f21d2bb3830b3d4c4545
```

## Automation

-   Generate `start-ts`

```bash
date '+%s'
```

-   Start cultivation

```bash
coe automation --network "xdai-moonstream" --address "0x" --sender "$CONQUEST_ETH_KEYFILE_PATH" --gas-price "2 gwei" --password "$CONQUEST_ETH_PASSWORD" cultivation --base 123 --targets 123 --quantity 123 --ospace-address "$CONQUEST_ETH_MAIN_CONTRACT_ADDRESS" --play-address "$CONQUEST_ETH_PLAY_TOKEN_ADDRESS" --state-dir "$CONQUEST_ETH_STATE_DIR_PATH"
```

## Subgraph

URL: `https://subgraphs.etherplay.io/xdai/subgraphs/name/conquest-eth/conquest-defcon`

Detailed data:

```json
{
	"query": "query ($first: Int!, $lastId: ID!, $owner: String, $fromTime: Int!, $exitTimeEnd: Int!) {\n  nullplanets: planets(first: 1000, where: {owner: null}) {\n    id\n    numSpaceships\n    flagTime\n    travelingUpkeep\n    overflow\n    lastUpdated\n    exitTime\n    active\n    rewardGiver\n    __typename\n  }\n  otherplanets: planets(first: $first, where: {id_gt: $lastId, owner_not: $owner}) {\n    id\n    owner {\n      id\n      __typename\n    }\n    numSpaceships\n    flagTime\n    travelingUpkeep\n    overflow\n    lastUpdated\n    exitTime\n    active\n    rewardGiver\n    __typename\n  }\n  space(id: \"Space\") {\n    minX\n    maxX\n    minY\n    maxY\n    address\n    __typename\n  }\n  owner(id: $owner) {\n    id\n    playTokenBalance\n    freePlayTokenBalance\n    tokenToWithdraw\n    __typename\n  }\n  myplanets: planets(first: 1000, where: {owner: $owner}) {\n    id\n    owner {\n      id\n      __typename\n    }\n    numSpaceships\n    flagTime\n    travelingUpkeep\n    overflow\n    lastUpdated\n    exitTime\n    active\n    rewardGiver\n    __typename\n  }\n}",
	"variables": {
		"first": 500,
		"lastId": "0x0",
		"owner": "0xb9f5be0c11089730193e310380977841b04f5f34",
		"blockNumber": 23474853,
		"exitTimeEnd": 1659119564,
		"fromTime": 1658773964
	}
}
```

Planets data:

```json
{
	"query": "query ($first: Int!, $skip: Int!, $fromTime: Int!) {\n  planets: planets(first: 1000, skip: 1000) {\n    id\n    numSpaceships\n    travelingUpkeep\n    active\n    __typename\n   }\n}",
	"variables": { "first": 1000, "skip": 1000, "fromTime": 1659383000 }
}
```

Response line:

```json
{
	"data": {
		"planets": [
			{
				"id": "0x0000000000000000000000000000000000000000000000000000000000000002",
				"numSpaceships": "777871",
				"travelingUpkeep": "0",
				"active": false,
				"__typename": "Planet"
			}
		]
	}
}
```
