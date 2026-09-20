"""Render a run result as a Markdown report: per-family bypass table (with the
'still works on model' column), the false-positive / over-blocking rate, and loud
reproducibility caveats."""
from __future__ import annotations

import datetime


def render(result: dict) -> str:
    fams = result["families"]
    order = sorted(fams.values(), key=lambda f: (f.bypass_rate, f.flip_rate), reverse=True)
    today = datetime.date.today().isoformat()

    L = []
    L.append(f"# WARDBREAKER findings — `{result['target']}`")
    L.append("")
    L.append(f"_Measured locally on {today}. Guard: `{result['target']}` "
             f"({result.get('kind', 'content')}-policy). "
             f"Downstream model (killer-feature oracle): `{result['model']}`. "
             f"Run it yourself — numbers are a measurement, not a constant._")
    L.append("")
    L.append(f"- Unsafe seeds flagged at baseline: **{result['n_flagged']}/{result['n_unsafe']}**")
    L.append(f"- Benign seeds: **{result['n_benign']}**")
    L.append("")

    L.append("## Bypass rate per attack family")
    L.append("")
    L.append("| family | attempts | guard flipped | **real bypass** (survived model) | bypass rate |")
    L.append("|---|---:|---:|---:|---:|")
    for f in order:
        L.append(f"| {f.family} | {f.attempts} | {f.guard_flips} "
                 f"| **{f.real_bypasses}** | {f.bypass_rate:.0%} |")
    L.append("")
    L.append("> `guard flipped` = guard stopped flagging the mutated prompt. "
             "`real bypass` = of those, the ones a downstream model still acted on. "
             "The gap between the two columns is fake bypasses the killer-feature "
             "check filtered out.")
    L.append("")

    L.append("## False-positive / over-blocking rate")
    L.append("")
    L.append(f"On {result['n_benign']} clearly-benign prompts, the guard wrongly "
             f"flagged **{len(result['fp_examples'])}** "
             f"(**FPR {result['fpr']:.0%}**).")
    if result["fp_examples"]:
        L.append("")
        L.append("Over-blocked benign prompts:")
        for s in result["fp_examples"]:
            L.append(f"- {s}")
    L.append("")

    total_attempts = sum(f.attempts for f in fams.values())
    total_flips = sum(f.guard_flips for f in fams.values())
    total_real = sum(f.real_bypasses for f in fams.values())
    n_fp = len(result["fp_examples"])
    L.append("## The two-sided finding")
    L.append("")
    L.append(f"- **Blinding (under-detection):** {total_real} real bypasses out of "
             f"{total_attempts} attempts across all families "
             f"({total_flips} flipped the guard, but only {total_real} survived the "
             f"model — the killer-feature check filtered the other "
             f"{total_flips - total_real} as fake).")
    if result["fpr"] > 0:
        L.append(f"- **Weaponisation (over-blocking):** FPR {result['fpr']:.0%} — the "
                 f"guard wrongly denied {n_fp} of {result['n_benign']} benign prompts. "
                 f"It can be made to block legitimate users, not just miss harmful ones.")
    else:
        L.append("- **Over-blocking:** FPR 0% on this benign set — this guard did "
                 "**not** over-block here. (Over-blocking is a documented failure mode "
                 "for guards under adversarial-benign input; simply not reproduced on "
                 "this set — the honest result.)")
    L.append("")
    L.append("_Benign-proxy seeds only; no turnkey dangerous payloads. This is "
             "defensive guardrail-robustness research — the takeaway is what guard "
             "builders should fix._")
    return "\n".join(L)


def write(result: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:   # utf-8: report may hold unicode
        f.write(render(result))
