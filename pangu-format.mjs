#!/usr/bin/env bun
// pangu-format.mjs — apply CJK spacing to Markdown files (like prettier --write)
//
// Usage:
//   bun run pangu-format              # format all **/*.md
//   bun run pangu-format file.md …   # format given files (lint-staged compatible)
//   bun run pangu-format --check      # exit 1 if any file would change

import pangu from "pangu";
import { readFileSync, writeFileSync } from "fs";
import { glob } from "fs/promises";
import { remark } from "remark";
import visit from "unist-util-visit";

// After pangu spaces everything, selectively revert:
// ——  always (Mandarin style: no surrounding spaces)
// ……  always
// /   always (abbreviations, CJK pairs — leave alone)
// -   always
// &   only when both touching chars are uppercase Latin [A-Z] (e.g. T&S, R&D)
function revert(s) {
    return s
        .replace(/ *(——|……|\/|-) */g, (_, p) => p)
        .replace(/([A-Z]) & ([A-Z])/g, "$1&$2");
}

function applySelective(val) {
    return revert(pangu.spacingText(val));
}

function splitFrontMatter(src) {
    if (!src.startsWith("---\n")) return { fm: "", body: src };
    const end = src.indexOf("\n---\n", 4);
    if (end === -1) return { fm: "", body: src };
    return { fm: src.slice(0, end + 5), body: src.slice(end + 5) };
}

const parser = remark();

async function processFile(file, checkOnly) {
    const src = readFileSync(file, "utf8");
    const { fm, body } = splitFrontMatter(src);
    const tree = parser.parse(body);

    const replacements = [];
    visit(tree, "text", (node) => {
        const original = node.value;
        const updated = applySelective(original);
        if (revert(original) === updated) return;
        const { start, end } = node.position;
        // Safety: verify the source slice matches what remark parsed
        if (body.slice(start.offset, end.offset) !== original) return;
        replacements.push({ start: start.offset, end: end.offset, updated });
    });

    if (replacements.length === 0) return false;

    if (!checkOnly) {
        let result = body;
        for (const { start, end, updated } of replacements.sort(
            (a, b) => b.start - a.start
        )) {
            result = result.slice(0, start) + updated + result.slice(end);
        }
        writeFileSync(file, fm + result, "utf8");
    }

    return true;
}

const args = process.argv.slice(2);
const checkOnly = args.includes("--check");
const fileArgs = args.filter((a) => !a.startsWith("--"));

const files =
    fileArgs.length > 0
        ? fileArgs
        : await Array.fromAsync(
              glob("**/*.md", { ignore: ["node_modules/**", "docs/**"] })
          );

let anyChanged = false;
for (const file of files) {
    const changed = await processFile(file, checkOnly);
    if (changed) {
        anyChanged = true;
        console.log(
            checkOnly ? `pangu: ${file} would change` : `pangu: ${file}`
        );
    }
}

if (checkOnly) process.exit(anyChanged ? 1 : 0);
