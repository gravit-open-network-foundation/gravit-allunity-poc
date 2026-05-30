"""
Scenario 1: AI-agent payment via x402 with Gravit verification
"""

from allunity_integration.x402_adapter import X402Adapter
from epistemic_core.proofs import AuditProofGenerator


def run():
    print("=== Scenario 1: x402 Agentic Payment ===")

    # 1. Simulate AI-agent payment request
    payment = {
        "amount": 1000,
        "currency": "CHFAU",
        "agent_id": "agent_sygnum_001",
        "epistemic_commitment": "0x7a8f..."
    }

    # 2. Verify via Gravit
    adapter = X402Adapter()
    result = adapter.verify_agentic_payment(payment)

    # 3. Generate BaFin audit proof
    proof_gen = AuditProofGenerator()
    audit_proof = proof_gen.generate(result)

    # 4. Output
    if result["valid"]:
        print(f"✅ Payment verified (score: {result['score']})")
        print(f"✅ Audit proof: {audit_proof[:16]}...")
    else:
        print(f"❌ Verification failed: {result['error']}")

    return result


if __name__ == "__main__":
    run()