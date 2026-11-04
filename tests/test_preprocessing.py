import pytest

from src.data.preprocessing import clean_text


@pytest.mark.parametrize("raw, expected", [
    ("Check https://example.com now", "check now"),
    ("www.example.com great", "great"),
    ("@bob hello #fun", "hello"),
    ("WOW!!! 100% Great...", "wow great"),
    ("don't", "dont"),
    ("I&#39;m here<br>today", "im here today"),
    ("best part 1:23 here", "best part here"),
    ("I love it 🔥", "i love it great"),
    ("", ""),
    ("🦄🦄", ""),
    ("!!!", ""),
])
def test_clean_text(raw, expected):
    assert clean_text(raw) == expected


@pytest.mark.parametrize("value", [None, 12, 1.5])
def test_clean_text_non_string(value):
    assert clean_text(value) == ""
