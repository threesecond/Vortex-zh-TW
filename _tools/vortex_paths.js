// 共用：找 Vortex 安裝目錄、讀 app.asar、找語言檔目錄。
// 以 Vortex 自帶的 Electron 當 Node 執行（不需另裝 Node）：
//   ELECTRON_RUN_AS_NODE=1 ELECTRON_NO_ASAR=1 Vortex.exe <script>
//
// process.noAsar 必須為 true，否則 Electron 會把含 .asar 的路徑攔成壓縮包內部路徑，
// 讀不到 app.asar 本身。
process.noAsar = true;

const fs = require('fs');
const path = require('path');

const CANDIDATE_DIRS = [
  process.env.VORTEX_DIR,
  'C:\\Program Files\\Black Tree Gaming Ltd\\Vortex',
  'C:\\Program Files\\Vortex',
  process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'Programs', 'Vortex'),
].filter(Boolean);

function findVortexDir() {
  for (const dir of CANDIDATE_DIRS) {
    if (fs.existsSync(path.join(dir, 'resources', 'app.asar'))) return dir;
  }
  throw new Error('找不到 Vortex 安裝目錄，請設定環境變數 VORTEX_DIR。試過：\n  ' + CANDIDATE_DIRS.join('\n  '));
}

const TOOLS_DIR = __dirname;
const PROJECT_DIR = path.resolve(TOOLS_DIR, '..');
const LOCALE_DIR = path.join(PROJECT_DIR, 'locales', 'zh-TW');
const APPDATA_LOCALE_DIR = process.env.APPDATA ? path.join(process.env.APPDATA, 'Vortex', 'locales', 'zh-TW') : null;

// 最小 asar 讀取器（格式：pickle 標頭 + JSON 目錄 + 連續檔案內容）。
// bundledPlugins 全部是 unpacked，實際檔案在 app.asar.unpacked\ 下。
function openAsar(asarPath) {
  const buf = fs.readFileSync(asarPath);
  const headerLen = buf.readUInt32LE(12);
  const header = JSON.parse(buf.slice(16, 16 + headerLen).toString('utf8'));
  const base = 8 + buf.readUInt32LE(4);
  const files = {};
  (function walk(node, prefix) {
    for (const name of Object.keys(node.files)) {
      const entry = node.files[name];
      if (entry.files) walk(entry, prefix + name + '/');
      else files[prefix + name] = entry;
    }
  })(header, '');

  function read(relPath) {
    const entry = files[relPath];
    if (!entry) throw new Error('asar 內沒有這個檔案：' + relPath);
    if (entry.unpacked) return fs.readFileSync(path.join(asarPath + '.unpacked', relPath), 'utf8');
    const offset = base + parseInt(entry.offset, 10);
    return buf.slice(offset, offset + entry.size).toString('utf8');
  }

  return { files, read, list: () => Object.keys(files) };
}

// 要掃描的原始碼：renderer.js + 每個內建擴充套件的頂層 js（不含它們的 node_modules）。
// main.cjs / bootstrap.mjs / preload.cjs 裡的 t( 全是別的函式（XDG_DATA_HOME、copy、stat…），不掃。
function sourceFiles(asar) {
  return asar.list().filter((p) =>
    p === 'renderer.js' ||
    /^bundledPlugins\/[^/]+\/[^/]+\.(js|cjs|mjs)$/.test(p));
}

// Vortex 內建的 en 語言檔目錄（ID 式鍵的 namespace 以此為準）
function bundledLocaleDir(vortexDir) {
  return path.join(vortexDir, 'resources', 'locales', 'en');
}

// renderer.js 裡 design_system_dev 示範頁的 webpack 模組範圍 [start, end)。
// 那些模組的字串（"Text Input"、"Bethesda Games"…）只在開發者示範頁出現，刻意不翻。
// 判定：模組 export 名稱以 Demo 結尾，或無名模組內含 Demo 字樣。（與 vortex_paths.py 的 demo_ranges 同邏輯）
function demoRanges(source) {
  const bounds = [];
  const re = /[,{]\d{3,6}\((?:__unused_webpack_module|module),exports/g;
  let m;
  while ((m = re.exec(source))) bounds.push(m.index);
  bounds.push(source.length);
  const out = [];
  for (let i = 0; i + 1 < bounds.length; i++) {
    const [a, b] = [bounds[i], bounds[i + 1]];
    const seg = source.slice(a, b);
    const nm = /exports\.(\w+)=/.exec(seg.slice(0, 400));
    const name = nm ? nm[1] : '';
    if (name.endsWith('Demo') || (!name && /\bDemo\b|Demo=\(|Demo,/.test(seg))) out.push([a, b]);
  }
  return out;
}

function inRanges(pos, ranges) {
  return ranges.some(([a, b]) => a <= pos && pos < b);
}

function vortexVersion(asar) {
  return JSON.parse(asar.read('package.json')).version;
}

module.exports = { findVortexDir, openAsar, sourceFiles, bundledLocaleDir, demoRanges, inRanges, vortexVersion, TOOLS_DIR, PROJECT_DIR, LOCALE_DIR, APPDATA_LOCALE_DIR };
