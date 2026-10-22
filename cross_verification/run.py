#!/usr/bin/env python3
"""Eight mint requests for CHFAU, each against a reserve report checked by
independent parties. Writes results/cross-verification*.json* (deterministic)."""

import json
from pathlib import Path

from cross_verification import MintGate, ReserveReport, World, chain_check, custodian_check, verdict

AS_OF = "2026-10-22T08:00:00Z"
NOW = "2026-10-22T08:10:00Z"
TRUTH = World(held_by_custodian={"custodian-bank": 6_200_000.00}, supply_on_chain=10_000_000.00)


def report(rid, supply=10_000_000.00, bank=6_200_000.00, other=4_300_000.00, as_of=AS_OF):
    return ReserveReport(rid, "CHFAU", as_of, supply, {"custodian-bank": bank}, other)


def scenarios():
    r = report("r-01")
    yield "Report confirmed by custodian bank and chain observer", r, 250_000, custodian_check(r, TRUTH) + chain_check(r, TRUTH)
    r = report("r-02", bank=6_900_000.00)
    yield "Issuer overstates the balance at the bank", r, 250_000, custodian_check(r, TRUTH) + chain_check(r, TRUTH)
    r = report("r-03", supply=9_400_000.00)
    yield "Issuer understates the supply on chain", r, 250_000, custodian_check(r, TRUTH) + chain_check(r, TRUTH)
    r = report("r-04")
    yield "Only the issuer confirms its own report", r, 250_000, [verdict(r, "issuer", True)]
    r = report("r-05")
    yield "Custodian bank offline: not evaluable", r, 250_000, custodian_check(r, World(TRUTH.held_by_custodian, TRUTH.supply_on_chain, False)) + chain_check(r, TRUTH)
    r = report("r-06")
    yield "Custodian statement is stale", r, 250_000, custodian_check(r, TRUTH, when="2026-10-21T08:00:00Z") + chain_check(r, TRUTH)
    r = report("r-07")
    yield "Mint larger than the reserve surplus", r, 900_000, custodian_check(r, TRUTH) + chain_check(r, TRUTH)
    r = report("r-08", bank=3_000_000.00, other=7_500_000.00)
    yield "Too few reserves held as bank deposits", r, 250_000, custodian_check(r, World({"custodian-bank": 3_000_000.00}, 10_000_000.00)) + chain_check(r, TRUTH)


def main() -> int:
    gate = MintGate()
    rows = []
    for name, rep, amount, ev in scenarios():
        d = gate.mint(rep, amount, ev, NOW)
        out = "MINT" if d.execute else "BLOCK"
        signed = ", ".join(f"{e.verifier_id}={e.result}" for e in ev) or "none"
        rows.append({"scenario": name, "report": rep.report_id, "mint": amount, "outcome": out, "reason": d.reason, "verdicts": signed})
        print(f"{out:6} {name:52} {d.reason[:90]}")
    res = Path(__file__).resolve().parent.parent / "results"
    res.mkdir(exist_ok=True)
    (res / "cross-verification.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    gate.audit.write(res / "cross-verification-log.jsonl")
    print(f"\naudit log: {len(gate.audit.entries)} entries, chain intact: {gate.audit.verify_chain(gate.audit.entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
