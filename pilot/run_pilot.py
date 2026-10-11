#!/usr/bin/env python3
"""
Gravit x AllUnity - x402 agentic payment scenarios.

Runs seven payments through the gate and writes
results/pilot-results.json and results/audit-log.jsonl. Everything is
deterministic (fixed timestamps, deterministic Ed25519 test keys), so CI
regenerates both files and fails if a single byte differs.
"""

import json
from pathlib import Path

from allunity_integration.x402_adapter import X402Adapter, payment_action
from gravit_gate import TEST_EVALUATION_TIME as NOW
from gravit_gate import AuditLog, EpistemicGate, attest, demo_registry
from gravit_gate.gate import action_hash

OUT = Path(__file__).resolve().parent.parent / "results"
STALE = "2026-10-11T11:40:00Z"  # 20 minutes before NOW; freshness limit is 5 minutes


def pay(pid, amount, currency="CHFAU", payee="merchant-zurich-01", purpose="cloud compute invoice 2026-10"):
    return {"payment_id": pid, "agent_id": "agent-treasury-01", "payee": payee,
            "amount": amount, "currency": currency, "purpose": purpose}


def signed(p, *signers, ts=NOW, thetas=None):
    a, h = f"x402:{p['payment_id']}", action_hash(payment_action(p))
    thetas = thetas or [0.92, 0.89, 0.9, 0.88, 0.91]
    return [attest(a, h, s, thetas[i], timestamp=ts) for i, s in enumerate(signers)]


def scenarios():
    ok = pay("pay-001", 1_000)
    yield "Payment verified by two independent operators", ok, signed(ok, "verifier-a", "verifier-b")

    syb = pay("pay-002", 1_000, "EURAU")
    yield "Sybil: two keys of the same operator", syb, signed(syb, "verifier-a", "verifier-a2")

    tam = pay("pay-003", 1_000)
    ev = signed(tam, "verifier-a", "verifier-b")
    tam = {**tam, "amount": 9_000}  # agent changes the amount after attestation
    yield "Tampered: amount changed after attestation", tam, ev

    gh = pay("pay-004", 2_500, "SEKAU")
    yield "Forged attestation from an unregistered key", gh, signed(gh, "verifier-a", "ghost")

    pol = pay("pay-005", 1_000, "USDT")
    yield "Policy: currency is not an AllUnity stablecoin", pol, signed(pol, "verifier-a", "verifier-b")

    st = pay("pay-006", 1_000)
    yield "Stale attestations (older than 5 minutes)", st, signed(st, "verifier-a", "verifier-b", ts=STALE)

    big = pay("pay-007", 25_000, "EURAU", purpose="quarterly supplier settlement")
    yield "High-impact payment, three independent operators", big, signed(big, "verifier-a", "verifier-b", "verifier-c")


def main() -> int:
    audit = AuditLog()
    adapter = X402Adapter(EpistemicGate(demo_registry(), audit))
    rows = []
    for name, payment, attestations in scenarios():
        d = adapter.verify_agentic_payment(payment, attestations, NOW)
        rows.append({"scenario": name, "payment_id": payment["payment_id"], "execute": d.execute,
                     "reason": d.reason, "decision_id": (d.decision or {}).get("decision_id")})
        print(f"{'SETTLE' if d.execute else 'BLOCK ':6}  {name:52}  {d.reason[:90]}")
    OUT.mkdir(exist_ok=True)
    (OUT / "pilot-results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    audit.write(OUT / "audit-log.jsonl")
    print(f"\naudit log: {len(audit.entries)} entries, chain intact: {AuditLog.verify_chain(audit.entries)}, head {audit.head[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
