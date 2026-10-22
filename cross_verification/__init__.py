"""
Cross-verification of stablecoin reserves: the issuer never confirms itself.

The issuer (AllUnity's role) publishes a reserve report for CHFAU: on-chain
supply and the reserves behind it, per custodian. Before a new mint the report
must be a "Verified Fact" for the public Gravit Verifier v0.6.0, from signed
verdicts of at least two INDEPENDENT operators, each checking only what it can
see itself:

- the custodian bank (Sygnum's role) compares the balance the report claims at
  the bank with the balance it actually holds;
- an independent chain observer compares the reported supply with the token's
  supply on chain.

Each signs the hash of the exact report with result=True if its part is
right, result=False if it is wrong. A single signed "false" blocks the mint
even when outvoted (CANON-RES-012). The issuer's own signature never counts
as independent. Hard policy first: reserves cover supply plus the new mint,
and the MiCAR share of deposits at credit institutions is respected.

Everything is a TEST fixture: roles, balances and keys are fictitious; no
connection to AllUnity, Sygnum or any chain.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from gravit_verifier import EvidenceRecord
from gravit_verifier.registry import (TrustRoot, VerifierRegistry, key_id_for, registry_signing_message,
                                      signing_message)

from gravit_gate import AuditLog, EpistemicGate
from gravit_gate.gate import action_hash

# key name -> operator. Roles only: these are TEST keys, not the institutions' keys.
OPERATORS = {
    "custodian-bank": "Custodian bank (Sygnum role, TEST key)",
    "chain-observer": "Independent chain observer (TEST key)",
    "issuer": "Issuer (AllUnity role, TEST key)",
}
MIN_DEPOSIT_SHARE = 0.30   # MiCAR: share of reserve funds held as deposits at credit institutions


def _key(n: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"gravit-reserves-test:" + n.encode()).digest())


def _pub(n: str) -> bytes:
    return _key(n).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


def registry() -> VerifierRegistry:
    doc = lambda o: (json.dumps(o, indent=1, sort_keys=True) + "\n").encode()
    roots = [f"root-{i}" for i in range(1, 6)]
    tr = TrustRoot.from_bytes(doc({"trust_root_version": 1, "threshold": 3, "root_keys": [
        {"key_id": key_id_for(_pub(r)), "public_key": base64.b64encode(_pub(r)).decode()} for r in roots]}))
    reg = doc({"registry_version": 1, "verifiers": [
        {"key_id": key_id_for(_pub(n)), "public_key": base64.b64encode(_pub(n)).decode(), "operator": op, "revoked": False}
        for n, op in OPERATORS.items()]})
    msg = registry_signing_message(reg)
    sigs = "".join(f"{key_id_for(_pub(r))} {base64.b64encode(_key(r).sign(msg)).decode()}\n" for r in roots[:3])
    return VerifierRegistry.from_bytes(reg, sigs, tr)


@dataclass
class ReserveReport:
    report_id: str
    token: str
    as_of: str
    supply: float                                   # tokens in circulation, as reported by the issuer
    deposits: Dict[str, float]                      # custodian bank -> deposit balance (CHF)
    other_reserves: float = 0.0                     # e.g. high-quality liquid assets (CHF)

    def total(self) -> float:
        return round(sum(self.deposits.values()) + self.other_reserves, 2)

    def as_action(self) -> Dict[str, Any]:
        return {"type": "reserve_report", **asdict(self)}


@dataclass
class World:
    """What each independent party can actually see (the ground truth of the demo)."""
    held_by_custodian: Dict[str, float]             # what the bank really holds for the issuer
    supply_on_chain: float                          # what the chain really shows
    custodian_online: bool = True


def verdict(report: ReserveReport, signer: str, result: Optional[bool], when: Optional[str] = None) -> EvidenceRecord:
    h = action_hash(report.as_action())
    r = EvidenceRecord(record_id=f"{signer}:{report.report_id}", theta=0.97, result=result, verifier_id=signer,
                       timestamp=when or report.as_of, provenance=OPERATORS.get(signer, "unregistered"),
                       integrity_hash=h, key_id=key_id_for(_pub(signer)))
    r.signature = base64.b64encode(_key(signer).sign(signing_message(report.report_id, r))).decode()
    return r


def custodian_check(report: ReserveReport, world: World, bank: str = "custodian-bank", when: Optional[str] = None):
    """The bank signs only what it can see: the balance it holds for the issuer."""
    if not world.custodian_online:
        return []
    claimed = report.deposits.get(bank)
    return [verdict(report, bank, claimed is not None and abs(claimed - world.held_by_custodian.get(bank, 0.0)) < 0.005, when)]


def chain_check(report: ReserveReport, world: World):
    """The chain observer signs only what it can see: the supply on chain."""
    return [verdict(report, "chain-observer", abs(report.supply - world.supply_on_chain) < 0.005)]


def policy_error(report: ReserveReport, mint: float) -> Optional[str]:
    total = report.total()
    if total < report.supply + mint:
        return f"reserves {total:,.2f} do not cover supply {report.supply:,.2f} + mint {mint:,.2f}"
    dep = sum(report.deposits.values()) / total if total else 0.0
    if dep < MIN_DEPOSIT_SHARE:
        return f"deposits at credit institutions {dep:.0%} below the MiCAR minimum {MIN_DEPOSIT_SHARE:.0%}"
    return None


class MintGate:
    def __init__(self, freshness_seconds: int = 3600) -> None:
        self.audit = AuditLog()
        self.gate = EpistemicGate(registry(), self.audit, freshness_max_age_seconds=freshness_seconds)

    def mint(self, report: ReserveReport, amount: float, evidence: List[EvidenceRecord], now: str):
        # the issuer may sign its own report, but that is never independent evidence
        own = [e for e in evidence if e.verifier_id == "issuer"]
        evidence = [e for e in evidence if e.verifier_id != "issuer"]
        if own and not evidence:
            return self.gate.check(report.report_id, report.as_action(), [], now,
                                   policy_error="only the issuer confirmed its own report; that is not independent evidence")
        return self.gate.check(f"{report.report_id}", report.as_action(), evidence, now,
                               policy_error=policy_error(report, amount), min_operators=2, high_impact=True)
