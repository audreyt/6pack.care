# Repository Guidelines

## Project Structure & Module Organization
- Top-level Markdown files such as `index.md`, `manifesto.md`, and `tw-*.md` define published pages; keep new pages alongside them with clear slugs.
- `_layouts/` holds Liquid layouts for shared chrome and metadata, while `_config.yml` centralizes site-wide settings and collections.
- Assets live in `img/`, `fonts/`, and `styles.css`; optimize images before committing and reuse typography tokens defined in CSS.
- `_site/` is generated output from Jekyll—never edit or commit manual changes there.

## Build, Test, and Development Commands
- `bundle install` installs the pinned Jekyll toolchain from `Gemfile`.
- `bundle exec jekyll serve --livereload` runs the local dev server at `http://127.0.0.1:4000` and rebuilds on change; verify new content there before pushing.
- `bundle exec jekyll build` produces a production-ready build in `_site/` and surfaces Markdown or Liquid errors.
- `bundle exec jekyll doctor` catches common configuration issues; run it before deployment-facing changes.

## Coding Style & Naming Conventions
- Front matter uses YAML with two-space indentation and double-quoted strings for values containing spaces; keep keys in `snake_case` for consistency.
- Write Markdown with sentence-case headings and keep line width under ~100 characters for easier diffs.
- Liquid expressions should stay terse and declarative; prefer includes over duplicating layout HTML.
- CSS updates belong in `styles.css`; follow the existing mobile-first order and group related selectors together.

## Testing Guidelines
- There is no automated test suite; rely on `bundle exec jekyll build` to ensure the site compiles cleanly.
- For content changes, confirm internal links resolve and language variants render correctly via the dev server.
- Capture a quick before/after screenshot when adjusting layout, typography, or imagery to document visual impact.

## Commit & Pull Request Guidelines
- Keep commits focused; mirror the short imperative style seen in history (e.g., `* add manifesto link`).
- Reference related issues in the body and describe scope, dependencies, and any manual QA performed.
- Pull requests should summarize changes, attach screenshots for UI updates, and note follow-up tasks or translation needs.
