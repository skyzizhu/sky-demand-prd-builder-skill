#!/usr/bin/env python3
"""
Scan a PRD Markdown file for AI-WIREFRAME blocks and generate simple HTML
wireframe pages (no external APIs), saving them to the specified output paths.

Usage:

    python scripts/generate_ai_wireframes.py /path/to/prd.md

The PRD markdown can contain blocks like:

```ai-wireframe
type: list_page
name: message_list_read_status
title: 信息列表已读/未读状态线框
output_path: wireframes/message-list-read-status.html
variant: mobile
notes: 用于展示未读亮色、已读浅灰的对比
```
"""

import re
import sys
from pathlib import Path
from typing import Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def parse_blocks(text: str) -> List[Dict[str, str]]:
    """
    Parse AI wireframe definition blocks from the PRD markdown text.

    Supported formats:
    1) HTML comment:
       <!-- AI-WIREFRAME
       key: value
       ... -->

    2) Code block:
       ```ai-wireframe
       key: value
       ...
       ```
    """
    blocks: List[Dict[str, str]] = []

    # HTML comment style
    comment_pattern = re.compile(
        r"<!--\s*AI-WIREFRAME(.*?)-->",
        re.DOTALL | re.IGNORECASE,
    )
    for match in comment_pattern.finditer(text):
        content = match.group(1)
        block = _parse_key_values(content)
        if block:
            blocks.append(block)

    # Code block style
    code_pattern = re.compile(
        r"```ai-wireframe(.*?)```",
        re.DOTALL | re.IGNORECASE,
    )
    for match in code_pattern.finditer(text):
        content = match.group(1)
        block = _parse_key_values(content)
        if block:
            blocks.append(block)

    return blocks


def _parse_key_values(content: str) -> Dict[str, str]:
    """Parse simple `key: value` lines from a block."""
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            result[key] = val
    # Require at least output_path
    if "output_path" in result:
        return result
    return {}


def _build_list_page_html(block: Dict[str, str]) -> str:
    """Generate a simple HTML wireframe for a list page."""
    name = block.get("name") or "list_page"
    title = block.get("title") or "列表页线框"
    notes = block.get("notes") or ""
    thumb_image_url = block.get("image_url") or ""
    variant = (block.get("variant") or "mobile").lower()

    page_class = "wf-page--mobile" if variant == "mobile" else "wf-page--web"

    # Resolve default thumbnail images in skill assets
    skill_root = Path(__file__).resolve().parent.parent
    assets_dir = skill_root / "assets"
    # 纵向、横向、列表专用占位图
    vertical_thumb = (assets_dir / "vertical-general-placeholder.jpeg").as_uri() if (assets_dir / "vertical-general-placeholder.jpeg").exists() else ""
    landscape_thumb = (assets_dir / "landscape-general -placeholder.jpeg").as_uri() if (assets_dir / "landscape-general -placeholder.jpeg").exists() else ""
    list_thumb = (assets_dir / "list-thumb-placeholder.jpeg").as_uri() if (assets_dir / "list-thumb-placeholder.jpeg").exists() else ""

    # 对于 list_page，默认使用列表占位图，其次回退到纵向/横向中的任意一个存在的资源
    default_thumb_candidates = [list_thumb, vertical_thumb, landscape_thumb]
    default_thumb_src = next((c for c in default_thumb_candidates if c), "")

    thumb_src = ""
    # image_url 用于 item 左侧缩略图，不再用于页面顶部 hero
    if thumb_image_url:
        if thumb_image_url.startswith(("http://", "https://")):
            try:
                with urlopen(thumb_image_url) as resp:
                    if getattr(resp, "status", 200) < 400:
                        thumb_src = thumb_image_url
            except (HTTPError, URLError, Exception):
                thumb_src = default_thumb_src
        else:
            thumb_src = thumb_image_url
    else:
        thumb_src = default_thumb_src

    css = """
    body {
      margin: 0;
      padding: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f5f5f5;
    }
    .wf-page {
      margin: 0 auto;
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      border: 1px solid #e0e0e0;
      overflow: hidden;
    }
    .wf-page--mobile {
      max-width: 414px;
    }
    .wf-page--web {
      max-width: 960px;
    }
    .wf-header {
      background: #f0f0f0;
      border-bottom: 1px solid #e0e0e0;
    }
    .wf-status-bar {
      height: 12px;
      background: linear-gradient(90deg, #d0d0d0 20%, #e0e0e0 40%, #d0d0d0 60%);
    }
    .wf-nav-bar {
      display: flex;
      align-items: center;
      padding: 8px 12px;
    }
    .wf-nav-back,
    .wf-nav-action {
      width: 24px;
      height: 24px;
      border-radius: 6px;
      border: 1px solid #cccccc;
      background: #f5f5f5;
    }
    .wf-nav-title {
      flex: 1;
      text-align: center;
      font-size: 14px;
      color: #666666;
    }
    .wf-content {
      padding: 12px;
      background: #f8f8f8;
    }
    .wf-list-item {
      border-radius: 8px;
      border: 1px solid #d0d0d0;
      padding: 8px 10px;
      margin-bottom: 8px;
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }
    .wf-list-item--unread {
      background: #ffffff;
    }
    .wf-list-item--read {
      background: #e4e4e4;
      border-color: #c8c8c8;
    }
    .wf-list-thumb {
      width: 64px;
      height: 64px;
      border-radius: 8px;
      background: #d0d0d0;
      flex-shrink: 0;
      overflow: hidden;
    }
    .wf-list-thumb img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .wf-list-item--read .wf-list-thumb {
      background: #c4c4c4;
    }
    .wf-list-body {
      flex: 1;
      min-width: 0;
    }
    .wf-list-title {
      font-size: 13px;
      color: #555555;
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .wf-list-item--read .wf-list-title {
      color: #777777;
    }
    .wf-list-meta {
      font-size: 11px;
      color: #999999;
    }
    .wf-list-item--read .wf-list-meta {
      color: #aaaaaa;
    }
    .wf-notes {
      padding: 8px 12px 12px;
      font-size: 12px;
      color: #999999;
      border-top: 1px dashed #e0e0e0;
      background: #fafafa;
    }
    h1 {
      font-size: 16px;
      margin: 0 0 12px;
      text-align: center;
      color: #555555;
    }
    """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
  {css}
  </style>
</head>
<body>
  <div class="wf-page {page_class}" data-wireframe-type="list_page" data-wireframe-name="{name}">
    <h1>{title}</h1>
    <header class="wf-header">
      <div class="wf-status-bar"></div>
      <div class="wf-nav-bar">
        <div class="wf-nav-back"></div>
        <div class="wf-nav-title">列表</div>
        <div class="wf-nav-action"></div>
      </div>
    </header>
    <main class="wf-content">
      <div class="wf-list-item wf-list-item--unread">
        <div class="wf-list-thumb"><img src="{thumb_src}" alt="缩略图" /></div>
        <div class="wf-list-body">
          <div class="wf-list-title">示例未读标题一，文案略长截断展示</div>
          <div class="wf-list-meta">今天 · 10:24</div>
        </div>
      </div>
      <div class="wf-list-item wf-list-item--unread">
        <div class="wf-list-thumb"><img src="{thumb_src}" alt="缩略图" /></div>
        <div class="wf-list-body">
          <div class="wf-list-title">示例未读标题二</div>
          <div class="wf-list-meta">今天 · 09:05</div>
        </div>
      </div>
      <div class="wf-list-item wf-list-item--unread">
        <div class="wf-list-thumb"><img src="{thumb_src}" alt="缩略图" /></div>
        <div class="wf-list-body">
          <div class="wf-list-title">示例未读标题三</div>
          <div class="wf-list-meta">昨天 · 18:32</div>
        </div>
      </div>
      <div class="wf-list-item wf-list-item--read">
        <div class="wf-list-thumb"><img src="{thumb_src}" alt="缩略图" /></div>
        <div class="wf-list-body">
          <div class="wf-list-title">示例已读标题一 · 已读内容</div>
          <div class="wf-list-meta">昨天 · 15:10</div>
        </div>
      </div>
      <div class="wf-list-item wf-list-item--read">
        <div class="wf-list-thumb"><img src="{thumb_src}" alt="缩略图" /></div>
        <div class="wf-list-body">
          <div class="wf-list-title">示例已读标题二 · 已读内容</div>
          <div class="wf-list-meta">前天 · 20:48</div>
        </div>
      </div>
      <div class="wf-list-item wf-list-item--read">
        <div class="wf-list-thumb"><img src="{thumb_src}" alt="缩略图" /></div>
        <div class="wf-list-body">
          <div class="wf-list-title">示例已读标题三 · 已读内容</div>
          <div class="wf-list-meta">本周内 · 08:15</div>
        </div>
      </div>
    </main>
    <footer class="wf-notes">
      {notes}
    </footer>
  </div>
</body>
</html>
"""
    return html


def _build_detail_page_html(block: Dict[str, str]) -> str:
    """Generate a simple HTML wireframe for a detail page."""
    name = block.get("name") or "detail_page"
    title = block.get("title") or "详情页线框"
    notes = block.get("notes") or ""
    hero_image_url = block.get("image_url") or ""
    variant = (block.get("variant") or "mobile").lower()

    page_class = "wf-page--mobile" if variant == "mobile" else "wf-page--web"

    # Resolve default hero images in skill assets
    skill_root = Path(__file__).resolve().parent.parent
    assets_dir = skill_root / "assets"
    vertical_hero = (assets_dir / "vertical-general-placeholder.jpeg").as_uri() if (assets_dir / "vertical-general-placeholder.jpeg").exists() else ""
    landscape_hero = (assets_dir / "landscape-general -placeholder.jpeg").as_uri() if (assets_dir / "landscape-general -placeholder.jpeg").exists() else ""
    list_hero = (assets_dir / "list-thumb-placeholder.jpeg").as_uri() if (assets_dir / "list-thumb-placeholder.jpeg").exists() else ""

    # 对于 detail_page，优先使用纵向/横向占位图，其次退回到列表占位图
    default_hero_candidates = [vertical_hero, landscape_hero, list_hero]
    default_hero_src = next((c for c in default_hero_candidates if c), "")

    hero_src = ""
    if hero_image_url:
        if hero_image_url.startswith(("http://", "https://")):
            try:
                with urlopen(hero_image_url) as resp:
                    if getattr(resp, "status", 200) < 400:
                        hero_src = hero_image_url
            except (HTTPError, URLError, Exception):
                hero_src = default_hero_src
        else:
            hero_src = hero_image_url
    else:
        hero_src = default_hero_src

    css = """
    body {
      margin: 0;
      padding: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f5f5f5;
    }
    .wf-page {
      margin: 0 auto;
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      border: 1px solid #e0e0e0;
      overflow: hidden;
    }
    .wf-page--mobile {
      max-width: 414px;
    }
    .wf-page--web {
      max-width: 960px;
    }
    .wf-header {
      background: #f0f0f0;
      border-bottom: 1px solid #e0e0e0;
    }
    .wf-status-bar {
      height: 12px;
      background: linear-gradient(90deg, #d0d0d0 20%, #e0e0e0 40%, #d0d0d0 60%);
    }
    .wf-nav-bar {
      display: flex;
      align-items: center;
      padding: 8px 12px;
    }
    .wf-nav-back,
    .wf-nav-action {
      width: 24px;
      height: 24px;
      border-radius: 6px;
      border: 1px solid #cccccc;
      background: #f5f5f5;
    }
    .wf-nav-title {
      flex: 1;
      text-align: center;
      font-size: 14px;
      color: #666666;
    }
    .wf-hero {
      width: 100%;
      background: #e8e8e8;
      border-bottom: 1px solid #e0e0e0;
    }
    .wf-hero img {
      display: block;
      width: 100%;
      height: auto;
      object-fit: cover;
    }
    .wf-content {
      padding: 16px 16px 12px;
      background: #ffffff;
    }
    .wf-detail-title {
      font-size: 15px;
      color: #444444;
      margin: 4px 0 6px;
      line-height: 1.4;
    }
    .wf-detail-meta {
      font-size: 11px;
      color: #999999;
      margin-bottom: 12px;
    }
    .wf-detail-paragraph {
      font-size: 13px;
      color: #666666;
      line-height: 1.6;
      margin-bottom: 6px;
    }
    .wf-notes {
      padding: 8px 16px 12px;
      font-size: 12px;
      color: #999999;
      border-top: 1px dashed #e0e0e0;
      background: #fafafa;
    }
    h1 {
      font-size: 16px;
      margin: 0 0 12px;
      text-align: center;
      color: #555555;
    }
    """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
  {css}
  </style>
</head>
<body>
  <div class="wf-page {page_class}" data-wireframe-type="detail_page" data-wireframe-name="{name}">
    <h1>{title}</h1>
    <header class="wf-header">
      <div class="wf-status-bar"></div>
      <div class="wf-nav-bar">
        <div class="wf-nav-back"></div>
        <div class="wf-nav-title">详情</div>
        <div class="wf-nav-action"></div>
      </div>
    </header>
    {"<div class=\"wf-hero\"><img src=\"" + hero_src + "\" alt=\"详情主图\" /></div>" if hero_src else ""}
    <main class="wf-content">
      <div class="wf-detail-title">示例信息标题：展示已读/未读状态的详情内容</div>
      <div class="wf-detail-meta">作者 · 今天 10:24 · 已读状态将在阅读完成后更新</div>
      <p class="wf-detail-paragraph">这是一段示例正文，用于说明在详情页中用户将看到的主要内容摘要，以及与已读状态相关的提示信息。</p>
      <p class="wf-detail-paragraph">可以在这里模拟两到三行的文本，让评审时能快速感知信息密度和阅读节奏。</p>
      <p class="wf-detail-paragraph">例如：阅读完成后返回列表，列表项会变为浅灰色，并在数据层记录该条内容已读。</p>
    </main>
    <footer class="wf-notes">
      {notes}
    </footer>
  </div>
</body>
</html>
"""
    return html


def generate_wireframe(block: Dict[str, str], base_dir: Path) -> None:
    """Generate a local HTML wireframe file for a single block."""
    output_path = base_dir / block["output_path"]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    wf_type = (block.get("type") or "list_page").lower()

    if wf_type == "list_page":
        html = _build_list_page_html(block)
    elif wf_type == "detail_page":
        html = _build_detail_page_html(block)
    else:
        print(f"[skip] Unsupported wireframe type: {wf_type!r} for {output_path}")
        return

    output_path.write_text(html, encoding="utf-8")
    print(f"[ok] Generated HTML wireframe: {output_path}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_ai_wireframes.py /path/to/prd.md")
        sys.exit(1)

    prd_path = Path(sys.argv[1]).expanduser()
    if not prd_path.is_file():
        print(f"[error] PRD file not found: {prd_path}")
        sys.exit(1)

    text = prd_path.read_text(encoding="utf-8")
    blocks = parse_blocks(text)

    if not blocks:
        print("[info] No AI-WIREFRAME blocks found in PRD.")
        sys.exit(0)

    base_dir = prd_path.parent
    for block in blocks:
        generate_wireframe(block, base_dir)


if __name__ == "__main__":
    main()
