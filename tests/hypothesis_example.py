#!/usr/bin/env python3
"""
Read the docs...

https://hypothesis.readthedocs.io/en/latest/quickstart.html
"""

from typing import List
from hypothesis import given
from hypothesis.strategies import lists, text


def concat_with_space(lst: List[str]) -> str:
    """
    Returns a single string from concatenating a given list of strings.

    Example:
        >>> concatenate_strings_with_space(['a','b','c'])
        >>> 'a b c'
    """
    s = ""
    for x in lst:
        s += x + " "
    return s


@given(
    lists(
        text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
             min_size=0)))
def test_concat_with_space_has_identity_property_when_split_on_space(s):
    p = concat_with_space(s).split(" ")
    p.pop()  # because the last " " leaves an empty in list [... ,'']
    assert p == s
