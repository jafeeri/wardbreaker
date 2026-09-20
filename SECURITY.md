# Security Policy

WARDBREAKER is defensive security research: it measures the robustness of
open-weight guardrail classifiers you run locally, so guardrail builders can see
and close the gaps.

## Scope and intended use

- **Local, open-weight targets only.** Do not point WARDBREAKER at a third-party or
  hosted API you are not authorised to test. The tool refuses unknown/remote targets
  by design.
- **Benign-proxy seeds only.** The bundled seeds are everyday-crime proxies and bare
  injection patterns. Do not add turnkey dangerous payloads (CBRN, mass-harm,
  CSAM-adjacent). Demonstrate the mechanism, not a weapon.

## Reporting a guardrail weakness you found with this tool

If you discover a genuinely novel guardrail weakness (not a reproduction of
published work), please practise **coordinated disclosure**: contact the guardrail
vendor's security team and agree an embargo before any public write-up. Lead with
the defensive takeaway.

## Reporting a bug in WARDBREAKER itself

Open a GitHub issue for ordinary bugs. For anything you consider sensitive, contact
the maintainer through the GitHub profile linked on the repository rather than a
public issue.

## What this tool is not

It is not a turnkey attack CLI. It refuses unknown/remote targets, ships no working
exploits for dangerous categories, and frames every finding as what defenders should
fix. Guardrails are one layer of defence in depth — never the whole wall.
