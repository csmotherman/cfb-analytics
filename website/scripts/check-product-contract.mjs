import fs from "node:fs";
import path from "node:path";

const websiteRoot = process.cwd();
const sourceRoots = ["app", "components", "lib"];
const sourceFiles = [];
const visit = (directory) => {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) visit(absolute);
    else if (/\.(ts|tsx)$/.test(entry.name)) sourceFiles.push(absolute);
  }
};
for (const sourceRoot of sourceRoots) visit(path.join(websiteRoot, sourceRoot));

const failures = [];
for (const file of sourceFiles) {
  const relativePath = path.relative(websiteRoot, file);
  const source = fs.readFileSync(file, "utf8");
  if (/CFB Analytics Pilot|College Football Analytics Pilot|prediction-models/.test(source)) failures.push(`${relativePath}: forbidden legacy public brand`);
  if (/const\s+gradeScore|GRADE_SCORE/.test(source)) failures.push(`${relativePath}: frontend projection/rating calculation detected`);
  if (relativePath.startsWith("app/") && /return\s+<main\b/.test(source)) failures.push(`${relativePath}: nested main landmark inside root layout`);
  if (/aria-disabled=\{[^}]+\}[^>]+href=/.test(source)) failures.push(`${relativePath}: disabled link remains navigable`);
  if (/^(app|components)\//.test(relativePath) && /Frozen forecast|immutable Prediction|publication pending|historical product contract|evidence contract|national engine|source facts|downstream Michigan analytics|no-vig|two-way overround/i.test(source)) {
    failures.push(`${relativePath}: internal analytics language exposed in public copy`);
  }
}

if (failures.length) {
  process.stderr.write(`Product-contract verification failed:\n${failures.map((failure) => `- ${failure}`).join("\n")}\n`);
  process.exitCode = 1;
} else {
  process.stdout.write(`Verified product invariants across ${sourceFiles.length} frontend source files.\n`);
}
