#!/usr/bin/env python3
"""
Paper2Product — arXiv 论文监控
按关键词抓取 cs.AI / cs.CL / cs.HC 的最新论文，写入 papers/inbox/
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


def main():
    parser = argparse.ArgumentParser(description="arXiv 论文监控")
    parser.add_argument("--days", type=int, default=3, help="回溯天数")
    parser.add_argument("--max", type=int, default=50, help="最大结果数")
    parser.add_argument("--dry-run", action="store_true", help="只显示不保存")
    args = parser.parse_args()

    print(f"🔍 搜索最近 {args.days} 天的论文...")
    url = build_query(KEYWORDS, args.days, args.max)
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Paper2Product/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_text = resp.read().decode("utf-8")
    except Exception as e:
        print(f"❌ API 请求失败: {e}", file=sys.stderr)
        sys.exit(1)

    papers = parse_arxiv_response(xml_text)
    print(f"📄 找到 {len(papers)} 篇论文")

    relevant = [p for p in papers if is_product_relevant(p)]
    print(f"🎯 产品相关: {len(relevant)} 篇")

    if args.dry_run:
        for p in relevant[:10]:
            print(f"  • {p['title'][:80]}...")
        return

    saved = 0
    for p in relevant:
        fp = save_to_inbox(p)
        print(f"  ✅ {fp.name}")
        saved += 1

    print(f"\n📥 已保存 {saved} 篇到 papers/inbox/")
    print(f"💡 下一步: 用 paper-summarizer.py 提取关键信息")


if __name__ == "__main__":
    main()
