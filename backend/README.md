# backend

Fetch all events and generate data for frontend

```bash
cem generate -q "most-recent-event-per-planet-loc-based.sql" --output ../frontend/public/eventsLocationBased.json
```

Make snapshot

```bash
cem snapshot-info --output ../frontend/public/snapshotInfo.json
```
