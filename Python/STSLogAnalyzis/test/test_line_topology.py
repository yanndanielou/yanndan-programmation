import pytest

from logger import logger_config

from stsloganalyzis import line_topology
from typing import cast


@pytest.fixture(scope="session", name="next_line_fixture")
def next_line() -> line_topology.Line:
    line = line_topology.Line.load_from_csv(
        segments_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_segment.csv",
        track_circuits_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_track_circuit.csv",
        tracking_blocks_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_tracking_block.csv",
        switches_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_switch.csv",
        segments_relations_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsSegmentRelation.csv",
        tracking_block_on_segments_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsLocUnitTopo.csv",
        ignore_tracking_blocks_without_circuits=True,
    )
    logger_config.print_and_log_info("next_line_fixture is ready!")
    return cast("line_topology.Line", line)


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

    class TestDistances:

        class TestSegmentsExtremities:

            class TestSegmentExtremities0ToLength:
                def test_increasing(self, next_line_fixture: line_topology.Line) -> None:
                    line = next_line_fixture
                    seg1 = line.get_segment_from_segment_id_number_or_segment("SEG_010812")
                    assert seg1
                    distance_0_to_length = line.get_distance_in_cm_between_to_locations(
                        line_topology.ExactLocation(segment=seg1, abscissa=0),
                        line_topology.ExactLocation(segment=seg1, abscissa=seg1.length),
                        line_topology.SegmentDirection.INCREASING_OFFSET,
                    )
                    assert distance_0_to_length is not None
                    assert distance_0_to_length > 0
                    assert distance_0_to_length == seg1.length

                def test_decreasing(self, next_line_fixture: line_topology.Line) -> None:
                    line = next_line_fixture
                    seg1 = line.get_segment_from_segment_id_number_or_segment("SEG_010812")
                    assert (
                        line.get_distance_in_cm_between_to_locations(
                            line_topology.ExactLocation(segment=seg1, abscissa=0),
                            line_topology.ExactLocation(segment=seg1, abscissa=seg1.length),
                            line_topology.SegmentDirection.DECREASING_OFFSET,
                        )
                        is None
                    )

            class TestSegmentExtremitiesLengthTo0:

                def test_increasing(self, next_line_fixture: line_topology.Line) -> None:
                    line = next_line_fixture
                    seg = line.get_segment_from_segment_id_number_or_segment("SEG_010812")
                    assert (
                        line.get_distance_in_cm_between_to_locations(
                            line_topology.ExactLocation(segment=seg, abscissa=seg.length),
                            line_topology.ExactLocation(segment=seg, abscissa=0),
                            line_topology.SegmentDirection.INCREASING_OFFSET,
                        )
                        is None
                    )

                def test_decreasing(self, next_line_fixture: line_topology.Line) -> None:
                    line = next_line_fixture
                    seg = line.get_segment_from_segment_id_number_or_segment("SEG_010812")
                    assert (
                        line.get_distance_in_cm_between_to_locations(
                            line_topology.ExactLocation(segment=seg, abscissa=seg.length),
                            line_topology.ExactLocation(segment=seg, abscissa=0),
                            line_topology.SegmentDirection.DECREASING_OFFSET,
                        )
                        is not None
                    )

        class TestNeighbors:
            def test_increasing(self, next_line_fixture: line_topology.Line) -> None:
                line = next_line_fixture
                origin_seg = line.get_segment_from_segment_id_number_or_segment("SEG_010613")
                dest_seg = line.get_segment_from_segment_id_number_or_segment("SEG_010601")
                assert (
                    line.get_distance_in_cm_between_to_locations(
                        line_topology.ExactLocation(segment=origin_seg, abscissa=0),
                        line_topology.ExactLocation(segment=dest_seg, abscissa=0),
                        line_topology.SegmentDirection.INCREASING_OFFSET,
                    )
                    is not None
                )

        class TestComplexPaths:
            def test_increasing(self, next_line_fixture: line_topology.Line) -> None:
                line = next_line_fixture
                origin_seg = line.get_segment_from_segment_id_number_or_segment("SEG_011003")
                dest_seg = line.get_segment_from_segment_id_number_or_segment("SEG_010713")
                assert (
                    line.get_distance_in_cm_between_to_locations(
                        line_topology.ExactLocation(segment=origin_seg, abscissa=0),
                        line_topology.ExactLocation(segment=dest_seg, abscissa=0),
                        line_topology.SegmentDirection.INCREASING_OFFSET,
                    )
                    is not None
                )

        def test_segments_distances(self, next_line_fixture: line_topology.Line) -> None:
            line = next_line_fixture
            seg1 = line.get_segment_from_segment_id_number_or_segment("SEG_010812")
            seg1 = line.get_segment_from_segment_id_number_or_segment("SEG_010812")
            seg2 = line.get_segment_from_segment_id_number_or_segment("SEG_010702")
            seg3 = line.get_segment_from_segment_id_number_or_segment("SEG_010704")
