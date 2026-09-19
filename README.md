# Vortex 繁體中文（臺灣正體）語言包

[![Release](https://img.shields.io/github/v/release/threesecond/Vortex-zh-TW?include_prereleases&color=blue&label=最新版本)](https://github.com/threesecond/Vortex-zh-TW/releases)
[![Target Vortex](https://img.shields.io/badge/Vortex-2.6.3-brightgreen)](https://www.nexusmods.com/site/mods/1)
[![License](https://img.shields.io/badge/授權-自由轉載與修改-blue)](#授權)

適用於 Nexus Mods 官方模組管理器 [Vortex](https://www.nexusmods.com/site/mods/1) 的臺灣繁體正體中文語言包。

Vortex 官方具備完整的多國語言架構，但長年未內建臺灣繁體中文。本專案補齊了這個缺口，完整翻譯 Vortex 本體與全部 76 個內建擴充套件介面，涵蓋 **3,700+ 條字串**。

---

## 目錄

- [一、專案特色與涵蓋範圍](#一專案特色與涵蓋範圍)
- [二、相容版本](#二相容版本)
- [三、下載與安裝教學](#三下載與安裝教學)
  - [方法 A：一鍵安裝（推薦）](#方法-a一鍵安裝推薦)
  - [方法 B：手動安裝](#方法-b手動安裝)
  - [解除安裝](#解除安裝)
- [四、重要：請先移除簡體中文語言包](#四重要請先移除簡體中文語言包)
- [五、為何採用 Zip 方式而非擴充套件版？](#五為何採用-zip-方式而非擴充套件版)
- [六、翻譯規範與術語標準](#六翻譯規範與術語標準)
- [七、已知限制與無法翻譯項目](#七已知限制與無法翻譯項目)
- [八、專案結構與工具鏈](#八專案結構與工具鏈)
- [九、問題回報與參與貢獻](#九問題回報與參與貢獻)
- [授權](#授權)

---

## 一、專案特色與涵蓋範圍

- **介面全覆蓋**：包含首頁、Mods、合集、下載、遊戲支援、擴充套件、設定、健康檢查等所有模組。
- **對話框與系統通知**：涵蓋所有操作提示、錯誤警示、進度對話框以及部署訊息。
- **76 個內建擴充套件**：包括 LOOT 插件排序、存檔管理、FNIS、Script Extender、BepInEx，以及各遊戲專用支援（Baldur's Gate 3、Witcher 3、Stardew Valley、Cyberpunk 2077 等）。
- **臺灣正體在地化**：軟體、檔案、預設、快取、支援、使用者、記錄檔、解除安裝等在地標準用語。
- **尊重社群習慣**：關鍵名詞「mod」一律保留英文不翻，複數形與大小寫如實保留。

---

## 二、相容版本

| Vortex 版本 | 相容性 | 說明 |
|---|---|---|
| **Vortex 2.6.3** | 完整支援（推薦） | 本語言包依此版本為基準製作，完成完整掃描與校對 |
| **Vortex 2.5.x** | 相容可用 | 少數新版新增字串會自動退回英文顯示 |
| **Vortex 2.4.x** | 相容可用 | 同上 |
| **Vortex 1.x** | 不支援 | 1.x 介面與核心架構完全不同，語言包無法通用 |

> [!NOTE]
> Vortex 後續更新不會清除此語言包；若新版本引進了新字串，在尚未更新語言包之前，該新字串會直接顯示預設英文，不會造成閃退或介面損壞。

---

## 三、下載與安裝教學

請先前往 [Releases 頁面](https://github.com/threesecond/Vortex-zh-TW/releases) 下載最新的 `Vortex-zhTW-<版本>.zip` 壓縮檔。

### 方法 A：一鍵安裝（推薦）

1. 完全關閉 Vortex（包含 Windows 右下角系統匣中的 Vortex 圖示）。
2. 將下載的 `Vortex-zhTW-*.zip` 解壓縮至任意資料夾。
3. 執行資料夾內的 `install.bat`，依視窗提示完成安裝。
   * 啟動器會自動偵測並調用 PowerShell，僅將譯檔複製到 Vortex 設定目錄，不修改 Vortex 主程式、不刪除你的任何現有設定。
4. 開啟 Vortex，點選 **「Settings（設定）→ Interface（介面）→ Language（語言）」**，選擇 **「中文 (Zhōngwén), 汉语, 漢語 (臺灣)」** 即可。
   * 初次切換若部分文字未更新，請重新啟動 Vortex。

### 方法 B：手動安裝

1. 完全關閉 Vortex。
2. 按下鍵盤 `Win + R`，輸入 `%APPDATA%\Vortex` 後按 Enter，開啟 Vortex 使用者資料夾。
   * 若你的 Vortex 設定為「共用模式（Shared Mode）」，路徑則為 `C:\ProgramData\vortex`。
3. 將 zip 壓縮檔內的 `locales` 資料夾直接複製到上述路徑下。
   * 正確放置後的路徑範例：`%APPDATA%\Vortex\locales\zh-TW\common.json`。
4. 開啟 Vortex，前往「Settings → Interface → Language」切換為臺灣繁體中文。

### 解除安裝

若要還原為英文介面，只需刪除 `%APPDATA%\Vortex\locales\zh-TW` 資料夾（共用模式為 `C:\ProgramData\vortex\locales\zh-TW`），重開 Vortex 即可完全還原。

---

## 四、重要：請先移除簡體中文語言包

> [!WARNING]
> 若系統中曾經安裝過簡體中文語言包，強烈建議在安裝本繁體包前先將其完全移除。

### 為什麼？
Vortex 採用 i18next 機制，當繁體中文包遇到少數未定義的字串時，其語言解析階層為：
$$\text{zh-TW（繁體）} \longrightarrow \text{zh（簡體）} \longrightarrow \text{en（英文）}$$

只要你的電腦中殘留簡體中文語言包或擴充套件，任何未被翻譯到的冷門字串就會自動降級到簡體中文，導致畫面出現繁簡夾雜的混亂現象；將簡中包移除後，未翻譯文字則會乾淨地維持英文原貌。

### 移除方法
1. 前往 `%APPDATA%\Vortex\locales\`，若發現 `zh`、`zh-CN`、`zh-Hans`、`zh-SG` 等資料夾，請手動刪除。
2. 開啟 Vortex，進入「Extensions（擴充套件）」頁面，搜尋名稱包含 `Chinese` 或 `简体` 的語言擴充套件並停用/移除。
   * 或手動檢查 `%APPDATA%\Vortex\plugins\` 刪除對應的簡中外掛資料夾。
3. 重新啟動 Vortex。

---

## 五、為何採用 Zip 方式而非擴充套件版？

Vortex 尋找語言檔時依序檢查三個層級，且採取**命中即停（First Match Wins）**原則：

| 優先序 | 來源 | 路徑 | 說明 |
|:---:|---|---|---|
| **1（最高）** | **使用者層級** | `%APPDATA%\Vortex\locales\<語言>\` | **本語言包採用位置** |
| **2** | 擴充套件層級 | `plugins\<擴充套件>\locales\<語言>\` | Nexus 上的翻譯外掛套件 |
| **3（最低）** | Vortex 內建 | `resources\locales\<語言>\` | 官方原始目錄（僅內建 en） |

採用使用者層級（Zip 安裝）的優勢：
- **不受版本更新影響**：Vortex 自動升級時經常會覆蓋 `resources\` 甚至清理 `plugins\`，但**絕對不會清空**使用者設定目錄 `%APPDATA%`。
- **優先順序最高**：即使系統中有其他擴充套件，也會優先以使用者層級的檔案為準。
- **無審核延遲**：無需等待 Nexus 官方擴充套件的繁瑣審核流程，更新即發即用。

---

## 六、翻譯規範與術語標準

為維持介面品質與專業度，本語言包遵循以下統一定義的規範：

### 核心原則
1. **保留「mod」原文**：一律維持英文 `mod` / `mods` / `Mod` / `Mods`，不刻意譯為「模組」，貼合社群長久共識。
2. **區分關鍵操作詞**：
   - **`override`（覆蓋）vs `overwrite`（覆寫）**：前者代表 mod 規則衝突中的優先序設定；後者代表實體檔案被取代寫入。
   - **`remove`（移除）vs `delete`（刪除）**：嚴格劃分操作差異，防止使用者誤將實體檔案抹除。
3. **第二人稱稱謂**：全面統一使用「**你**」，避免生硬的「您」。

### 核心術語對照表

| 英文術語 | 繁體中文譯名 | 備註 |
|---|---|---|
| collection | 合集 | 不使用「收藏」，避免與收藏夾混淆 |
| profile | 設定檔 | |
| deploy / deployment | 部署 | 統一名詞，非「佈署」 |
| purge | 清除部署 | 明確指示為清除部署連結，非清空 mod |
| staging folder | 模組暫存資料夾 | 存放 mod 解壓內容的目錄 |
| load order | 載入順序 | |
| plugin | 插件 | 特指 esp/esm/esl 檔案，與 extension（擴充套件）嚴格區隔 |
| extension | 擴充套件 | 指 Vortex 自身的附加功能外掛 |
| loadout | 模組配置 | Nexus 近期導入的新概念 |
| workshop | 工作區 | Vortex 內部的合集編輯工作區 |
| endorse | 推薦 | 對應 Nexus Mods 的推薦功能，不用「點贊」 |
| dashlet | 儀表板元件 | 主頁介面小卡片 |
| replicate | 複製安裝 | 合集的還原部署選項之一 |
| fresh install | 全新安裝 | 合集的初始化部署選項之一 |

---

## 七、已知限制與無法翻譯項目

以下介面文字顯示英文為正常現象，無法透過語言包修改：

1. **Vortex 程式碼寫死（Hardcoded Strings）**：
   部分較新的 React 元件將英文直接寫死在 JSX 代碼中未接入 `t()` 函式（如：合集瀏覽頁面的排序選單 `Most Endorsed`、下載時的 `Free vs Premium` 比較彈窗、首頁的 Premium 宣傳區塊等）。需待 Vortex 官方後續改版支援國際化。
2. **動態外部資料（Data）**：
   - 來自 Nexus Mods 伺服器的動態內容（首頁新聞、更新日誌、教學影片標題）。
   - 各 Mod 的名稱、作者說明與分類標籤（如 `Vanilla Plus`、`Adult` 等）。
   - 遊戲本體名稱（Baldur's Gate 3、Cyberpunk 2077 等）與外部輔助工具名（LOOT、FNIS、SMAPI、BepInEx）。
   - 底層系統錯誤代碼（如 `ENOENT`、JS 例外訊息）。

---

## 八、專案結構與工具鏈

```
Vortex-zh-TW/
├── locales/
│   └── zh-TW/
│       ├── common.json       # 核心通用翻譯（包含擴充套件 fallback 字串）
│       └── *.json            # 各擴充套件獨立語系檔（共 76 個）
├── install.bat               # 純 ASCII 啟動腳本（相容所有語系環境）
├── install.ps1               # 繁體中文安裝互動介面（UTF-8 with BOM）
├── README.txt                # 隨附於發布 zip 中的離線說明手冊
├── README.md                 # 本專案 GitHub 首頁說明文件
├── CLAUDE.md                 # 專案詳細維護紀錄與技術手冊
└── _tools/                   # 萃取、比對與發布工具鏈（不進入 Release zip）
```

維護工具位於 `_tools/` 目錄下：
- `scan_sources.py`：主力掃描器，直接解析 Vortex 內附的完整 source map 與明碼原始碼，自動比對漏譯字串。
- `apply.js`：套用補丁檔案並自動排序、進行佔位符一致性校驗。
- `make_release.py`：依規範自動檢查檔案編碼與格式，封裝出可發布的 `Vortex-zhTW-<版本>.zip`。

---

## 九、問題回報與參與貢獻

若在實際遊戲與管理過程中使用本語言包，發現任何：
- 漏譯且可翻譯的文字
- 翻譯不通順或用詞錯誤
- 格式化符號（`{{variable}}`）異常

歡迎提交 [GitHub Issue](https://github.com/threesecond/Vortex-zh-TW/issues) 或發送 Pull Request！
亦歡迎在 Issue 中附上畫面截圖與文字描述。

---

## 授權

本語言包可自由轉載、修改與整合，轉載請保留本說明與原作者出處標示。
本專案與 Nexus Mods 或 Black Tree Gaming Ltd 無官方附屬關係。
