#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Install PokeWrap's helper scripts globally so they can be invoked
    from any project on your machine.

.DESCRIPTION
    Copies check.ps1 and commit.ps1 to a well-known user folder and
    adds that folder to the user's PATH. After running this once and
    restarting your shell, you can call:

        pw-check            # run quality gates in the current project
        pw-commit           # commit + push
        pw-commit -Release  # commit + bump + publish

.PARAMETER TargetDir
    Destination folder. Defaults to $env:USERPROFILE\.local\bin,
    which is the same folder used by uv, cargo and other modern tools.

.PARAMETER Uninstall
    Remove the globally installed scripts and the PATH entry.
#>

param(
    [string]$TargetDir = "$env:USERPROFILE\.local\bin",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

function Write-Step { param($m) Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok   { param($m) Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Err  { param($m) Write-Host "[ERROR] $m" -ForegroundColor Red }

# --- Uninstall path -------------------------------------------------------

if ($Uninstall) {
    Write-Step "Uninstalling PokeWrap helper scripts"

    foreach ($name in @("pw-check.ps1", "pw-commit.ps1")) {
        $path = Join-Path $TargetDir $name
        if (Test-Path $path) {
            Remove-Item $path -Force
            Write-Ok "Removed $path"
        }
    }

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = $userPath -split ";" | Where-Object { $_ -and $_ -ne $TargetDir }
    [Environment]::SetEnvironmentVariable("Path", ($parts -join ";"), "User")
    Write-Ok "Removed $TargetDir from user PATH"

    Write-Host ""
    Write-Host "Restart your shell for the change to take effect." -ForegroundColor Yellow
    exit 0
}

# --- Install --------------------------------------------------------------

Write-Step "Installing PokeWrap helper scripts"

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    Write-Ok "Created $TargetDir"
}

$sourceDir = $PSScriptRoot
$mapping = @{
    "check.ps1"  = "pw-check.ps1"
    "commit.ps1" = "pw-commit.ps1"
}

foreach ($src in $mapping.Keys) {
    $srcPath = Join-Path $sourceDir $src
    if (-not (Test-Path $srcPath)) {
        Write-Err "Source script not found: $srcPath"
        exit 1
    }
    $dstPath = Join-Path $TargetDir $mapping[$src]
    Copy-Item $srcPath $dstPath -Force
    Write-Ok "Installed $($mapping[$src])"
}

# --- Update PATH ----------------------------------------------------------

Write-Step "Updating user PATH"

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$alreadyInPath = $userPath -split ";" -contains $TargetDir

if ($alreadyInPath) {
    Write-Ok "$TargetDir is already in user PATH"
} else {
    $newPath = if ($userPath) { "$userPath;$TargetDir" } else { $TargetDir }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Ok "Added $TargetDir to user PATH"
}

# Update the current session too, so the user can use it right away
if ($env:Path -notlike "*$TargetDir*") {
    $env:Path = "$env:Path;$TargetDir"
}

# --- Done -----------------------------------------------------------------

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " Installation complete" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands (after restarting your shell):" -ForegroundColor Cyan
Write-Host "  pw-check              Run quality gates" -ForegroundColor White
Write-Host "  pw-check -Install     Install missing tools, then run gates" -ForegroundColor White
Write-Host "  pw-commit             Commit and push" -ForegroundColor White
Write-Host "  pw-commit -NoPush     Commit and not push" -ForegroundColor White
Write-Host "  pw-commit -Release    Commit, bump, push and publish" -ForegroundColor White
Write-Host "  pw-commit -Help       Show full help" -ForegroundColor White
Write-Host ""
Write-Host "  Both commands must be run from a project root that" -ForegroundColor DarkGray
Write-Host "  contains pyproject.toml and is inside a git repository." -ForegroundColor DarkGray
Write-Host ""
Write-Host "To uninstall: .\install-global.ps1 -Uninstall" -ForegroundColor DarkGray