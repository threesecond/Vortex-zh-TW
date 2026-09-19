"""把專案裡的 locales\\zh-TW\\*.json 同步到 Vortex 實際讀取的 %APPDATA%\\Vortex\\locales\\zh-TW\\。

    py -3.11 -X utf8 sync_appdata.py            → 列出差異並複製（專案 → APPDATA）
    py -3.11 -X utf8 sync_appdata.py --check    → 只列差異，不動檔案
    py -3.11 -X utf8 sync_appdata.py --pull     → 反向：APPDATA → 專案（在 Vortex 裡直接改過檔案時用）

專案目錄是唯一的正本；APPDATA 那份只是安裝出去的副本。Vortex 需要重啟（或切換語言）才會重讀。
"""
from __future__ import annotations

import filecmp
import shutil
import sys

from vortex_paths import APPDATA_LOCALE_DIR, LOCALE_DIR


def main():
    args = sys.argv[1:]
    check, pull = "--check" in args, "--pull" in args
    if APPDATA_LOCALE_DIR is None:
        raise SystemExit("沒有 %APPDATA%")
    src, dst = (APPDATA_LOCALE_DIR, LOCALE_DIR) if pull else (LOCALE_DIR, APPDATA_LOCALE_DIR)
    dst.mkdir(parents=True, exist_ok=True)

    changed = []
    for f in sorted(src.glob("*.json")):
        target = dst / f.name
        state = "新增" if not target.exists() else ("不同" if not filecmp.cmp(f, target, shallow=False) else None)
        if state:
            changed.append((state, f, target))
    orphans = sorted(p.name for p in dst.glob("*.json") if not (src / p.name).exists())

    print(f"{'APPDATA → 專案' if pull else '專案 → APPDATA'}：{src}  →  {dst}")
    if not changed and not orphans:
        print("兩邊完全一致。")
        return
    for state, f, target in changed:
        print(f"  {state}  {f.name}")
        if not check:
            shutil.copy2(f, target)
    for name in orphans:
        print(f"  只在目的地有（未刪除）  {name}")
    print("（--check，未動檔案）" if check else f"已複製 {len(changed)} 個檔案。重啟 Vortex 後生效。")


if __name__ == "__main__":
    main()
