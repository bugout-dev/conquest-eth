WITH on_location_events AS (
    SELECT
        label_data -> 'args' ->> 'location' as planet_location
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
        label_data->'args'->>'from' as planet_location
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
        label_data->'args'->>'destination' as planet_location
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
        planet_location
    FROM
        on_location_events
    UNION
    SELECT
        planet_location
    FROM
        fleet_sent_events
    UNION
    SELECT
        planet_location
    FROM
        fleet_arrived_events
),
all_events AS (
    SELECT
        *
    FROM
        union_events
)
SELECT
    DISTINCT ON(planet_location)
    planet_location
FROM
    all_events;