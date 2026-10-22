# Cross-verification of reserves: the issuer never confirms itself

Before a new CHFAU mint, the issuer's reserve report must be a **Verified Fact** for the public [Gravit Verifier](https://github.com/gravit-open-network-foundation/verifier) v0.6.0, from signed verdicts of at least two **independent** operators. Each checks only what it can see itself:

- **Custodian bank** (the role Sygnum could take): is the balance the report claims at the bank the balance the bank actually holds?
- **Independent chain observer:** is the reported supply the supply on chain?

Each signs the hash of the exact report: `result=true` if its part is right, `result=false` if not. One signed "false" blocks the mint even when outvoted. The issuer's own signature never counts. Hard policy first: reserves cover supply plus the new mint, and the MiCAR minimum share of deposits at credit institutions (30 %) holds.

```bash
make setup PYTHON=python3.12 && make cross && make test
```

| Scenario | Outcome | Why |
|---|---|---|
| Report confirmed by custodian bank and chain observer | MINT | Verified Fact from two independent operators |
| Issuer overstates the balance at the bank | BLOCK | the bank signs "false" (CANON-RES-012) |
| Issuer understates the supply on chain | BLOCK | the chain observer signs "false" |
| Only the issuer confirms its own report | BLOCK | not independent evidence |
| Custodian bank offline | BLOCK | not evaluable; distinct from a contradiction |
| Custodian statement is stale | BLOCK | freshness (CANON-FRS-005) |
| Mint larger than the reserve surplus | BLOCK | policy: reserves do not cover supply + mint |
| Too few reserves held as bank deposits | BLOCK | policy: below the MiCAR minimum |

Why it matters: the issuer, the bank and the observer each keep their own key and see only their own data; nobody has to trust the issuer's word or a single party. The same pattern lets partners act as independent operators for each other.

Status: runnable demonstration. Roles, balances and keys are fictitious TEST fixtures; no connection to AllUnity, Sygnum or any chain; no institution has agreed to act as an operator.
