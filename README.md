# Gravit × AllUnity – Proof of Concept

**Epistemic gate for AI-agent payments (x402) in AllUnity stablecoins (CHFAU, EURAU, SEKAU)**

An AI agent wants to pay. Before settlement the payment must pass a gate:

1. **AllUnity's hard rules** – supported stablecoin, positive amount, per-payment limit, payee present.
   No evidence can override them.
2. **Binding** – every attestation is signed over the SHA3-256 hash of *exactly this* payment;
   change one field after signing and the attestation no longer counts.
3. **The public [Gravit Verifier](https://github.com/gravit-open-network-foundation/verifier) v0.5.0**
   must classify the payment as a *Verified Fact*: signed attestations from at least two
   **independent** operators listed in a verifier registry that 3 of 5 root keys have signed;
   fresh (≤ 5 minutes); for payments from 10 000 with strong provenance (CANON-PRV-006).
   Many votes from one operator never add up to a Verified Fact.

Every decision – settled or blocked – is appended to a **hash-chained audit log**
(`results/audit-log.jsonl`): each entry carries its timestamp and the hash of the previous
entry, so history can be extended but not rewritten.

## Run it

```bash
make setup PYTHON=python3.12   # Python ≥ 3.10; installs the verifier at tag v0.5.0
make run                       # 7 scenarios → results/
make test
```

| # | Scenario | Result |
|---|---|---|
| 1 | Payment, two independent operators | **settle** |
| 2 | Sybil: two keys of the same operator | block |
| 3 | Amount changed after attestation | block |
| 4 | Forged attestation (unregistered key) | block |
| 5 | Currency is not an AllUnity stablecoin | block |
| 6 | Attestations older than 5 minutes | block |
| 7 | 25 000 EURAU, three independent operators | **settle** |

CI runs the tests and regenerates `results/` on every change; it fails if a single byte differs,
so anyone can check that the published results come from this code.

## Status – what this is and is not

- **Is:** a runnable demonstration. The verification is the real, tested Gravit Verifier.
- **Is not:** connected to AllUnity. x402 requests and settlement are simulated; there are no
  live transactions.
- **Keys:** `gravit_gate/testkeys.py` contains **test keys only**, derived from public seeds.
  A deployment uses the Foundation's registry signed by the root key holders.
- `docs/` describes the intended partnership and compliance mapping; it is a plan and has not
  been reviewed by AllUnity, BaFin or legal counsel.

**Next step with AllUnity:** replace the simulated x402 request with AllUnity's real x402
payload format (test environment), and let two independent operators run verifier keys.
