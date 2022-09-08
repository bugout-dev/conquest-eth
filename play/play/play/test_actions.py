import os
import unittest

from .actions import (
    gen_file_hash_name,
    get_latest_state_from_file,
    write_latest_state_to_file,
    get_state_from_file,
)


class TestActions(unittest.TestCase):
    def setUp(self):
        self.start_ts = 1655329800
        self.to_loc = 9868188640707215440437863615521278132084
        self.from_loc = 9868188640707215440437863615521278132085
        self.hash_str_expected = "a2914ea6316f1e188edc0c43333cce142317aa986fd0"
        self.start_state = {"action": 1, "ts": 0, "confirmation_event_ts": 0}

        self.this_dir = os.path.abspath(os.path.dirname(__file__))

    def test_gen_file_hash_name(self):
        hash_str = gen_file_hash_name(self.start_ts, self.to_loc, self.from_loc, True)

        self.assertEqual(hash_str, self.hash_str_expected)

    def test_file_start_state(self):
        state_file_hash = gen_file_hash_name(self.start_ts, self.to_loc, self.from_loc, True)
        file_path = os.path.join(self.this_dir, f"{state_file_hash}.jsonl")

        latest_state, file_path = get_latest_state_from_file(file_path)
        self.assertEqual(latest_state, None)

        write_latest_state_to_file(self.start_state, file_path)
        latest_state, file_path = get_latest_state_from_file(file_path)
        self.assertEqual(latest_state, self.start_state)

        os.remove(file_path)

    def test_file_new_state(self):
        state_file_hash = gen_file_hash_name(self.start_ts, self.to_loc, self.from_loc, True)
        file_path = os.path.join(self.this_dir, f"{state_file_hash}.jsonl")

        write_latest_state_to_file(self.start_state, file_path)
        new_state = {"action": 2, "ts": 1655296200, "confirmation_event_ts": 0}
        write_latest_state_to_file(new_state, file_path)
        latest_state, file_path = get_latest_state_from_file(file_path)
        self.assertEqual(latest_state, new_state)

        os.remove(file_path)

    def test_file_update_existing_state(self):
        state_file_hash = gen_file_hash_name(self.start_ts, self.to_loc, self.from_loc, True)
        file_path = os.path.join(self.this_dir, f"{state_file_hash}.jsonl")

        write_latest_state_to_file(self.start_state, file_path)
        new_state = {"action": 2, "ts": 1655296200, "confirmation_event_ts": 0}
        write_latest_state_to_file(new_state, file_path)
        latest_state, file_path = get_latest_state_from_file(file_path)
        self.assertEqual(latest_state, new_state)

        updated_state = latest_state
        updated_state["confirmation_event_ts"] = 1655318300
        write_latest_state_to_file(updated_state, file_path)
        latest_state, file_path = get_latest_state_from_file(file_path)
        self.assertEqual(latest_state, updated_state)

        os.remove(file_path)

    def test_file_get_state_by_index(self):
        state_file_hash = gen_file_hash_name(self.start_ts, self.to_loc, self.from_loc, True)
        file_path = os.path.join(self.this_dir, f"{state_file_hash}.jsonl")

        write_latest_state_to_file(self.start_state, file_path)
        new_state = {"action": 2, "ts": 1655296200, "confirmation_event_ts": 0}
        write_latest_state_to_file(new_state, file_path)
        state, file_path = get_state_from_file(1, file_path)
        self.assertEqual(state, self.start_state)

        os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
