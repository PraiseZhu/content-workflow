#!/usr/bin/env python3
"""cli.py 的紧凑版入口：关闭 converter 的中英/数字自动加空格，并收紧列表项间距；其余参数与 cli.py 完全一致。

converter._fix_cjk_spacing 会在每个「汉字或全角标点」与「英文字母或数字」之间插入半角空格
（含 bot，→ bot ，），且没有开关。本入口只在进程内把它替换为原样返回，不改 converter.py。
_convert_lists_to_sections 写死了 margin-bottom: 8px / 序号 line-height: 1.8 / 圆点 18px，
本入口在进程内把列表项改成 margin-bottom: 4px、行高 1.65、圆点 15px，图片上下 14px，表格短表头/短首列不折行，与 claude-warm-compact 对齐。
用法同 cli.py，例如：
  .venv/bin/python toolkit/cli_compact.py preview <md> -t claude-warm-compact -o <html> --no-open
  .venv/bin/python toolkit/cli_compact.py publish <md> --theme claude-warm-compact ...
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import converter  # noqa: E402

converter.WeChatConverter._fix_cjk_spacing = lambda self, text: text

_orig_lists = converter.WeChatConverter._convert_lists_to_sections


def _compact_lists(self, html):
    html = _orig_lists(self, html)
    return (
        html.replace("display: flex; align-items: flex-start; margin-bottom: 8px;",
                     "display: flex; align-items: flex-start; margin-bottom: 4px;")
        .replace("flex-shrink: 0; font-size: 18px; line-height: 1.6", "flex-shrink: 0; font-size: 15px; line-height: 1.65")
        .replace("flex-shrink: 0; font-weight: 700; line-height: 1.8", "flex-shrink: 0; font-weight: 700; line-height: 1.65")
    )


converter.WeChatConverter._convert_lists_to_sections = _compact_lists


_orig_images = converter.WeChatConverter._process_images


def _compact_images(self, html):
    html, images = _orig_images(self, html)
    return html.replace("display: block; margin: 24px auto", "display: block; margin: 14px auto"), images


converter.WeChatConverter._process_images = _compact_images

_orig_fixes = converter.WeChatConverter._apply_wechat_fixes


def _compact_tables(self, html):
    """短表头/短首列（≤6 字）不折行，避免 375px 下「执行层」被拆成两行。"""
    html = _orig_fixes(self, html)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for tr in soup.find_all("tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        for i, cell in enumerate(cells):
            if (cell.name == "th" or i == 0) and len(cell.get_text(strip=True)) <= 6:
                st = cell.get("style", "")
                if "white-space" not in st:
                    cell["style"] = f"{st}; white-space: nowrap" if st else "white-space: nowrap"
    return str(soup)


converter.WeChatConverter._apply_wechat_fixes = _compact_tables

import cli  # noqa: E402

if __name__ == "__main__":
    cli.main()
