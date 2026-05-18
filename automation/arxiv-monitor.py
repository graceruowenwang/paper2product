#!/usr/bin/env python3
"""
Paper2Product — arXiv 论文监控
按关键词抓取 cs.AI / cs.CL / cs.HC 的最新论文，写入 papers/inbox/

输出模式：
  wechat  → 精美的 WeChat Markdown 通知（默认）
  text    → 原始纯文本（调试用）
  email   → 保存 HTML 邮件到 papers/digests/
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 导入模板
from templates import (
    wechat_daily_full,
    wechat_daily_empty,
    email_daily_full,
)

ARXIV_API = "http://export.arxiv.org/api/query"

# 产品导向的关键词（可根据兴趣调整）
KEYWORDS = [
    "agent", "rag", "retrieval augmented", "llm agent",
    "tool use", "function calling", "code generation",
    "multimodal", "vision language", "text to image",
    "fine tuning", "lora", "alignment", "rlhf",
    "reasoning", "chain of thought", "planning",
    "evaluation", "benchmark", "safety",
    "embedding", "vector search", "knowledge graph",
    "ai product", "human ai interaction", "UX",
]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INBOX = PROJECT_ROOT / "papers" / "inbox"
DIGESTS = PROJECT_ROOT / "papers" / "digests"


def build_query(keywords: list[str], days_back: int = 3, max_results: int = 50) -> str:
    """构造 arXiv API 查询"""
    cat = "cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.HC"
    kw_parts = "+OR+".join(f'all:{urllib.parse.quote(k)}' for k in keywords)
    return (
        f"{ARXIV_API}?search_query=({cat})+AND+({kw_parts})"
        f"&start=0&max_results={max_results}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )


def parse_arxiv_response(xml_text: str) -> list[dict]:
    """解析 arXiv API XML 响应"""
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        link = entry.find("atom:id", ns)
        published = entry.find("atom:published", ns)
        authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]

        papers.append({
            "arxiv_id": (link.text or "").split("/abs/")[-1],
            "title": (title.text or "").strip().replace("\n", " "),
            "authors": authors[:3],
            "published": (published.text or "")[:10],
            "summary": (summary.text or "").strip().replace("\n", " ")[:800],
            "url": link.text or "",
            "categories": [
                c.get("term", "") for c in entry.findall("atom:category", ns)
            ],
        })
    return papers


def is_product_relevant(paper: dict) -> bool:
    """快速判断论文是否有产品价值（启发式）"""
    text = (paper["title"] + " " + paper["summary"]).lower()
    signals = [
        "code", "github", "open source", "release", "demo",
        "outperform", "state of the art", "benchmark",
        "product", "application", "deploy", "user study",
        "real world", "practical", "scale", "production",
    ]
    return any(s in text for s in signals)


def save_to_inbox(paper: dict):
    """保存论文到 inbox，文件名: YYYY-MM-DD_arxiv_id.md"""
    INBOX.mkdir(parents=True, exist_ok=True)
    filename = f"{paper['published']}_{paper['arxiv_id']}.md"
    filepath = INBOX / filename

    content = f"""# {paper['title']}

- **arXiv**: [{paper['arxiv_id']}]({paper['url']})
- **作者**: {', '.join(paper['authors'][:3])}
- **发表**: {paper['published']}
- **分类**: {', '.join(paper['categories'][:3])}
- **状态**: 待评估

## 摘要

{paper['summary']}

---
*自动收录于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    filepath.write_text(content, encoding="utf-8")
    return filepath


def fetch_with_retry(url: str, max_retries: int = 3) -> str:
    """带指数退避的 API 请求"""
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Paper2Product/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = 5 * (2 ** attempt)
                print(f"  ⏳ 限流，{wait}s 后重试...", file=sys.stderr)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("max retries exceeded")


def main():
    parser = argparse.ArgumentParser(description="arXiv 论文监控")
    parser.add_argument("--days", type=int, default=3, help="回溯天数 (默认 3)")
    parser.add_argument("--max", type=int, default=50, help="最大结果数 (默认 50)")
    parser.add_argument("--dry-run", action="store_true", help="只显示不保存")
    parser.add_argument(
        "--output", choices=["wechat", "text", "email"],
        default="wechat",
        help="输出格式: wechat (精美通知), text (纯文本), email (HTML 邮件)",
    )
    parser.add_argument(
        "--max-show", type=int, default=8,
        help="WeChat 消息中最多展示几篇 (默认 8)",
    )
    args = parser.parse_args()

    # ─── 1. 获取论文 ───
    print(f"🔍 搜索最近 {args.days} 天的论文...", file=sys.stderr)
    url = build_query(KEYWORDS, args.days, args.max)

    try:
        xml_text = fetch_with_retry(url)
    except Exception as e:
        print(f"❌ API 请求失败: {e}", file=sys.stderr)
        sys.exit(1)

    papers = parse_arxiv_response(xml_text)
    print(f"📄 找到 {len(papers)} 篇论文", file=sys.stderr)

    relevant = [p for p in papers if is_product_relevant(p)]
    print(f"🎯 产品相关: {len(relevant)} 篇", file=sys.stderr)

    # ─── 2. Dry run ───
    if args.dry_run:
        for p in relevant[:10]:
            print(f"  • {p['title'][:80]}...")
        return

    # ─── 3. Text 模式 (原始输出) ───
    if args.output == "text":
        for p in relevant:
            fp = save_to_inbox(p)
            print(f"  ✅ {fp.name}")
        print(f"\n📥 已保存 {len(relevant)} 篇到 papers/inbox/")
        return

    # ─── 4. 保存论文 ───
    saved = 0
    for p in relevant:
        fp = save_to_inbox(p)
        print(f"  ✅ {fp.name}", file=sys.stderr)
        saved += 1

    print(f"📥 已保存 {saved} 篇到 papers/inbox/", file=sys.stderr)

    # ─── 5. WeChat 模式 (精美通知) ───
    if args.output == "wechat":
        if not relevant:
            print(wechat_daily_empty())
        else:
            print(wechat_daily_full(
                papers=relevant,
                paper_count=len(papers),
                relevant_count=len(relevant),
                saved_count=saved,
                max_show=args.max_show,
            ))
        return

    # ─── 6. Email 模式 (HTML 文件) ───
    if args.output == "email":
        DIGESTS.mkdir(parents=True, exist_ok=True)
        today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
        html = email_daily_full(
            papers=relevant,
            paper_count=len(papers),
            relevant_count=len(relevant),
        )
        email_path = DIGESTS / f"arxiv-digest-{today}.html"
        email_path.write_text(html, encoding="utf-8")
        print(f"📧 HTML 邮件已保存: {email_path}")
        print(email_path)  # 供 cron 脚本抓取路径
        return


if __name__ == "__main__":
    main()
