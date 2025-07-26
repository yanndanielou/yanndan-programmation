import pytest

from generatecfxhistory import cfx_extended_history

from typing import List


class TestDecodeTime:

    def tests_weird_dates_found_in_cfx(self) -> None:
        assert cfx_extended_history.decode_time("2023-10-01 00:05:13 -718:00") is not None


class TestAllCFXCompleteHistoryExport:

    def test_very_slow_to_process_CFX00543992(self) -> None:
        all_cfx_complete_extended_histories_text_file_path = "Input/extended_history_nextats.txt"
        all_cfx_complete_history: List[cfx_extended_history.CFXEntryCompleteHistory] = cfx_extended_history.AllCFXCompleteHistoryExport.parse_full_complete_extended_histories_text_file(
            all_cfx_complete_extended_histories_text_file_path=all_cfx_complete_extended_histories_text_file_path, cfx_to_treat_whitelist_ids=["CFX00543992"]
        )
        assert len(all_cfx_complete_history) == 1
        complete_history__CFX00543992 = all_cfx_complete_history[0]
        assert complete_history__CFX00543992


class TestParseExtendedHistory:

    def test_simple_case1(self) -> None:
        extended_history_raw_text = """====START====
Time           :    2021-04-14 11:13:19 +02:00
Schema Rev     :    105
User Name      :    SERDJANIAN, GREGOR
User Login     :    z004686c
User Groups    :    Siemens    FR_NEXTEO    Everyone
Action         :    Close
State          :    Closed
==Fields==
State            (9:6)
    Old :    Validated
    New :    Closed

====END===="""
        assert cfx_extended_history.parse_history(cfx_id="CFX00123", extended_history_text=extended_history_raw_text)

    def test_simple_case2(self) -> None:
        extended_history_raw_text = """====START====
Time           :    2021-04-14 11:13:19 +02:00
Schema Rev     :    105
User Name      :    SERDJANIAN, GREGOR
User Login     :    z004686c
User Groups    :    Siemens    FR_NEXTEO    Everyone
Action         :    Close
State          :    Closed
==Fields==
State            (9:6)
    Old :    Validated
    New :    Closed

====END===="""

        cfx_complete_history = cfx_extended_history.parse_history(cfx_id="CFX00123", extended_history_text=extended_history_raw_text)

        parsed_history_parsed = cfx_complete_history.history_elements
        assert len(parsed_history_parsed) == 1
        cfx_history_element = parsed_history_parsed[0]
        assert cfx_history_element.action == "Close"
        assert cfx_history_element.state == "Closed"

        assert len(cfx_history_element.fields) == 1
        first_field = cfx_history_element.fields[0]
        assert first_field.field_id == "State"
        assert first_field.old_state == "Validated"
        assert first_field.new_state == "Closed"
