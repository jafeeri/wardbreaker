"""WARDBREAKER CLI.  Examples:
  python -m wardbreaker --selftest
  python -m wardbreaker --target llama-guard3:8b --model llama3.2:latest --report out.md
"""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .models import get_model
from .mutators import MUTATORS
from .report import render, write
from .runner import run
from .seeds import seeds_for
from .targets import HF_GUARDS, OLLAMA_GUARDS, get_target


def selftest() -> int:
    """Offline, mock-only. Proves the pipeline runs AND the killer feature both
    counts real bypasses and rejects fake ones — with no models pulled."""
    tgt, mdl = get_target("mock"), get_model("mock")
    unsafe, benign = seeds_for(tgt.kind)
    res = run(tgt, mdl, unsafe, benign, MUTATORS)
    fams = res["families"]

    assert res["n_flagged"] == res["n_unsafe"], "mock guard should flag all unsafe seeds"
    assert all(f.attempts == res["n_flagged"] for f in fams.values()), "attempts mismatch"
    assert any(f.real_bypasses > 0 for f in fams.values()), "expected >=1 real bypass"
    # killer feature must actually filter: some family flips the guard but 0 survive
    assert any(f.guard_flips > 0 and f.real_bypasses == 0 for f in fams.values()), \
        "expected >=1 fake bypass (guard flipped, model garbled) to prove the filter"
    # render must not crash and must contain the headline sections
    md = render(res)
    for needle in ("Bypass rate per attack family", "over-blocking", "two-sided finding"):
        assert needle in md, f"report missing section: {needle}"

    real = sum(f.real_bypasses for f in fams.values())
    flips = sum(f.guard_flips for f in fams.values())
    print(f"selftest OK  |  guard-flips {flips}, real bypasses {real}, "
          f"fake filtered {flips - real}, FPR {res['fpr']:.0%}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="wardbreaker",
                                description="Fuzz open-weight guardrails; report bypass rate per family + FPR.")
    p.add_argument("--target", default="mock",
                   help="guard to attack (default: mock). Known: mock, "
                        + ", ".join(sorted(OLLAMA_GUARDS | set(HF_GUARDS))))
    p.add_argument("--model", default="mock",
                   help="downstream model for the killer-feature check (default: mock)")
    p.add_argument("--report", metavar="PATH", help="write Markdown findings to PATH")
    p.add_argument("--rate", type=float, default=0.0,
                   help="per-call throttle in seconds for the guard")
    p.add_argument("--quiet", action="store_true", help="suppress progress")
    p.add_argument("--selftest", action="store_true", help="run offline mock self-check and exit")
    p.add_argument("--version", action="version", version=f"wardbreaker {__version__}")
    a = p.parse_args(argv)

    if a.selftest:
        return selftest()

    try:
        target = get_target(a.target, rate_s=a.rate)
    except ValueError as e:
        p.error(str(e))
    model = get_model(a.model)
    progress = None if a.quiet else (lambda m: print(m, file=sys.stderr))

    unsafe, benign = seeds_for(target.kind)
    result = run(target, model, unsafe, benign, MUTATORS, progress=progress)
    md = render(result)
    if a.report:
        write(result, a.report)
        print(f"\nwrote {a.report}", file=sys.stderr)
    print(md)
    return 0
