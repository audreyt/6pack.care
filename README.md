# 6-Pack of Care

A governance framework by [Audrey Tang](https://afp.oxford-aiethics.ox.ac.uk/people/ambassador-audrey-tang) and [Caroline Green](https://www.oxford-aiethics.ox.ac.uk/caroline-emmer-de-albuquerque-green) at Oxford's Institute for Ethics in AI that translates Joan Tronto's political ethics of care into six machine-codeable design primitives for **Civic AI** — deliberately bounded, purpose-specific AI stewards engineered to nurture a community's relational health rather than maximise abstract global metrics.

## Why care ethics for AI alignment?

Standard alignment approaches try to derive values from data — but no amount of "is" produces an "ought." Care ethics sidesteps this by starting, as Tronto puts it, "in the middle of things": within an existing commitment to democratic values, asking what those commitments demand once we take mutual dependence seriously. The result is **alignment-by-process** — a continuous, democratically governed practice rather than a one-time engineering solution.

Where the vertical narrative of a technological singularity concentrates power in a single unbounded optimiser, the 6-Pack proposes a horizontal alternative: plural stewardship by many bounded intelligences — local _kami_ — in close interaction with human communities. Each kami is bound to a specific place and purpose; its success is the health of the relationships it supports, not indefinite expansion.

## The six packs

| #   | Pack                                        | Tronto phase   | Core question                                                                  |
| --- | ------------------------------------------- | -------------- | ------------------------------------------------------------------------------ |
| 1   | [**Attentiveness**](https://6pack.care/1/)  | Caring about   | What do the people closest to the pain notice that we're missing?              |
| 2   | [**Responsibility**](https://6pack.care/2/) | Taking care of | Who is accountable, with what authority, and what happens if they fail?        |
| 3   | [**Competence**](https://6pack.care/3/)     | Care-giving    | Does the system demonstrably work — audited, explainable, safe-to-fail?        |
| 4   | [**Responsiveness**](https://6pack.care/4/) | Care-receiving | Can those affected correct the system, and does correction actually change it? |
| 5   | [**Solidarity**](https://6pack.care/5/)     | Caring with    | Does the ecosystem structurally reward cooperation over lock-in?               |
| 6   | [**Symbiosis**](https://6pack.care/6/)      | Kami of care   | Is the system bounded, sunset-ready, and incapable of imperial creep?          |

Packs 1 – 4 form Tronto's feedback loop. Pack 5 (from _Caring Democracy_) ensures the loop operates within democratic commitments to justice, equality, and freedom. Pack 6 is Tang and Green's addition: the anti-Singleton architecture that keeps care local, bounded, and provisional.

Also: [**Measures**](https://6pack.care/measures/) (one metric per pack) and [**FAQ**](https://6pack.care/faq/) (speed, cost, bad actors, and how the framework handles them).

## Who it's for

- **Academics.** A rigorous "alignment-by-process" theory grounded in Tronto, Margaret Urban Walker's expressive-collaborative morality, and Ostrom-style polycentric governance. Navigates the Is-Ought problem without collapsing into thin universalism or cultural relativism.
- **Policymakers.** Hard governance levers: citizen alignment assemblies, structural data portability (Utah Digital Choice Act), escrow-backed engagement contracts, bridging-based ranking transparency, and federated trust-and-safety (ROOST).
- **System designers.** Actionable technical scaffolding: bridging algorithms (PCA/embedding overlap), shadow/canary orchestration with rollback, decision-trace schemas, community-authored eval registries (Weval), RLCF reward pipelines, and guardrail-as-code engines.

## Key concepts

- **Bridging algorithms.** Recommenders score content by cross-group endorsement, not outrage. Smaller, coherent clusters earn higher bridging weight because they are harder to reach.
- **Engagement contracts.** Published, auditable specs — purpose, SLAs, pause triggers, remedies, sunset — that make power accountable and irresponsibility visible.
- **Kami model.** Every agent has purpose bounds, resource caps, and a sunset timer. The component sunsets; the service duty persists through succession.
- **RLCF.** Reinforcement Learning from Community Feedback — training agents to optimise for cross-group endorsement and trust-under-loss, not raw engagement.
- **Meronymity.** Partial anonymity: verify an agent is anchored to a real entity without exposing the person.

## Site

**[6pack.care](https://6pack.care/)** — bilingual (British English / Traditional Mandarin) static site.

Built with [Eleventy](https://www.11ty.dev/) v3 and [Bun](https://bun.sh/):

```bash
bun install          # install dependencies
bun run dev          # local dev server at http://127.0.0.1:4000
bun run build        # production build → ./docs/
```

## Contributing

Pull requests are welcome. By contributing, you agree to release your work under the [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) public domain dedication.

When editing content, maintain parity between English (`*.md`) and Traditional Mandarin (`tw-*.md`) variants.
