#!/usr/bin/env python3
"""
Product Lens — X/社区热门 AI 帖子采集
从 Reddit AI 子版 + Hacker News 抓取当日热门讨论
（X/Twitter 需 API 认证，暂用 Reddit/HN 覆盖同样的 AI 讨论热点）
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── 数据源 ─────────────────────────────────────────────

REDDIT_SUBS = [
    "MachineLearning",
    "artificial",
    "LocalLLaMA",
    "singularity",
    "OpenAI",
]

HN_URL = "https://hacker-news.firebaseio.com/v0"

AI_KEYWORDS = [
    "ai", "llm", "gpt", "agent", "openai", "claude", "gemini",
    "model", "deepseek", "qwen", "llama", "mistral", "anthropic",
    "rag", "fine-tun", "transformer", "diffusion", "embedding",
    "benchmark", "sota", "opensource", "open source",
    "chatgpt", "copilot", "cursor", "reasoning", "alignment",
    "multimodal", "vision", "text to", "generative",
    "rlhf", "dpo", "lora", "qlora", "quantiz",
]


def fetch_json(url: str, timeout: int = 15, retries: int = 2) -> dict | list | None:
    """带重试的 JSON 抓取"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ProductLens/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"  ⚠️  fetch failed: {url[:80]} — {e}", file=sys.stderr)
    return None


def is_ai_related(title: str) -> bool:
    """判断帖子是否 AI 相关"""
    t = title.lower()
    return any(k in t for k in AI_KEYWORDS)


# ─── Reddit ─────────────────────────────────────────────

def scrape_reddit(limit_per_sub: int = 5) -> list[dict]:
    """抓取 Reddit 多个 AI 子版热门"""
    posts = []
    for sub in REDDIT_SUBS:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit_per_sub}"
        data = fetch_json(url)
        if not data:
            continue

        for child in data.get("data", {}).get("children", []):
            p = child["data"]
            title = p.get("title", "")
            if not is_ai_related(title):
                continue
            # 跳过置顶帖（通常是 mod post）
            if p.get("stickied"):
                continue

            posts.append({
                "source": "Reddit",
                "sub": f"r/{sub}",
                "title": title,
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "score": p.get("score", 0),
                "comments": p.get("num_comments", 0),
                "author": p.get("author", ""),
                "flair": p.get("link_flair_text", ""),
            })

        time.sleep(0.5)  # 避免触发 rate limit

    return posts


# ─── Hacker News ────────────────────────────────────────

def scrape_hn(max_stories: int = 100) -> list[dict]:
    """抓取 HN 首页 AI 相关帖子"""
    top_ids = fetch_json(f"{HN_URL}/topstories.json")
    if not top_ids:
        return []

    posts = []
    for sid in top_ids[:max_stories]:
        story = fetch_json(f"{HN_URL}/item/{sid}.json")
        if not story:
            continue

        title = story.get("title", "")
        if not is_ai_related(title):
            continue

        posts.append({
            "source": "HN",
            "sub": "Hacker News",
            "title": title,
            "url": story.get("url") or f"https://news.ycombinator.com/item?id={sid}",
            "score": story.get("score", 0),
            "comments": story.get("descendants", 0),
            "author": story.get("by", ""),
        })
        time.sleep(0.02)

    return posts


# ─── 排序 & 去重 ────────────────────────────────────────

def deduplicate(posts: list[dict]) -> list[dict]:
    """按标题相似度去重（简单字符集重叠判断）"""
    seen = set()
    unique = []
    for p in posts:
        # 取标题前 60 字符做去重 key
        key = p["title"][:60].lower().strip()
        # 简化：去掉常见停用词
        for w in ["the ", "a ", "an ", "is ", "are ", "to ", "in ", "of "]:
            key = key.replace(w, "")
        if key not in seen and len(key) > 15:
            seen.add(key)
            unique.append(p)
    return unique


def rank(posts: list[dict], top_n: int = 5) -> list[dict]:
    """按热度排序（score + comments 加权）"""
    ranked = sorted(posts, key=lambda p: p["score"] + p["comments"] * 2, reverse=True)
    return ranked[:top_n]


# ─── 输出模板 ───────────────────────────────────────────

def wechat_hot_posts(posts: list[dict]) -> str:
    """WeChat Markdown 格式"""
    if not posts:
        return ""

    lines = ["", "**今日 AI 圈热门讨论**", ""]
    for i, p in enumerate(posts, 1):
        sub = p["sub"]
        score = p["score"]
        comments = p["comments"]
        title = p["title"][:80]
        url = p["url"]

        # 热度标记
        if score + comments * 2 > 500:
            fire = "🔥 "
        elif score + comments * 2 > 200:
            fire = "⭐ "
        else:
            fire = ""

        lines.append(f"{fire}{i}. {title}")
        lines.append(f"    {sub} · {score}⬆ {comments}💬")
        lines.append(f"    {url}")
        lines.append("")

    return "\n".join(lines)


def html_hot_posts(posts: list[dict]) -> str:
    """HTML 邮件格式"""
    if not posts:
        return ""

    items = ""
    for i, p in enumerate(posts, 1):
        score = p["score"]
        comments = p["comments"]
        title = p["title"]
        url = p["url"]
        sub = p["sub"]

        fire = "🔥 " if score + comments * 2 > 500 else ("⭐ " if score + comments * 2 > 200 else "")

        items += f"""\
<div class="hot-item">
    <div class="hot-idx">{fire}NO. {i} · {sub}</div>
    <div class="hot-title"><a href="{url}">{title}</a></div>
    <div class="hot-meta">{score}⬆ · {comments}💬 讨论</div>
</div>
"""

    return f"""\
<div class="hot-section">
    <div class="hot-header">今日 AI 圈热门讨论</div>
    {items}
</div>"""


def html_hot_css() -> str:
    """热门讨论 CSS（追加到邮件样式表）"""
    return """
.hot-section {
    margin-top: 24px;
    padding: 0 28px 20px 28px;
}
.hot-header {
    font-size: 14px;
    font-weight: 700;
    color: #374151;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e5e7eb;
}
.hot-item {
    padding: 12px 0;
    border-bottom: 1px solid #f3f4f6;
}
.hot-item:last-child { border: none; }
.hot-idx {
    font-size: 11px;
    font-weight: 600;
    color: #9ca3af;
    margin-bottom: 4px;
}
.hot-title {
    font-size: 14px;
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: 4px;
}
.hot-title a {
    color: #1a1a2e;
    text-decoration: none;
}
.hot-title a:hover { color: #4f46e5; }
.hot-meta {
    font-size: 11px;
    color: #aaa;
}
"""


# ─── Main ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="热门 AI 帖子采集")
    parser.add_argument("--top", type=int, default=5, help="输出前 N 条 (默认 5)")
    parser.add_argument("--output", choices=["wechat", "email", "text"],
                        default="wechat", help="输出格式")
    parser.add_argument("--dry-run", action="store_true", help="只抓取不输出")
    args = parser.parse_args()

    print("🔍 抓取 Reddit AI 子版...", file=sys.stderr)
    reddit_posts = scrape_reddit(limit_per_sub=5)
    print(f"   Reddit: {len(reddit_posts)} 篇 AI 相关", file=sys.stderr)

    print("🔍 抓取 Hacker News...", file=sys.stderr)
    hn_posts = scrape_hn(max_stories=30)
    print(f"   HN: {len(hn_posts)} 篇 AI 相关", file=sys.stderr)

    all_posts = deduplicate(reddit_posts + hn_posts)
    ranked = rank(all_posts, top_n=args.top)
    print(f"📊 去重后 {len(all_posts)} 篇，精选 top {len(ranked)}", file=sys.stderr)

    if args.dry_run:
        for p in ranked:
            print(f"  [{p['sub']}] {p['title'][:80]}")
        return

    if args.output == "text":
        for i, p in enumerate(ranked, 1):
            print(f"{i}. [{p['sub']}] {p['title']}")
            print(f"   {p['url']}")
            print()
        return

    if args.output == "wechat":
        print(wechat_hot_posts(ranked))
        return

    if args.output == "email":
        print(html_hot_posts(ranked))
        return


if __name__ == "__main__":
    main()
