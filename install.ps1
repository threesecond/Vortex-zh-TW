#Requires -Version 5.1
# Vortex 繁體中文（臺灣正體）語言包 - 安裝腳本
# 由 install.bat 啟動。本檔必須存成 UTF-8 with BOM，
# 否則 Windows PowerShell 5.1 會用系統 ANSI 碼頁讀取而使中文變亂碼。

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$Root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src    = Join-Path $Root 'locales\zh-TW'
$Vortex = Join-Path $env:APPDATA 'Vortex'
$Target = Join-Path $Vortex 'locales\zh-TW'

function Line { param([string]$s = '') Write-Host "  $s" }
function Rule { Write-Host ('  ' + ('=' * 64)) }
function Thin { Write-Host ('  ' + ('-' * 64)) }

Write-Host ''
Rule
Line 'Vortex 繁體中文（臺灣正體）語言包'
Rule
Write-Host ''
Line "安裝來源： $Src"
Line "安裝位置： $Target"
Write-Host ''

# ── 前置檢查 ────────────────────────────────────────────────
if (-not (Test-Path (Join-Path $Src 'common.json'))) {
    Line '[錯誤] 找不到語言檔。'
    Line '       請先將壓縮檔「完整解壓」後再執行，'
    Line '       install.bat 必須與 locales 資料夾放在同一層。'
    Write-Host ''
    Read-Host '按 Enter 結束' | Out-Null
    exit 1
}

if (-not (Test-Path $Vortex)) {
    Line '[錯誤] 找不到 Vortex 的資料夾：'
    Line "       $Vortex"
    Line '       請先安裝並至少執行過一次 Vortex。'
    Write-Host ''
    Read-Host '按 Enter 結束' | Out-Null
    exit 1
}

# ── 偵測既有的簡體中文語系 ──────────────────────────────────
$scDirs = @()
foreach ($d in @('zh', 'zh-CN', 'zh-Hans', 'zh-SG')) {
    if (Test-Path (Join-Path $Vortex "locales\$d")) { $scDirs += $d }
}

$scExts = @()
$pluginDir = Join-Path $Vortex 'plugins'
if (Test-Path $pluginDir) {
    $scExts = @(Get-ChildItem -Path $pluginDir -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -match 'Chinese|简体|簡體' } |
                Select-Object -ExpandProperty Name)
}

if ($scDirs.Count -gt 0 -or $scExts.Count -gt 0) {
    Thin
    Line '[建議] 偵測到既有的簡體中文語系'
    Thin
    if ($scDirs.Count -gt 0) {
        Line ("語系資料夾：" + ($scDirs -join '、'))
        Line "  位於 $Vortex\locales\"
    }
    if ($scExts.Count -gt 0) {
        Line ("翻譯擴充套件：" + ($scExts -join '、'))
        Line "  位於 $pluginDir\"
    }
    Write-Host ''
    Line '建議你「手動移除」上述項目後再安裝。'
    Write-Host ''
    Line '原因：Vortex 找不到某個字串時，會依'
    Line '      zh-TW → zh → en 的順序往下尋找。'
    Line '      若保留簡體語系，本語言包尚未涵蓋的字串'
    Line '      會顯示成簡體中文，造成繁簡混雜；'
    Line '      移除後則會顯示英文，風格比較一致。'
    Write-Host ''
    Line '本腳本不會自動刪除任何檔案，請自行斟酌。'
    Write-Host ''
}

# ── 確認 ────────────────────────────────────────────────────
$answer = Read-Host '  要現在安裝嗎？(Y=安裝 / 其他鍵=取消)'
if ($answer -notmatch '^[Yy]') {
    Write-Host ''
    Line '已取消，未做任何變更。'
    Write-Host ''
    Read-Host '按 Enter 結束' | Out-Null
    exit 0
}

# ── 安裝 ────────────────────────────────────────────────────
Write-Host ''
if (Test-Path $Target) { Line '偵測到既有版本，將覆蓋更新…' } else { Line '建立資料夾…' }

try {
    New-Item -ItemType Directory -Force -Path $Target | Out-Null
    Copy-Item -Path (Join-Path $Src '*.json') -Destination $Target -Force
} catch {
    Write-Host ''
    Line '[錯誤] 複製失敗：'
    Line "       $($_.Exception.Message)"
    Line '       請確認 Vortex 已完全關閉後再試一次。'
    Write-Host ''
    Read-Host '按 Enter 結束' | Out-Null
    exit 1
}

$count = @(Get-ChildItem -Path $Target -Filter '*.json' -File).Count

Write-Host ''
Rule
Line "安裝完成，共 $count 個語言檔"
Rule
Write-Host ''
Line '接下來：'
Line '  1. 重新啟動 Vortex'
Line '  2. 前往 設定 → 介面 → 語言'
Line '  3. 選擇「中文 (Zhōngwén), 汉语, 漢語 (臺灣)」'
Write-Host ''
Line '若清單中沒有出現，請完全關閉 Vortex 後再開一次。'
Write-Host ''
Line '解除安裝：直接刪除下列資料夾即可'
Line "  $Target"
Write-Host ''
Read-Host '按 Enter 結束' | Out-Null
