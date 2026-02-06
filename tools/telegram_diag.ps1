param(
  [string]$BotToken,
  [string]$PublicBase = "",
  [string]$WebhookPath = "",
  [switch]$DropPending
)

function Get-TokenFromEnv {
  $t = $env:TELEGRAM_BOT_TOKEN
  if ($t -and $t.Trim().Length -gt 20) { return $t.Trim() }

  $t = [Environment]::GetEnvironmentVariable("TELEGRAM_BOT_TOKEN","User")
  if ($t -and $t.Trim().Length -gt 20) {
    $env:TELEGRAM_BOT_TOKEN = $t.Trim()
    return $t.Trim()
  }
  return ""
}

function SafeLen([string]$s){ if($s){$s.Length}else{0} }

function TgCall([string]$token, [string]$method){
  $u = "https://api.telegram.org/bot$token/$method"
  try {
    $r = Invoke-RestMethod -Uri $u -TimeoutSec 20
    return @{ ok=$true; data=$r; status=200; err="" }
  } catch {
    $status = $null
    try { $status = $_.Exception.Response.StatusCode.value__ } catch {}
    return @{ ok=$false; data=$null; status=$status; err=$($_.Exception.Message) }
  }
}

function HttpStatus([string]$url){
  try {
    $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
    return @{ ok=$true; status=$r.StatusCode; err="" }
  } catch {
    $status = $null
    try { $status = $_.Exception.Response.StatusCode.value__ } catch {}
    return @{ ok=$false; status=$status; err=$($_.Exception.Message) }
  }
}

$token = $BotToken
if (-not $token) { $token = Get-TokenFromEnv }

Write-Host ""
Write-Host "=== TELEGRAM DIAG (safe output) ==="
Write-Host ("TokenPresent=" + [bool]$token + " TokenLen=" + (SafeLen $token))

if (-not $token) {
  Write-Host "ERROR: Missing TELEGRAM_BOT_TOKEN (User env or current session)."
  exit 2
}

$me = TgCall $token "getMe"
Write-Host ("getMe_status=" + $me.status + " ok=" + $me.ok)
if ($me.ok) {
  Write-Host ("bot_username=" + $me.data.result.username)
} else {
  Write-Host ("getMe_error=" + $me.err)
}

$wh = TgCall $token "getWebhookInfo"
Write-Host ("getWebhookInfo_status=" + $wh.status + " ok=" + $wh.ok)
if ($wh.ok) {
  $url = $wh.data.result.url
  $pend = $wh.data.result.pending_update_count
  $hasErr = [bool]$wh.data.result.last_error_message
  Write-Host ("webhook_set=" + [bool]$url + " webhook_url_len=" + (SafeLen $url) + " pending=" + $pend + " has_last_error=" + $hasErr)
} else {
  Write-Host ("getWebhookInfo_error=" + $wh.err)
}

if ($DropPending) {
  $d = TgCall $token "deleteWebhook?drop_pending_updates=true"
  Write-Host ("deleteWebhook(drop_pending)_status=" + $d.status + " ok=" + $d.ok)
}

if ($PublicBase) {
  if ($PublicBase -notmatch '^https?://') { $PublicBase = "https://$PublicBase" }
  $PublicBase = $PublicBase.TrimEnd("/")
  $h = HttpStatus "$PublicBase/health"
  Write-Host ("backend_health_status=" + $h.status + " ok=" + $h.ok)

  if ($WebhookPath) {
    if ($WebhookPath -notmatch '^/') { $WebhookPath = "/" + $WebhookPath }
    $w = HttpStatus "$PublicBase$WebhookPath"
    Write-Host ("webhook_endpoint_GET_status=" + $w.status + " ok=" + $w.ok + " (GET only)")
  }
}

Write-Host "=== END ==="
