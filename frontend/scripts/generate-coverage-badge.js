#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read coverage summary
const coveragePath = path.join(__dirname, '../coverage/coverage-summary.json');

if (!fs.existsSync(coveragePath)) {
  console.error('Coverage summary not found. Run tests with coverage first.');
  process.exit(1);
}

const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
const totalCoverage = coverage.total;

// Generate badge data
const generateBadge = (type, percentage) => {
  let color = 'red';
  if (percentage >= 90) color = 'brightgreen';
  else if (percentage >= 80) color = 'yellow';
  else if (percentage >= 70) color = 'orange';

  return {
    schemaVersion: 1,
    label: type,
    message: `${percentage.toFixed(1)}%`,
    color: color
  };
};

// Create badges directory
const badgesDir = path.join(__dirname, '../coverage/badges');
if (!fs.existsSync(badgesDir)) {
  fs.mkdirSync(badgesDir, { recursive: true });
}

// Generate badges for each coverage type
['lines', 'functions', 'branches', 'statements'].forEach(type => {
  const badge = generateBadge(type, totalCoverage[type].pct);
  fs.writeFileSync(
    path.join(badgesDir, `${type}.json`),
    JSON.stringify(badge, null, 2)
  );
});

console.log('Coverage badges generated successfully!');
console.log(`Lines: ${totalCoverage.lines.pct.toFixed(1)}%`);
console.log(`Functions: ${totalCoverage.functions.pct.toFixed(1)}%`);
console.log(`Branches: ${totalCoverage.branches.pct.toFixed(1)}%`);
console.log(`Statements: ${totalCoverage.statements.pct.toFixed(1)}%`);