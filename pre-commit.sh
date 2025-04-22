#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo "Running pre-commit checks..."

# Check for API keys or secrets
echo "Checking for API keys..."

# Patterns to search for
PATTERNS=(
  "sk-[a-zA-Z0-9]{32,}"  # OpenAI API key pattern
  "OPENAI_API_KEY=(?!your_openai_api_key_here)[a-zA-Z0-9_-]+"  # API key in .env files
  "api[_-]?key[\"':= ][a-zA-Z0-9_-]+"  # Generic API key pattern
  "secret[\"':= ][a-zA-Z0-9_-]+"  # Generic secret pattern
  "password[\"':= ][a-zA-Z0-9_-]+"  # Password pattern
)

# Files to ignore
IGNORE_FILES=(
  ".git"
  ".env"
  "venv"
  "node_modules"
  ".gitignore"
  "pre-commit.sh"
)

# Build ignore pattern
IGNORE_PATTERN=""
for ignore in "${IGNORE_FILES[@]}"; do
  IGNORE_PATTERN="$IGNORE_PATTERN -not -path \"./$ignore/*\""
done

# Search for patterns
FOUND_SECRETS=false

for pattern in "${PATTERNS[@]}"; do
  # Use eval to properly handle the ignore pattern
  RESULTS=$(eval "grep -r -E \"$pattern\" --include=\"*.{py,js,json,yml,yaml,md,txt,html,css}\" . $IGNORE_PATTERN")
  
  if [ ! -z "$RESULTS" ]; then
    echo -e "${RED}Potential API key or secret found:${NC}"
    echo "$RESULTS"
    FOUND_SECRETS=true
  fi
done

# Check if .env file is being committed
ENV_FILES=$(git diff --cached --name-only | grep "\.env$")
if [ ! -z "$ENV_FILES" ]; then
  echo -e "${RED}Warning: You are trying to commit .env file which may contain secrets!${NC}"
  echo "Files: $ENV_FILES"
  FOUND_SECRETS=true
fi

if [ "$FOUND_SECRETS" = true ]; then
  echo -e "${RED}Error: Potential secrets found in commit. Please remove them before committing.${NC}"
  echo "You can run 'git diff --cached' to see what you're about to commit."
  exit 1
else
  echo -e "${GREEN}No API keys or secrets found in commit.${NC}"
fi

echo -e "${GREEN}All checks passed!${NC}"
exit 0 