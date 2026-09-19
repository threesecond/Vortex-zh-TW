"""把 2.6.3 的 health_check 新鍵併入 locales\\zh-TW\\health_check.json（巢狀結構，不走 apply.js）。

    py -3.11 -X utf8 patch_health_check_263.py

帶 {{ count }} 的鍵同時寫 base / _0 / _plural 三份（中文 nplurals=1）。
"""
import json
from vortex_paths import LOCALE_DIR

NEW = {
    "divider::and": "且",
    "divider::or": "或",
    "shared::requires_files": "需要安裝 {{ count }} 個額外的 mod 檔案才能正常運作：",
    "shared::requires_pick": "需要挑選 {{ count }} 個額外的 mod 檔案才能正常運作：",
    "shared::wrong_version_installed": "需要安裝這個現有 mod 檔案的另一個版本才能正常運作：",
    "shared::wrong_version_installed_plural": "需要安裝 {{ count }} 個現有 mod 檔案的另一個版本才能正常運作：",
    "shared::wrong_version_enabled": "需要啟用這個已安裝 mod 檔案的另一個版本才能正常運作：",
    "shared::wrong_version_enabled_plural": "需要啟用 {{ count }} 個已安裝 mod 檔案的另一個版本才能正常運作：",
    "shared::correct_version_uninstalled": "需要安裝這個先前已下載的 mod 檔案才能正常運作：",
    "shared::correct_version_uninstalled_plural": "需要安裝 {{ count }} 個先前已下載的 mod 檔案才能正常運作：",
    "listing::no_results_logged_out::title": "還有其他檢查可用",
    "listing::no_results_logged_out::message": "健康檢查在它能執行的檢查中沒有發現問題。登入後還能檢查是否缺少 Nexus Mods 的需求項目。",
    "listing::no_results_logged_out::action": "登入以完成健康檢查",
    "listing::external_mod_install": "外部 mod 安裝",
    "detail::item::may_require_file": "可能需要安裝這個額外的 mod 檔案才能正常運作：",
    "detail::item::mod_page_source_note": "這項需求是從 mod 頁面辨識出來的，而非來自檔案層級的需求系統，所以對你的特定配置可能不是必要的。<modLink>檢視 mod 頁面以取得完整細節</modLink>。",
    "detail::item::external_hosted_note": "這個 mod 託管在 Nexus Mods 之外。安裝前請先查看說明。",
    "detail::item::downloading": "正在下載…",
    "detail::item::installing": "正在安裝…",
    "detail::item::install_required": "需要安裝",
    "detail::item::different_version_required": "需要安裝另一個版本",
    "detail::item::current_version": "目前版本",
    "detail::item::enable_required": "啟用需要的版本",
    "detail::item::adult": "成人",
    "detail::item::installed": "已安裝",
    "detail::item::enabled": "已啟用",
    "detail::item::disabled": "已停用",
}


def main():
    path = LOCALE_DIR / "health_check.json"
    data = json.loads(path.read_text("utf-8"))
    added = 0
    for key, value in NEW.items():
        variants = [key]
        if "{{ count }}" in key or "{{count}}" in value:
            variants = [key, key + "_0", key + "_plural"] if not key.endswith("_plural") else [key]
        elif "{{ count }}" in value and not key.endswith(("_0", "_plural")):
            variants = [key, key + "_0", key + "_plural"]
        for k in variants:
            node = data
            parts = k.split("::")
            for p in parts[:-1]:
                node = node.setdefault(p, {})
            if parts[-1] not in node:
                added += 1
            node[parts[-1]] = value
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"health_check.json：新增 {added} 條")


if __name__ == "__main__":
    main()
