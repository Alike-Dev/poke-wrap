#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Pre-commit workflow for PokeWrap projects.

.DESCRIPTION
    Runs the quality gates, stages your changes with confirmation,
    creates a conventional commit and pushes to origin. With -Release,
    also bumps the version and pushes the tag, triggering a PyPI release.

.PARAMETER NoPush
    Skip pushing to origin after the commit.

.PARAMETER NoAutoAdd
    Skip 'git add -A'. Commit only what is already staged.

.PARAMETER Release
    Run 'cz bump' and push tags to publish a new version to PyPI.

.PARAMETER Install
    Install missing required tools before running.

.PARAMETER Help
    Show a descriptive help message and exit.

.NOTES
    Required tools:
        uv          Python runner and dependency manager.
                    https://docs.astral.sh/uv/
        git         Version control.
                    https://git-scm.com/download/win
        commitizen  Conventional commits and version bumps.
                    Install: uv tool install commitizen

    Missing tools can be installed automatically with -Install.

.EXAMPLE
    pw-commit
    Commit and push.

.EXAMPLE
    pw-commit -Release
    Commit, bump and publish to PyPI.

.EXAMPLE
    pw-commit -NoPush
    Commit only, no push.
#>

param(
    [switch]$NoPush,
    [switch]$NoAutoAdd,
    [switch]$Release,
    [switch]$Install,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# --- Output helpers ------------------------------------------------------
function Show-Help {
    Write-Host ""
    Write-Host "pw-commit" -ForegroundColor Cyan -NoNewline
    Write-Host "  Pre-commit workflow for PokeWrap projects"
    Write-Host ""
    Write-Host "USAGE" -ForegroundColor Yellow
    Write-Host "  pw-commit [options]"
    Write-Host ""
    Write-Host "DESCRIPTION" -ForegroundColor Yellow
    Write-Host "  Runs quality gates (format, lint, types, tests), stages"
    Write-Host "  your changes with confirmation, creates a conventional"
    Write-Host "  commit, and pushes to origin."
    Write-Host ""
    Write-Host "  With -Release, also bumps the version with commitizen and"
    Write-Host "  pushes the tag. GitHub Actions then publishes the new"
    Write-Host "  version to PyPI automatically."
    Write-Host ""
    Write-Host "OPTIONS" -ForegroundColor Yellow
    Write-Host "  -NoPush      " -NoNewline -ForegroundColor Green
    Write-Host "Do not push to origin after committing."
    Write-Host "  -NoAutoAdd   " -NoNewline -ForegroundColor Green
    Write-Host "Skip 'git add -A'. Commit only staged files."
    Write-Host "  -Release     " -NoNewline -ForegroundColor Green
    Write-Host "Run 'cz bump' and push tags to publish to PyPI."
    Write-Host "  -Install     " -NoNewline -ForegroundColor Green
    Write-Host "Install missing required tools before running."
    Write-Host "  -Help        " -NoNewline -ForegroundColor Green
    Write-Host "Show this message and exit."
    Write-Host ""
    Write-Host "REQUIRED TOOLS" -ForegroundColor Yellow
    Write-Host "  uv           " -NoNewline -ForegroundColor Green
    Write-Host "Python runner and dependency manager."
    Write-Host "               https://docs.astral.sh/uv/"
    Write-Host "  git          " -NoNewline -ForegroundColor Green
    Write-Host "Version control, required for staging and committing."
    Write-Host "               https://git-scm.com/download/win"
    Write-Host "  commitizen   " -NoNewline -ForegroundColor Green
    Write-Host "Conventional commits and version bumps."
    Write-Host "               Install: uv tool install commitizen"
    Write-Host ""
    Write-Host "  Check with: pw-commit -Install" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "EXAMPLES" -ForegroundColor Yellow
    Write-Host "  pw-commit              " -NoNewline -ForegroundColor DarkGray
    Write-Host "Commit and push"
    Write-Host "  pw-commit -Release     " -NoNewline -ForegroundColor DarkGray
    Write-Host "Commit, bump and publish to PyPI"
    Write-Host "  pw-commit -NoPush      " -NoNewline -ForegroundColor DarkGray
    Write-Host "Commit only, no push"
    Write-Host "  pw-commit -NoAutoAdd   " -NoNewline -ForegroundColor DarkGray
    Write-Host "Commit only already-staged files"
    Write-Host "  pw-commit -Install     " -NoNewline -ForegroundColor DarkGray
    Write-Host "Install tools, then run"
    Write-Host ""
}

function Test-ProjectRoot {
    <#
    .SYNOPSIS
        Verify that the current directory looks like a PokeWrap project.
    #>
    $cwd = Get-Location

    if (-not (Test-Path "pyproject.toml")) {
        Write-Err "No pyproject.toml found in the current directory."
        Write-Host "  Current directory: $cwd" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "  This script must be run from the root of a Python project" -ForegroundColor Yellow
        Write-Host "  that uses pyproject.toml (e.g. poke-wrap)." -ForegroundColor Yellow
        Write-Hint "cd into your project root and try again."
        return $false
    }

    # Check that we are inside a git repository
    git rev-parse --is-inside-work-tree *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Err "The current directory is not inside a git repository."
        Write-Host "  Current directory: $cwd" -ForegroundColor DarkGray
        Write-Hint "Run 'git init' to create one, or cd into an existing repo."
        return $false
    }

    # Optional: warn if there is no virtual environment
    if (-not (Test-Path ".venv")) {
        Write-Warn "No .venv found in the current directory."
        Write-Hint "Run 'uv sync' first if this is a fresh clone."
    }

    return $true
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "=== $Message ===" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Err {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Hint {
    param([string]$Message)
    Write-Host "  Hint: $Message" -ForegroundColor DarkGray
}

# --- Help ----------------------------------------------------------------

if ($Help) {
    Show-Help
    exit 0
}

# --- 1. Validate the current directory -----------------------------------

if (-not (Test-ProjectRoot)) {
    exit 1
}

# --- 2. Quality gates ----------------------------------------------------

$checkScript = Join-Path $PSScriptRoot "pw-check.ps1"
if (-not (Test-Path $checkScript)) {
    # Fallback to the in-repo name when running from the source checkout
    $checkScript = Join-Path $PSScriptRoot "check.ps1"
}

if (-not (Test-Path $checkScript)) {
    Write-Err "Cannot find the check script."
    Write-Host "  Looked for: pw-check.ps1 and check.ps1" -ForegroundColor DarkGray
    Write-Host "  In folder:  $PSScriptRoot" -ForegroundColor DarkGray
    Write-Hint "Re-run '.\scripts\install-global.ps1' to refresh the global install."
    exit 1
}

$checkArgs = @{}
if ($Install) { $checkArgs["Install"] = $true }

& $checkScript @checkArgs
if ($LASTEXITCODE -ne 0) {
    Write-Err "Quality gates failed. Fix the issues above and retry."
    Write-Hint "Run 'pw-check' alone to reproduce."
    exit $LASTEXITCODE
}

# --- 3. Stage changes (with confirmation) --------------------------------

if (-not $NoAutoAdd) {
    Write-Step "Files that will be staged"

    $status = git status --porcelain
    if (-not $status) {
        Write-Warn "Working tree is clean. Nothing to stage."
        exit 0
    }

    $status -split "`n" | Where-Object { $_ -ne "" } | ForEach-Object {
        $code = $_.Substring(0, 2)
        $file = $_.Substring(3)
        $color = switch -Regex ($code.Trim()) {
            "^\?\?$" { "Yellow" }
            "^D"     { "Red"    }
            "^A"     { "Green"  }
            default  { "White"  }
        }
        Write-Host ("  {0}  {1}" -f $code, $file) -ForegroundColor $color
    }

    Write-Host ""
    Write-Host "Legend: " -NoNewline -ForegroundColor DarkGray
    Write-Host "?? untracked " -NoNewline -ForegroundColor Yellow
    Write-Host "M modified " -NoNewline -ForegroundColor White
    Write-Host "A added " -NoNewline -ForegroundColor Green
    Write-Host "D deleted" -ForegroundColor Red
    Write-Host ""

    $confirm = Read-Host "Stage these files? [y/N]"
    if ($confirm -notmatch '^[yY]') {
        Write-Warn "Aborted by user. No files were staged."
        exit 0
    }

    Write-Step "Staging all changes"
    git add -A
    if ($LASTEXITCODE -ne 0) {
        Write-Err "git add -A failed (exit $LASTEXITCODE)"
        exit $LASTEXITCODE
    }
    Write-Ok "Files staged"
}

# --- 4. Sanity check -----------------------------------------------------

$staged = git diff --cached --name-only
if (-not $staged) {
    Write-Warn "Nothing staged. Aborting."
    Write-Hint "Run without -NoAutoAdd to stage everything automatically."
    exit 0
}

# --- 5. Create the commit ------------------------------------------------

Write-Step "Creating commit with commitizen"
Write-Host "Answer the prompts below to build a conventional commit." -ForegroundColor DarkGray
uv run cz commit
if ($LASTEXITCODE -ne 0) {
    Write-Err "cz commit failed (exit $LASTEXITCODE)"
    Write-Hint "Your changes remain staged. Fix the message and retry."
    exit $LASTEXITCODE
}
Write-Ok "Commit created"

# --- 6. Release (optional) -----------------------------------------------

if ($Release) {
    Write-Step "Bumping version with commitizen"
    Write-Host "This updates pyproject.toml and CHANGELOG.md, then creates" -ForegroundColor DarkGray
    Write-Host "a bump commit and a tag." -ForegroundColor DarkGray
    uv run cz bump
    if ($LASTEXITCODE -ne 0) {
        Write-Err "cz bump failed (exit $LASTEXITCODE)"
        Write-Hint "'cz bump' fails if there are no feat/fix commits since the last tag."
        exit $LASTEXITCODE
    }
    Write-Ok "Version bumped and tagged"
}

# --- 7. Push -------------------------------------------------------------

if (-not $NoPush) {
    Write-Step "Pushing to origin"
    git push
    if ($LASTEXITCODE -ne 0) {
        Write-Err "git push failed (exit $LASTEXITCODE)"
        Write-Hint "The commit exists locally only. Check network or credentials."
        exit $LASTEXITCODE
    }
    Write-Ok "Pushed to origin"

    if ($Release) {
        Write-Step "Pushing tags"
        git push --tags
        if ($LASTEXITCODE -ne 0) {
            Write-Err "git push --tags failed (exit $LASTEXITCODE)"
            Write-Hint "The tag exists locally only. Run 'git push origin <tag>' manually."
            exit $LASTEXITCODE
        }
        Write-Ok "Tags pushed"
        Write-Host ""
        Write-Host "GitHub Actions will publish the new version to PyPI." -ForegroundColor Cyan
        Write-Host "Watch the release:" -ForegroundColor Cyan
        Write-Host "  https://github.com/Alike-Dev/poke-wrap/actions" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Ok "All done"