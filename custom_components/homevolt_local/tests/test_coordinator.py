import unittest
from datetime import timedelta
from unittest.mock import Mock, MagicMock
from custom_components.homevolt_local import HomevoltDataUpdateCoordinator


class TestCoordinator(unittest.TestCase):
    def test_merge_data(self):
        """Test the merging of data from multiple systems."""
        # Create a mock coordinator object with minimal setup
        coordinator = Mock(spec=HomevoltDataUpdateCoordinator)

        # Get the actual _merge_data method from the class
        merge_method = HomevoltDataUpdateCoordinator._merge_data

        main_data = {
            "aggregated": {"ecu_id": 1},
            "ems": [{"ecu_id": 1, "data": "main_ems_1"}],
            "sensors": [{"euid": "sensor1", "data": "main_sensor_1"}],
        }

        results = [
            (
                "host1",
                {
                    "ems": [
                        {"ecu_id": 1, "data": "host1_ems_1"},
                        {"ecu_id": 2, "data": "host1_ems_2"},
                    ],
                    "sensors": [{"euid": "sensor1", "data": "host1_sensor_1"}],
                },
            ),
            (
                "host2",
                {
                    "ems": [{"ecu_id": 3, "data": "host2_ems_3"}],
                    "sensors": [
                        {"euid": "sensor2", "data": "host2_sensor_2"},
                        {"euid": "sensor3", "data": "host2_sensor_3"},
                    ],
                },
            ),
        ]

        # Call the method with the mock self
        merged_data = merge_method(coordinator, results, main_data)

        # The aggregated data should be from the main data
        self.assertEqual(merged_data["aggregated"]["ecu_id"], 1)

        # The ems list should contain unique devices from all results
        self.assertEqual(len(merged_data["ems"]), 3)
        self.assertIn({"ecu_id": 1, "data": "main_ems_1"}, merged_data["ems"])
        self.assertIn({"ecu_id": 2, "data": "host1_ems_2"}, merged_data["ems"])
        self.assertIn({"ecu_id": 3, "data": "host2_ems_3"}, merged_data["ems"])

        # The sensors list should contain unique sensors from all results
        self.assertEqual(len(merged_data["sensors"]), 3)
        self.assertIn(
            {"euid": "sensor1",
                "data": "main_sensor_1"}, merged_data["sensors"]
        )
        self.assertIn(
            {"euid": "sensor2",
                "data": "host2_sensor_2"}, merged_data["sensors"]
        )
        self.assertIn(
            {"euid": "sensor3",
                "data": "host2_sensor_3"}, merged_data["sensors"]
        )


if __name__ == "__main__":
    unittest.main()
