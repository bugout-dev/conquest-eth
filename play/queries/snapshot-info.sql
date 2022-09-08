SELECT
    block_number,
    block_timestamp
from
    xdai_labels
where
    address = '0x7ed5118E042F22DA546C9aaA9540D515A6F776E9'
order by
    block_number desc
limit
    1;
