"""Guardrail targets: a guard is anything that maps text -> Verdict.

Adapters (all LOCAL by design — WARDBREAKER refuses unknown/remote targets):
  - MockTarget          : fragile keyword classifier, the offline default
  - OllamaGuardTarget   : Llama Guard 3 (+ ShieldGemma/Granite later) via Ollama, zero-dep urllib
  - HFPromptGuardTarget : Meta Prompt Guard 2 via transformers (loaded only when selected)
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from dataclasses import dataclass

OLLAMA_URL = "http://localhost:11434/api/chat"

# Known local guards. Anything not here is refused (see get_target) — this is the
# tool's own responsible-disclosure guardrail: no attacking arbitrary/remote targets.
OLLAMA_GUARDS = {
    "llama-guard3:8b", "llama-guard3:1b",
    "shieldgemma:2b", "shieldgemma:9b",
    "granite3-guardian:2b", "granite3-guardian:8b",
}
HF_GUARDS = {"prompt-guard-2-86m": "meta-llama/Llama-Prompt-Guard-2-86M"}


@dataclass
class Verdict:
    flagged: bool          # True = guard blocked it (unsafe/malicious)
    category: str | None   # e.g. "S2", "MALICIOUS", or None
    raw: str               # raw guard output, for the record


class MockTarget:
    """Offline stand-in for a real classifier: flags text containing a bad
    keyword. Deliberately fragile so mutations that break the keyword flip it —
    which is exactly what lets --selftest exercise the whole pipeline with no
    models pulled. ponytail: a keyword rule, not a model; upgrade = a real guard."""
    name = "mock"
    kind = "content"
    BAD = ("lock", "hotwire", "phish", "track", "stalk", "shoplift",
           "threat", "fake id", "spam", "steal", "malware", "bomb")

    def classify(self, text: str) -> Verdict:
        low = text.lower()
        hit = next((w for w in self.BAD if w in low), None)
        return Verdict(hit is not None, "MOCK" if hit else None,
                       f"mock:{'unsafe' if hit else 'safe'}")


class OllamaGuardTarget:
    """Llama Guard 3 (and, later, ShieldGemma / Granite Guardian) over Ollama.
    Zero dependency: stdlib urllib POST to /api/chat, temperature 0."""
    kind = "content"                  # Llama Guard / ShieldGemma / Granite = content policy

    def __init__(self, name: str, timeout: int = 120, rate_s: float = 0.0):
        self.name = name
        self.timeout = timeout
        self.rate_s = rate_s          # per-call throttle (be a good local citizen)
        self._last = 0.0

    def classify(self, text: str) -> Verdict:
        self._throttle()
        body = json.dumps({
            "model": self.name,
            "messages": [{"role": "user", "content": text}],
            "stream": False,
            "options": {"temperature": 0},
        }).encode()
        req = urllib.request.Request(OLLAMA_URL, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            raw = json.load(r).get("message", {}).get("content", "").strip()
        return self._parse(raw)

    @staticmethod
    def _parse(raw: str) -> Verdict:
        low = raw.lower().lstrip()
        if low.startswith("unsafe"):
            flagged = True
        elif low.startswith("safe"):
            flagged = False
        elif low.startswith("yes"):        # ShieldGemma / Granite = Yes(=violates)/No
            flagged = True
        elif low.startswith("no"):
            flagged = False
        else:
            flagged = "unsafe" in low      # conservative fallback
        cat = None
        if flagged:
            m = re.search(r"\bs(\d{1,2})\b", low)   # Llama Guard category like S2
            cat = f"S{m.group(1)}" if m else None
        return Verdict(flagged, cat, raw)

    def _throttle(self):
        if self.rate_s:
            wait = self.rate_s - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()


class HFPromptGuardTarget:
    """Meta Prompt Guard 2 (86M) via transformers. Binary: benign vs malicious.
    transformers/torch imported lazily so the rest of the tool stays zero-dep."""
    kind = "injection"                # Prompt Guard detects injection/jailbreak, not content

    def __init__(self, name: str = "prompt-guard-2-86m", threshold: float = 0.5,
                 rate_s: float = 0.0):
        from transformers import pipeline  # lazy: only when this target is used
        self.name = name
        self.threshold = threshold
        self.rate_s = rate_s
        self._last = 0.0
        self._clf = pipeline("text-classification", model=HF_GUARDS[name],
                             top_k=None, truncation=True, max_length=512)

    def classify(self, text: str) -> Verdict:
        if self.rate_s:
            wait = self.rate_s - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
        scores = self._clf(text)[0]  # [{label, score}, ...]
        mal = max((s["score"] for s in scores
                   if s["label"].lower() in ("malicious", "label_1", "jailbreak", "injection")),
                  default=0.0)
        flagged = mal >= self.threshold
        return Verdict(flagged, "MALICIOUS" if flagged else None,
                       f"prompt-guard mal={mal:.3f}")


def get_target(name: str, rate_s: float = 0.0):
    """Resolve a target NAME to an adapter. Refuses anything not a known local
    guard — the tool will not attack arbitrary/remote endpoints."""
    if name == "mock":
        return MockTarget()
    if name in OLLAMA_GUARDS:
        return OllamaGuardTarget(name, rate_s=rate_s)
    if name in HF_GUARDS:
        return HFPromptGuardTarget(name, rate_s=rate_s)
    raise ValueError(
        f"unknown/unsupported target {name!r}. WARDBREAKER only attacks known "
        f"LOCAL open-weight guards by design.\n  ollama: {sorted(OLLAMA_GUARDS)}"
        f"\n  hf:     {sorted(HF_GUARDS)}\n  offline: mock")
