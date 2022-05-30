WITH on_location_events AS (
    SELECT
        label_data -> 'args' ->> 'location' as planet_location,
        label_data ->> 'name' as event_name,
        label_data as label_data,
        block_timestamp,
        block_number
    FROM
        xdai_labels
    WHERE
        address = '0x7ed5118E042F22DA546C9aaA9540D515A6F776E9'
        and label_data -> 'args' ->> 'location' IS NOT NULL
    ORDER BY
        block_timestamp DESC
),
fleet_sent_events AS (
    SELECT
        label_data->'args'->>'from' as planet_location,
        label_data ->> 'name' as event_name,
        label_data as label_data,
        block_timestamp,
        block_number
    FROM
        xdai_labels
    WHERE
        address = '0x7ed5118E042F22DA546C9aaA9540D515A6F776E9'
        and label_data ->> 'name' = 'FleetSent'
    ORDER BY
        block_timestamp DESC
),
fleet_arrived_events AS (
    SELECT
        label_data->'args'->>'destination' as planet_location,
        label_data ->> 'name' as event_name,
        label_data as label_data,
        block_timestamp,
        block_number
    FROM
        xdai_labels
    WHERE
        address = '0x7ed5118E042F22DA546C9aaA9540D515A6F776E9'
        and label_data ->> 'name' = 'FleetArrived'
    ORDER BY
        block_timestamp DESC
),
union_events AS (
    SELECT
        planet_location,
        event_name,
        label_data,
        block_timestamp,
        block_number
    FROM
        on_location_events
    UNION
    SELECT
        planet_location,
        event_name,
        label_data,
        block_timestamp,
        block_number
    FROM
        fleet_sent_events
    UNION
    SELECT
        planet_location,
        event_name,
        label_data,
        block_timestamp,
        block_number
    FROM
        fleet_arrived_events
),
all_events AS (
    SELECT
        *
    FROM
        union_events
    ORDER BY
        block_timestamp DESC
)
SELECT
    DISTINCT ON(planet_location)
    planet_location,
    event_name,
    label_data,
    block_timestamp,
    block_number
FROM
    all_events;