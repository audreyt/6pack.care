# 6-Pack of Care

Civic AI is alignment by public process: community-authored safeguards, public accountability, and bounded local systems.

This repository contains the public site for the 6-Pack of Care, a governance framework by [Audrey Tang](https://afp.oxford-aiethics.ox.ac.uk/people/ambassador-audrey-tang) and [Caroline Green](https://www.oxford-aiethics.ox.ac.uk/caroline-emmer-de-albuquerque-green) at Oxford's Institute for Ethics in AI.

The core idea is simple: instead of asking a small group of developers to define "aligned" for everyone, the 6-Pack asks who is affected, who can contest decisions, what gets logged publicly, and how systems stay local and reversible. The 6-Pack treats AI not as a sovereign optimiser but as a bounded local steward, or Kami.

## The six packs

| #   | Pack                                        | Tronto phase   | Core question                                                                  |
| --- | ------------------------------------------- | -------------- | ------------------------------------------------------------------------------ |
| 1   | [**Attentiveness**](https://6pack.care/1/)  | Caring about   | What do the people closest to the pain notice that we're missing?              |
| 2   | [**Responsibility**](https://6pack.care/2/) | Taking care of | Who is accountable, with what authority, and what happens if they fail?        |
| 3   | [**Competence**](https://6pack.care/3/)     | Care-giving    | Does the system demonstrably work — audited, explainable, safe-to-fail?        |
| 4   | [**Responsiveness**](https://6pack.care/4/) | Care-receiving | Can those affected correct the system, and does correction actually change it? |
| 5   | [**Solidarity**](https://6pack.care/5/)     | Caring with    | Does the ecosystem structurally reward cooperation over lock-in?               |
| 6   | [**Symbiosis**](https://6pack.care/6/)      | Kami of Care   | Is the system bounded, sunset-ready, and incapable of imperial creep?          |

Packs 1 – 4 form Tronto's feedback loop. Pack 5 (from _Caring Democracy_) ensures the loop operates within democratic commitments to justice, equality, and freedom. Pack 6 is Tang and Green's addition: the meta-level guardrail that keeps care local, bounded, and provisional.

Also: [**Measures**](https://6pack.care/measures/) and [**FAQ**](https://6pack.care/faq/).

## Start here

- **Policy.** [Manifesto](https://6pack.care/manifesto/), [FAQ](https://6pack.care/faq/), and [AI Alignment Cannot Be Top-Down](https://6pack.care/ai-alignment-cannot-be-top-down/).
- **Engineering.** [Pack 3](https://6pack.care/3/), [Inside the Kami](https://6pack.care/inside-the-kami/), and [Measures](https://6pack.care/measures/).
- **Civic practice.** [Pack 1](https://6pack.care/1/), [Pack 2](https://6pack.care/2/), and [Pack 4](https://6pack.care/4/).

## Site

**[6pack.care](https://6pack.care/)** — bilingual (British English / Traditional Mandarin) static site.

Built with [Eleventy](https://www.11ty.dev/) v3 and [Bun](https://bun.sh/):

```bash
bun install          # install dependencies
bun run dev          # local dev server at http://127.0.0.1:8080
bun run build        # production build → ./docs/
```

## Contributing

Pull requests are welcome. By contributing, you agree to release your work under the [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) public domain dedication.

When editing content, maintain parity between English (`*.md`) and Traditional Mandarin (`tw-*.md`) variants.

Part of the [Accelerator Fellowship Programme](https://afp.oxford-aiethics.ox.ac.uk/), [Oxford Institute for Ethics in AI](https://www.oxford-aiethics.ox.ac.uk/).
