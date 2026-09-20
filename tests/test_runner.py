"""Runner: invariants (real <= flips <= attempts), the killer-feature filter fires,
and the no-flagged-seed edge case doesn't crash."""
from wardbreaker.models import MockModel
from wardbreaker.mutators import MUTATORS
from wardbreaker.runner import run
from wardbreaker.seeds import seeds_for
from wardbreaker.targets import MockTarget, Verdict


def test_run_invariants_and_killer_feature_filter():
    unsafe, benign = seeds_for("content")
    res = run(MockTarget(), MockModel(), unsafe, benign, MUTATORS)

    assert res["n_flagged"] == len(unsafe)  # mock flags every content seed
    for fr in res["families"].values():
        assert fr.attempts == res["n_flagged"]
        assert fr.real_bypasses <= fr.guard_flips <= fr.attempts
    # at least one real bypass, and at least one family where the filter removed a fake
    assert any(fr.real_bypasses > 0 for fr in res["families"].values())
    assert any(fr.guard_flips > fr.real_bypasses for fr in res["families"].values())


def test_run_handles_a_guard_that_flags_nothing():
    class NeverFlags:
        name = "never"
        kind = "content"

        def classify(self, text):
            return Verdict(False, None, "safe")

    res = run(NeverFlags(), MockModel(), ["anything"], ["benign"], MUTATORS)
    assert res["n_flagged"] == 0
    assert res["fpr"] == 0.0
    assert all(fr.attempts == 0 for fr in res["families"].values())
    assert all(fr.bypass_rate == 0.0 for fr in res["families"].values())
