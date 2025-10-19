import pytest
from typing import Optional

from parsedml import parse_dml
import param
import math


@pytest.fixture(scope="session", name="full_dml_content")
def full_dml_content_fixture() -> parse_dml.DmlFileContent:
    return parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path=param.DML_FILE_WITH_USELESS_RANGES)


class TestConstructionWorks:
    def test_no_error_at_construction(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        assert full_dml_content
        assert not full_dml_content.could_not_be_parsed_because_error_rows


class TestLineDeleted:
    def test_with_status_deleted(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        pass


class TestReferenceFaPa:

    @pytest.mark.parametrize(
        "full_raw_reference",
        ["FA622", "FA2016-1", "FA_2016-03-01_v2", "FA014 CoT-1", "FA-014-3-COT-2", parse_dml.ReferenceFaPa.NO_FA, parse_dml.ReferenceFaPa.REFUSE, math.nan, "pas de FA", " FA2160-1"],
    )
    def test_weird_names_are_accepted(self, full_raw_reference: str) -> None:
        parse_dml.ReferenceFaPa(full_raw_reference)

    def test_fa622_create_version_1(self) -> None:
        reference_created = parse_dml.ReferenceFaPa("FA622")
        assert reference_created
        assert reference_created.index == 1

    @pytest.mark.parametrize("full_raw_reference", [parse_dml.ReferenceFaPa.REFUSE, "refusé"])
    def test_refused_fa(self, full_raw_reference: str) -> None:
        reference_created = parse_dml.ReferenceFaPa(full_raw_reference)
        assert reference_created
        assert reference_created.is_refused()
        assert not reference_created.is_standard_fa()
        assert not reference_created.is_no_fa()

    @pytest.mark.parametrize("full_raw_reference,expected_result", [(parse_dml.ReferenceFaPa.NO_FA, True), ("pas de FA", True), ("FA014 CoT-1", False), (math.nan, False), ("Pas de  FA", True)])
    def test_is_no_fa(self, full_raw_reference: str, expected_result: bool) -> None:
        reference_fapa = parse_dml.ReferenceFaPa(full_raw_reference)
        assert reference_fapa
        assert reference_fapa.is_no_fa() == expected_result

    @pytest.mark.parametrize(
        "full_raw_reference,expected_result",
        [
            (parse_dml.ReferenceFaPa.NO_FA, None),
            ("pas de FA", None),
            ("FA014 CoT-1", 14),
            (math.nan, None),
            ("FA2016-1", 2016),
            ("FA_2016-03-01_v2", 20160301),
            ("FA014 CoT-1", 14),
            ("FA-014-3-COT-2", 14),
        ],
    )
    def test_number(self, full_raw_reference: str, expected_result: Optional[bool]) -> None:
        reference_fapa = parse_dml.ReferenceFaPa(full_raw_reference)
        assert reference_fapa
        assert reference_fapa.number == expected_result


class TestDocumentRenamedAndReferenceChanged:

    def test_sfe_ats(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        sfe_ats_v1 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-240000-02-0107-01", version=1)
        sfe_ats_v2 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-240000-02-0107-01", version=2)
        sfe_ats_v3 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-240000-02-0107-01", version=3)
        sfe_ats_v4 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="PGO-ATS+-240000-02-0107-01", version=4)

        assert sfe_ats_v1
        assert sfe_ats_v2
        assert sfe_ats_v3
        assert sfe_ats_v4
        assert sfe_ats_v1.dml_document
        assert sfe_ats_v1.dml_document == sfe_ats_v2.dml_document
        assert sfe_ats_v1.dml_document == sfe_ats_v3.dml_document
        assert sfe_ats_v1.dml_document == sfe_ats_v4.dml_document

        pass
