# check_docs.ps1 - repository documentation health check
#
# Usage:
#   pwsh -File scripts/maintenance/check_docs.ps1
#   pwsh -File scripts/maintenance/check_docs.ps1 -Quiet
#
# Checks (see docs/guides/AI_文档更新与推送工作流.md):
#   1. JSON validity of project_config.json, configs/**/*.json and the
#      evidence manifests under experiments/.
#   2. Relative markdown link audit across the whole repository
#      (http/https/mailto/anchor-only links are skipped).
#   3. Structure counters for the main briefing report (pages, evidence
#      entries, open checklist items, anticipated questions).
#   4. Image reference audit for docs/**/figures/* (orphan detection).
#   5. Terminology residue scan (e.g. the mistranslation of "metalens").
#   6. Git state summary (branch, HEAD, number of dirty files).
#
# Exit code: 0 when no blocking failure (bad JSON or broken links), 1 otherwise.
#
# NOTE: this source file is intentionally ASCII-only. Chinese patterns are
# written as .NET regex \uXXXX escapes so the script survives any encoding
# or PowerShell version.

[CmdletBinding()]
param(
    [string]$Repo = '',
    [string]$Git = '',
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'
$blocking = 0

# Resolve the repository root here (not in the param default): $PSScriptRoot is
# not reliably populated while parameter defaults are evaluated.
if (-not $Repo) {
    if ($PSScriptRoot) { $Repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
    else { $Repo = (Get-Location).Path }
}
$Repo = (Resolve-Path -LiteralPath $Repo).Path

# Git is optional for a full checkout, but lets sparse/partial checkouts verify
# links against the committed tree instead of reporting unmaterialized files as
# broken. An explicit path is useful in managed environments where Git is not
# inherited by a child PowerShell process.
$gitExe = $null
if ($Git -and (Test-Path -LiteralPath $Git)) {
    $gitExe = (Resolve-Path -LiteralPath $Git).Path
}
elseif (Get-Command git -ErrorAction SilentlyContinue) {
    $gitExe = (Get-Command git).Source
}

$trackedPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
if ($gitExe) {
    try {
        & $gitExe -c "safe.directory=$Repo" -c core.quotepath=false -C $Repo ls-tree -r --name-only HEAD 2>$null |
            ForEach-Object { [void]$trackedPaths.Add($_.Replace('\', '/')) }
    }
    catch {
        Write-Host '   [warn] unable to read the Git tree; sparse-checkout links may be reported as missing' -ForegroundColor Yellow
    }
}

function Write-Head([string]$text) {
    if (-not $Quiet) { Write-Host ""; Write-Host "== $text" -ForegroundColor Cyan }
}
function Write-Item([string]$text) {
    if (-not $Quiet) { Write-Host "   $text" }
}
function Write-Warn2([string]$text) {
    Write-Host "   [warn] $text" -ForegroundColor Yellow
}
function Write-Fail([string]$text) {
    Write-Host "   [FAIL] $text" -ForegroundColor Red
    $script:blocking++
}

if (-not (Test-Path (Join-Path $Repo 'project_config.json'))) {
    Write-Fail "repository root not found: $Repo"
    exit 1
}
Write-Host "repo = $Repo"

# ---------------------------------------------------------------- 1. JSON ---
Write-Head '1) JSON validity'
$jsonFiles = @()
$jsonFiles += Get-ChildItem $Repo -Filter '*.json' -File -ErrorAction SilentlyContinue
$jsonFiles += Get-ChildItem (Join-Path $Repo 'configs') -Filter '*.json' -File -Recurse -ErrorAction SilentlyContinue
$jsonFiles += Get-ChildItem (Join-Path $Repo 'experiments') -Filter '*.json' -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @('run_manifest.json', 'simulation_result.json', 'resolved_config.json') }
$jsonFiles = $jsonFiles | Sort-Object FullName -Unique

$jsonOk = 0
foreach ($f in $jsonFiles) {
    try {
        $null = Get-Content $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $jsonOk++
    }
    catch {
        Write-Fail "invalid JSON: $($f.FullName.Replace($Repo + '\', ''))"
    }
}
Write-Item "json files checked = $($jsonFiles.Count), valid = $jsonOk"

# --------------------------------------------------------------- 2. links ---
Write-Head '2) Relative markdown link audit'
$mdFiles = Get-ChildItem $Repo -Filter '*.md' -File -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\\.git\\' }

$checked = 0
$broken = @()
foreach ($f in $mdFiles) {
    $text = Get-Content $f.FullName -Raw -Encoding UTF8
    if (-not $text) { continue }
    foreach ($m in [regex]::Matches($text, '\]\(([^)\s]+)\)')) {
        $target = $m.Groups[1].Value
        if ($target -match '^(https?:|mailto:|#)') { continue }
        $target = $target.Split('#')[0].Trim('<', '>')
        if ($target -eq '') { continue }
        $checked++
        $decoded = [uri]::UnescapeDataString($target)
        $path = if ($decoded -match '^[A-Za-z]:') { $decoded } else { Join-Path $f.DirectoryName $decoded }
        $exists = Test-Path -LiteralPath $path
        if (-not $exists -and $trackedPaths.Count -gt 0) {
            try {
                $full = [System.IO.Path]::GetFullPath($path)
                if ($full.StartsWith($Repo, [System.StringComparison]::OrdinalIgnoreCase)) {
                    $rel = $full.Substring($Repo.Length).TrimStart('\', '/').Replace('\', '/')
                    $exists = $trackedPaths.Contains($rel)
                    if (-not $exists) {
                        $prefix = $rel.TrimEnd('/') + '/'
                        foreach ($item in $trackedPaths) {
                            if ($item.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                                $exists = $true
                                break
                            }
                        }
                    }
                }
            }
            catch {}
        }
        if (-not $exists) {
            $broken += "$($f.FullName.Replace($Repo + '\', '')) -> $target"
        }
    }
}
Write-Item "markdown files = $($mdFiles.Count), links checked = $checked, broken = $($broken.Count)"
if ($broken.Count -gt 0) {
    foreach ($b in ($broken | Select-Object -First 20)) { Write-Fail "broken link: $b" }
    if ($broken.Count -gt 20) { Write-Fail "... and $($broken.Count - 20) more" }
}

# ----------------------------------------------------------- 3. structure ---
Write-Head '3) Briefing report structure'
# Note: the briefing filename contains Chinese characters; locate it by its
# ASCII prefix instead of hardcoding non-ASCII text in this ASCII-only script.
$briefing = Get-ChildItem (Join-Path $Repo 'docs/reports/fabrication') -Filter '2026-09-09_1550nm*.md' -File -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
if ($briefing -and (Test-Path -LiteralPath $briefing)) {
    $lines = Get-Content -LiteralPath $briefing -Encoding UTF8
    $pages = ($lines | Select-String -Pattern '^### [\u7B2C]\d+[\u9875]').Count
    $evid = ($lines | Select-String -Pattern '^### \[E\d+').Count
    $todo = ($lines | Select-String -Pattern '^- \[ \]').Count
    $qs = ($lines | Select-String -Pattern '^### Q\d').Count
    Write-Item "lines=$($lines.Count) pages=$pages evidence=$evid open_checklist=$todo questions=$qs"
    if ($pages -lt 10) { Write-Warn2 "expected at least 10 briefing pages" }
    if ($evid -lt 18) { Write-Warn2 "expected at least 18 evidence entries" }
}
else {
    Write-Warn2 "briefing report not found (renamed?)"
}

# -------------------------------------------------------------- 4. images ---
Write-Head '4) Image reference audit'
$imgPaths = @()
if ($trackedPaths.Count -gt 0) {
    $imgPaths = @($trackedPaths | Where-Object { $_ -match '^docs/.+\.png$' })
}
else {
    $imgPaths = @(Get-ChildItem (Join-Path $Repo 'docs') -Filter '*.png' -File -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object { $_.FullName.Substring($Repo.Length).TrimStart('\', '/').Replace('\', '/') })
}
if ($imgPaths.Count -gt 0) {
    $refs = ($mdFiles | ForEach-Object { Get-Content $_.FullName -Raw -Encoding UTF8 }) -join "`n"
    $orphans = @()
    foreach ($imgPath in $imgPaths) {
        $imgName = Split-Path -Leaf $imgPath
        if ($refs -notmatch [regex]::Escape($imgName)) {
            $orphans += $imgPath
        }
    }
    Write-Item "images = $($imgPaths.Count), orphans = $($orphans.Count)"
    foreach ($o in $orphans) { Write-Warn2 "never referenced: $o" }
}
else {
    Write-Item "no images under docs/"
}

# --------------------------------------------------------- 5. terminology ---
Write-Head '5) Terminology residue scan'
$terms = @(
    @{ name = 'metalens mistranslation (should be chao tou jing)'; pattern = '\u91D1\u5C5E\u900F\u955C' }
)
foreach ($t in $terms) {
    $hits = @()
    foreach ($f in $mdFiles) {
        $text = Get-Content $f.FullName -Raw -Encoding UTF8
        $n = ([regex]::Matches($text, $t.pattern)).Count
        if ($n -gt 0) { $hits += "$($f.FullName.Replace($Repo + '\', '')) x$n" }
    }
    if ($hits.Count -eq 0) { Write-Item "$($t.name): clean" }
    else {
        Write-Item "$($t.name): $($hits.Count) file(s) contain it (explanatory text is allowed - verify)"
        foreach ($h in $hits) { Write-Warn2 $h }
    }
}

# ---------------------------------------------------------------- 6. git ----
Write-Head '6) Git state'
try {
    if (-not $gitExe) { throw 'git not available' }
    $branch = (& $gitExe -c "safe.directory=$Repo" -C $Repo rev-parse --abbrev-ref HEAD 2>$null)
    $head = (& $gitExe -c "safe.directory=$Repo" -C $Repo log --oneline -1 2>$null)
    $dirty = (& $gitExe -c "safe.directory=$Repo" -C $Repo status --short 2>$null | Measure-Object).Count
    Write-Item "branch=$branch"
    Write-Item "head=$head"
    Write-Item "uncommitted files=$dirty"
}
catch {
    Write-Warn2 'git not available'
}

# -------------------------------------------------------------- summary ----
Write-Host ''
if ($blocking -eq 0) {
    Write-Host 'RESULT: OK (no bad JSON, no broken links)' -ForegroundColor Green
    exit 0
}
else {
    Write-Host "RESULT: $blocking blocking problem(s) - fix before commit" -ForegroundColor Red
    exit 1
}
