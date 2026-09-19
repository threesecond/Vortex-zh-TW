"""依官方建議的格式打包發布 zip。

    py -3.11 -X utf8 make_release.py [--out <目錄>]

版本號直接從 Vortex 的 app.asar 讀，避免與實際安裝的版本脫節。產出：
    <專案根目錄>\\Vortex-zhTW-<版本>.zip
    ├── locales\\zh-TW\\*.json
    ├── install.bat      純 ASCII、CRLF（cmd.exe 讀 UTF-8 批次檔會截斷多位元組字元，所以不能有中文）
    ├── install.ps1      UTF-8 with BOM、CRLF（沒 BOM 的話 Windows PowerShell 5.1 會用 ANSI 碼頁讀，中文變亂碼）
    └── README.txt       給玩家看的說明（UTF-8 with BOM、CRLF）

官方 Wiki 要使用者解壓到 %APPDATA%\\Vortex（不是 ...\\Vortex\\locales），所以 zip 自帶 locales\\ 這層。
打包前會檢查 .json 可解析、.bat 純 ASCII、.ps1 帶 BOM；行尾一律正規化成 CRLF。
"""
from __future__ import annotations

import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from vortex_paths import LOCALE_DIR, PROJECT_DIR, open_asar


def crlf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def main():
    args = sys.argv[1:]
    out_dir = Path(args[args.index("--out") + 1]) if "--out" in args else PROJECT_DIR

    asar = open_asar()
    version = asar.version()
    zip_path = out_dir / f"Vortex-zhTW-{version}.zip"

    json_files = sorted(LOCALE_DIR.glob("*.json"))
    assert json_files, f"{LOCALE_DIR} 底下沒有 .json"
    for f in json_files:
        json.loads(f.read_text("utf-8"))   # 壞掉的 JSON 會讓 Vortex 整個語言載入失敗，先擋

    bat = (PROJECT_DIR / "install.bat").read_bytes()
    assert all(b < 0x80 for b in bat), "install.bat 含非 ASCII 字元——cmd.exe 會把它截壞，中文請放 install.ps1"
    ps1 = (PROJECT_DIR / "install.ps1").read_bytes()
    if not ps1.startswith(b"\xef\xbb\xbf"):
        ps1 = b"\xef\xbb\xbf" + ps1
    ps1.decode("utf-8")   # 確認是合法 UTF-8

    stamp = datetime.now().timetuple()[:6]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        def put(arcname: str, data: bytes):
            info = zipfile.ZipInfo(arcname, date_time=stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)

        for f in json_files:
            put(f"locales/zh-TW/{f.name}", f.read_bytes())
        put("install.bat", crlf(bat))
        put("install.ps1", crlf(ps1))
        readme = PROJECT_DIR / "README.txt"   # 給玩家看的說明；存成 UTF-8 with BOM + CRLF，記事本才不會亂碼
        if readme.is_file():
            data = readme.read_bytes()
            if not data.startswith(b"\xef\xbb\xbf"):
                data = b"\xef\xbb\xbf" + data
            put("README.txt", crlf(data))

    total = sum(f.stat().st_size for f in json_files)
    print(f"Vortex {version} → {zip_path}")
    print(f"  {len(json_files)} 個 .json（{total / 1024:.1f} KB）+ install.bat + install.ps1" + (" + README.txt" if (PROJECT_DIR / "README.txt").is_file() else "（沒有 README.txt）"))


if __name__ == "__main__":
    main()
