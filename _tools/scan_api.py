"""撈「不經 t() 但 Vortex 執行時會自己翻譯」的字串：通知、對話框標題、錯誤標題、部署方式名稱等。

    py -3.11 -X utf8 scan_api.py

這些字串在原始碼裡不是 t('...')，而是傳給 API 後由 Vortex 內部再 translate：
    api.sendNotification({ title: '...', message: '...' })
    api.showDialog('error', 'Title', ...)
    showError(dispatch, 'Title', err, ...)
    api.showErrorNotification('Title', ...)
    actions: [{ title: 'More', ... }]、[{ label: 'Close' }]
    super('symlink_activator', 'Symlink Deployment', 'Deploys mods by ...')   ← 部署方式的名稱與說明
    registerMainPage('icon', 'Title', ...)、registerSettings('Title', ...)、registerDashlet('Title', ...)
所以 extract.js / scan_aliases.py 都抓不到，畫面上卻會顯示英文。

產出：api_missing.txt、api_missing.json（{"原文": ""} 可直接填成 patch）
"""
from __future__ import annotations

import json
import re
from collections import defaultdict

from vortex_paths import TOOLS_DIR, demo_ranges, find_vortex_dir, in_ranges, open_asar, source_files
from scan_aliases import STR, load_translated, looks_like_noise, pick, unescape_js

S = STR
PATTERNS = {
    "sendNotification.title":   re.compile(r"sendNotification\(\{[^{}]{0,200}?(?<![\w$])title:" + S),
    "sendNotification.message": re.compile(r"sendNotification\(\{[^{}]{0,200}?(?<![\w$])message:" + S),
    "showDialog.title":         re.compile(r"showDialog\(\s*['\"`]\w+['\"`]\s*,\s*" + S),
    "showDialog.text":          re.compile(r"showDialog\(\s*['\"`]\w+['\"`]\s*,\s*" + S + r"\s*,\s*\{\s*(?:text|message|bbcode):" + S),
    "showError.title":          re.compile(r"showError\)?\(\s*[\w$.]+\s*,\s*" + S),
    "showErrorNotification":    re.compile(r"showErrorNotification\(\s*" + S),
    "showErrorNotification.2":  re.compile(r"showErrorNotification\(\s*" + S + r"\s*,\s*" + S),
    "showSuccessNotification":  re.compile(r"showSuccessNotification\(\s*" + S),
    "action.title":             re.compile(r"[{,]title:" + S + r"\s*,\s*action:"),
    "action.label":             re.compile(r"[{,]label:" + S + r"\s*[},]"),
    "deployment.super":         re.compile(r"super\(\s*" + S + r"\s*,\s*" + S + r"\s*,\s*" + S),
    "registerMainPage":         re.compile(r"registerMainPage\(\s*" + S + r"\s*,\s*" + S),
    "registerSettings":         re.compile(r"registerSettings\(\s*" + S),
    "registerDashlet":          re.compile(r"registerDashlet\(\s*" + S),
    "registerAction.title":     re.compile(r"registerAction\([^()]{0,120}?,\s*" + S + r"\s*,\s*(?:\(\)\s*=>|function|[\w$.]+\s*[,)])"),
    "registerToDo":             re.compile(r"registerToDo\([^()]{0,200}?" + S),
}
# 每個 pattern 裡 STR 群組有 3 個；要取哪幾組（1-based 起點）
GROUP_STARTS = {
    "showDialog.text": (1, 4),
    "showErrorNotification.2": (1, 4),
    "deployment.super": (4, 7),          # 第 1 組是 id，跳過
    "registerMainPage": (4,),            # 第 1 組是 icon
    "registerAction.title": (1,),
}


def main():
    vortex_dir = find_vortex_dir()
    asar = open_asar(vortex_dir)
    translated = load_translated()
    key_src: dict[str, set[str]] = defaultdict(set)

    for f in source_files(asar):
        src = asar.read(f)
        short = re.sub(r"^bundledPlugins/([^/]+)/.*", r"\1", f)
        demos = demo_ranges(src) if f == "renderer.js" else []
        for name, pat in PATTERNS.items():
            for m in pat.finditer(src):
                if in_ranges(m.start(), demos):
                    continue
                for base in GROUP_STARTS.get(name, (1,)):
                    k = pick(m, base)
                    if k is not None:
                        key_src[k].add(f"{short}:{name}")

    missing, found, noise = [], [], []
    for k in key_src:
        if looks_like_noise(k) or re.search(r"^[a-z0-9_-]+$", k):
            noise.append(k)
        elif k in translated:
            found.append(k)
        else:
            missing.append(k)
    missing.sort(key=lambda k: (len(k), k))

    lines = [
        f"Vortex {asar.version()}  {vortex_dir}",
        f"API 註冊式字串唯一鍵 {len(key_src)} 條：已翻譯 {len(found)}、未翻譯 {len(missing)}、雜訊 {len(noise)}",
        "",
        "未翻譯（[] 內是 來源:形式）：",
    ]
    for k in missing:
        lines.append(f"  [{','.join(sorted(key_src[k]))}] {json.dumps(k, ensure_ascii=False)}")
    (TOOLS_DIR / "api_missing.txt").write_text("\n".join(lines) + "\n", "utf-8")
    (TOOLS_DIR / "api_missing.json").write_text(json.dumps({k: "" for k in missing}, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print("\n".join(lines[:2]))
    print("→ api_missing.txt / api_missing.json")


if __name__ == "__main__":
    main()
