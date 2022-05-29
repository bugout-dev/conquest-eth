WITH on_location_events AS (
    SELECT
        label_data->'args'->>'location' as planet_location,
        label_data->>'name' as event_name,
        label_data->'args' as event_data,
        block_timestamp
    FROM
        xdai_labels
    WHERE
        address = '0x7ed5118E042F22DA546C9aaA9540D515A6F776E9'
    ORDER BY block_timestamp DESC
),
fleet_sent_events AS (
    SELECT
        label_data->'args'->>'from' as planet_location,
        label_data->>'name' as event_name,
        label_data->'args' as event_data,
        block_timestamp
    FROM
        xdai_labels
    WHERE
        address = '0x7ed5118E042F22DA546C9aaA9540D515A6F776E9'
        and label_data->>'name' = 'FleetSent'
    ORDER BY block_timestamp DESC
),
all_events AS (
    SELECT * FROM on_location_events UNION SELECT * FROM fleet_sent_events ORDER BY block_timestamp DESC
)
SELECT DISTINCT ON(planet_location) planet_location, event_name, event_data, block_timestamp FROM all_events;
