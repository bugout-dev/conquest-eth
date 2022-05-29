select
    label_data->'args'->>'location' as planet_location,
    count(*) as num_transfers
from
    xdai_labels
where
    address = '0x7ed5118E042F22DA546C9aaA9540D515A6F776E9'
    and label_data->>'name' = 'Transfer'
group by label_data->'args'->>'location'
order by num_transfers desc;
