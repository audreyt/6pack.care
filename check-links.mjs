import { readFileSync, existsSync, statSync } from "fs";
import { resolve, dirname, join } from "path";
import { globSync } from "fs";

const DOCS = resolve("docs");
const htmlFiles = [];

// Collect all HTML files recursively
function walk(dir) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
        const full = join(dir, entry.name);
        if (entry.isDirectory()) walk(full);
        else if (entry.name.endsWith(".html")) htmlFiles.push(full);
    }
}

import { readdirSync } from "fs";
walk(DOCS);

// Parse all ids from each HTML file (cached)
const idCache = new Map();
function getIds(file) {
    if (idCache.has(file)) return idCache.get(file);
    const html = readFileSync(file, "utf8");
    const ids = new Set();
    for (const m of html.matchAll(/\bid="([^"]+)"/g)) ids.add(m[1]);
    idCache.set(file, ids);
    return ids;
}

// Resolve a local path to a file in docs/
function resolveLocal(href, fromFile) {
    // Strip query string and fragment for path resolution
    const [pathPart] = href.split(/[?#]/, 1);
    let target;
    if (pathPart.startsWith("/")) {
        target = join(DOCS, pathPart);
    } else {
        target = resolve(dirname(fromFile), pathPart);
    }
    // If it points to a directory, look for index.html
    if (existsSync(target) && statSync(target).isDirectory()) {
        return join(target, "index.html");
    }
    return target;
}

const errors = [];

for (const file of htmlFiles) {
    const html = readFileSync(file, "utf8");
    const rel = file.slice(DOCS.length);

    // Match href="..." and src="..."
    for (const m of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
        const ref = m[1];

        // Skip external, mailto, data URIs, template variables
        if (
            ref.startsWith("http://") ||
            ref.startsWith("https://") ||
            ref.startsWith("mailto:") ||
            ref.startsWith("data:") ||
            ref.includes("{{")
        )
            continue;

        // Pure fragment link — check within same file
        if (ref.startsWith("#")) {
            const ids = getIds(file);
            if (!ids.has(ref.slice(1))) {
                errors.push(`${rel} → ${ref} (anchor not found)`);
            }
            continue;
        }

        // Local path (absolute or relative)
        const fragment = ref.includes("#") ? ref.split("#")[1] : null;
        const targetFile = resolveLocal(ref, file);

        if (!existsSync(targetFile)) {
            errors.push(`${rel} → ${ref} (file not found)`);
            continue;
        }

        // If there's a fragment, verify the anchor exists in the target
        if (fragment && targetFile.endsWith(".html")) {
            const ids = getIds(targetFile);
            if (!ids.has(fragment)) {
                errors.push(`${rel} → ${ref} (anchor #${fragment} not found)`);
            }
        }
    }
}

if (errors.length) {
    console.error(`\n  Broken links (${errors.length}):\n`);
    for (const e of errors) console.error(`    ${e}`);
    console.error();
    process.exit(1);
} else {
    console.log("All internal links OK");
}
