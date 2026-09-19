"""反推壓縮後的 t() 別名，撈出 extract.js 抓不到的翻譯鍵。

    py -3.11 -X utf8 scan_aliases.py

問題：程式碼壓縮後翻譯函式的名字不固定。核心是 t(...)，但許多擴充套件被壓成
    let{t:e,currentTheme:t}=this.props; ... e(`Appearance`)
extract.js 只認 t(，會整包漏掉。

做法：先找出 t 被綁到哪個名字（別名），再在那個名字的作用範圍內抓它的呼叫。
綁定的形式有三種：
    1. 解構     {t:e} / {foo:x,t:e,bar:y}         ← 最常見（this.props、useTranslation() 都是）
    2. 陣列解構 [e]=(0,r.useTranslation)(...)
    3. 直接指定 e=this.props.t / e=r.props.t
作用範圍靜態算不準，用啟發式：從綁定處往後掃，直到同一個名字被重新綁定或超過 WINDOW 個字元。

產出：alias_missing.txt（含來源、別名）、alias_missing.json（{"原文": ""} 可直接填成 patch）
"""
from __future__ import annotations

import json
import re
from collections import defaultdict

from vortex_paths import LOCALE_DIR, TOOLS_DIR, demo_ranges, find_vortex_dir, in_ranges, open_asar, source_files

WINDOW = 40_000  # 一個綁定往後最多看多遠（字元）

IDENT = r"[A-Za-z_$][\w$]*"
BIND_RES = [
    re.compile(r"[{,]t:(" + IDENT + r")[,}]"),
    re.compile(r"\[(" + IDENT + r")[\],][^=]{0,40}=\(0,[\w$]+\.useTranslation\)"),
    re.compile(r"(?<![\w$])(" + IDENT + r")=(?:[\w$]+\.)?props\.t(?![\w$])"),
]

STR = r"(?:'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`((?:[^`\\$]|\\.|\$(?!\{))*)`)"
# 直接以字串當第一個參數：e(`...`)
# 或三元運算兩邊都是字串：e(cond?`...`:`...`)
CALL_TPL = r"(?<![\w$.])%s\(\s*" + STR
TERNARY_TPL = r"(?<![\w$.])%s\(\s*[^()`'\"]{1,80}\?\s*" + STR + r"\s*:\s*" + STR

_ESC = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def unescape_js(raw: str) -> str:
    def sub(m):
        s = m.group(1)
        if s.startswith("u{"):
            return chr(int(s[2:-1], 16))
        if s[0] == "u":
            return chr(int(s[1:], 16))
        if s[0] == "x":
            return chr(int(s[1:], 16))
        if s in ("\n", "\r\n"):
            return ""
        return _ESC.get(s, s)
    return re.sub(r"\\(u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|\r?\n|.)", sub, raw, flags=re.S)


def pick(m, base):
    for i in range(base, base + 3):
        if m.group(i) is not None:
            return unescape_js(m.group(i))
    return None


def flatten(obj, prefix, out):
    for k, v in obj.items():
        if isinstance(v, dict):
            flatten(v, f"{prefix}{k}::", out)
        else:
            out.add(prefix + k)


def load_translated() -> set[str]:
    out: set[str] = set()
    for f in LOCALE_DIR.glob("*.json"):
        flatten(json.loads(f.read_text("utf-8")), "", out)
    return out


def looks_like_noise(key: str) -> bool:
    """沒有空白、又不是大寫開頭的單一 token（div、md5、theme-x）多半是別的函式的參數，不是 UI 字串。"""
    if "${" in key or not key.strip():
        return True
    if not re.search(r"[A-Za-z]", key):          # {{ value }}、純符號
        return True
    if not re.search(r"\s", key) and not key[0].isupper():
        return True
    return False


def scan(source: str, demos=()):
    """回傳 [(key, alias, pos)]"""
    binds: list[tuple[int, str]] = []
    for r in BIND_RES:
        for m in r.finditer(source):
            binds.append((m.end(), m.group(1)))
    binds.sort()
    # 每個名字的所有綁定位置，用來決定作用範圍
    by_name: dict[str, list[int]] = defaultdict(list)
    for pos, name in binds:
        by_name[name].append(pos)

    hits = []
    for pos, name in binds:
        if name == "t":            # extract.js 已處理
            continue
        later = [p for p in by_name[name] if p > pos]
        end = min(pos + WINDOW, later[0] if later else len(source))
        region = source[pos:end]
        esc = re.escape(name)
        for m in re.finditer(CALL_TPL % esc, region):
            k = pick(m, 1)
            if k is not None and not in_ranges(pos + m.start(), demos):
                hits.append((k, name, pos + m.start()))
        for m in re.finditer(TERNARY_TPL % esc, region):
            if in_ranges(pos + m.start(), demos):
                continue
            for base in (1, 4):
                k = pick(m, base)
                if k is not None:
                    hits.append((k, name, pos + m.start()))
    return hits


def main():
    vortex_dir = find_vortex_dir()
    asar = open_asar(vortex_dir)
    translated = load_translated()

    key_sources: dict[str, set[str]] = defaultdict(set)
    per_file: dict[str, set[str]] = {}
    for f in source_files(asar):
        src = asar.read(f)
        hits = scan(src, demo_ranges(src) if f == "renderer.js" else [])
        if not hits:
            continue
        short = re.sub(r"^bundledPlugins/([^/]+)/.*", r"\1", f)
        per_file[short] = {k for k, _, _ in hits}
        for k, alias, _ in hits:
            key_sources[k].add(f"{short}:{alias}")

    missing, found, noise = [], [], []
    for k in key_sources:
        if looks_like_noise(k):
            noise.append(k)
        elif k in translated:
            found.append(k)
        else:
            missing.append(k)
    missing.sort(key=lambda k: (len(k), k))
    noise.sort(key=lambda k: (len(k), k))

    lines = [
        f"Vortex {asar.version()}  {vortex_dir}",
        f"別名呼叫抓到唯一鍵 {len(key_sources)} 條：已翻譯 {len(found)}、未翻譯 {len(missing)}、判定為雜訊 {len(noise)}",
        "",
        "各來源檔（唯一鍵 / 未翻譯）：",
    ]
    miss_set = set(missing)
    for name, keys in sorted(per_file.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"  {len(keys):4d} / {len(keys & miss_set):3d}  {name}")
    if missing:
        lines += ["", "未翻譯（[] 內是 來源:別名）："]
        for k in missing:
            lines.append(f"  [{','.join(sorted(key_sources[k]))}] {json.dumps(k, ensure_ascii=False)}")
    if noise:
        lines += ["", "判定為雜訊、未列入（若其中有真的 UI 字串，直接手動加進 patch）："]
        for k in noise:
            lines.append(f"  [{','.join(sorted(key_sources[k]))}] {json.dumps(k, ensure_ascii=False)}")

    (TOOLS_DIR / "alias_missing.txt").write_text("\n".join(lines) + "\n", "utf-8")
    (TOOLS_DIR / "alias_missing.json").write_text(json.dumps({k: "" for k in missing}, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("\n".join(lines[:2]))
    print("→ alias_missing.txt / alias_missing.json")


if __name__ == "__main__":
    main()
