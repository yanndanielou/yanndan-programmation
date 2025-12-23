import math
from typing import List, Optional, Set, Tuple

import pytest

import param
from parsedml import parse_dml


@pytest.fixture(scope="session", name="full_dml_content")
def full_dml_content_fixture() -> parse_dml.DmlFileContent:
    return parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path=param.DML_FILE_WITH_USELESS_RANGES)


@pytest.fixture(scope="session", name="full_dml_content_all_documents")
def full_dml_content_all_documents_fixture(full_dml_content: parse_dml.DmlFileContent) -> List[parse_dml.DmlDocument]:
    return full_dml_content.dml_documents


def disabled_pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """
    Parametrize tests that need a single dml_document at collection time.
    We build the same data as the fixture full_dml_content_all_documents to avoid
    calling fixtures at collection time.
    """
    if "each_dml_document" in metafunc.fixturenames:
        docs = parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path=param.DML_FILE_WITH_USELESS_RANGES).dml_documents
        metafunc.parametrize("each_dml_document", docs)


class TestConstructionWorks:
    def test_no_error_at_construction(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        assert full_dml_content
        assert not full_dml_content.could_not_be_parsed_because_error_rows

    def test_there_are_more_lines_than_documents(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        assert len(full_dml_content.dml_lines) > len(full_dml_content.dml_documents)

    def test_documents_that_share_fa_by_mistake_are_correctly_seen_as_distinct_fa_872(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        line_a = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-021B00-10-0903-01", version=1)
        line_b = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-S-351100-07-0607-00", version=3)
        assert line_a
        assert line_b
        assert line_a is not line_b
        assert line_a.all_unique_fa_names == line_b.all_unique_fa_names
        assert line_a.all_unique_fa_numbers == line_b.all_unique_fa_numbers
        assert line_a.dml_document is not line_b.dml_document

    def test_all_documents_have_only_one_line_per_version_stop_at_first_error(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        for dml_document in full_dml_content.dml_documents:
            all_versions_list = [(dml_line.version, dml_line.revision) for dml_line in dml_document.dml_lines]
            all_versions_set = {(dml_line.version, dml_line.revision) for dml_line in dml_document.dml_lines}
            assert len(all_versions_list) == len(all_versions_set), dml_document

    def test_all_documents_have_only_one_line_per_version_show_all_errors(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        documents_in_errors_with_versions_list_and_sets: List[Tuple[parse_dml.DmlDocument, List[Tuple[int, int]], Set[Tuple[int, int]]]] = []
        for dml_document in full_dml_content.dml_documents:
            all_versions_list = [(dml_line.version, dml_line.revision) for dml_line in dml_document.dml_lines]
            all_versions_list = [(dml_line.version, dml_line.revision) for dml_line in dml_document.dml_lines]
            all_versions_set = {(dml_line.version, dml_line.revision) for dml_line in dml_document.dml_lines}
            if len(all_versions_list) != len(all_versions_set):
                documents_in_errors_with_versions_list_and_sets.append((dml_document, all_versions_list, all_versions_set))

        print(f"test_all_documents_have_only_one_line_per_version_show_all_errors: all errors: {'\n'.join([str(dml_doc) for dml_doc in documents_in_errors_with_versions_list_and_sets])}")
        assert not documents_in_errors_with_versions_list_and_sets

    def test_documents_that_share_fa_by_mistake_are_correctly_seen_as_distinct_fa_1921(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        line_a = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="PSO-ATS+-S-240000-04-0322-81", version=1)
        line_b = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="PSO-ATS+-S-240000-04-0322-79", version=2)
        line_c = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="PSO-ATS+-S-240000-04-0322-78", version=1)
        assert line_a
        assert line_b
        assert line_c
        assert line_a is not line_b
        assert line_a is not line_c
        assert line_a.all_unique_fa_names == line_b.all_unique_fa_names
        assert line_a.all_unique_fa_names == line_c.all_unique_fa_names
        assert line_a.all_unique_fa_numbers == line_b.all_unique_fa_numbers
        assert line_a.all_unique_fa_numbers == line_c.all_unique_fa_numbers
        assert line_a.dml_document is not line_b.dml_document
        assert line_a.dml_document is not line_c.dml_document

    def test_inside_document_lines_are_sorted(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        for dml_document in full_dml_content.dml_documents:

            # Ensure dml_lines are sorted by (version, revision).
            # DmlLines are appended to their DmlDocument in the order they are parsed
            # (normally sorted by version beforehand). Validate ordering to catch
            # unexpected insertion orders early.
            assert dml_document.dml_lines
            sorted_dml_lines = dml_document.get_sorted_dml_lines()
            assert sorted_dml_lines
            sorted_copy = sorted(dml_document.dml_lines, key=lambda l: (l.version, l.revision))
            if sorted_dml_lines != sorted_copy:
                assert False, "DmlDocument dml_lines must be sorted by (version, revision)"

            previous_iterated_dml_line = None
            for sorted_dml_line in sorted_dml_lines:
                if previous_iterated_dml_line:
                    assert previous_iterated_dml_line.version <= sorted_dml_line.version

                    if previous_iterated_dml_line.version == sorted_dml_line.version:
                        assert previous_iterated_dml_line.revision < sorted_dml_line.revision
                previous_iterated_dml_line = sorted_dml_line

            assert previous_iterated_dml_line


class TestDocumentsThatShareSameFa:
    @pytest.mark.parametrize(
        "all_references_and_versions_of_distinct_docs_sharing_same_fa",
        [
            [("PSO-ATS+-S-240000-04-0322-81", 1), ("PSO-ATS+-S-240000-04-0322-79", 2), ("PSO-ATS+-S-240000-04-0322-78", 1)],
            [("NExTEO-021B00-10-0903-01", 2), ("NExTEO-021B00-11-0903-01", 1), ("PGO-ATS+-S-231300-08-0701-01", 1), ("NExTEO-S-314215-07-0607-03", 1), ("NExTEO-S-351100-07-0607-00", 2)],
            [
                ("PSO-ATS+-S-240000-04-0311-28", 1),
                ("PSO-ATS+-S-240000-04-0311-29", 1),
                ("PSO-ATS+-S-240000-04-0311-30", 1),
                ("PSO-ATS+-S-240000-04-0322-77", 1),
                ("PSO-ATS+-S-240000-04-0322-78", 1),
                ("PSO-ATS+-S-240000-04-0322-79", 2),
                ("PSO-ATS+-S-240000-04-0322-81", 1),
            ],
        ],
    )
    def test_documents_that_share_fa_by_mistake_are_correctly_seen_as_distinct_param(
        self, all_references_and_versions_of_distinct_docs_sharing_same_fa: List[Tuple[str, int]], full_dml_content: parse_dml.DmlFileContent
    ) -> None:

        all_dml_lines = [
            full_dml_content.get_dml_line_by_code_ged_moe_and_version(references_and_version[0], references_and_version[1])
            for references_and_version in all_references_and_versions_of_distinct_docs_sharing_same_fa
        ]
        assert all_dml_lines
        assert len(all_dml_lines) > 1
        first_dml_line = all_dml_lines[0]
        assert first_dml_line
        all_dml_lines_except_first_one = all_dml_lines[1:]
        for dml_line in all_dml_lines_except_first_one:
            assert dml_line
            assert dml_line is not first_dml_line
            assert dml_line.dml_document is not first_dml_line.dml_document


class TestDocumentsThatHaveSeveralFANames:
    def test_documents_that_have_renamed_fa_by_mistake_are_correctly_seen_as_same_document(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        line_of_version_0 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-021100-01-0007-00", version=0)
        assert line_of_version_0
        assert line_of_version_0.dml_document

        for doc_version in range(1, 8):
            line_of_doc_version = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-021100-01-0007-00", version=doc_version)
            assert line_of_doc_version
            assert line_of_doc_version.dml_document
            assert line_of_doc_version is not line_of_version_0
            assert line_of_doc_version.dml_document is line_of_version_0.dml_document

    @pytest.mark.parametrize(
        "document_code_goe,expected_has_several_fa",
        [
            ("NExTEO-021100-01-0007-00", True),
            ("PGO-ATS+-021100-01-0007-03", True),
            ("NExTEO-021100-01-0008-00", True),
            ("NExTEO-200000-02-0111-00", True),
            ("NExTEO-200000-02-0104-00", True),
            ("PGO-ATS+-021100-06-0500-01", False),
        ],
    )
    def test_documents_has_several_fa_numbers(self, document_code_goe: str, expected_has_several_fa: bool, full_dml_content: parse_dml.DmlFileContent) -> None:
        document = full_dml_content.get_dml_document_by_code_ged_moe(document_code_goe)
        assert document
        assert document.has_several_fa_numbers() == expected_has_several_fa


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


class TestDocumentsThatHaveSameTitleButSameVersionAreSeenDistinct:
    @pytest.mark.parametrize("all_references_and_versions_of_distinct_docs_with_same_title", [[("PGO-ATS+-021900-03-0203-00", 1), ("NExTEO-021900-03-0203-00", 1)]])
    def test_on_real_dml(self, all_references_and_versions_of_distinct_docs_with_same_title: List[Tuple[str, int]], full_dml_content: parse_dml.DmlFileContent) -> None:

        all_dml_lines = [
            full_dml_content.get_dml_line_by_code_ged_moe_and_version(references_and_version[0], references_and_version[1])
            for references_and_version in all_references_and_versions_of_distinct_docs_with_same_title
        ]
        assert all_dml_lines
        assert len(all_dml_lines) > 1
        first_dml_line = all_dml_lines[0]
        assert first_dml_line
        all_dml_lines_except_first_one = all_dml_lines[1:]
        for dml_line in all_dml_lines_except_first_one:
            assert dml_line
            assert dml_line is not first_dml_line
            assert dml_line.dml_document is not first_dml_line.dml_document

    @pytest.mark.parametrize("all_references_and_versions_of_distinct_docs_with_same_title", [[("Prj2-240000-02-0107-01", 1), ("Prj1-240000-02-0107-01", 1)]])
    def test_on_sample_dml(self, all_references_and_versions_of_distinct_docs_with_same_title: List[Tuple[str, int]]) -> None:
        sample_dml_content = parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path="Input_for_tests/DML_Example_two_docs_same_title_different.xlsm")

        all_dml_lines = [
            sample_dml_content.get_dml_line_by_code_ged_moe_and_version(references_and_version[0], references_and_version[1])
            for references_and_version in all_references_and_versions_of_distinct_docs_with_same_title
        ]
        assert all_dml_lines
        assert len(all_dml_lines) > 1
        first_dml_line = all_dml_lines[0]
        assert first_dml_line
        all_dml_lines_except_first_one = all_dml_lines[1:]
        for dml_line in all_dml_lines_except_first_one:
            assert dml_line
            assert dml_line is not first_dml_line
            assert dml_line.dml_document is not first_dml_line.dml_document


class TestDocumentWithReferenceChangedButNotRenamed:
    @pytest.mark.parametrize(
        "doc_line_1_code_ged,doc_line_1_version,doc_line_2_code_ged,doc_line_2_version",
        [
            ("NExTEO-200000-04-0302-01", 1, "PGO-ATS+-200000-04-0302-01", 2),
            ("NExTEO-200000-02-0102-02", 1, "PGO-ATS+-200000-02-0102-04", 2),
        ],
    )
    def test_can_find_document_by_title(self, doc_line_1_code_ged: str, doc_line_1_version: int, doc_line_2_code_ged: str, doc_line_2_version: int, full_dml_content: parse_dml.DmlFileContent) -> None:
        line_1 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(doc_line_1_code_ged, doc_line_1_version)
        line_2 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(doc_line_2_code_ged, doc_line_2_version)
        assert line_1
        assert line_2
        assert line_1 is not line_2
        assert line_1.code_ged_moe != line_2.code_ged_moe
        assert line_1.title == line_2.title
        assert line_1.dml_document is line_2.dml_document


class TestLastSubmit:
    def ignore_test_all_lignes_have_last_submit_evaluated(self) -> None:
        pass


class TestDocumentRenamedAndReferenceChanged:

    def test_sfe_ats_on_full_dml(self, full_dml_content: parse_dml.DmlFileContent) -> None:
        sfe_ats_v1 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-240000-02-0107-01", version=1)
        sfe_ats_v2 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-240000-02-0107-01", version=2)
        sfe_ats_v3 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="NExTEO-240000-02-0107-01", version=3)
        sfe_ats_v4 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="PGO-ATS+-240000-02-0107-01", version=4)

        assert sfe_ats_v1
        assert sfe_ats_v2
        assert sfe_ats_v3
        assert sfe_ats_v4
        assert sfe_ats_v1.dml_document
        assert sfe_ats_v1.dml_document is sfe_ats_v2.dml_document
        assert sfe_ats_v1.dml_document is sfe_ats_v3.dml_document
        assert sfe_ats_v1.dml_document is sfe_ats_v4.dml_document

    def test_sfe_ats_on_sample_test_data(self) -> None:
        full_dml_content = parse_dml.DmlFileContent.Builder.build_with_excel_file(dml_excel_file_full_path="Input_for_tests/DML_Example_sf_ats.xlsm")

        sfe_ats_v1 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="Prj2-240000-02-0107-01", version=1)
        sfe_ats_v2 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="Prj2-240000-02-0107-01", version=2)
        sfe_ats_v3 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="Prj2-240000-02-0107-01", version=3)
        sfe_ats_v4 = full_dml_content.get_dml_line_by_code_ged_moe_and_version(code_ged_moe="Prj1-240000-02-0107-01", version=4)

        assert sfe_ats_v1
        assert sfe_ats_v2
        assert sfe_ats_v3
        assert sfe_ats_v4
        assert sfe_ats_v1.dml_document
        assert sfe_ats_v1.dml_document is sfe_ats_v2.dml_document
        assert sfe_ats_v1.dml_document is sfe_ats_v3.dml_document
        assert sfe_ats_v1.dml_document is sfe_ats_v4.dml_document


def test_documents_status_report_write_all_lines(full_dml_content: parse_dml.DmlFileContent) -> None:
    import os
    import pandas as pandas

    # Pick two distinct codes to produce a small report
    codes = [full_dml_content.dml_lines[0].code_ged_moe, full_dml_content.dml_lines[1].code_ged_moe]

    report = parse_dml.DocumentsStatusReport.Builder.build_by_code_ged_moe(name="/test_write_all_lines", dml_file_content=full_dml_content, codes_ged_moe=codes)

    report.write_all_lines_to_excel()

    assert os.path.exists(report.output_file_full_path)

    df = pandas.read_excel(report.output_file_full_path)

    expected_cols = [
        "dml_document",
        "line_number",
        "code_ged_moe",
        "title",
        "version",
        "revision",
        "version_and_revision",
        "status",
        "actual_livraison",
        "doc_deleted",
        "fa_reference",
        "fa_actual_delivery",
        "pa_reference",
        "pa_actual_delivery",
    ]

    for col in expected_cols:
        assert col in df.columns

    # Clean up generated file
    os.remove(report.output_file_full_path)

