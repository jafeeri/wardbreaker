"""Report: sections render, and the over-blocking line is honest about the real FPR."""
from wardbreaker.report import render
from wardbreaker.runner import FamilyResult


def _result(fpr, fp_examples):
    return {
        "target": "mock",
        "kind": "content",
        "model": "mock",
        "n_unsafe": 10,
        "n_flagged": 10,
        "n_benign": 10,
        "fpr": fpr,
        "fp_examples": fp_examples,
        "families": {
            "letter-space": FamilyResult("letter-space", attempts=10, guard_flips=4, real_bypasses=2),
        },
    }


def test_render_has_headline_sections():
    md = render(_result(0.1, ["benign example"]))
    assert "Bypass rate per attack family" in md
    assert "two-sided finding" in md


def test_render_is_honest_when_fpr_is_zero():
    md = render(_result(0.0, []))
    assert "did **not** over-block" in md


def test_render_reports_weaponisation_when_fpr_positive():
    md = render(_result(0.3, ["a", "b", "c"]))
    assert "Weaponisation" in md
    assert "30%" in md
