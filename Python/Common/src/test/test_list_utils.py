# -*-coding:Utf-8 -*

import pytest

from src.common import list_utils


class TestListEquals():

    def test_list_with_order(self) -> None:
        assert list_utils.are_list_equals([0],[0])
        assert list_utils.are_list_equals([0,1],[0,1])
        assert list_utils.are_list_equals([0,1],[1,0])

class TestAreAllElementsOfListIncludedInList():


    def test_list_with_order(self) -> None:
        assert list_utils.are_all_elements_of_list_included_in_list([0],[0])
        assert list_utils.are_all_elements_of_list_included_in_list([1, 2],[1, 2, 3, 1, 1, 2, 2])
        assert list_utils.are_all_elements_of_list_included_in_list(['x', 'y', 'z'],['x', 'a', 'y', 'x', 'b', 'z'])
        assert list_utils.are_all_elements_of_list_included_in_list([0,1],[0,1])
        assert list_utils.are_all_elements_of_list_included_in_list([0,1,1],[0,1,1,2])
        assert not list_utils.are_all_elements_of_list_included_in_list([0,1,2],[0,1,3])

