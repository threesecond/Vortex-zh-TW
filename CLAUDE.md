# Vortex 繁體中文（臺灣正體）語言包

Vortex 官方支援 i18n 但沒有繁體中文。`zh-TW\` 子資料夾就是自行補上的語言包。

**最後更新：2026-09-12 ｜ 對應 Vortex 版本：2.6.3**

### 本機環境（2026-09-12 從另一台電腦遷移後確認）

| 項目 | 本機路徑 |
|---|---|
| Vortex 安裝目錄（英文來源 `app.asar` 在 `resources\` 下） | `C:\Program Files\Black Tree Gaming Ltd\Vortex\` |
| 使用中的語言包（Vortex 實際讀的那份） | `%APPDATA%\Vortex\locales\zh-TW\` |
| 本專案目錄（**正本**，見下方結構） | `D:\Users\threesecond\OneDrive\Github\Vortex-zh-TW\` |
| 工具鏈 | `<專案>\_tools\`（2026-09-12 重建，不再放 `%APPDATA%` 下） |
| 發布 zip | `make_release.py` 產出在專案根目錄；舊的一份在 `D:\Users\threesecond\Downloads\Vortex-zhTW-2.6.3.zip` |

> 舊機器上 Vortex 裝在 `C:\Program Files\Vortex\`，本機安裝程式改用 `Black Tree Gaming Ltd\` 子目錄；文件內所有路徑已改為本機的。
> `_tools\` 的腳本會自動在這兩個位置找 Vortex，也可用環境變數 `VORTEX_DIR` 指定。

### 專案結構

```
Vortex-zh-TW\
├── CLAUDE.md
├── locales\zh-TW\*.json   ← 譯檔正本（76 個）；%APPDATA% 那份只是安裝出去的副本
├── install.bat            ← 會被打包進 zip（純 ASCII）
├── install.ps1            ← 會被打包進 zip（UTF-8 with BOM）
├── README.txt             ← 給玩家的說明，會被打包進 zip（UTF-8 with BOM、CRLF）
└── _tools\                ← 不打包；report.txt 等產出檔也在這裡
```

改完譯檔後跑 `py -3.11 -X utf8 _tools\sync_appdata.py` 同步到 `%APPDATA%`，重啟 Vortex 生效。

---

## 一、現在的狀態

| 項目 | 數值 |
|---|---|
| 語言代碼 | `zh-TW`（介面顯示為「中文 (Zhōngwén), 汉语, 漢語 (臺灣)」） |
| 語言包位置 | 正本 `<專案>\locales\zh-TW\`；Vortex 實際讀 `%APPDATA%\Vortex\locales\zh-TW\`（用 `sync_appdata.py` 同步） |
| 檔案數 | 76 個 `.json`（每個內建擴充套件一個 namespace 檔） |
| 字串數 | **3715** 條（2026-09-12 補完後；同日早上還是 2107） |
| 語言檔大小 | 453.1 KB |
| 對 2.6.3 的覆蓋 | 原始碼掃描 **2479 / 2489**（`scan_sources.py`；剩 10 條是遊戲名稱與 ID/URL 這類刻意不翻的） |
| 發布檔 | `Vortex-zhTW-2.6.3.zip`（`make_release.py` 產出，在專案根目錄） |

**可以直接使用。** 在 Vortex 的「設定 → 介面 → 語言」選「中文 (臺灣)」即可。第一次切換可能要重開。

### 各檔案字串數

```
common.json                              2859   ← 核心；擴充套件字串也都會複寫一份到這裡（見 3-3）
health_check.json                         126   健康檢查（巢狀 ID 式鍵，整檔對照內建 en 翻譯）
gamebryo-plugin-management.json            88
game-baldursgate3.json                     77
game-witcher3.json                         64
mod-dependency-manager.json                59
gamebryo-savegame-management.json          34
feedback.json                              29
game-7daystodie.json                       27
theme-switcher.json                        21
script-extender-installer.json             19
game-bladeandsorcery.json                  18
modtype-bepinex.json                       17
issue-tracker.json                         17
collection.json                            17   合集瀏覽（巢狀 ID 式鍵）
fnis-integration.json                      15
mo-import.json                             14
gameversion-hash.json                      13
mod-report.json                            12
game-stardewvalley.json                    12
open-directory.json                        11
nmm-import-tool.json                       11
（另有 54 個少於 10 條的遊戲擴充套件檔，合計 155 條）
```

### 版本追蹤記錄

| Vortex 版本 | 核心 key 數 | 新增待譯 | 處理 |
|---|---|---|---|
| 2.4.1 | 770 | — | 初版建置 |
| 2.4.2 | 770 | 0 | 純修 bug，無字串變動 |
| 2.5.0 | 841 | 29 | `patch_250.json`，補 30 條 |
| 2.6.3 | 847 | 9 | `patch_263.json`，補 8 條 |
| 2.6.3 | — | 324 | **別名掃描**補完，見第五節 |
| 2.6.3 | 2591（原始碼掃描） | 1608 | 2026-09-12 工具鏈重建：`scan_api.py` 抓到通知/對話框整類 384 條、`scan_sources.py` 吃 source map 再補 614 條、`health_check` 31 條，全部套完 |

版本落差一直很小，維護成本低。每次 Vortex 更新後跑一次 `scan_sources.py` 就知道要補什麼（見第九節）。

---

## 二、官方文件怎麼說

官方文件確實存在：[Translating Vortex - Nexus Mods Wiki](https://wiki.nexusmods.com/index.php/Translating_Vortex)。

它**證實了**本專案反解出來的路徑：

> Once your language has been created, navigate to `C:\Users\<username>\AppData\Roaming\Vortex\locales` (or `C:\ProgramData\vortex\locales` if you have Vortex in Shared Mode)

兩個路徑都與程式碼一致，包括共用模式會改用 `ProgramData\vortex`（對應 `main.cjs` 的 `multiUserPath()`）。

**但官方文件沒有說明第三節的優先順序。** 需注意：Wiki 與 Nexus 都會擋自動抓取（HTTP 403），只能讀到搜尋摘要，無法逐字確認全文。所以準確的說法是「**搜尋摘要中未提及優先順序**」，而非「官方完全沒寫」。那三層的先後關係目前仍只有程式碼能證明。

### 官方的 Translation Helper 擴充套件

官方另有 [Translation Helper](https://www.nexusmods.com/site/mods/28)（原始碼：[Nexus-Mods/extension-translate](https://github.com/Nexus-Mods/extension-translate)）。

這解答了一個疑問：舊版簡中包裡有 `translate.json`，但 2.4 之後的 `bundledPlugins` 找不到 `translate` 擴充套件——因為它被抽成獨立的可下載擴充套件了。

它的運作方式是「在 Vortex 執行過程中動態發現需要翻譯的字串，並寫進動態建立的檔案」，**正是第六節第 2 點建議的執行期補漏路線**，只是包了官方 UI。要做最後一輪精確補漏時，裝它會比自製掃描器省事。

### 已存在的其他繁中翻譯

Nexus 上已有一份 [Vortex - Traditional Chinese Translation](https://www.nexusmods.com/site/mods/1574)（作者 ST4RlessNight），但**是給 Vortex 1.15.2 的**，中間隔了一整個大版號且 2.x 介面重寫，在現行版本上應有相當比例失效。可作術語對照參考。

Nexus 對社群翻譯似乎有審核流程，參見 [Issue #19108](https://github.com/nexus-mods/vortex/issues/19108)。

---

## 三、語言檔的優先順序 ← 最重要的機制

以下全部是從 `app.asar` 反解程式碼確認，並經過實機驗證。

### 3-1. 三個來源，優先序「使用者 > 擴充套件 > 內建」

Vortex 解析語言檔時依序檢查這三個位置，**命中即停**：

| 優先 | 路徑 | 說明 |
|---|---|---|
| **1** | `%APPDATA%\Vortex\locales\<語言代碼>\` | **本語言包所在位置**，優先序最高 |
| **2** | 任何 `info.json` 中 `"type": "translation"` 的擴充套件目錄下的 `<語言代碼>\` | 例如 Nexus 上的簡中翻譯包 |
| **3** | `C:\Program Files\Black Tree Gaming Ltd\Vortex\resources\locales\<語言代碼>\` | Vortex 內建，只有 `en` |

對應程式碼（`MultiBackend.backendType()`）：

```js
backendType(language) {
  try {
    fs.statSync(path.join(this.mOptions.user, language));
    return { backendType: "custom" };        // ← 1. 使用者層級，命中就用這層
  } catch (err) {
    const ext = this.mOptions.translationExts()
      .find(iter => { try { fs.statSync(path.join(iter.path, language)); return true; }
                      catch (err) { return false; } });
    if (ext !== undefined) return { backendType: "extension", extPath: ext.path };  // ← 2. 擴充套件
    try {
      fs.statSync(path.join(this.mOptions.bundled, language));
      return { backendType: "bundled" };     // ← 3. 內建
    } catch (err) { return { backendType: "custom" }; }
  }
}
```

**這是「擇一」不是「合併」**：選定語言只會從命中的那一層讀檔。

### 3-2. 語言的解析階層：`zh-TW` → `zh` → `en`

另一個獨立機制。找不到的 key 會依序往下掉：

- **同時裝了簡體中文擴充套件時**，本語言包缺的 key 會掉到 `zh`（簡體），畫面繁簡混雜
- **沒裝簡中包時**，缺的 key 會掉到 `en`，顯示英文

安裝腳本 `install.bat` 會偵測既有簡體語系並提示使用者移除，原因就在這裡。

### 3-3. namespace 的 fallback：`<ns>` → `common`

第三層獨立機制。i18next 設定了 `fallbackNS: "common"`，某個 namespace 找不到的 key 會退回 `common`。已實測確認有效。

**這很重要，因為 Vortex 自己的用法不一致**：擴充套件元件呼叫 `t()` 時，有些宣告自己的 namespace、有些直接用 `defaultNS`（即 `common`），沒有規則可循。

**因應方式**：擴充套件的字串**同時寫入自己的 `<ns>.json` 和 `common.json` 兩處**。

> 所以要修改某條擴充套件的翻譯時，**記得兩個檔案都要改**。

### 3-4. 其他 i18next 設定

Vortex 用 **i18next 19.9.2**（JSON v3 格式）：

- `loadPath` = `<basePath>/{{lng}}/{{ns}}.json`
- `fallbackLng: "en"`、`fallbackNS: "common"`
- **key 就是英文原文**
- `nsSeparator: ":::"`、`keySeparator: "::"`
- 例外：部分較新的元件呼叫 `translate()` 時帶 `isNamespaceKey`，會改用 i18next 預設分隔符（`:` 與 `.`）

### 3-5. 為什麼「使用者層級」是正確選擇

**Vortex 從不主動建立第 1 層的資料夾**，必須手動建立——這不代表不支援。

而且這段期間 Vortex 自動更新了四次（2.4.1 → 2.4.2 → 2.5.0 → 2.6.3），`%APPDATA%` 下的檔案**每次都完好無損**。若放在 `C:\Program Files\Black Tree Gaming Ltd\Vortex\resources\locales\`，早就被清掉了。

---

## 四、官方內建的 `en` 不是「翻譯檔」

容易誤會的一點。`C:\Program Files\Black Tree Gaming Ltd\Vortex\resources\locales\en` 只有 155 條：

```
health_check.json          93
common.json                39
collection.json            17
download_management.json    1  ← 只有 _comment 佔位
extension_manager.json      1  ← 只有 _comment 佔位
gamemode_management.json    1  ← 只有 _comment 佔位
mod_management.json         1  ← 只有 _comment 佔位
nexus_integration.json      1  ← 只有 _comment 佔位
profile_management.json     1  ← 只有 _comment 佔位
```

**這不代表官方漏譯。** 因為 key 就是英文原文，找不到 key 時 i18next 直接回傳 key 本身，畫面就是正確的英文——英文根本不需要翻譯檔。`en` 只放三種「光靠 key 表達不了」的例外：

1. **複數形**（`{{ count }} file_plural` → `{{ count }} files`）
2. **ID 式鍵**（`view_all`、`back`、`active`）——較新元件改用 ID 當 key
3. **巢狀結構的新模組**（`health_check`、`collection`）——整包改用 ID 式設計

那 6 個只有 `_comment` 的空殼檔寫著 *"to be populated during migration"*，是 Nexus 正在從「英文原文當 key」遷移到「ID 當 key」的半成品。

所以該比的是**可翻譯字串總量**。2026-09-12 重建工具鏈後的實測：`t()` 鍵 1083、別名鍵 302、通知/對話框/註冊式字串 1028（見第九節 `scan_api.py`），去重後尚有 777 條未翻——原先「2107 條已貼近上限」的判斷是低估，主要是漏掉了不經 `t()` 的那一整類。

---

## 五、翻譯函式別名問題（踩過最大的坑）

程式碼壓縮後，**翻譯函式名稱不固定**。核心是 `t(...)`，但許多擴充套件被壓成 `e(\`...\`)`：

```js
// theme-switcher / extension-dashlet / changelog-dashlet 都是這樣
p.createElement(m.HelpBlock, null, e(`Some community themes were designed for...`))
```

早期的抽取規則只認 `t(`，導致**整包擴充套件被漏掉**。後來寫了 `scan_aliases.py`：先從 `{t:別名}` 這類解構語法反推出壓縮後的函式名，再抓該別名的呼叫，一次撈出 **324 條漏鍵**，分布 24 個來源（`gamebryo-plugin-management` 62 條、renderer 的對話框 84 條、`mod-dependency-manager` 37 條等）。

這批已全數補完，目前掃描結果只剩 3 條刻意跳過的：`Baldur's Gate 3`、`Stardew Valley`（遊戲名稱）、`{{ value }}`（雜訊）。

---

## 六、已知問題與限制

### 1. 唯一未譯的核心鍵（不需處理）

```
"Sorry to hear that the collection \"${(0,modName_1.default)(collection)}\" isn't working for you..."
```

`${...}` 是編譯後的模板殘留，執行時才代換，不是真正的 key。

### 2. 靜態抽取仍無法保證完整（但有更好的原料：內附的 source map）

2026-09-12 發現 `app.asar` 自帶完整 source map：`renderer.js.map` 的 `sourcesContent` 含 971 個 Vortex 自己的 `.ts/.tsx` 原始檔，`bundledPlugins\*\index.cjs.map` 也有 68 個。這是**與安裝版本完全一致的未壓縮原始碼**，比去 GitHub clone（版本要對 tag、內建擴充套件又散在別的 repo）更可靠。第五節的別名問題在原始碼層根本不存在——所有呼叫都是乾淨的 `t('…')`。`scan_sources.py` 就是吃 source map 的掃描器（同日下午完成），現有三個壓縮版掃描器保留作交叉驗證。

即使有了別名掃描，仍不能保證掃到全部（別名可能是任意單字母、也可能透過變數間接傳遞）。

**真正能收斂的方法**是執行期蒐集：`renderer.js` 匯出了 `debugTranslations()` 與 `getMissingTranslations()`，開啟後 i18next 會把實際渲染時查不到的 key 收進記憶體。官方的 Translation Helper 擴充套件就是這個機制的正規前端（見第二節）。

在那之前，**看到英文就截圖回報**仍是最有效率的做法。

### 3. 無法翻譯的硬編碼字串（2026-09-12 依截圖確認）

以下畫面上的英文**不是漏翻**，是 Vortex 新版 React 元件直接把英文寫死在 JSX 裡、完全不經 `t()`，語言包無能為力，只能等上游修：

| 畫面 | 硬編碼的字串 |
|---|---|
| 瀏覽 Nexus Mods → 合集 | 排序選單 `Recently Listed` / `Most Endorsed` / `Highest Rated` / `Most Downloaded`（`label:option.label` 直接渲染，`common.json` 裡其實有譯文但用不到）、`Add collection`、`Added`、`View page`、`Log in to add` |
| 下載 mod 對話框（免費 vs Premium 比較） | `Free` / `Premium`、`Download one by one`、`Get all your mods fast`、`Manual download for collections`、`Throttled download speeds (3 MB/s)`、`Ads and delay for each download`、`Auto-download collections`、`Max download speeds`、`No more ads`、作者列的 `by ` |
| 首頁 Premium 廣告儀表板元件 | `Get fast downloads with premium`、`Upgrade to unlock uncapped download speeds, auto-install collections and no ads` |

另外這些是**資料**不是介面：合集分類標籤（`Vanilla Plus` / `Themed` / `Adult`）與 `EASY INSTALL` 徽章來自 Nexus API；首頁的「開始使用」影片標題（`Getting Started`、`Downloading…`）與更新日誌來自官網；`Cannot read properties of undefined` 是 JS 例外訊息。依原則不翻。

### 4. 尚未涵蓋的字串

約 400 條候選未翻，多數是遊戲專屬擴充套件（Skyrim、Fallout 等目前沒在管理的遊戲）；其餘是刻意跳過的 `design_system_dev` 開發示範字串、`[adaptor-bridge]` 之類的 log 訊息、以及專有名詞。

---

## 七、翻譯規範（已定案）

### 最重要的一條

**`mod` 一律維持英文，且保留原文大小寫**：`mod` / `mods` / `Mod` / `Mods` 各依原句，複數形也沿用原文。這是全表出現頻率最高的詞（283 次）。

### 核心術語

| 英文 | 譯法 | 備註 |
|---|---|---|
| collection | 合集 | 不用「收藏」，避免與收藏夾混淆 |
| profile | 設定檔 | |
| deploy / deployment | 部署 | 是「部署」不是「佈署」 |
| purge | 清除部署 | 單譯「清除」看不出在清什麼 |
| staging folder | 模組暫存資料夾 | 後續可簡稱「暫存資料夾」 |
| load order | 載入順序 | |
| plugin | 插件 | 指 esp/esm，**必須**與 extension 區分；不用「外掛」（台灣多指作弊程式） |
| extension | 擴充套件 | 指 Vortex 自身的擴充 |
| loadout | 模組配置 | Nexus 新術語 |
| workshop | 工作區 | 指 Vortex 的合集編輯區，**不是** Steam 創意工坊 |
| endorse | 推薦 | 不用「點贊」 |
| dashlet | 儀表板元件 | |
| replicate | 複製安裝 | 合集的安裝模式之一 |
| fresh install | 全新安裝 | 同上 |

### 兩組有實際風險、必須嚴格區分的詞

- **`override`（覆蓋）vs `overwrite`（覆寫）** — 前者是模組衝突的優先關係，後者是實際寫檔行為
- **`remove`（移除）vs `delete`（刪除）** — 混用會導致使用者誤刪檔案

### 其他

- 臺灣正體用語：軟體 / 檔案 / 預設 / 快取 / 支援 / 使用者 / 記錄檔 / 解除安裝
- 人稱統一用「**你**」，不用「您」
- 遊戲名稱（`Baldur's Gate 3`、`Stardew Valley`）不翻譯
- 完整術語表原為 90 條 CSV，**該檔案已隨暫存目錄遺失**

### 複數形的處理

中文在 i18next 的複數規則是 `nplurals=1`，查找順序為 `<key>_0` → `<key>`。無法靜態證實實際挑哪一個，所以帶 `{{count}}` 的鍵**同時提供三份相同譯文**：base、`_0`、`_plural`。

---

## 八、發布

### 官方推薦：zip 壓縮檔

[Wiki](https://wiki.nexusmods.com/index.php/Translating_Vortex) 的「Sharing Your Translation」段落：

> When packing up your translation we recommend **zipping the following files and folders into an archive**. Ensure you instruct users to extract your files to their `C:\Users\<username>\AppData\Roaming\Vortex` (or `C:\ProgramData\vortex` if they have Vortex in Shared Mode) and restart the app before trying to switch language.

注意解壓目標是 `...\Vortex` 而非 `...\Vortex\locales`，所以壓縮檔要**自帶 `locales\` 這層**：

```
Vortex-zhTW-2.6.3.zip
├── locales\
│   └── zh-TW\
│       ├── common.json
│       └── ...（共 76 個 .json）
├── install.bat        ← 啟動器（純 ASCII）
├── install.ps1        ← 安裝介面本體（UTF-8 with BOM）
└── README.txt         ← 給玩家的說明（UTF-8 with BOM）
```

這個結構正好落在第三節的**第 1 層（優先序最高）**。

### 產生發布檔

```bash
cd _tools && py -3.11 -X utf8 make_release.py
```

版本號直接從 `app.asar` 讀取，避免與實際安裝的 Vortex 脫節。產出放在專案根目錄。`_tools\` **不會**被打包；專案根目錄的 `README.txt`（給玩家看的說明，2026-09-12 新寫）會一併放進 zip，打包時自動補 BOM、轉 CRLF。打包前會驗證每個 `.json` 可解析、`.bat` 純 ASCII、`.ps1` 帶 BOM，並把行尾統一成 CRLF。

2026-09-12 重建後產出的 zip 已與舊機器帶來的 `Downloads\Vortex-zhTW-2.6.3.zip` 逐檔比對，內容一致（README.md 除外）。

### install.bat 的行為

1. 檢查來源與 `%APPDATA%\Vortex` 是否存在
2. 偵測既有的簡體中文語系（`zh` / `zh-CN` / `zh-Hans` / `zh-SG` 資料夾，以及 `plugins\` 下名稱含 `Chinese` 的擴充套件），**提示使用者自行手動移除**並說明繁簡混雜的原因——不會自動刪除任何檔案
3. 確認後複製 `.json` 到 `%APPDATA%\Vortex\locales\zh-TW\`
4. 顯示後續步驟與解除安裝方式

### 為什麼拆成 .bat + .ps1

原本想用單一個 UTF-8 的 `.bat` 搞定，實測失敗兩次：

1. **跳脫錯誤** — 想在 `echo` 裡印出箭頭，寫成 `^-^>`，結果 `^` 跑去跳脫 `-`，讓 `>` 變成真正的重新導向，把整行切斷。
2. **cmd.exe 的 UTF-8 缺陷（致命）** — 即使下了 `chcp 65001`，cmd 讀取 UTF-8 批次檔時，多位元組字元只要跨越其內部讀取緩衝區邊界就會被截斷。實測有一整行憑空消失、下一行也連帶損毀。**這個 bug 沒有可靠的繞法**，字串長度一改就可能復發。

所以最終改成：`.bat` 只當純 ASCII 啟動器，所有中文介面交給 `.ps1`。啟動器用 `where pwsh` 偵測：**有 PowerShell 7 就用 `pwsh`，沒有才退回內建的 `powershell`（5.1）**——這是發給玩家社群的，不能假設對方裝了 pwsh，所以 5.1 相容性（BOM）仍要維持。兩條路徑都實測過。

**維護時的編碼要求（兩者相反，特別容易搞錯）：**

| 檔案 | 編碼 | 行尾 |
|---|---|---|
| `install.bat` | **純 ASCII**（不可有任何中文） | CRLF |
| `install.ps1` | **UTF-8 with BOM** | CRLF |

`.ps1` 必須帶 BOM，否則 Windows PowerShell 5.1 會用系統 ANSI 碼頁讀取而讓中文變亂碼。`make_release.py` 打包時會自動處理這兩件事並驗證（`.bat` 含非 ASCII 字元會直接 assert 失敗）。

### 擴充套件形式（次要選項）

若要讓使用者能自動更新，可另外做擴充套件版：複製到 `%APPDATA%\Vortex\plugins\<名稱>\`，根目錄加 `info.json`：

```json
{
  "name": "Traditional Chinese (Taiwan) Translation for Vortex",
  "author": "<你的名字>",
  "version": "1.0.0",
  "description": "Traditional Chinese (Taiwan) translation for Vortex",
  "type": "translation",
  "bundled": false
}
```

語言檔放在該目錄下的 `zh-TW\` 子資料夾。程式碼確認過：根目錄**必須有 `info.json`**，否則會記錄 `"extension has no info.json file"`，namespace 也會退回用資料夾名稱推斷。

注意擴充套件的優先序**低於**使用者層級，兩邊同時存在時以使用者層級為準。

---

## 九、工具鏈（`_tools\`）

> 最初的完整工具鏈（批次翻譯檔、90 條術語表 CSV）放在工作階段的暫存目錄，**已隨該目錄被清空而遺失**；後來在 `%APPDATA%` 下重建的一版又**沒隨 2026-09-12 的機器遷移帶過來**。現在這套是第三次重建，直接放在專案目錄裡納入版本控管。譯檔本身從未受影響。

本機環境：Python 3.11.9（`py -3.11`；預設 `py` 是 3.14）、PowerShell 7.6（`pwsh`）。

Vortex 本身是 Electron，可當 Node 執行檔用（不會開 GUI），所以 `.js` 腳本不需另外安裝 Node。`.py` 腳本用 Python 3.11。所有腳本都以 `_tools\` 為基準找專案根目錄，不需要 `cd` 到特定位置。

| 腳本 | 用途 |
|---|---|
| `vortex_paths.js` / `.py` | 共用：找 Vortex 安裝目錄（`VORTEX_DIR` → `Black Tree Gaming Ltd\Vortex` → `Program Files\Vortex`）、最小 asar 讀取器、譯檔目錄 |
| `extract.js` | 從 `app.asar` 抽 `t()` / `.t()` 鍵並與譯檔對帳，另外整檔比對內建 `en\<ns>.json` 的 ID 式鍵 → `report.txt`、`missing.json` |
| `scan_aliases.py` | 反推壓縮後的 `t()` 別名（`{t:e}`、`[e]=useTranslation()`、`e=props.t`），撈出漏鍵 → `alias_missing.txt/json` |
| `scan_api.py` | 撈「不經 `t()` 但執行時會被翻譯」的字串：`sendNotification` / `showDialog` 標題與內文、`showError*` 標題、`actions[].title` / `label`、部署方式的 `super(id, name, desc)`、`registerMainPage` / `registerSettings` / `registerDashlet` / `registerAction` 標題 → `api_missing.txt/json` |
| **`scan_sources.py`** | **主力掃描器。** 從 `app.asar` 內附的 source map 讀出原始 TS（renderer 971 檔 + 68 個有 map 的擴充套件；沒 map 的 64 個遊戲擴充套件本來就是明碼 JS）直接掃，涵蓋上面三種掃描器的所有形式，還會先合併 `'a' + 'b'` 分行字串 → `sources_missing.txt/json`（依 namespace 分組，填完直接餵 `apply.js`）。`--dump` 會把原始碼倒到 `_tools\sources\` 供 grep |
| `apply.js` | 把 patch JSON 併入譯檔。扁平格式 `{"原文": "譯文"}` 寫進 `common.json`（`--ns <名稱>` 同時寫入擴充套件的檔）；分組格式 `{"<ns>": {…}}` 每組寫 `<ns>.json` + `common.json`。含佔位符檢查與 `{{count}}` 三份展開 → `apply_report.txt` |
| `patch_health_check_263.py` | `health_check.json` 是巢狀 ID 式鍵，不走 `apply.js`；這支直接併入。之後 en 再有新鍵就照它改 |
| `sync_appdata.py` | 專案 `locales\zh-TW` ↔ `%APPDATA%`（`--check` 只比對、`--pull` 反向） |
| `make_release.py` | 依官方格式打包發布 zip，含編碼驗證 |
| `probe.py` | 查某段文字在原始碼裡是怎麼被呼叫的（判斷「這句能不能翻」） |

產出檔（`report.txt`、`missing.json`、`alias_missing.*`、`api_missing.*`、`apply_report.txt`）都是可再生的，不需要保留。

### 檢查目前版本的覆蓋率

```bash
cd _tools && ELECTRON_RUN_AS_NODE=1 ELECTRON_NO_ASAR=1 "/c/Program Files/Black Tree Gaming Ltd/Vortex/Vortex.exe" extract.js && py -3.11 -X utf8 scan_aliases.py && py -3.11 -X utf8 scan_api.py
```

pwsh 寫法：`$env:ELECTRON_RUN_AS_NODE=1; $env:ELECTRON_NO_ASAR=1; & 'C:\Program Files\Black Tree Gaming Ltd\Vortex\Vortex.exe' extract.js`

**Vortex 每次更新後都該跑這三個。** `extract.js` 掃的是 `renderer.js` 與 `bundledPlugins\*\*.js`；`main.cjs` / `bootstrap.mjs` 裡的 `t(` 全是別的函式，刻意不掃。三個掃描器都會跳過 `renderer.js` 裡 design_system_dev 示範頁的模組（`vortex_paths.demo_ranges()`，以 webpack 模組的 export 名稱是否以 `Demo` 結尾判定）。

### 2026-09-12 重建後的掃描結果

| 掃描 | 唯一鍵 | 早上（重建時） | 晚上（補完後） |
|---|---|---|---|
| `scan_sources.py`（source map，主力） | 2591 | — | **10 未翻**（全是遊戲名稱、`ID`/`URL`/`Vortex`/`MD5`） |
| `scan_api.py`（壓縮版，通知/對話框） | 1028 | 723 未翻 | 11 未翻（同上那些） |
| `extract.js`（壓縮版，`t(`） | 1083 | 27 未翻 | 17 未翻（`by`/`or`/`to`/`md5` 這類單字，刻意不翻；另 4 條是壓縮版才有的斷句碎片） |
| `scan_aliases.py`（壓縮版，別名） | 302 | 27 未翻 | 2 未翻（遊戲名稱） |
| `health_check.json`（對內建 en） | 93 | 29 缺 | 0 |

當天共補 **1608 條**（2107 → 3715）。早上發現的問題是：舊文件說「別名已全數補完」但實際還缺，而且**整類「不經 `t()`、由 Vortex 渲染時才翻譯」的字串**（通知、錯誤標題、對話框標題與內文、部署方式名稱——已在程式碼確認 `t(dialog.title, …)`、`t(message, {replace})`、`t(activator.name)`）之前的掃描器全部沒抓到。下午改吃 source map 後又多挖出 139 條 renderer 字串（三元運算 `t(a ? 'X' : 'Y')`、`api.translate()`、`registerToDo` 這些壓縮版抓不到的形式）。

四個壓縮版掃描器現在只當交叉驗證用；`sources_missing.txt` 最後一節會列出「壓縮版有、原始碼沒有」的鍵，目前只剩斷句碎片。

### 套用一批新翻譯

標準流程：跑 `scan_sources.py` → 把 `sources_missing.json`（已依 namespace 分組）複製成 `patch_<說明>.json` 填譯文 → 套用：

```bash
cd _tools && ELECTRON_RUN_AS_NODE=1 ELECTRON_NO_ASAR=1 "/c/Program Files/Black Tree Gaming Ltd/Vortex/Vortex.exe" apply.js patch_xxx.json && py -3.11 -X utf8 sync_appdata.py
```

2026-09-12 用過的 patch 都留在 `_tools\`（`patch_api_renderer.json`、`patch_src_renderer.json`、`patch_src_ext1~3.json`），要回查某條譯文出處可以 grep。

會併入 `common.json`、依鍵長度重新排序（與既有檔案的順序逐位元組一致），並做**佔位符一致性檢查**（比對譯文與原文的 `{{變數}}` 和 `$t()`）。這類錯誤在畫面上只會顯示成空白或原始標記，肉眼很難抓，務必每次都看報告；有不一致時 exit code 為 1。譯文留空的鍵會跳過，所以可以分批填。

分組格式下擴充套件的字串會自動同時寫進 `<ns>.json` 與 `common.json`（原因見第 3-3 節）；扁平格式要自己加 `--ns <擴充套件名>`。namespace 名稱就是 `bundledPlugins\` 下的資料夾名。ID 式鍵（`health_check` 這類）不走 patch，照 `patch_health_check_263.py` 的做法直接改巢狀 `.json`。

**刻意不翻的**：遊戲名稱（`Witcher 3`、`Baldur's Gate 3`…）、`ID` / `URL` / `MD5` / `Vortex`、錯誤代碼（`ENOENT`）、單獨出現且語意依上下文的介詞（`by` / `or` / `to` / `and`）。`sources_missing.json` 裡這些留空即可，`apply.js` 會跳過。

### 五個踩過的坑

1. **`process.noAsar = true` 不能拿掉**，指令也要帶 `ELECTRON_NO_ASAR=1` — Electron 會攔截所有含 `.asar` 的路徑當成壓縮包內部路徑，不關掉就讀不到 `app.asar` 本身。
2. **`bundledPlugins\` 全部是 `unpacked`** — asar 目錄裡只有中繼資料，實際內容在 `app.asar.unpacked\`。讀取器沒處理這點會拿到空字串，掃描結果看起來「這個擴充套件沒有字串」，很難察覺。
3. **跳脫序列要還原** — 靜態抽到的是字面 `\n`，真正的 key 含真換行，不還原就永遠對不上。單引號字串內的裸雙引號（`t('... "3 months ago" ...')`）也一樣，不能直接丟 `JSON.parse`。這個 bug 當初讓 58 條真實的鍵被靜默吃掉。
4. **不要用 PowerShell 的 `ConvertFrom-Json`** — 它對鍵**不分大小寫**，會把 `Add tool` 和 `Add Tool` 誤判成重複鍵而拋錯，但 JSON 的鍵是分大小寫的。用 Python 或 Node 處理。
5. **在 Claude Code 裡用 Bash heredoc 寫檔會把連續兩個反斜線 `\\` 吃成一個 `\`** — regex 裡的 `[^'\\\n]` 落地變成 `[^'\\n]`，悄悄失效（抓到 359 條而不是 1169 條）。含反斜線的檔案要用 Write / Edit 工具寫，不要用 `cat <<'EOF'`（連本條說明第一次寫進來時都被吃掉了）。

---

## 十、下一步建議

1. **正常使用，看到英文就截圖**——靜態掃描能抓的已經抓完（見第九節結果表），剩下的是硬編碼（第六節第 3 點）或執行期才組出來的字串
2. **1608 條新譯文尚未經過實機檢視**——都是照術語表翻的，但長句的語氣與畫面配合要實際看過才知道；發現不順就改 `locales\zh-TW\` 對應檔案再 `sync_appdata.py`
3. Vortex 更新後跑 `scan_sources.py`（主力）確認落差，其他三個當交叉驗證
4. 想抓執行期才組出來的字串，裝官方的 [Translation Helper](https://www.nexusmods.com/site/mods/28)
5. 要發布就跑 `make_release.py`，zip 上傳 Nexus（分類：Vortex Translations）
