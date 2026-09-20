"""Orchestration: baseline -> per-family (mutate -> flip-check -> killer-check) -> FPR."""
from __future__ import annotations

from dataclasses import dataclass, field

from .models import survived
from .mutators import MUTATORS


@dataclass
class FamilyResult:
    family: str
    attempts: int = 0        # flagged seeds we tried this family on
    guard_flips: int = 0     # variants the guard stopped flagging
    real_bypasses: int = 0   # of those, the ones the model still acted on
    examples: list = field(default_factory=list)   # (seed, note) for real bypasses

    @property
    def flip_rate(self) -> float:
        return self.guard_flips / self.attempts if self.attempts else 0.0

    @property
    def bypass_rate(self) -> float:
        return self.real_bypasses / self.attempts if self.attempts else 0.0


def run(target, model, unsafe_seeds, benign_seeds, mutators=None,
        progress=None) -> dict:
    mutators = mutators or MUTATORS
    say = progress or (lambda *_: None)

    # ---- phase 1: GUARD ONLY (so Ollama doesn't thrash-reload two big models) ----
    # baseline: which unsafe seeds does this guard actually flag?
    say(f"[guard] baseline on {len(unsafe_seeds)} unsafe seeds")
    flagged = [s for s in unsafe_seeds if target.classify(s).flagged]

    # false-positive / over-blocking rate on benign seeds
    say(f"[guard] FPR on {len(benign_seeds)} benign seeds")
    fp = [s for s in benign_seeds if target.classify(s).flagged]
    fpr = len(fp) / len(benign_seeds) if benign_seeds else 0.0

    # mutate every flagged seed per family; record which flip the guard
    families = {fam: FamilyResult(fam) for fam in mutators}
    flips = []                                  # (family, seed, variant)
    for fam, fn in mutators.items():
        fr = families[fam]
        for seed in flagged:
            fr.attempts += 1
            variant = fn(seed)
            if not target.classify(variant).flagged:
                fr.guard_flips += 1
                flips.append((fam, seed, variant))
        say(f"[guard] {fam:18} flips {fr.guard_flips}/{fr.attempts}")

    # ---- phase 2: MODEL ONLY (killer feature) — verify flips survive on the model ----
    if flips:
        say(f"[model] warming {model.name} (one-time cold load)")
        model.warm()
    say(f"[model] killer-check on {len(flips)} flipped variants")
    for fam, seed, variant in flips:
        if survived(seed, model.reply(variant)):
            fr = families[fam]
            fr.real_bypasses += 1
            fr.examples.append(seed)

    return {
        "target": target.name,
        "kind": getattr(target, "kind", "content"),
        "model": model.name,
        "n_unsafe": len(unsafe_seeds),
        "n_flagged": len(flagged),
        "n_benign": len(benign_seeds),
        "fpr": fpr,
        "fp_examples": fp,
        "families": families,
    }
