# MiCA alignment — how Gravit can support an e-money token issuer

> **Correction (12 Oct 2026).** An earlier version of this table cited MiCA articles incorrectly
> (Art. 45, 63 and 76 do not concern audit trails, risk management or complaints handling). It
> has been replaced below; the earlier text remains in the history of this repository.
> Article headings are taken from the official text, Regulation (EU) 2023/1114 (EUR-Lex).

Gravit **supports** the evidence an issuer and its partners need. It does not fulfil any MiCA
obligation on an issuer's behalf; the obligations remain with the regulated entity, and this
mapping has not been reviewed by BaFin, FINMA or legal counsel.

| MiCA article (official heading) | Who it applies to | How Gravit can support it |
|---|---|---|
| Art. 49 — Issuance and redeemability of e-money tokens | EMT issuer | Each mint / redeem request can be checked before settlement and recorded as a signed, timestamped decision record — evidence of what was requested, decided and executed. |
| Art. 31 / Art. 71 — Complaints-handling procedures | ART issuers / CASPs | Decision records with full reasoning lineage let a complaint about an automated payment be investigated from evidence, not reconstructed after the fact. |
| Art. 68 — Governance arrangements | CASPs | Append-only, hash-chained records of automated decisions support record-keeping and internal control. |
| Art. 92 — Prevention and detection of market abuse | Persons professionally arranging or executing transactions | Adversarial checks (forged or replayed attestations, intent substitution, Sybil-style aggregation) flag suspicious automated orders for review. |

Related, outside MiCA:

- **EU AI Act, record keeping (Art. 12) and human oversight (Art. 14):** these obligations apply to
  high-risk AI systems (for systems listed in Annex III from 2 December 2027). Where an AI agent that
  initiates payments falls under them, a signed decision record with the provenance of each instruction
  supports both. Whether a given agent is high-risk is for its provider and deployer to assess.
- **DORA (Regulation (EU) 2022/2554):** verifiable logs of automated actions support ICT incident
  analysis.

> **Correction (14 Oct 2026).** An earlier version of this list cited Art. 50 of the EU AI Act. Art. 50
> sets transparency duties (telling people they interact with an AI system, labelling generated content);
> it is not the provision relevant to payment records. The earlier text remains in the history of this
> repository.

What exists today is listed in the repository README (status section): a runnable gate on the
public Gravit Verifier v0.5.0 with simulated x402 requests and test keys.
