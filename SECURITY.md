# Security Best Practices

This document outlines security best practices for this project, especially regarding API keys and secrets.

## API Keys and Secrets

1. **Never commit API keys or secrets to version control**
   - The `.env` file is included in `.gitignore` to prevent accidental exposure
   - Use `.env.example` as a template, but never put real credentials in it

2. **Use environment variables for deployment**
   - In production, use environment variables or a secure secrets management service
   - Different cloud providers have different ways to handle secrets securely

## Setting Up Git Pre-Commit Hook

To prevent accidentally committing secrets, set up a pre-commit hook:

### On Windows:

1. Create a `.git/hooks/pre-commit` file (no extension) with the following PowerShell script:

```powershell
#!/usr/bin/env powershell
Write-Host "Running pre-commit checks..."

# Check for API keys or secrets
Write-Host "Checking for API keys..."

# Patterns to search for
$patterns = @(
  "sk-[a-zA-Z0-9]{32,}",  # OpenAI API key pattern
  "OPENAI_API_KEY=(?!your_openai_api_key_here)[a-zA-Z0-9_-]+",  # API key in .env files
  "api[_-]?key[\"':= ][a-zA-Z0-9_-]+",  # Generic API key pattern
  "secret[\"':= ][a-zA-Z0-9_-]+",  # Generic secret pattern
  "password[\"':= ][a-zA-Z0-9_-]+"  # Password pattern
)

# Files to ignore
$ignoreFiles = @(
  ".git",
  ".env",
  "venv",
  "node_modules",
  ".gitignore"
)

$foundSecrets = $false

foreach ($pattern in $patterns) {
  foreach ($file in (Get-ChildItem -Recurse -File | Where-Object { $ignoreFiles -notcontains $_.Directory.Name })) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match $pattern) {
      Write-Host "Potential API key or secret found in $($file.FullName)" -ForegroundColor Red
      $foundSecrets = $true
    }
  }
}

# Check if .env file is being committed
$envFiles = (git diff --cached --name-only) -match "\.env$"
if ($envFiles) {
  Write-Host "Warning: You are trying to commit .env file which may contain secrets!" -ForegroundColor Red
  Write-Host "Files: $envFiles"
  $foundSecrets = $true
}

if ($foundSecrets) {
  Write-Host "Error: Potential secrets found in commit. Please remove them before committing." -ForegroundColor Red
  Write-Host "You can run 'git diff --cached' to see what you're about to commit."
  exit 1
} else {
  Write-Host "No API keys or secrets found in commit." -ForegroundColor Green
}

Write-Host "All checks passed!" -ForegroundColor Green
exit 0
```

2. Make the script executable (if needed, may not be necessary on Windows)

### On Unix/Linux/macOS:

1. Make the `pre-commit.sh` script executable:
   ```bash
   chmod +x pre-commit.sh
   ```

2. Create a symbolic link to the script in the `.git/hooks` directory:
   ```bash
   ln -sf ../../pre-commit.sh .git/hooks/pre-commit
   ```

## Regular Security Checks

Run regular security checks on your codebase:

1. Check for exposed API keys or credentials
2. Keep dependencies updated to avoid security vulnerabilities
3. Perform code reviews with a security mindset

## Reporting Security Issues

If you discover a security vulnerability, please send an email to [YOUR_EMAIL]. All security vulnerabilities will be promptly addressed. 