---
layout: chapter
title: "Inside the Kami"
author: "Audrey Tang"
lang: en-gb
alt_lang_url: "/tw/inside-the-kami"
permalink: "/inside-the-kami/"
date: 2026-03-05
description: "What recent ML research suggests goes inside a bounded Civic AI — and what it cannot provide."
nav_next:
    url: "/"
    text: "Home"
---

The 6-Pack describes the governance around a Civic AI. This essay asks a narrower question: what kind of technical substrate makes that governance easier to uphold?

## In brief

- Recent work from Yoshua Bengio and Yann LeCun points toward bounded, specialised systems rather than one general-purpose governor.
- That convergence does not settle politics, but it does narrow the technical search space.
- The inside still cannot decide legitimacy, standing, pace, or justice. Those remain institutional questions.

## A technical argument for boundedness

The 6-Pack is deliberately technology-agnostic. Its governance should
outlast any one model family. But technology-agnostic is not
technology-indifferent. A deceptive model turns oversight into permanent
combat. A general-purpose optimiser strains every boundary. An opaque
system makes Pack 3 impossible to verify.

Two recent ML programmes — Yoshua Bengio's [Scientist AI](https://lawzero.ai/)
and Yann LeCun's [Superhuman Adaptable Intelligence](https://arxiv.org/abs/2602.23643)
agenda — converge on a useful design lesson: the best substrate for Civic AI is
not a universal agent. It is a bounded, specialised system whose action remains
under human authorisation.

That convergence does not settle politics. It does narrow the technical search
space.

## Bengio: truth without appetite

Bengio's Scientist AI starts from a simple model of trust. The laws of physics
do not want anything. A good scientific model is trustworthy because it tries
to describe the world, not bend the world toward a goal.

His programme asks whether AI can be trained in that spirit: as a predictor of
reality rather than an agent with objectives.

The key move is the **truthification pipeline.** Training data is rewritten with
explicit epistemic markers. A verified measurement or proved theorem is
represented as a factual claim: "X is true." A tweet, speech or paper claim is
represented differently: "someone wrote X."

That distinction matters. It teaches the system to separate the state of the
world from human rhetoric about the world. At runtime, a factual query asks
"what does the model judge to be true?" A communicative query asks "what have
people said?" Those are not the same task.

In Bengio's own framing, this yields **epistemic correctness**: asymptotically,
high-confidence factual answers are not deceptive. The programme is strongest
when the system says "this is true" with confidence. It is weaker when the
system says "unknown": that may be honest uncertainty, or it may be strategic
silence. That gap matters for governance.

The second crucial claim is architectural. Agency is not treated as the
default. It enters through the scaffold around the model — the questions humans
ask, the tools they attach and the actions they authorise. That is exactly
where governance belongs.

## SAI: capability through specialisation

LeCun's SAI programme attacks a different myth: that the right goal is one
general intelligence good at everything.

Its case is mathematical before it is political. The No Free Lunch theorem says
no single algorithm dominates every class of problem. Multi-task systems suffer
negative transfer when tasks compete for the same representational capacity.
Even models that look general often hide specialisation internally, routing
different tasks to different subsystems.

The slogan version is memorable because it is correct: **the AI that folds our
proteins should not be the AI that folds our laundry.**

For Civic AI, the implication is direct. A Kami should not be a mini-sovereign
mind roaming across domains. It should be a specialist: good at one class of
community work, replaceable when its job changes, and unable to turn local
success into universal mandate.

SAI does not solve governance either. A specialist can still be deployed for
bad ends. But it does remove one bad default: the assumption that safer or
smarter AI requires one system to do everything.

## The shared design lesson

Bengio and LeCun are solving different problems. One is asking how to make
prediction trustworthy. The other is asking how to make capability efficient.
Still, they point toward the same Civic AI shape.

| Research result                               | Civic AI implication                                                       |
| --------------------------------------------- | -------------------------------------------------------------------------- |
| Separate truth-tracking from speech imitation | Decision traces can distinguish verified claims from reported claims       |
| Specialisation beats generality               | Each Kami should have a narrow mandate                                     |
| Modular systems beat monoliths                | Civic AI should be composable, replaceable and federated                   |
| Action is the danger point                    | Authorise tools and interventions in governance, not inside opaque weights |

The strongest reading is modest but important: these programmes do not prove
the 6-Pack, but they make the 6-Pack easier to implement. They reduce the
amount of governance work wasted fighting the wrong machine shape.

## What this changes in the 6-Pack

**Pack 1: Attentiveness.** Truthification helps a bridging system tell apart
three things that usually get muddled together: what is verified, what is
claimed and what is contested. That makes disagreement more legible. It does
not answer whose voices get into the training set in the first place. That
remains a listening problem, not a modelling one.

**Pack 2: Responsibility.** Bengio leaves a crucial gap open: who decides which
questions may be asked, in which domains, for which purposes? The Engagement
Contract ([Pack 2](/2/)) fills that gap. It governs the scaffold around the
model: authorised queries, source rules, pause conditions, escrow and
adopt-or-explain duties.

**Pack 3: Competence.** Better-calibrated uncertainty makes decision traces
more honest. A trace that says "0.92 likely" should mean what it says. But
Pack 3 is broader than prediction quality. Sandboxing, least power, data
minimalism and graduated release remain operational duties. Good architecture
reduces risk. It does not replace disciplined practice.

**Pack 4: Responsiveness.** A truth-tracking model gives cleaner failure
analysis: was the factual judgement wrong, was uncertainty miscalibrated or was
the harm introduced by the deployment layer? That is useful, but it is not
repair. Appeals, public repair logs and community-authored evals such as
[Weval](https://weval.org/) still do the moral work of response. They are also
how we probe the hardest case in Bengio's framework: "unknown."

**Pack 5: Solidarity.** These architectures suggest a better basis for
federation. Kamis can share provenance, schemas, eval results and verified
factual claims without flattening local context into one global authority.
Federation should move institutional knowledge, not intimate histories. Shared
facts; local judgement.

**Pack 6: Symbiosis.** SAI strengthens the case for boundedness because
specialisation is not just politically safer; it is technically better. But
Pack 6 still has to do work the ML programmes do not: sunset, succession,
anti-capture rules and non-expansion pacts. And any world-model planner,
however scoped, needs agency audits. Goal-directed behaviour inside a boundary
can still be dangerous.

## What the substrate cannot decide

This is where the limit becomes clear.

**It cannot decide standing.** A non-agentic predictor can still be used
without the consent of the people it affects. Architecture cannot grant the
affected a voice.

**It cannot decide legitimacy.** "What counts as true?", "Which sources
qualify?", and "What tasks matter?" are not technical questions. They are
constitutional questions.

**It cannot decide pace.** Machine outputs arrive quickly. Democratic
authorisation takes time. The two-lane system of the 6-Pack exists because
responsible use requires slow guardrails around fast tools.

**It cannot decide justice.** A prediction can be accurate and still be used
cruelly. Repair, compensation and restored trust do not come from a posterior
distribution.

**It cannot prevent capture.** The same truthful specialist can serve a
democracy, a monopoly or an authoritarian state. Governance determines which.

## The Scientist Kami

Put the pieces together and a plausible technical substrate comes into view:

- a non-agentic, truth-tracking core
- specialist modules for bounded domains
- explicit governance over tools, queries and actions
- community-authored evals probing both confident answers and strategic
  silence
- sunset and handover rules so the service can persist without permanent
  dependence on one model or steward

This is what I mean by a **Scientist Kami**: not a universal governor, but a
civic instrument that is trustworthy inside and accountable outside.

It is not the only possible substrate. It is simply the strongest one now in
view. Bengio helps explain how the inside can stay honest. LeCun helps explain
why the inside should stay narrow. The 6-Pack explains how that system remains
answerable to the people around it.

The field is getting clearer about what belongs inside a Kami. The more
important question — who gets to authorise it, limit it and retire it — is
still, irreducibly, ours.
