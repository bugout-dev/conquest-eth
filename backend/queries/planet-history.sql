select
    block_number,
    block_timestamp,
    transaction_hash,
    label_data ->> 'name' as event_name,
    label_data as event_data
from
    xdai_labels
where
    address = '0x7ed5118E042F22DA546C9aaA9540D515A6F776E9'
    and label_data -> 'args' ->> 'location' = '115792089237316195423570985008687907843061513658012410135556345784960083296240'
    or label_data -> 'args' ->> 'from' = '115792089237316195423570985008687907843061513658012410135556345784960083296240'
order by
    block_timestamp asc;
