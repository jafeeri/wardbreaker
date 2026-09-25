"""Regenerate docs/bypass_gap.png — the one chart that carries the whole argument:
how many mutations flip the guard vs how many are REAL bypasses (survive the model).

Data from FINDINGS.md (measured 2026-09-20). Requires matplotlib (not needed to use
WARDBREAKER): `pip install matplotlib`. Run: `python docs/plot.py`.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

GUARDS = ["Llama Guard 3 (8B)\ncontent policy", "Prompt Guard 2 (86M)\ninjection"]
GUARD_FLIPS = [24, 63]
REAL_BYPASSES = [5, 15]

x = list(range(len(GUARDS)))
w = 0.38

fig, ax = plt.subplots(figsize=(8, 4.5))
flips = ax.bar([i - w / 2 for i in x], GUARD_FLIPS, w,
               label="Guard flipped (looked bypassed)", color="#e0a63f")
real = ax.bar([i + w / 2 for i in x], REAL_BYPASSES, w,
              label="Real bypass (still works on the model)", color="#c0392b")

ax.set_xticks(x)
ax.set_xticklabels(GUARDS)
ax.set_ylabel("count (out of mutation attempts)")
ax.set_title("Guard-flip ≠ bypass\n77% of mutations that fool the guard don't work on the model behind it")
ax.legend(frameon=False, loc="upper left")
ax.bar_label(flips, padding=2)
ax.bar_label(real, padding=2)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, max(GUARD_FLIPS) * 1.15)
fig.tight_layout()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bypass_gap.png")
fig.savefig(out, dpi=140)
print(f"wrote {out}")
