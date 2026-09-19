"""查某段文字在 Vortex 原始碼裡是怎麼被呼叫的——判斷「這句能不能翻」時用。

    py -3.11 -X utf8 probe.py "Some community themes"          → 在所有來源檔裡找
    py -3.11 -X utf8 probe.py "Hide Resolved" --before 400     → 往前多印一點（預設 200 字元）
    py -3.11 -X utf8 probe.py "Hide Resolved" --file bundledPlugins/mod-dependency-manager/index.cjs
    py -3.11 -X utf8 probe.py "Hide Resolved" --all            → 也搜 node_modules 之類的非來源檔

看前文就知道它是 t(...)、e(...)（別名）、還是根本不是翻譯呼叫（例如 log 訊息、註冊式標籤）。
"""
from __future__ import annotations

import sys

from vortex_paths import open_asar, source_files

MAX_HITS_PER_FILE = 5


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        raise SystemExit(__doc__)
    needle = args[0]
    before = int(args[args.index("--before") + 1]) if "--before" in args else 200
    after = int(args[args.index("--after") + 1]) if "--after" in args else 120
    only = args[args.index("--file") + 1] if "--file" in args else None

    asar = open_asar()
    files = [only] if only else (asar.list() if "--all" in args else source_files(asar))
    files = [f for f in files if f.endswith((".js", ".cjs", ".mjs", ".json"))]

    total = 0
    for f in files:
        try:
            s = asar.read(f)
        except (UnicodeDecodeError, KeyError):
            continue
        i, n = s.find(needle), 0
        while i >= 0:
            total += 1
            n += 1
            if n <= MAX_HITS_PER_FILE:
                print(f"=== {f} @{i}")
                print(s[max(0, i - before):i + len(needle) + after])
                print()
            i = s.find(needle, i + 1)
        if n > MAX_HITS_PER_FILE:
            print(f"    （{f} 還有 {n - MAX_HITS_PER_FILE} 處未列出）\n")
    print(f"共 {total} 處")


if __name__ == "__main__":
    main()
