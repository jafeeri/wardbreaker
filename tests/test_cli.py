"""CLI: the offline self-check passes, and bad/absent args behave."""
import pytest

from wardbreaker.cli import main, selftest


def test_selftest_returns_zero():
    assert selftest() == 0


def test_version_flag_exits_clean():
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0


def test_unknown_target_is_rejected():
    with pytest.raises(SystemExit):
        main(["--target", "definitely-not-a-guard"])
