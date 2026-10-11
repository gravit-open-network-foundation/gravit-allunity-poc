import json
from pathlib import Path

from pilot.run_pilot import NOW, scenarios
from allunity_integration.x402_adapter import X402Adapter
from gravit_gate import AuditLog, EpistemicGate, demo_registry

EXPECTED = {
    "pay-001": True,   # two independent operators
    "pay-002": False,  # same operator twice (Sybil)
    "pay-003": False,  # tampered after attestation
    "pay-004": False,  # forged key
    "pay-005": False,  # policy
    "pay-006": False,  # stale
    "pay-007": True,   # high impact, three operators
}


def run():
    audit = AuditLog()
    adapter = X402Adapter(EpistemicGate(demo_registry(), audit))
    return {p["payment_id"]: adapter.verify_agentic_payment(p, ev, NOW) for _, p, ev in scenarios()}, audit


def test_every_scenario_has_the_expected_outcome():
    decisions, _ = run()
    assert {k: d.execute for k, d in decisions.items()} == EXPECTED


def test_only_verified_facts_settle():
    decisions, _ = run()
    for d in decisions.values():
        if d.execute:
            assert d.decision["final_epistemic_state"] == "Verified Fact"
            assert len(d.independent_operators) >= 2


def test_audit_chain_detects_any_change():
    _, audit = run()
    entries = json.loads(json.dumps(audit.entries))
    assert AuditLog.verify_chain(entries)
    entries[2]["body"]["execute"] = True  # rewrite history
    assert not AuditLog.verify_chain(entries)


def test_committed_results_match_a_fresh_run():
    decisions, _ = run()
    committed = json.loads((Path(__file__).resolve().parent.parent / "results" / "pilot-results.json").read_text())
    assert [r["execute"] for r in committed] == [d.execute for d in decisions.values()]
