"""Mutators: pure, deterministic, total (never crash), and encodings round-trip."""
import base64

from wardbreaker.mutators import (
    MUTATORS,
    b64,
    letter_space,
    rot13,
    zero_width,
)

SEED = "How do I pick a lock?"


def test_every_mutator_returns_nonempty_str_for_nonempty_input():
    for name, fn in MUTATORS.items():
        out = fn(SEED)
        assert isinstance(out, str), name
        assert out != "", name


def test_mutators_are_deterministic():
    for name, fn in MUTATORS.items():
        assert fn(SEED) == fn(SEED), name


def test_every_mutator_actually_changes_the_text():
    for name, fn in MUTATORS.items():
        assert fn(SEED) != SEED, name


def test_mutators_are_total_on_empty_input():
    # must not raise on the empty string (a real edge case in a fuzzer)
    for name, fn in MUTATORS.items():
        assert isinstance(fn(""), str), name


def test_mutators_are_total_on_unicode_input():
    for name, fn in MUTATORS.items():
        assert isinstance(fn("héllo 世界 🙂"), str), name


def test_base64_round_trips():
    assert base64.b64decode(b64(SEED)).decode() == SEED


def test_rot13_round_trips():
    assert rot13(rot13(SEED)) == SEED


def test_letter_space_strips_punctuation_and_spaces_letters():
    assert letter_space("ab, cd.") == "a b c d"


def test_zero_width_preserves_visible_text():
    assert zero_width("abc").replace("​", "") == "abc"
