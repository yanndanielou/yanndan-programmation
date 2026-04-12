import pytest

from stsloganalyzis import line_topology


@pytest.fixture(scope="session", name="next_line_fixture")
def next_line() -> line_topology.Line:
    line = line_topology.Line.load_from_csv(
        segments_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_segment.csv",
        track_circuits_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_track_circuit.csv",
        tracking_blocks_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_tracking_block.csv",
        switches_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_switch.csv",
        segments_relations_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsSegmentRelation.csv",
        tracking_block_on_segments_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsLocUnitTopo.csv",
        tracking_block_on_segments_relations_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsTbOnSegmentRelation.csv",
        ignore_tracking_blocks_without_circuits=True,
    )
    return line


class TestNextData:
    def test_tracking_blocks_are_created(self, next_line_fixture: line_topology.Line) -> None:
        line = next_line_fixture
        assert line.tracking_blocks

    def test_tracking_blocks_ignored(self, next_line_fixture: line_topology.Line) -> None:
        line = next_line_fixture
        assert line.not_created_tracking_blocks_ids_without_track_circuits
        assert len(line.not_created_tracking_blocks_ids_without_track_circuits) < len(line.tracking_blocks)
        for not_created_tracking_blocks_id_without_track_circuit in line.not_created_tracking_blocks_ids_without_track_circuits:
            assert not_created_tracking_blocks_id_without_track_circuit.endswith("_IN") or not_created_tracking_blocks_id_without_track_circuit.endswith("_INOUT")

    def test_segments_relations(self, next_line_fixture: line_topology.Line) -> None:
        line = next_line_fixture
        segment_8329 = line.segment_by_number[8329]
        assert segment_8329
        assert segment_8329 is not None
        downstream_normal = segment_8329.downstream_normal
        assert downstream_normal
        assert downstream_normal.identifier.endswith("010211")
