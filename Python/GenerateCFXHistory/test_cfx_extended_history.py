import pytest

import cfx_extended_history


class TestParseExtendedHistory:

    def test_simple_case1(self):
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
        assert cfx_extended_history.parse_history(extended_history_raw_text)

    def test_simple_case2(self):
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
        parsed_history_parsed = cfx_extended_history.parse_history(extended_history_raw_text)
        assert len(parsed_history_parsed) == 1
        cfx_history_element = parsed_history_parsed[0]
        assert cfx_history_element.action == "Close"
        assert cfx_history_element.state == "Closed"

        assert len(cfx_history_element.fields) == 1
        first_field = cfx_history_element.fields[0]
        assert first_field.field_id == "State"
        assert first_field.old_state == "Validated"
        assert first_field.new_state == "Closed"
