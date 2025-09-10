#!/bin/bash
# Script to check for hardcoded credentials in the codebase

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored status messages
print_status() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Check if grep is installed
if ! command -v grep &> /dev/null; then
  print_error "grep could not be found. Please install it."
  exit 1
fi

# Set the repository path
REPO_PATH=${1:-$(pwd)}

print_status "Scanning repository at: $REPO_PATH"

# Create a temporary file to store results
TEMP_FILE=$(mktemp)

# Define patterns to search for
PATTERNS=(
  "password"
  "passwd"
  "pwd"
  "secret"
  "token"
  "api[_-]?key"
  "auth[_-]?key"
  "credentials"
  "jdbc"
  "ssh[_-]?key"
  "private[_-]?key"
  "BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY"
)

# Files and directories to exclude
EXCLUDES=(
  "--exclude-dir=node_modules"
  "--exclude-dir=venv"
  "--exclude-dir=.git"
  "--exclude-dir=__pycache__"
  "--exclude=*.min.js"
  "--exclude=*.min.css"
  "--exclude=package-lock.json"
  "--exclude=yarn.lock"
)

# Scan for each pattern
print_status "Scanning for potential hardcoded credentials..."
for pattern in "${PATTERNS[@]}"; do
  print_status "Searching for pattern: $pattern"
  grep -r -i -n --include="*.{js,jsx,ts,tsx,py,sh,yml,yaml,json,md,html,css}" "${EXCLUDES[@]}" "$pattern" "$REPO_PATH" | grep -v "check_credentials.sh" >> "$TEMP_FILE"
done

# Check for IP addresses
print_status "Scanning for hardcoded IP addresses..."
grep -r -i -n --include="*.{js,jsx,ts,tsx,py,sh,yml,yaml,json,md,html,css}" "${EXCLUDES[@]}" -E '([0-9]{1,3}\.){3}[0-9]{1,3}' "$REPO_PATH" | grep -v "check_credentials.sh" | grep -v "127.0.0.1" | grep -v "0.0.0.0" | grep -v "255.255.255.255" >> "$TEMP_FILE"

# Check for URLs with potential credentials
print_status "Scanning for URLs with potential credentials..."
grep -r -i -n --include="*.{js,jsx,ts,tsx,py,sh,yml,yaml,json,md,html,css}" "${EXCLUDES[@]}" -E '(https?|ftp)://[^:]+:[^@]+@[^/]+' "$REPO_PATH" | grep -v "check_credentials.sh" >> "$TEMP_FILE"

# Count the number of potential issues
ISSUE_COUNT=$(wc -l < "$TEMP_FILE")

if [ "$ISSUE_COUNT" -eq 0 ]; then
  print_status "No potential hardcoded credentials found!"
else
  print_warning "Found $ISSUE_COUNT potential hardcoded credentials:"
  cat "$TEMP_FILE"
  
  # Save results to a file
  RESULTS_FILE="credential_scan_results_$(date +%Y%m%d_%H%M%S).txt"
  cp "$TEMP_FILE" "$RESULTS_FILE"
  print_warning "Results saved to: $RESULTS_FILE"
fi

# Clean up
rm "$TEMP_FILE"

print_status "Scan complete!"

if [ "$ISSUE_COUNT" -gt 0 ]; then
  print_warning "Please review the findings and remove any hardcoded credentials."
  print_warning "Replace them with environment variables or secure secrets management."
  exit 1
fi

exit 0
