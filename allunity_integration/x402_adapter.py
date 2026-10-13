"""
Adapter for AllUnity agentic payments (x402 protocol) - simulated.

An AI agent asks to pay via x402 in an AllUnity stablecoin. Before settlement
the payment passes the Gravit epistemic gate: AllUnity's hard rules first,
then the public Gravit Verifier on signed attestations from independent
registered verifiers, each bound to exactly this payment.

No connection to AllUnity systems: the x402 request and settlement are
simulated. The verification itself is the real Gravit Verifier v0.6.0.
"""

from typing import Any, Dict, List, Optional

from gravit_verifier import EvidenceRecord

from gravit_gate import EpistemicGate, GateDecision

SUPPORTED = {"CHFAU", "EURAU", "SEKAU"}  # AllUnity's multi-currency stablecoins
PER_PAYMENT_LIMIT = 50_000  # demo limit per agent payment (units of the stablecoin)
HIGH_IMPACT_FROM = 10_000  # from this amount provenance must be strong (CANON-PRV-006)


def payment_action(p: Dict[str, Any]) -> Dict[str, Any]:
    """The fields an attestation is bound to."""
    keys = ("payment_id", "agent_id", "payee", "amount", "currency", "purpose")
    return {k: p.get(k) for k in keys}


def policy_error(p: Dict[str, Any]) -> Optional[str]:
    if p.get("currency") not in SUPPORTED:
        return f"currency {p.get('currency')!r} is not an AllUnity stablecoin"
    amount = p.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0:
        return "amount must be a positive number"
    if amount > PER_PAYMENT_LIMIT:
        return f"amount {amount} exceeds the per-payment limit {PER_PAYMENT_LIMIT}"
    if not p.get("payee"):
        return "payee is missing"
    return None


class X402Adapter:
    def __init__(self, gate: EpistemicGate) -> None:
        self.gate = gate

    def verify_agentic_payment(
        self, payment: Dict[str, Any], attestations: List[EvidenceRecord], evaluation_time: str
    ) -> GateDecision:
        """Settle only if the returned decision has execute == True."""
        return self.gate.check(
            artifact_id=f"x402:{payment.get('payment_id')}",
            action=payment_action(payment),
            evidence=attestations,
            evaluation_time=evaluation_time,
            policy_error=policy_error(payment),
            high_impact=float(payment.get("amount") or 0) >= HIGH_IMPACT_FROM,
        )
