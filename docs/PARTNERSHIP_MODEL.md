# Gravit × AllUnity: proposed collaboration

> **Replaced on 14 Oct 2026.** The earlier version of this page described a plan that was never agreed
> with AllUnity ("mandatory trust layer", "exclusive partnership for Europe", "BaFin sandbox
> participation"). It is withdrawn; it remains readable in the history of this repository. This page is a
> proposal for discussion. Nothing here has been agreed with AllUnity.

## The idea in one paragraph

AllUnity's Agentic Facilitator verifies an already signed x402 payment authorization and submits it
unchanged for execution: it checks that a payment is correctly authorized. Whether the payment *should*
happen, for example whether the data or the delivery an AI agent relied on is confirmed, is a different
question. The Gravit Verifier answers that question before settlement, and records the decision so that
an auditor or a supervisor can check it without access to either party. It complements AllUnity's products;
it does not replace any of them.

## What exists today (this repository)

* A gate for x402 agent payments in CHFAU, EURAU and SEKAU: AllUnity's hard rules first; attestations bound
  to the exact payment; the public Gravit Verifier (v0.6.0) requires a Verified Fact from at least two
  independent operators, with fresh evidence.
* Seven scenarios (two payments settled, five correctly blocked) and a hash-chained decision log, checked
  byte for byte in CI.
* Simulated x402 requests and test keys; not connected to AllUnity.

Related public work on AllUnity's tokens, from public data only:
[EURAU venue study](https://github.com/gravit-open-network-foundation/graviteron/tree/main/benchmarks/real_eurau),
[CHFAU on-chain study](https://github.com/gravit-open-network-foundation/graviteron/tree/main/benchmarks/real_chfau),
[EURAU history journal](https://github.com/gravit-open-network-foundation/history-keeper/tree/main/journals/eurau-2026-10).

## Proposed steps

1. **Test environment.** Replace the simulated request with AllUnity's real x402 payload format; two
   independent operators (for example AllUnity's transaction monitoring and a third party) run verifier keys.
2. **Optional "verified payment" in the Agentic Facilitator.** A merchant or payer may require a verified
   decision before settlement; the decision record travels with the payment.
3. **Verifiable reporting per token.** Supply per chain, compared with reserve attestations; transfer volume
   net of AllUnity's own operational transfers (once AllUnity confirms the roles of those wallets); history
   kept in History Keeper, time confirmed by independent authorities.

## Per token

| Token | Proposal |
|---|---|
| CHFAU | verifiable monthly reporting; a three-party pilot with a Swiss bank partner (see the Gravit × Sygnum proof of concept) |
| SEKAU | transparency from day one, from the launch of the token |
| EURAU | daily check of trading at par across venues, with alerts |
| USDAU | transparency from day one |

## What Gravit does not do

Gravit does not fulfil any obligation under MiCA, the EU AI Act or other law on AllUnity's behalf; those
obligations remain with the regulated entity. Gravit provides evidence that anyone can check.
