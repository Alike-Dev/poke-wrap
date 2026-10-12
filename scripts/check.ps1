#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run all quality gates for PokeWrap.

.DESCRIPTION
    Detects required tools, optionally installs them, then runs
    ruff format, ruff check, mypy and pytest in sequence. Stops at
    the first failure.

.PARAMETER Install
    Install any missing required tool before running the checks.
    Uses winget for git and the official installers for uv and cz.

.PARAMETER Help
    Show this help and exit.
#>

param(
    [switch]$Install,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

function Write-Step { param($m) Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok   { param($m) Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err  { param($m) Write-Host "[ERROR] $m" -ForegroundColor Red }
function Write-Hint { param($m) Write-Host "  Hint: $m" -ForegroundColor DarkGray }

if ($Help) {
    Get-Help $PSCommandPath -Detailed
    exit 0
}

# --- Tool detection -------------------------------------------------------

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

$requiredTools = @(
    @{
        Name    = "uv"
        Command = "uv"
        Purpose = "Runs Python, resolves dependencies and invokes tools"
        Install = {
            Write-Host "  Installing uv via the official installer..." -ForegroundColor DarkGray
            Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        }
    },
    @{
        Name    = "git"
        Command = "git"
        Purpose = "Version control; required for staging and committing"
        Install = {
            if (-not (Test-Command "winget")) {
                throw "winget is not available. Install git manually: https://git-scm.com/download/win"
            }
            Write-Host "  Installing git via winget..." -ForegroundColor DarkGray
            winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
        }
    },
    @{
        Name    = "cz"
        Command = "cz"
        Purpose = "Commitizen; used for conventional commits and version bumps"
        Install = {
            Write-Host "  Installing commitizen as a uv tool..." -ForegroundColor DarkGray
            uv tool install commitizen
        }
    }
)

Write-Step "Checking required tools"

$missing = @()
foreach ($tool in $requiredTools) {
    if (Test-Command $tool.Command) {
        Write-Ok "$($tool.Name) is available"
    } else {
        Write-Warn "$($tool.Name) is missing - $($tool.Purpose)"
        $missing += $tool
    }
}

if ($missing.Count -gt 0) {
    if (-not $Install) {
        Write-Host ""
        Write-Err "Missing tools: $($missing.Name -join ', ')"
        Write-Hint "Re-run with -Install to install them automatically."
        Write-Hint "Or install them manually and re-run."
        exit 1
    }

    Write-Step "Installing missing tools"
    foreach ($tool in $missing) {
        try {
            & $tool.Install
            if ($LASTEXITCODE -ne 0) {
                throw "Installer exited with code $LASTEXITCODE"
            }
            Write-Ok "$($tool.Name) installed"
        } catch {
            Write-Err "Failed to install $($tool.Name): $_"
            Write-Hint "Install it manually and re-run."
            exit 1
        }
    }

    Write-Host ""
    Write-Warn "Some tools may need a new shell to be on PATH."
    Write-Hint "If the next step fails, close and reopen PowerShell, then retry."
}

# --- Quality gates --------------------------------------------------------

function Invoke-Gate {
    param(
        [string]$Name,
        [scriptblock]$Command
    )
    Write-Step $Name
    & $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Err "$Name failed (exit code $LASTEXITCODE)"
        exit $LASTEXITCODE
    }
}

Invoke-Gate "Formatting with ruff"  { uv run ruff format . }
Invoke-Gate "Linting with ruff"     { uv run ruff check . }
Invoke-Gate "Type-checking (mypy)"  { uv run mypy src tests }
Invoke-Gate "Running tests"         { uv run pytest }

Write-Host ""
Write-Ok "All checks passed"