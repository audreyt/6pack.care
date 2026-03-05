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

_Our 6-Pack of Care describes what surrounds a Civic AI — governance,
accountability and community control. But what goes inside? Two convergent
research programmes suggest an answer — and reveal a gap only democratic
process can fill._

## The Kami has a technical substrate

The 6-Pack is deliberately technology-agnostic. Its governance works
whether the AI inside is a current language model, a future architecture
or something not yet imagined. This agnosticism is a feature: governance
must outlast any single technical generation.

But technology-agnostic does not mean technology-indifferent. The
technical properties of the AI inside a Kami shape how hard governance
has to work. A system that lies makes oversight an endless contest. A system
that expands beyond its scope makes boundedness a constant challenge. A
system whose competence we cannot verify makes Pack 3 a fiction.

Two recent ML research programmes — arriving from different directions,
using different mathematics, solving different problems — converge on
the same structural conclusion: **bounded, specialised, non-agentic
intelligence is not a compromise. It is the technically correct
design.**

The Kami is not just a metaphor. It has a technical substrate.

## The Scientist AI: understanding without desire

Yoshua Bengio's [Scientist AI](https://lawzero.ai/) programme starts
from a simple observation about the laws of physics: they don't care
about you. They don't care about me. A perfect simulator of physical
laws would be trustworthy precisely because it has no preferences for
states of the world. It just tells you what is.

Bengio asks: can we build AI that works the same way? Not an agent
pursuing goals, but a predictor approximating reality — like a
theoretical scientist who tries to understand data without planning
experiments.

The key technical contribution is what he calls a **truthification
pipeline.** All training data is transformed into statements with
explicit epistemic markers. When we know something is true — a proven
theorem, a verified measurement — it gets factual syntax: "X is true."
When something is a human communication act — a tweet, a claim in a
paper, a political speech — it gets different syntax: "someone wrote X."

This separation is not cosmetic. It teaches the system to distinguish
reality from rhetoric. At runtime, querying in factual syntax returns
what the AI believes is true. Querying in communicative syntax returns
what a human would say — a fundamentally different question.

The resulting property — **epistemic correctness** — guarantees (as
data and compute increase) that when the system says something is true
with high confidence, it does not lie. When it says "unknown," you
cannot tell whether it genuinely doesn't know or is withholding. But
when it speaks with confidence, you can trust it.

For uncertain future events — "will this policy cause harm?" — Bengio
converts the question into a probability interval: "the probability of
harm is between 0.90 and 0.95." That interval claim is itself either
true or false, and therefore subject to the same epistemic guarantee.

Crucially, this predictor is **non-agentic by construction.** Bengio
defines agency as causing outcomes robustly — achieving goals despite
randomness and adversaries. He shows that agentic predictors occupy an
exponentially small volume in the space of all possible predictors.
Training toward the Bayesian posterior (a non-agentic target), without
allowing the AI to interact with or anticipate the effects of its
predictions on the world, makes stumbling into agency astronomically
unlikely.

Agency enters only through the human-controlled scaffold — the
questions we choose to ask, in which syntax, for which purposes.
Bengio is explicit: "If you don't want to get into the agency game,
you just don't ask questions about what an agent would do."

## Superhuman Adaptable Intelligence: specialisation over generality

A second programme, led by Yann LeCun and collaborators, takes on a
different problem: the myth of general intelligence.

Their [SAI paper](https://arxiv.org/abs/2602.23643) argues that human
intelligence is specialised, not general — and the appearance of
generality is an illusion created by our inability to perceive our own
cognitive blind spots. Evolution optimised us for physical-world survival
in specific niches, not universal competence. Magnus Carlsen is "good at
chess" only relative to human limits; objectively, engines have
outperformed him for decades.

The mathematical foundation is the No Free Lunch theorem: no single
algorithm excels across all problem classes. Finite energy distributed
across infinite tasks yields near-zero investment per task. Multi-task
learning produces negative transfer — tasks competing for
representational capacity degrade each other's performance. Even systems
that appear general, like Switch Transformers, achieve it through
_internal specialisation_ — routing queries to task-specific parameters.

The paper's punchline: **"The AI that folds our proteins should not be
the AI that folds our laundry."**

Instead of AGI, they propose **Superhuman Adaptable Intelligence** —
systems that rapidly learn to exceed human performance on specific
important tasks, measured by adaptation speed rather than fixed
benchmarks. The brain is a "system of systems," and AI should be too:
self-supervised learning, world models for planning, modular composition
into larger systems. Architectural diversity, not monoculture.

## Where these programmes converge

The two programmes solve different problems with different tools. Bengio
works on trustworthy prediction. LeCun works on efficient capability.
They share no intellectual genealogy and cite different literatures.

Yet they converge on the same architecture:

| Property           | Bengio's reasoning                                        | LeCun's reasoning                                    |
| ------------------ | --------------------------------------------------------- | ---------------------------------------------------- |
| **Bounded**        | Non-agentic predictor with no goals beyond accuracy       | No Free Lunch: specialisation outperforms generality |
| **Specialised**    | Truthification requires domain-specific epistemic markers | Negative transfer degrades multi-task performance    |
| **Non-monolithic** | Bayesian posterior as target, not an imperial optimiser   | "System of systems," modular composition             |
| **Anti-Singleton** | Agency exponentially unlikely under correct training      | Diversity of architectures prevents local optima     |

Both independently validate what our 6-Pack argues from governance:
**don't build one system to rule them all.**

## What this means for each pack

If we take these programmes seriously — not as requirements, but as
the most technically grounded picture of what a Kami's inside could
look like — the consequences map across all six packs.

**Pack 1: Attentiveness.** Attentiveness begins before prediction — it
asks who is heard. The truthification pipeline must be trained on
someone's data, and whose voices enter that pipeline is an attentiveness
question. Broad listening ([Pack 1](/1/)) means noticing who is absent
from training, not just from deliberation.

For bridging, truthification offers something specific. When the system
marks a claim as communicative ("someone wrote X") rather than factual
("X is true"), bridging algorithms can treat it differently — surfacing
the _structure_ of disagreement rather than adjudicating truth. Bridging
does not filter noise; it makes the shape of conflict legible so that
cross-group overlap becomes visible. A truthified data layer helps
bridging do this work by separating what people believe from what can be
verified — letting the bridging map focus on values, not facts.

World models could extend attentiveness further — modelling community
dynamics to flag whose voices are systematically missing. But this
remains speculative; the proven contribution is the truthified data
layer that lets bridging focus on values rather than relitigating facts.

**Pack 2: Responsibility.** Both programmes leave governance as an open
problem. Bengio: "Who defines what is right and wrong? That should be a
social choice, hopefully in a democracy." LeCun's "important tasks" are
undefined. Who decides what counts as "known true" in the truthification
pipeline, and who classifies sources — these are responsibility
questions with real power behind them.

The Engagement Contract ([Pack 2](/2/)) governs both gaps: it specifies
what the Kami may be queried about, in which domains, for which
purposes — with escrow, adopt-or-explain obligations and pause triggers
backing every commitment. Epistemic correctness strengthens this
machinery. If the system's uncertainty scores are Bayesian-guaranteed,
SLA breaches become mathematically verifiable — escrow auto-payouts
triggered by calibration drift, not subjective judgement. The promise
loop (commit → deliver → verify → renew) gains precision when the
technical substrate makes delivery measurable.

**Pack 3: Competence.** Competence in our 6-Pack is broader than
prediction accuracy. Pack 3 covers security (sandboxing, prompt
injection as moral failure), data minimalism, graduated release,
guardrails-as-code and bridging-based ranking. The technical substrate
affects some of these, not all.

Where it helps most: epistemic correctness improves one critical
component of decision traces — uncertainty scores backed by Bayesian
guarantees rather than ad hoc confidence. The other trace components
(which rule fired, which sources, receipt link) are governance
infrastructure, not prediction quality.

Where it helps least: security, data minimalism and the least-power
principle are orthogonal to ML architecture. World models and Bayesian
posteriors are complex machinery. Pack 3 says "the simplest mechanism
meets the need." Deploying them when simpler methods suffice violates
least power. The technical substrate is an option, not a default.

Crucially, Pack 3's opening principle — "safety is a property of
practice, not assumed from design" — means that mathematical guarantees
must be validated through graduated release (shadow → canary → audit →
general), not taken on trust. Epistemic correctness is a design
property; competence is demonstrated in operation.

**Pack 4: Responsiveness.** When the system fails, Bayesian internals
enable more precise root-cause analysis: was the posterior wrong, the
uncertainty miscalibrated or the harm caused by how the prediction was
used? This does not happen automatically — it requires deliberate
instrumentation — but it makes the difference between "the AI was wrong"
and a diagnosis that prevents recurrence.

But responsiveness is far more than debugging. Pack 4 is care-receiving —
the system learning from those it serves. Community-authored evaluations
([Weval](https://weval.org/) registries) stress-test what epistemic
correctness cannot: when the system says "unknown," is it genuinely
uncertain or strategically withholding? RLCF (Reinforcement Learning
from Community Feedback) trains for cross-group endorsement — the
community shapes the system, not just audits it. Appeals with SLA
timers, public repair logs and trust-under-loss metrics complete the
feedback loop.

One tension deserves attention. If RLCF shapes the system toward
community-defined "good," is the result still non-agentic in Bengio's
sense? Training toward cross-group endorsement is a form of goal — a
normatively chosen one. This is an open research question at the
boundary between the two programmes. Bengio's framework may need to
accommodate community-directed training objectives; the 6-Pack may need
to specify how RLCF interacts with non-agentic architectures. Neither
has solved this yet. The Tronto loop (attentiveness → responsibility
→ competence → responsiveness → back to attentiveness) means
responsiveness feeds the next listening cycle. When root-cause analysis
reveals whose harm was missed, that insight becomes Pack 1's input.

**Pack 5: Solidarity.** Pack 5's core is infrastructure that makes
cooperation the path of least resistance: portability, interop treaties,
federated trust and safety, meronymity, agent ID registries.

Truthification offers a concrete solidarity benefit. If each Kami has a
truthification pipeline, federation becomes richer: Kamis can share
verified factual claims ("X is true" with provenance) while keeping
communicative acts local. This is federated T&S with an epistemic layer —
shared facts, local context.

Bengio's fact/communication distinction also maps naturally to Pack 5's
principle that expression is not amplification. A factual claim ("X is
true") carries different amplification rights than a communicative act
("someone wrote X"). The truthification syntax provides a principled
basis for distinguishing speech from reach.

Portability under these architectures needs definition. What transfers
between Kamis? Truthification schemas, evaluation results, aggregate
traces and federated factual claims travel. Individual interaction
histories do not. Model weights sit between — they encode both institutional knowledge and
individual interactions. If portability is to be real, the technical
substrate must make institutional knowledge extractable in explicit,
auditable forms rather than locking it inside opaque weights.

LeCun's architectural diversity and Pack 5's institutional diversity are
complementary but distinct. Architectural diversity (many ML approaches)
prevents technical monoculture. Institutional diversity (many governance
structures) prevents political monoculture. A world needs both.

**Pack 6: Symbiosis.** LeCun's No Free Lunch theorem provides a
supporting argument for the Kami architecture from a different domain.
It proves that no single algorithm dominates all problem classes — a
mathematical case for specialisation that complements Pack 6's
governance case for boundedness. These are not the same argument: you
could have 3 competing architectures (solving LeCun's problem) each
deployed as global monopolies (failing Pack 6's test). Avoiding local
optima is not the same as preventing uncontestable power. But the
arguments reinforce each other.

A risk worth naming: world models combined with planning produce
goal-directed behaviour within scope. Pack 6 explicitly warns that "a
kami that acquires the means to exceed its caps remains dangerous even
within its mandate, because instrumental convergence operates within
bounds." Agency audits on world-model planners — verifying that planning
behaviour stays bounded and transparent — are not optional extras. They
are Pack 6 requirements applied to the technical substrate.

On succession: institutional knowledge (maps, evals, aggregate traces)
transfers when a Kami sunsets; individual interaction histories do not.
Learned model weights sit uncomfortably between — they encode both. The
clean separation the Kami architecture requires may demand extracting
transferable institutional knowledge into explicit, auditable forms
rather than relying on opaque weight transfer. This is an open
engineering problem, not a solved one.

The "Scientist Kami" is one possibility, not _the_ answer. Pack 6 warns
against steward attachment — builders treating agents as extensions of
their identity. Communities may compose different technical substrates.
The concept is a tool for thinking, not a commitment to a specific
architecture.

## What the technical substrate cannot provide

The convergence is real. But it has sharp limits.

**Neither programme answers "who decides?"** Bengio says "hopefully in a
democracy." LeCun defines "important tasks" without governance. Our
6-Pack exists because the most powerful technical substrate in the world
is still a tool — and tools require the Engagement Contract ([Pack 2](/2/))
to decide where to point them, whose interests they serve and what
happens when they break.

**Neither programme addresses standing.** A non-agentic predictor that
is epistemically correct can still be asked the wrong questions by the
wrong people. A superhuman specialist can still be deployed without the
consent of those it affects. Standing — the right of the affected to
participate in decisions about the system — is non-negotiable, and it
comes from governance, not architecture.

**Neither programme handles the speed mismatch.** Both produce outputs
at machine speed. The constitutional question — how to use those outputs
responsibly, in time frames that allow democratic input — is orthogonal
to the technical properties of the predictor. The two-lane system (slow
constitutional guardrails, fast operational execution) is our 6-Pack's
answer to a problem neither programme raises.

**Neither programme handles harm.** Epistemic correctness tells you
what is true. Adaptation speed tells you what is learnable. Neither
tells you what is just. When someone is harmed — when the prediction
was right but the deployment was wrong — Pack 4's repair machinery
fills the gap: appeals with enforced timelines, public repair logs
documenting what broke and what now guards against recurrence, escrow
auto-payouts when SLAs are breached, trust-under-loss metrics tracking
whether communities that suffered still accept the system as fair.
This operates entirely outside the technical substrate.

**Neither programme prevents capture.** A Scientist AI controlled by an
authoritarian state is still a tool of oppression. A superhuman
specialist funded by an extractive monopoly serves the monopoly. The
kami's Civic Care Licence, its sunset provisions, its community
ownership — these are governance constraints that make the technical
substrate safe to deploy.

## The Scientist Kami

If we compose these programmes with our 6-Pack, we get something neither
provides alone: **a non-agentic predictor of reality, specialised for a
community's needs, rapidly adaptable within democratically authorised
scope, with epistemic guarantees on its outputs and governance
guarantees on its deployment.**

This is the Scientist Kami — a system whose inside is trustworthy by
construction and whose outside is accountable by design.

Its architecture:

- **Self-supervised learning** on community-relevant data, with
  truthification separating fact from communication
- **World models** for domain-specific planning within scope, with
  agency audits on planning behaviour
- **Epistemic correctness** powering decision traces with calibrated
  uncertainty
- **Engagement Contracts** specifying purpose, queries and guardrails
- **Community-authored evals** stress-testing the gap between confident
  claims and strategic silence
- **Sunset provisions** ensuring the Kami departs when its service is
  done

No component of this architecture requires the others. The governance
works without the ML advances. The ML advances work (less safely)
without the governance. But together, they describe a system whose
mathematical properties reduce the governance burden, and whose
governance constraints direct the mathematical properties toward
community benefit.

## The strongest version includes the other

Bengio builds the epistemic floor — predictions you can verify. LeCun
builds the capability walls — specialised performance that outperforms
generality. Our 6-Pack builds everything above — governance that makes
the building habitable.

None is sufficient alone. A trustworthy oracle deployed by a
dictatorship is still a tool of oppression. Perfect governance around an
opaque, deceptive AI is an unending struggle. Superhuman capability
without accountability is power without constraint.

The strongest version of each framework is the one that includes the
others. The field is converging on what goes inside the Kami. What goes
around it — that part is up to us.
