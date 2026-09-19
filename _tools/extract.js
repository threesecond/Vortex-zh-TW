// 從 app.asar 抽出所有 t('...') / .t('...') 的字串鍵，與 locales\zh-TW\*.json 對帳。
//
// 用法（Git Bash）：
//   cd _tools && ELECTRON_RUN_AS_NODE=1 ELECTRON_NO_ASAR=1 "/c/Program Files/Black Tree Gaming Ltd/Vortex/Vortex.exe" extract.js
// 用法（pwsh）：
//   $env:ELECTRON_RUN_AS_NODE=1; $env:ELECTRON_NO_ASAR=1; & 'C:\Program Files\Black Tree Gaming Ltd\Vortex\Vortex.exe' extract.js
//
// 產出：report.txt（覆蓋率 + 缺漏清單）、missing.json（{"原文": ""} 可直接填成 patch）
//
// 只認 t( 這個名字。壓縮後被改名的呼叫（e(`...`) 之類）由 scan_aliases.py 處理。

const fs = require('fs');
const path = require('path');
const { findVortexDir, openAsar, sourceFiles, bundledLocaleDir, demoRanges, inRanges, vortexVersion, LOCALE_DIR, TOOLS_DIR } = require('./vortex_paths');

// ---- 字串抽取 -------------------------------------------------------------

// 前面不能是識別字字元（避免 fetch( / split( 之類），但允許 `.t(`（this.props.t(...)）。
const CALL_RE = /(?<![\w$])t\(\s*(?:'((?:[^'\\\n]|\\.)*)'|"((?:[^"\\\n]|\\.)*)"|`((?:[^`\\$]|\\.|\$(?!\{))*)`)/g;

// 還原 JS 字串字面值的跳脫序列。靜態抽到的是字面上的 \n，真正的 key 含真換行，不還原就對不上。
function unescapeJs(raw) {
  return raw.replace(/\\(u\{([0-9a-fA-F]+)\}|u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2})|\r?\n|.)/gs, (m, all, uBrace, u4, x2) => {
    if (uBrace) return String.fromCodePoint(parseInt(uBrace, 16));
    if (u4) return String.fromCharCode(parseInt(u4, 16));
    if (x2) return String.fromCharCode(parseInt(x2, 16));
    if (all === '\n' || all === '\r\n') return '';   // 行接續
    return { n: '\n', t: '\t', r: '\r', b: '\b', f: '\f', v: '\v', 0: '\0' }[all] ?? all;
  });
}

function extractKeys(source, demos = []) {
  const keys = [];
  let m;
  CALL_RE.lastIndex = 0;
  while ((m = CALL_RE.exec(source))) {
    if (inRanges(m.index, demos)) continue;   // design_system_dev 示範頁，刻意不翻
    const raw = m[1] ?? m[2] ?? m[3];
    keys.push(unescapeJs(raw));
  }
  return keys;
}

// ---- 譯檔載入 -------------------------------------------------------------

// i18next keySeparator 是 "::"，巢狀 JSON 攤平成 a::b；同時也保留 a.b（isNamespaceKey 的元件用預設分隔符）。
function flatten(obj, prefix, out) {
  for (const [k, v] of Object.entries(obj)) {
    if (v && typeof v === 'object') {
      flatten(v, prefix ? prefix + '::' + k : k, out);
      flatten(v, prefix ? prefix + '.' + k : k, out);
    } else {
      out.add(prefix ? prefix + '::' + k : k);
      if (prefix) out.add(prefix + '.' + k);
    }
  }
}

function loadTranslations(dir) {
  const perNs = {};
  const all = new Set();
  for (const f of fs.readdirSync(dir).filter((f) => f.endsWith('.json'))) {
    const ns = f.replace(/\.json$/, '');
    const set = new Set();
    flatten(JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')), '', set);
    perNs[ns] = set;
    for (const k of set) all.add(k);
  }
  return { perNs, all };
}

// ---- 主流程 ---------------------------------------------------------------

function main() {
  const vortexDir = findVortexDir();
  const asar = openAsar(path.join(vortexDir, 'resources', 'app.asar'));
  const version = vortexVersion(asar);
  const { all: translated, perNs: translated_perNs } = loadTranslations(LOCALE_DIR);

  const bySource = {};          // file -> Set(key)
  const keyToSources = new Map(); // key -> Set(file)
  let totalCalls = 0;
  for (const file of sourceFiles(asar)) {
    const source = asar.read(file);
    const keys = extractKeys(source, file === 'renderer.js' ? demoRanges(source) : []);
    if (keys.length === 0) continue;
    totalCalls += keys.length;
    bySource[file] = new Set(keys);
    for (const k of keys) {
      if (!keyToSources.has(k)) keyToSources.set(k, new Set());
      keyToSources.get(k).add(file);
    }
  }

  // 分類
  const ignored = [];   // 模板殘留、空字串
  const idKeys = [];    // ID 式鍵（detail::item::adult 這種），改由下面的 namespace 比對處理
  const missing = [];
  const found = [];
  for (const key of keyToSources.keys()) {
    let k = key;
    if (k.includes(':::')) k = k.split(':::').pop();   // ns:::key → 只比 key
    if (k.trim() === '' || k.includes('${')) { ignored.push(key); continue; }
    if (/^[a-z0-9_]+(::[a-z0-9_]+)+$/.test(k)) { idKeys.push(key); continue; }
    (translated.has(k) ? found : missing).push(key);
  }
  const byLen = (a, b) => a.length - b.length || a.localeCompare(b);
  missing.sort(byLen);
  ignored.sort(byLen);

  // report.txt
  const lines = [];
  lines.push(`Vortex ${version}  ${vortexDir}`);
  lines.push(`譯檔：${LOCALE_DIR}（${translated.size} 個可比對鍵）`);
  lines.push(`產生時間：${new Date().toISOString()}`);
  lines.push('');
  lines.push(`t() 呼叫 ${totalCalls} 次，唯一鍵 ${keyToSources.size} 條`);
  lines.push(`  已翻譯 ${found.length}`);
  lines.push(`  未翻譯 ${missing.length}`);
  lines.push(`  略過   ${ignored.length}（模板殘留 \${...} 或空字串）`);
  lines.push(`  ID 式鍵 ${idKeys.length}（見最後一節的 namespace 比對）`);
  lines.push('');
  lines.push('各來源檔（唯一鍵 / 未翻譯）：');
  const missingSet = new Set(missing);
  for (const [file, keys] of Object.entries(bySource).sort((a, b) => b[1].size - a[1].size)) {
    const miss = [...keys].filter((k) => missingSet.has(k)).length;
    lines.push(`  ${String(keys.size).padStart(4)} / ${String(miss).padStart(3)}  ${file}`);
  }
  if (missing.length) {
    lines.push('');
    lines.push('未翻譯（依長度排序，[] 內是來源）：');
    for (const k of missing) {
      const src = [...keyToSources.get(k)].map((f) => f.replace(/^bundledPlugins\/([^/]+)\/.*/, '$1')).join(',');
      lines.push(`  [${src}] ${JSON.stringify(k)}`);
    }
  }
  if (ignored.length) {
    lines.push('');
    lines.push('略過：');
    for (const k of ignored) lines.push(`  ${JSON.stringify(k)}`);
  }

  // ---- ID 式鍵：直接拿 Vortex 內建 en\<ns>.json 對 zh-TW\<ns>.json ----
  // health_check / collection 這類新模組整包用 ID 當 key，t('detail::item::adult') 在程式碼裡
  // 看得到，但 en 檔裡還有很多 key 是在資料驅動下才會用到，靜態掃不到，所以整檔比對。
  const nsMissing = {};   // ns -> [key]
  lines.push('');
  lines.push('ID 式鍵 namespace（對照內建 en\\<ns>.json）：');
  for (const f of fs.readdirSync(bundledLocaleDir(vortexDir)).filter((f) => f.endsWith('.json')).sort()) {
    const ns = f.replace(/\.json$/, '');
    const en = new Set();
    flatten(JSON.parse(fs.readFileSync(path.join(bundledLocaleDir(vortexDir), f), 'utf8')), '', en);
    const enKeys = [...en].filter((k) => !k.includes('.') && k !== '_comment');   // 只留 :: 形式
    if (enKeys.length === 0) { lines.push(`  ${ns}: en 是空殼（只有 _comment）`); continue; }
    const mine = translated_perNs[ns] || new Set();
    const miss = enKeys.filter((k) => !mine.has(k) && !(k.endsWith('_plural') && mine.has(k.replace(/_plural$/, '_0'))));
    lines.push(`  ${ns}: en ${enKeys.length} 條，zh-TW 缺 ${miss.length}${translated_perNs[ns] ? '' : '（zh-TW 沒有這個檔）'}`);
    if (miss.length) nsMissing[ns] = miss;
  }
  for (const [ns, keys] of Object.entries(nsMissing)) {
    lines.push('');
    lines.push(`  ${ns}.json 缺（英文原文見內建 en\\${ns}.json）：`);
    for (const k of keys) lines.push(`    ${k}`);
  }
  fs.writeFileSync(path.join(TOOLS_DIR, 'report.txt'), lines.join('\n') + '\n', 'utf8');

  // missing.json：可直接填譯文當 patch 用（只含 common 那類「英文原文當 key」的鍵；
  // ID 式鍵請直接改對應的 <ns>.json，結構要跟 en 一樣是巢狀的）
  const patch = {};
  for (const k of missing) patch[k] = '';
  fs.writeFileSync(path.join(TOOLS_DIR, 'missing.json'), JSON.stringify(patch, null, 2) + '\n', 'utf8');

  console.log(`Vortex ${version}：唯一鍵 ${keyToSources.size}，已翻譯 ${found.length}，未翻譯 ${missing.length}，略過 ${ignored.length}`);
  console.log('→ report.txt / missing.json');
}

main();
