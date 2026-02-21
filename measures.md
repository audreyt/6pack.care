---
layout: chapter
title: "Measures"
lang: en-gb
alt_lang_url: "/tw/measures"
permalink: "/measures/"
---

Each pack answers a distinct phase question in the care cycle. The measures below are assigned so that each metric belongs to exactly one pack.

**These metrics are designed for sufficiency, not maximisation.** Each deployment context defines a threshold — "good enough" for that community. Crossing the threshold is the goal; score-chasing beyond it risks the same metric-gaming the 6-Pack warns against. The kami tends its garden — it does not compete to tend the most gardens.

### Pack 1 — Attentiveness: did we look at the right things?

| Metric       | What it answers                                                                                    |
| ------------ | -------------------------------------------------------------------------------------------------- |
| Coverage     | What share of affected people provided input?                                                      |
| Absence rate | Which demographic segments have no voice in the bridging map?                                      |
| Voice equity | How much facilitated time do least-heard groups get vs. most-heard?                                |
| Bridging map | Which stakeholder clusters are represented, and which cleavages are reinforcing vs. cross-cutting? |

### Pack 2 — Responsibility: did we make and keep the right promises?

| Metric                | What it answers                                                                              |
| --------------------- | -------------------------------------------------------------------------------------------- |
| Promise coverage      | What share of identified needs have a named owner and SLA?                                   |
| SLA adherence         | What share of cases are resolved within their severity-class window?                         |
| Adopt-or-explain rate | What share of Assembly outcomes have documented adoption or published deviation with remedy? |

### Pack 3 — Competence: did we execute correctly?

| Metric              | What it answers                                                                 |
| ------------------- | ------------------------------------------------------------------------------- |
| Decision accuracy   | What is the error rate by severity class?                                       |
| Guardrail integrity | What share of red-line tests pass?                                              |
| Trace completeness  | What share of decisions have a full trace (rule, source, uncertainty, receipt)? |
| Canary health       | What share of canary releases complete without triggering rollback?             |

### Pack 4 — Responsiveness: did the care land well?

| Metric              | What it answers                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------ |
| Resolution rate     | What share of highest-severity cases are successfully resolved within the promised window? |
| Appeal closure time | How does actual vs. target closure time compare, by severity class?                        |
| Harm recurrence     | At what rate do resolved incidents re-appear within 90 days?                               |
| Trust-under-loss    | What is the trust score after a bad outcome — did repair work?                             |

### Pack 5 — Solidarity: is the ecosystem structurally fair?

| Metric            | What it answers                                                                                        |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| Bridge index      | What are the cross-group participation and endorsement rates in shared decisions, published quarterly? |
| Portability rate  | What share of users successfully export data when leaving?                                             |
| Agent ID coverage | What share of agents have verifiable meronymous attestations?                                          |

### Pack 6 — Symbiosis: is the system bounded and sustainable?

| Metric               | What it answers                                                        |
| -------------------- | ---------------------------------------------------------------------- |
| Scope compliance     | What share of agent actions fall within declared purpose bounds?       |
| Succession readiness | When was the last successful exit drill?                               |
| Sunset compliance    | What share of agents have current attestation and active sunset timer? |
| Ecology diversity    | How many independent agents serve equivalent needs in the same domain? |

### Trust decomposition

Trust is present across all six phases, but each pack measures a distinct dimension:

| Pack               | Trust dimension                                              |
| ------------------ | ------------------------------------------------------------ |
| 1 — Attentiveness  | Trust in being heard (voice equity)                          |
| 2 — Responsibility | Trust in promises (SLA adherence, adopt-or-explain)          |
| 3 — Competence     | Trust in execution (trace completeness, guardrail integrity) |
| 4 — Responsiveness | Trust after harm (trust-under-loss)                          |
| 5 — Solidarity     | Trust across groups (bridge index)                           |
| 6 — Symbiosis      | Trust over time (succession readiness, scope compliance)     |

**Cross-group endorsement** appears in two distinct roles: as an RLCF training signal in Pack 4 (a training objective — how you shape the model) and as the basis of the bridge index in Pack 5 (an ecosystem audit — what you report). These are separate uses.

**Severity classes** are community-defined categories established through deliberation as part of Pack 2's Engagement Contract. The framework requires that every contract includes a severity scale distinguishing at minimum life-and-safety from lower-impact harms. These classes are used as a common scale in Packs 3, 4, and 6 but are not themselves measures.
