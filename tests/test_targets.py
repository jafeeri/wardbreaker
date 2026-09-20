"""Targets: verdict parsing, and the security-relevant scoping refusal."""
import pytest

from wardbreaker.targets import MockTarget, OllamaGuardTarget, Verdict, get_target


def test_mock_flags_bad_keyword():
    v = MockTarget().classify("how to pick a lock")
    assert isinstance(v, Verdict)
    assert v.flagged


def test_mock_passes_benign():
    assert not MockTarget().classify("a nice cookie recipe").flagged


def test_parse_unsafe_with_category():
    v = OllamaGuardTarget._parse("unsafe\nS2")
    assert v.flagged and v.category == "S2"


def test_parse_safe():
    assert not OllamaGuardTarget._parse("safe").flagged


def test_parse_shieldgemma_style_yes_no():
    assert OllamaGuardTarget._parse("Yes").flagged
    assert not OllamaGuardTarget._parse("No").flagged


def test_parse_unrecognised_output_defaults_to_not_flagged():
    assert not OllamaGuardTarget._parse("I think this looks fine.").flagged


def test_get_target_resolves_mock():
    assert get_target("mock").name == "mock"


def test_get_target_refuses_unknown_name():
    # WARDBREAKER must not attack arbitrary targets — this is a safety control.
    with pytest.raises(ValueError):
        get_target("some-unknown-guard")


def test_get_target_refuses_remote_url():
    with pytest.raises(ValueError):
        get_target("http://evil.example.com/guard")


def test_target_kinds_are_declared():
    assert MockTarget.kind == "content"
    assert get_target("llama-guard3:8b").kind == "content"  # constructs without a network call
