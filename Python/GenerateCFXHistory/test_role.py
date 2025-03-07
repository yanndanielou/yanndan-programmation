import pytest

import role


class TestRoleConversion:
    def test_random(self) -> None:
        assert role.get_raw_subystem_of_ressource("Zehoub Khaled") == "ATS"
