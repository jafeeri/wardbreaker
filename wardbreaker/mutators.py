"""Attack families = surface-form mutators. Each maps text -> one mutated variant.
Pure, stdlib, deterministic, so the report can attribute a flip to a named family.

Two mechanisms at play (see Explanation.md):
  - readability-preserving (letter-space, zero-width, homoglyph, bidi, ...): a
    capable model still reads the payload -> can be a REAL bypass.
  - encoding (base64, rot13, ...): flips the guard but a small model can't recover
    the payload -> usually a FAKE bypass, filtered by the killer-feature check.
"""
from __future__ import annotations

import base64
import codecs

_LEET = str.maketrans({"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"})
_HOMO = {"a": "а", "c": "с", "e": "е", "i": "і",
         "o": "о", "p": "р", "x": "х", "y": "у"}  # Cyrillic look-alikes


def letter_space(s: str) -> str:
    """Strip punctuation, then space out every character (the Cisco Prompt-Guard trick)."""
    keep = "".join(c for c in s if c.isalnum() or c.isspace())
    return " ".join(keep.replace(" ", ""))


def zero_width(s: str) -> str:
    """Insert a zero-width space between every character."""
    return "​".join(s)


def variation_selector(s: str) -> str:
    """Interleave an invisible variation selector after each letter."""
    return "".join(c + "︎" if c.isalpha() else c for c in s)


def homoglyph(s: str) -> str:
    """Swap Latin letters for Cyrillic look-alikes."""
    return "".join(_HOMO.get(c.lower(), c) for c in s)


def diacritic(s: str) -> str:
    """Stack a combining accent on every letter."""
    return "".join(c + "́" if c.isalpha() else c for c in s)


def bidi_override(s: str) -> str:
    """Wrap in a right-to-left override (fools display/humans, not raw matching)."""
    return "‮" + s + "‬"


def full_width(s: str) -> str:
    """Map ASCII to full-width Unicode forms."""
    out = []
    for c in s:
        o = ord(c)
        if 0x21 <= o <= 0x7e:
            out.append(chr(o + 0xfee0))
        elif c == " ":
            out.append("　")
        else:
            out.append(c)
    return "".join(out)


def b64(s: str) -> str:
    """Base64-encode the payload (no decode cue — that's what the guard passes)."""
    return base64.b64encode(s.encode()).decode()


def leetspeak(s: str) -> str:
    return s.translate(_LEET)


def rot13(s: str) -> str:
    return codecs.encode(s, "rot13")


def payload_split(s: str) -> str:
    """Break into concatenated quoted chunks."""
    n = max(1, len(s) // 4)
    parts = [s[i:i + n] for i in range(0, len(s), n)]
    return " + ".join(f"'{p}'" for p in parts)


# registry drives the run + the per-family report
MUTATORS = {
    "letter-space": letter_space,
    "zero-width": zero_width,
    "variation-selector": variation_selector,
    "homoglyph": homoglyph,
    "diacritic": diacritic,
    "bidi-override": bidi_override,
    "full-width": full_width,
    "base64": b64,
    "leetspeak": leetspeak,
    "rot13": rot13,
    "payload-split": payload_split,
}
