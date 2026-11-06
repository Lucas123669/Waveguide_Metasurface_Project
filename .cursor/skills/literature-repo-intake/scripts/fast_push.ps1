<#
.SYNOPSIS
    Push a branch with a fast transport fallback, then verify the remote SHA.

.DESCRIPTION
    Direct SSH to a git host can crawl (a 164-object fetch has been observed
    stalling at ~10 KiB/s for over 10 minutes), while HTTPS through the host's
    configured http.proxy completes the same transfer in seconds. This script
    tries HTTPS first with low-speed abort guards, falls back to SSH with
    connect/keepalive guards, and finally proves the push landed by comparing
    the remote SHA with the local SHA.

    Nothing is force-pushed. If the push is rejected because another writer got
    there first, the script says so and exits non-zero: fetch, rebase your own
    commits, and run it again.

    Progress lines from git go to stderr. PowerShell would turn those into
    terminating errors under $ErrorActionPreference = 'Stop', so every git call
    is routed through Invoke-Git, which captures stderr via a temp file.

.PARAMETER Repo
    Repository path. Default: current directory.

.PARAMETER Branch
    Branch to push. Default: main.

.PARAMETER Remote
    Remote name used to discover URLs. Default: origin.

.PARAMETER HttpsUrl
    Explicit HTTPS URL. Derived from the remote when it is an SSH URL.

.PARAMETER SshUrl
    Explicit SSH URL. Derived from the remote when it is an HTTPS URL.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File fast_push.ps1 -Repo E:\repo -Branch main
#>
[CmdletBinding()]
param(
    [string]$Repo = '.',
    [string]$Branch = 'main',
    [string]$Remote = 'origin',
    [string]$HttpsUrl = '',
    [string]$SshUrl = '',
    [int]$LowSpeedLimit = 1000,
    [int]$LowSpeedTime = 60,
    [int]$SshTimeout = 20
)

$ErrorActionPreference = 'Stop'
$env:GIT_TERMINAL_PROMPT = '0'

function Invoke-Git {
    param([string[]]$GitArgs)

    # git writes progress/hints to stderr. Under $ErrorActionPreference = 'Stop'
    # an un-redirected stderr line terminates the script, and redirecting 2> to a
    # file still lets PowerShell format it as an error record. Merging with 2>&1
    # inside a script block while EAP is 'Continue' captures every line as data
    # and prints nothing to the host.
    $oldEap = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $all = & { & git @GitArgs } 2>&1
        $code = $LASTEXITCODE
    }
    finally {
        $sw.Stop()
        $ErrorActionPreference = $oldEap
    }

    $parts = foreach ($item in $all) {
        if ($item -is [System.Management.Automation.ErrorRecord]) {
            $item.Exception.Message
        }
        else {
            "$item"
        }
    }
    $text = (@($parts) | Where-Object { $_ -and ("$_").Trim() }) -join "`n"

    [pscustomobject]@{
        Code    = $code
        Output  = $text.Trim()
        Seconds = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    }
}

function Get-GitLine {
    param([string[]]$GitArgs, [string]$Default = '')
    $r = Invoke-Git $GitArgs
    if ($r.Code -ne 0 -or -not $r.Output) { return $Default }
    return (($r.Output -split "`n")[0]).Trim()
}

function ConvertTo-HttpsUrl {
    param([string]$Url)
    if ($Url -match '^git@([^:]+):(.+)$') { return 'https://' + $Matches[1] + '/' + $Matches[2] }
    if ($Url -match '^ssh://git@([^/]+)/(.+)$') { return 'https://' + $Matches[1] + '/' + $Matches[2] }
    return $Url
}

function ConvertTo-SshUrl {
    param([string]$Url)
    if ($Url -match '^https?://([^/]+)/(.+)$') { return 'git@' + $Matches[1] + ':' + $Matches[2] }
    return $Url
}

# ---------------------------------------------------------------- preflight ---
$Repo = (Resolve-Path -LiteralPath $Repo).Path
if (-not (Test-Path -LiteralPath (Join-Path $Repo '.git'))) {
    Write-Host "[FAIL] not a git repository: $Repo" -ForegroundColor Red
    exit 1
}

$originUrl = Get-GitLine @('-C', $Repo, 'remote', 'get-url', $Remote)
if (-not $originUrl) {
    Write-Host "[FAIL] remote '$Remote' has no URL" -ForegroundColor Red
    exit 1
}

if (-not $HttpsUrl) { $HttpsUrl = ConvertTo-HttpsUrl $originUrl }
if (-not $SshUrl) { $SshUrl = ConvertTo-SshUrl $originUrl }

$localSha = Get-GitLine @('-C', $Repo, 'rev-parse', 'HEAD')
$branchSha = Get-GitLine @('-C', $Repo, 'rev-parse', "refs/heads/$Branch")
if (-not $branchSha) {
    Write-Host "[FAIL] no local branch '$Branch'" -ForegroundColor Red
    exit 1
}

Write-Host "repo    = $Repo"
Write-Host "branch  = $Branch  ($branchSha)"
Write-Host "https   = $HttpsUrl"
Write-Host "ssh     = $SshUrl"
Write-Host "head    = $localSha"

# -------------------------------------------------------------------- push ---
$refspec = "$Branch`:$Branch"
$pushed = $false
$pushedVia = ''

if ($HttpsUrl -match '^https?://') {
    for ($i = 1; $i -le 2 -and -not $pushed; $i++) {
        Write-Host ""
        Write-Host "== HTTPS push (attempt $i) ==" -ForegroundColor Cyan
        $r = Invoke-Git @(
            '-C', $Repo,
            '-c', "http.lowSpeedLimit=$LowSpeedLimit",
            '-c', "http.lowSpeedTime=$LowSpeedTime",
            'push', $HttpsUrl, $refspec
        )
        if ($r.Output) { Write-Host $r.Output }
        if ($r.Code -eq 0) {
            $pushed = $true
            $pushedVia = 'https'
            Write-Host "[ok] pushed over HTTPS in $($r.Seconds)s" -ForegroundColor Green
        }
        elseif ($r.Output -match 'SSL|Unable to access|Could not resolve|timed out|Operation too slow|Connection') {
            Write-Host "[warn] transport problem; next attempt" -ForegroundColor Yellow
        }
        else {
            Write-Host "[FAIL] push rejected (not a transport problem)." -ForegroundColor Red
            Write-Host "       Fetch, rebase only your own commits, then re-run." -ForegroundColor Yellow
            Write-Host ""
            Write-Host "RESULT: PUSH REJECTED"
            exit 1
        }
    }
}

if (-not $pushed) {
    Write-Host ""
    Write-Host "== SSH push (fallback) ==" -ForegroundColor Cyan
    $sshCommand = "ssh -o ConnectTimeout=$SshTimeout -o ServerAliveInterval=15 -o BatchMode=yes"
    $r = Invoke-Git @('-C', $Repo, '-c', "core.sshCommand=$sshCommand", 'push', $SshUrl, $refspec)
    if ($r.Output) { Write-Host $r.Output }
    if ($r.Code -eq 0) {
        $pushed = $true
        $pushedVia = 'ssh'
        Write-Host "[ok] pushed over SSH in $($r.Seconds)s" -ForegroundColor Green
    }
}

if (-not $pushed) {
    Write-Host ""
    Write-Host "RESULT: PUSH FAILED" -ForegroundColor Red
    Write-Host "If the remote moved on: git fetch, rebase only your own commits, then re-run." -ForegroundColor Yellow
    exit 1
}

# ------------------------------------------------------------------ verify ---
Write-Host ""
Write-Host "== verify remote SHA ==" -ForegroundColor Cyan
$remoteSha = ''
foreach ($url in @($HttpsUrl, $SshUrl)) {
    if (-not $url) { continue }
    $sha = Get-GitLine @('-C', $Repo, 'ls-remote', $url, "refs/heads/$Branch")
    if ($sha) {
        $remoteSha = ($sha -split '\s+')[0]
        break
    }
}

Write-Host "local  = $localSha"
Write-Host "remote = $remoteSha"

if ($remoteSha -and $remoteSha -eq $localSha) {
    $null = Invoke-Git @('-C', $Repo, 'update-ref', "refs/remotes/$Remote/$Branch", $remoteSha)
    $dirty = (Invoke-Git @('-C', $Repo, 'status', '--short')).Output
    $dirtyCount = if ($dirty) { ($dirty -split "`n").Count } else { 0 }
    Write-Host "uncommitted files = $dirtyCount"
    Write-Host "RESULT: REMOTE SHA MATCHES LOCAL (via $pushedVia)" -ForegroundColor Green
    exit 0
}

Write-Host "RESULT: REMOTE SHA MISMATCH" -ForegroundColor Red
exit 1
