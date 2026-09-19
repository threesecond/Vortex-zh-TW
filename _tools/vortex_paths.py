"""共用：找 Vortex 安裝目錄、讀 app.asar、找語言檔目錄（Python 版，與 vortex_paths.js 對應）。

用 Python 3.11：py -3.11 -X utf8 <script>.py
"""
from __future__ import annotations

import json
import os
import struct
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TOOLS_DIR.parent
LOCALE_DIR = PROJECT_DIR / "locales" / "zh-TW"
APPDATA_LOCALE_DIR = Path(os.environ["APPDATA"]) / "Vortex" / "locales" / "zh-TW" if "APPDATA" in os.environ else None

_CANDIDATE_DIRS = [
    os.environ.get("VORTEX_DIR"),
    r"C:\Program Files\Black Tree Gaming Ltd\Vortex",
    r"C:\Program Files\Vortex",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Vortex") if os.environ.get("LOCALAPPDATA") else None,
]


def find_vortex_dir() -> Path:
    for d in _CANDIDATE_DIRS:
        if d and (Path(d) / "resources" / "app.asar").is_file():
            return Path(d)
    raise SystemExit("找不到 Vortex 安裝目錄，請設定環境變數 VORTEX_DIR。試過：\n  " + "\n  ".join(d for d in _CANDIDATE_DIRS if d))


def bundled_locale_dir(vortex_dir: Path) -> Path:
    return vortex_dir / "resources" / "locales" / "en"


class Asar:
    """最小 asar 讀取器。bundledPlugins 全部 unpacked，實際檔案在 app.asar.unpacked\\ 下。"""

    def __init__(self, asar_path: Path):
        self.path = Path(asar_path)
        with open(self.path, "rb") as f:
            self._buf = f.read()
        (_, pickle_size, _, header_len) = struct.unpack_from("<IIII", self._buf, 0)
        header = json.loads(self._buf[16:16 + header_len].decode("utf-8"))
        self._base = 8 + pickle_size
        self.files: dict[str, dict] = {}

        def walk(node, prefix):
            for name, entry in node["files"].items():
                if "files" in entry:
                    walk(entry, prefix + name + "/")
                else:
                    self.files[prefix + name] = entry

        walk(header, "")

    def read(self, rel: str) -> str:
        entry = self.files.get(rel)
        if entry is None:
            raise KeyError(f"asar 內沒有這個檔案：{rel}")
        if entry.get("unpacked"):
            return (Path(str(self.path) + ".unpacked") / rel).read_text("utf-8")
        off = self._base + int(entry["offset"])
        return self._buf[off:off + entry["size"]].decode("utf-8")

    def list(self) -> list[str]:
        return list(self.files)

    def version(self) -> str:
        return json.loads(self.read("package.json"))["version"]


def open_asar(vortex_dir: Path | None = None) -> Asar:
    return Asar((vortex_dir or find_vortex_dir()) / "resources" / "app.asar")


def source_files(asar: Asar) -> list[str]:
    """要掃描的原始碼：renderer.js + 每個內建擴充套件的頂層 js（同 vortex_paths.js）。"""
    import re
    pat = re.compile(r"^bundledPlugins/[^/]+/[^/]+\.(js|cjs|mjs)$")
    return [p for p in asar.list() if p == "renderer.js" or pat.match(p)]


def demo_ranges(source: str) -> list[tuple[int, int]]:
    """renderer.js 裡 design_system_dev 示範頁的 webpack 模組範圍（[start, end) 位移）。

    那些模組的字串（"Text Input"、"Bethesda Games"…）只在開發者示範頁出現，刻意不翻。
    判定：模組 export 名稱以 Demo 結尾，或無名模組內含 Demo 字樣。
    """
    import re
    bounds = [m.start() for m in re.finditer(r"[,{]\d{3,6}\((?:__unused_webpack_module|module),exports", source)] + [len(source)]
    out = []
    for a, b in zip(bounds, bounds[1:]):
        seg = source[a:b]
        name = re.search(r"exports\.(\w+)=", seg[:400])
        name = name.group(1) if name else ""
        if name.endswith("Demo") or (not name and re.search(r"\bDemo\b|Demo=\(|Demo,", seg)):
            out.append((a, b))
    return out


def in_ranges(pos: int, ranges: list[tuple[int, int]]) -> bool:
    return any(a <= pos < b for a, b in ranges)
