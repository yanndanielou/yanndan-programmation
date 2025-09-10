# -*-coding:Utf-8 -*
"""test custom"""
import pytest

from src.common.excel_utils import xl_column_name_to_index
from xlsxwriter.utility import xl_col_to_name


class TestExcelColumnNameToIndex:
    """SimpleIntCustomIncrementDecrementTest"""

    @pytest.mark.parametrize(
        "column_name, expected_column_index",
        [
            ("A", 0),
            ("B", 1),
            ("AA", 26),
        ],
    )
    def test_existing(self, column_name: str, expected_column_index: int) -> None:
        assert xl_column_name_to_index(column_name) == expected_column_index

    @pytest.mark.parametrize(
        "column_name",
        [
            ("A"),
            ("B"),
            ("AA"),
            ("ZZ"),
        ],
    )
    def test_convert_back_and_forth(self, column_name: str) -> None:
        assert xl_col_to_name(xl_column_name_to_index(column_name)) == column_name
