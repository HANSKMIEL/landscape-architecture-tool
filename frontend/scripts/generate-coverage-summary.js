#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read coverage summary
const coveragePath = path.join(__dirname, '../coverage/coverage-summary.json');

if (!fs.existsSync(coveragePath)) {
  console.error('Coverage summary not found.');
  process.exit(1);
}

const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
const { lines, functions, branches, statements } = coverage.total;

// Generate markdown summary
const summary = `
## 📊 Frontend Test Coverage Report

| Metric | Coverage | Status |
|--------|----------|--------|
| **Lines** | ${lines.pct.toFixed(1)}% | ${lines.pct >= 85 ? '✅' : '❌'} |
| **Functions** | ${functions.pct.toFixed(1)}% | ${functions.pct >= 85 ? '✅' : '❌'} |
| **Branches** | ${branches.pct.toFixed(1)}% | ${branches.pct >= 80 ? '✅' : '❌'} |
| **Statements** | ${statements.pct.toFixed(1)}% | ${statements.pct >= 85 ? '✅' : '❌'} |

### Coverage Details
- **Lines**: ${lines.covered}/${lines.total} covered
- **Functions**: ${functions.covered}/${functions.total} covered  
- **Branches**: ${branches.covered}/${branches.total} covered
- **Statements**: ${statements.covered}/${statements.total} covered

${lines.pct >= 85 && functions.pct >= 85 && branches.pct >= 80 && statements.pct >= 85 
  ? '🎉 All coverage thresholds met!' 
  : '⚠️ Some coverage thresholds not met. Please add more tests.'}

---
*Coverage report generated on ${new Date().toISOString()}*
`;

// Write summary to file
fs.writeFileSync(
  path.join(__dirname, '../coverage/coverage-summary.md'),
  summary
);

console.log('Coverage summary generated successfully!');