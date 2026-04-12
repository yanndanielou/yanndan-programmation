import datetime

import pytest
from stsloganalyzis import line_topology


@pytest.fixture(scope="session", name="next_line_fixture")
def next_line() -> line_topology.Line:
    line = line_topology.Line.load_from_csv(
        segments_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_segment.csv",
        track_circuits_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_track_circuit.csv",
        tracking_blocks_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_tracking_block.csv",
    )
    return line


class TestNextData:
    def test_tracking_blocks_are_created(self, next_line_fixture: line_topology.Line) -> None:
        line = next_line_fixture
        assert line.tracking_blocks
