"""從 app.asar 內附的 source map 讀出原始 TypeScript，直接掃乾淨的原始碼。

    py -3.11 -X utf8 scan_sources.py             → sources_missing.txt / sources_missing.json
    py -3.11 -X utf8 scan_sources.py --dump      → 另外把原始碼倒到 _tools\sources\ 方便 grep

原料：
    renderer.js.map                     → sourcesContent 含 Vortex 自己的 971 個 .ts/.tsx
    bundledPlugins\\<ext>\\index.*.map     → 68 個內建擴充套件的原始碼
    bundledPlugins\\<ext>\\*.js（沒 map 的）→ 本來就是未壓縮的 JS，直接掃
這是與安裝版本完全一致的未壓縮原始碼；壓縮才造成的別名問題（CLAUDE.md 第五節）在這裡不存在。

抓的形式：
    t('…')  props.t('…')  api.translate('…')                         ← 一般 t()
    api.sendNotification({ title: '…', message: '…' })
    api.showDialog('error', '標題', { text|message|bbcode: '…' })
    showError(dispatch, '標題', …)  api.showErrorNotification('標題', '內文')
    actions: [{ title: '…' }]  [{ label: '…' }]
    super(id, '部署方式名稱', '說明')
    registerMainPage / registerSettings / registerDashlet / registerAction / registerToDo 的標題
原始碼裡長字串常用 'aaa ' + 'bbb' 分行接起來，掃之前會先合併。

刻意跳過：*.demo.tsx、design_system_dev、__tests__、含 ${} 的模板字串、看起來像識別字的單字。
"""
from __future__ import annotations

import bisect
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from vortex_paths import TOOLS_DIR, find_vortex_dir, open_asar
from scan_aliases import load_translated, unescape_js

# ---- 字串字面值 -------------------------------------------------------------

STR = r"(?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"|`((?:[^`\\$]|\\.|\$(?!\{))*)`)"
STR_RE = re.compile(STR, re.S)
CONCAT_RE = re.compile(STR + r"(?:\s*\+\s*" + STR + r")+", re.S)


def lit_value(m, base=1):
    for i in range(base, base + 3):
        if m.group(i) is not None:
            return unescape_js(m.group(i))
    return None


def merge_concat(src: str) -> str:
    """把 'a' + 'b' + `c` 合併成單一個 "ab c" 字面值（JSON 跳脫 = 合法 JS 跳脫）。"""
    def repl(m):
        parts = [lit_value(x) for x in STR_RE.finditer(m.group(0))]
        return json.dumps("".join(parts), ensure_ascii=False)
    return CONCAT_RE.sub(repl, src)


# ---- 抓取樣式 ---------------------------------------------------------------

W = r"\s*"
PATTERNS = {
    "t":                      re.compile(r"(?<![\w$])t\(" + W + STR, re.S),
    "translate":              re.compile(r"(?<![\w$])translate\(" + W + STR, re.S),
    "sendNotification.title": re.compile(r"sendNotification\(\s*\{[^{}]{0,600}?(?<![\w$])title:" + W + STR, re.S),
    "sendNotification.msg":   re.compile(r"sendNotification\(\s*\{[^{}]{0,600}?(?<![\w$])message:" + W + STR, re.S),
    "showDialog.title":       re.compile(r"showDialog\(" + W + r"['\"`]\w+['\"`]" + W + "," + W + STR, re.S),
    "showDialog.text":        re.compile(r"showDialog\(" + W + r"['\"`]\w+['\"`]" + W + "," + W + STR + W + "," + W + r"\{" + W + r"(?:text|message|bbcode):" + W + STR, re.S),
    "showError.title":        re.compile(r"showError\(" + W + r"[\w$.]+" + W + "," + W + STR, re.S),
    "showErrorNotification":  re.compile(r"show(?:Error|Success|Info|Activity)?Notification\(" + W + STR, re.S),
    "showErrorNotification.2": re.compile(r"showErrorNotification\(" + W + STR + W + "," + W + STR, re.S),
    "showActivity":           re.compile(r"showActivity\(" + W + STR, re.S),
    "action.title":           re.compile(r"[{,]\s*title:" + W + STR + W + r",\s*action:", re.S),
    "action.label":           re.compile(r"[{,]\s*label:" + W + STR + W + r"[},]", re.S),
    "deployment.super":       re.compile(r"super\(" + W + STR + W + "," + W + STR + W + "," + W + STR, re.S),
    "registerMainPage":       re.compile(r"registerMainPage\(" + W + STR + W + "," + W + STR, re.S),
    "registerSettings":       re.compile(r"registerSettings\(" + W + STR, re.S),
    "registerDashlet":        re.compile(r"registerDashlet\(" + W + STR, re.S),
    # registerAction(group, position, icon, options, title, action, condition)
    "registerAction":         re.compile(r"registerAction\(" + W + STR + W + "," + W + r"[^,]+," + W + r"[^,]+," + W + r"(?:\{[^{}]*\}|[\w$.]+)" + W + "," + W + STR, re.S),
    "registerToDo":           re.compile(r"registerToDo\([^()]{0,300}?" + STR, re.S),
}
GROUP_STARTS = {
    "showDialog.text": (4,),
    "showErrorNotification.2": (4,),
    "deployment.super": (4, 7),
    "registerMainPage": (4,),
    "registerAction": (4,),
}

SKIP_FILE = re.compile(r"\.demo\.tsx?$|design_system_dev|__tests__|\.test\.|\.spec\.|/tests?/", re.I)


def looks_like_noise(key: str) -> bool:
    if "${" in key or not key.strip():
        return True
    if not re.search(r"[A-Za-z]", key):
        return True
    if key.startswith("<") or "{{" in key:       # <None>、{{rating}}% 這類是真的 UI 字串
        return False
    # 單一 token 且非大寫開頭：多半是 id / 路徑 / 事件名
    if not re.search(r"\s", key) and not key[0].isupper():
        return True
    if re.fullmatch(r"[\w.\-/:]+", key) and key.islower():
        return True
    return False


# ---- 原料 -------------------------------------------------------------------

def units(asar):
    """yield (unit, file, source)"""
    m = json.loads(asar.read("renderer.js.map"))
    for src, content in zip(m["sources"], m.get("sourcesContent") or []):
        if content and "node_modules" not in src and "/./src/" in src:
            yield "renderer", re.sub(r"^webpack://@vortex/renderer/\./", "", src), content

    plugins = sorted({p.split("/")[1] for p in asar.list() if p.startswith("bundledPlugins/")})
    for ext in plugins:
        files = [p for p in asar.list() if p.startswith(f"bundledPlugins/{ext}/")]
        maps = [p for p in files if p.endswith(".map")]
        if maps:
            for mp in maps:
                m = json.loads(asar.read(mp))
                for src, content in zip(m["sources"], m.get("sourcesContent") or []):
                    if content and "node_modules" not in src:
                        yield ext, re.sub(r"^(\.\./)+", "", src), content
        else:
            for p in files:
                if re.search(r"\.(js|cjs|mjs)$", p) and "/node_modules/" not in p:
                    yield ext, p.split("/", 2)[2], asar.read(p)


# ---- 主流程 -------------------------------------------------------------------

def main():
    dump = "--dump" in sys.argv
    vortex_dir = find_vortex_dir()
    asar = open_asar(vortex_dir)
    translated = load_translated()

    hits: dict[str, set[str]] = defaultdict(set)     # key -> {"unit:file:line (form)"}
    per_unit: dict[str, set[str]] = defaultdict(set)
    n_files = 0
    for unit, file, content in units(asar):
        if SKIP_FILE.search(file):
            continue
        n_files += 1
        if dump:
            out = TOOLS_DIR / "sources" / unit / file
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, "utf-8")
        src = merge_concat(content)
        nl = [m.start() for m in re.finditer("\n", src)]
        for form, pat in PATTERNS.items():
            for m in pat.finditer(src):
                for base in GROUP_STARTS.get(form, (1,)):
                    k = lit_value(m, base)
                    if k is None:
                        continue
                    line = bisect.bisect(nl, m.start()) + 1
                    hits[k].add(f"{unit}:{file}:{line} ({form})")
                    per_unit[unit].add(k)

    missing, found, noise = [], [], []
    for k in hits:
        if looks_like_noise(k):
            noise.append(k)
        elif k in translated or k.split(":::")[-1] in translated:
            found.append(k)
        else:
            missing.append(k)
    missing.sort(key=lambda k: (len(k), k))
    miss_set = set(missing)

    # 交叉驗證：壓縮版掃描器抓到、原始碼掃描卻沒抓到的鍵
    minified = set()
    for f in ("missing.json", "alias_missing.json", "api_missing.json"):
        p = TOOLS_DIR / f
        if p.exists():
            minified |= set(json.loads(p.read_text("utf-8")))
    only_minified = sorted(k for k in minified if k not in hits and not looks_like_noise(k))

    lines = [
        f"Vortex {asar.version()}  {vortex_dir}",
        f"原始檔 {n_files} 個；唯一鍵 {len(hits)} 條：已翻譯 {len(found)}、未翻譯 {len(missing)}、雜訊 {len(noise)}",
        "",
        "各單元（唯一鍵 / 未翻譯）：",
    ]
    for unit, keys in sorted(per_unit.items(), key=lambda kv: (-len(kv[1] & miss_set), -len(kv[1]))):
        if keys & miss_set or unit == "renderer":
            lines.append(f"  {len(keys):4d} / {len(keys & miss_set):3d}  {unit}")
    lines += ["", "未翻譯（依單元分組；[] 內是 檔案:行 (形式)）："]
    for unit, keys in sorted(per_unit.items(), key=lambda kv: -len(kv[1] & miss_set)):
        ks = sorted(keys & miss_set, key=lambda k: (len(k), k))
        if not ks:
            continue
        lines.append(f"\n## {unit}（{len(ks)}）")
        for k in ks:
            where = "; ".join(sorted(h.split(":", 1)[1] for h in hits[k] if h.startswith(unit + ":"))[:2])
            lines.append(f"  [{where}] {json.dumps(k, ensure_ascii=False)}")
    if only_minified:
        lines += ["", f"壓縮版掃描器有、原始碼掃描沒有的鍵（{len(only_minified)}，請人工確認）："]
        for k in only_minified:
            lines.append(f"  {json.dumps(k, ensure_ascii=False)}")
    if noise:
        lines += ["", f"判定為雜訊（{len(noise)}）："]
        for k in sorted(noise, key=lambda k: (len(k), k)):
            lines.append(f"  {json.dumps(k, ensure_ascii=False)}")

    (TOOLS_DIR / "sources_missing.txt").write_text("\n".join(lines) + "\n", "utf-8")
    by_unit = {u: {k: "" for k in sorted(keys & miss_set, key=lambda k: (len(k), k))} for u, keys in per_unit.items() if keys & miss_set}
    (TOOLS_DIR / "sources_missing.json").write_text(json.dumps(by_unit, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("\n".join(lines[:2]))
    print("→ sources_missing.txt / sources_missing.json（依單元分組）")


if __name__ == "__main__":
    main()
