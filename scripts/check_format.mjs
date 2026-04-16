import { readFileSync } from "node:fs";
import { execSync } from "node:child_process";

const targets = execSync(
  "rg --files app.js index.html styles.css js tests docs README.md .github/workflows scripts/check_format.mjs package.json",
  { encoding: "utf8" }
)
  .split("\n")
  .filter(Boolean)
  .filter(file => /\.(js|css|html|md|yml|yaml|json)$/.test(file));

const issues = [];
for (const file of targets) {
  const content = readFileSync(file, "utf8");
  if (/\t/.test(content)) issues.push(`${file}: contains tab characters`);
  if (/ +$/m.test(content)) issues.push(`${file}: contains trailing whitespace`);
  if (content.length > 0 && !content.endsWith("\n")) issues.push(`${file}: missing trailing newline`);
}

if (issues.length) {
  console.error("Formatting checks failed:\n" + issues.join("\n"));
  process.exit(1);
}

console.log(`Formatting checks passed for ${targets.length} files.`);
