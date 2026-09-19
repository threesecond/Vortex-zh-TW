// 把一批新翻譯（扁平 {"原文": "譯文"} 的 patch JSON）併入 locales\zh-TW\common.json。
//
// 用法：
//   ... Vortex.exe apply.js patch_263.json            → 扁平格式 {"原文": "譯文"}，併入 common.json
//   ... Vortex.exe apply.js patch.json --ns theme-switcher
//        → 同時併入 theme-switcher.json 與 common.json（擴充套件字串要兩邊都寫，見 CLAUDE.md 第 3-3 節）
//   ... Vortex.exe apply.js sources_patch.json         → 分組格式 {"<ns>": {"原文": "譯文"}}（scan_sources.py 的產出），
//        每組寫 <ns>.json + common.json；"renderer" 組只寫 common.json
//   ... Vortex.exe apply.js patch.json --dry-run      → 只出報告不寫檔
//
// 產出 apply_report.txt。務必看報告：佔位符不一致在畫面上只會顯示成空白或原始 {{標記}}，肉眼很難抓。
//
// 規則：
//   - 譯文為空字串的鍵跳過（missing.json 直接填一半也能套）
//   - 帶 {{count}} 的鍵同時寫 base / _0 / _plural 三份相同譯文（中文 nplurals=1，靜態無法確定實際挑哪個）
//   - 寫回時依鍵長度重新排序（短的在前，同長度依字典序），與既有檔案一致

const fs = require('fs');
const path = require('path');
const { LOCALE_DIR, TOOLS_DIR } = require('./vortex_paths');

const args = process.argv.slice(2);
const patchFile = args.find((a) => !a.startsWith('--'));
const dryRun = args.includes('--dry-run');
const nsIdx = args.indexOf('--ns');
const extraNs = nsIdx >= 0 ? args[nsIdx + 1] : null;
if (!patchFile) { console.error('用法：apply.js <patch.json> [--ns <namespace>] [--dry-run]'); process.exit(2); }

// ---- 佔位符檢查 ------------------------------------------------------------

function placeholders(s) {
  // {{ count }} 與 {{count}} 視為同一個；$t(...) 巢狀翻譯也算
  const set = new Set();
  for (const m of s.matchAll(/\{\{\s*([^}]*?)\s*\}\}/g)) set.add('{{' + m[1] + '}}');
  for (const m of s.matchAll(/\$t\(([^)]*)\)/g)) set.add('$t(' + m[1] + ')');
  return set;
}

function placeholderDiff(key, value) {
  const a = placeholders(key), b = placeholders(value);
  const missing = [...a].filter((x) => !b.has(x));
  const extra = [...b].filter((x) => !a.has(x));
  return missing.length || extra.length ? { missing, extra } : null;
}

// ---- 讀寫 -------------------------------------------------------------------

function readJson(file) {
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
}

function sortByKeyLength(obj) {
  return Object.fromEntries(Object.entries(obj).sort(([a], [b]) => a.length - b.length || a.localeCompare(b)));
}

function writeJson(file, obj) {
  fs.writeFileSync(file, JSON.stringify(sortByKeyLength(obj), null, 2) + '\n', 'utf8');
}

// ---- 主流程 ---------------------------------------------------------------

const raw = JSON.parse(fs.readFileSync(path.resolve(patchFile), 'utf8'));
// 兩種格式：扁平 {"原文": "譯文"}，或依 namespace 分組 {"game-witcher3": {"原文": "譯文"}, ...}
// （scan_sources.py 的 sources_missing.json 就是分組格式，填完直接套）。
// 分組格式下每一組都寫進 <ns>.json 與 common.json；"renderer" 組只寫 common.json。
const grouped = Object.values(raw).every((v) => v && typeof v === 'object');
const groups = grouped ? Object.entries(raw) : [[extraNs, raw]];

const report = [];
report.push(`patch：${path.resolve(patchFile)}（${grouped ? Object.keys(raw).length + ' 組、' : ''}${groups.reduce((n, [, p]) => n + Object.keys(p).length, 0)} 條）${dryRun ? '（dry-run，未寫檔）' : ''}`);
report.push('');

const problems = [];
const skippedEmpty = [];
const perFile = {};   // ns -> [ [key, value] ]  展開複數形之後
for (const [ns, patch] of groups) {
  const entries = [];
  for (const [key, value] of Object.entries(patch)) {
    if (typeof value !== 'string' || value.trim() === '') { skippedEmpty.push(key); continue; }
    const diff = placeholderDiff(key, value);
    if (diff) problems.push({ key, value, ...diff });
    entries.push([key, value]);
    if (/\{\{\s*count\s*\}\}/.test(key) && !/_(0|plural)$/.test(key)) {
      entries.push([key + '_0', value]);
      entries.push([key + '_plural', value]);
    }
  }
  const targets = ['common', ...(ns && ns !== 'renderer' && ns !== 'common' ? [ns] : [])];
  for (const t of targets) (perFile[t] = perFile[t] || []).push(...entries);
}

for (const ns of Object.keys(perFile).sort((a, b) => (a === 'common' ? -1 : b === 'common' ? 1 : a.localeCompare(b)))) {
  const file = path.join(LOCALE_DIR, ns + '.json');
  const data = readJson(file);
  let added = 0, updated = 0, same = 0;
  const updatedList = [];
  for (const [k, v] of perFile[ns]) {
    if (!(k in data)) added++;
    else if (data[k] === v) same++;
    else { updated++; updatedList.push([k, data[k], v]); }
    data[k] = v;
  }
  if (!dryRun) writeJson(file, data);
  report.push(`${ns}.json：新增 ${added}、更新 ${updated}、相同 ${same}，寫入後共 ${Object.keys(data).length} 條`);
  for (const [k, oldV, newV] of updatedList) report.push(`  更新 ${JSON.stringify(k)}\n    舊：${JSON.stringify(oldV)}\n    新：${JSON.stringify(newV)}`);
}

if (skippedEmpty.length) {
  report.push('');
  report.push(`譯文為空、跳過 ${skippedEmpty.length} 條：`);
  for (const k of skippedEmpty) report.push('  ' + JSON.stringify(k));
}
if (problems.length) {
  report.push('');
  report.push(`!! 佔位符不一致 ${problems.length} 條（已寫入，請立刻修正）：`);
  for (const p of problems) {
    report.push(`  ${JSON.stringify(p.key)}`);
    report.push(`    譯文：${JSON.stringify(p.value)}`);
    if (p.missing.length) report.push(`    譯文缺少：${p.missing.join(' ')}`);
    if (p.extra.length) report.push(`    譯文多出：${p.extra.join(' ')}`);
  }
} else {
  report.push('');
  report.push('佔位符檢查：全部一致');
}

fs.writeFileSync(path.join(TOOLS_DIR, 'apply_report.txt'), report.join('\n') + '\n', 'utf8');
console.log(report.join('\n'));
if (problems.length) process.exit(1);
