import json
from pathlib import Path

from cross_verification import MintGate, World, chain_check, custodian_check
from cross_verification.run import NOW, TRUTH, main, report

RESULTS = Path(__file__).resolve().parent.parent / "results"


def test_outcomes():
    assert main() == 0
    rows = json.loads((RESULTS / "cross-verification.json").read_text())
    assert [r["outcome"] for r in rows] == ["MINT"] + ["BLOCK"] * 7


def test_one_signed_no_from_the_bank_blocks_even_if_issuer_and_chain_agree():
    r = report("t-01", bank=6_900_000.00)
    ev = custodian_check(r, TRUTH) + chain_check(r, TRUTH)
    assert [e.result for e in ev] == [False, True]
    d = MintGate().mint(r, 1.0, ev, NOW)
    assert not d.execute and "CANON-RES-012" in d.reason


def test_bank_offline_is_not_the_same_as_bank_says_no():
    r = report("t-02")
    offline = MintGate().mint(r, 1.0, custodian_check(r, World(TRUTH.held_by_custodian, TRUTH.supply_on_chain, False)) + chain_check(r, TRUTH), NOW)
    assert not offline.execute and "CANON-RES-012" not in offline.reason


def test_issuer_cannot_confirm_itself():
    rows = json.loads((RESULTS / "cross-verification.json").read_text())
    assert "not independent" in rows[3]["reason"]
