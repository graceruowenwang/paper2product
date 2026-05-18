#!/usr/bin/env python3
"""
Paper2Product — 通知模板
WeChat Markdown + HTML 邮件两种格式

WeChat Markdown 设计原则：
  - 层次清晰：标题 → 副标题 → 正文，视觉节奏分明
  - 移动优先：每行 ≤ 30 字符，卡片紧凑不撑屏
  - 信号即价值：标签一眼判断是否值得点开
"""

from datetime import datetime, timezone, timedelta
from typing import Optional


# ─── 常量 ─────────────────────────────────────────────────

WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]
DIV = "──────────────────────"
THIN = "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"


# ─── WeChat Markdown ──────────────────────────────────────

def paper_card(paper: dict, idx: int) -> str:
    """单篇论文卡片

    结构：
      序号 + 标题 (粗体)
      元信息行 (小字)
      信号标签行 (蓝底灰字风格)
    """
    title = paper["title"].strip()
    arxiv_id = paper.get("arxiv_id", "")
    authors = ", ".join(paper.get("authors", [])[:2])
    cats = ", ".join(paper.get("categories", [])[:2])
    url = paper.get("url", f"https://arxiv.org/abs/{arxiv_id}")
    signals = _extract_signals(paper)

    meta = f"`{arxiv_id}` · {cats}"
    if not signals:
        signals = "—"

    return f"""\
**{idx}.**  {title}
    {meta}
    {authors}
    {signals}"""


def _extract_signals(paper: dict) -> str:
    """从摘要提取产品信号标签，去重后最多 3 个"""
    text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
    seen = set()
    badges = []

    signal_map = [
        ("open source", "Open Source"),
        ("github", "GitHub"),
        ("code", "代码开源"),
        ("release", "已发布"),
        ("demo", "有 Demo"),
        ("user study", "用户研究"),
        ("production", "生产环境"),
        ("state of the art", "SOTA"),
        ("outperform", "SOTA"),
        ("benchmark", "基准测试"),
        ("real world", "真实场景"),
        ("deploy", "已部署"),
        ("scale", "规模化"),
        ("product", "产品化"),
        ("application", "应用导向"),
        ("practical", "实用"),
    ]

    for keyword, label in signal_map:
        if keyword in text and label not in seen:
            seen.add(label)
            badges.append(f"▸ {label}")
            if len(badges) >= 3:
                break

    return "  ".join(badges) if badges else ""


def wechat_daily_header(paper_count: int, relevant_count: int) -> str:
    """WeChat 简报头部"""
    today = datetime.now(timezone(timedelta(hours=8)))
    date_str = f"{today.month}/{today.day}"
    weekday = WEEKDAYS[today.weekday()]

    return f"""\
**arXiv Daily**  周{weekday} · {date_str}

{paper_count} 篇论文 · {relevant_count} 篇与你相关
{DIV}"""


def wechat_daily_footer(saved_count: int) -> str:
    """WeChat 简报尾部"""
    return f"""\
{DIV}
📁 {saved_count} 篇已存 inbox  ·  Obsidian 即看"""


def wechat_daily_empty() -> str:
    """无新论文"""
    today = datetime.now(timezone(timedelta(hours=8)))
    date_str = f"{today.month}/{today.day}"
    return f"""\
**arXiv Daily**  {date_str}

今天没有符合关键词的新论文
存量阅读日 📖"""


def wechat_daily_full(
    papers: list[dict],
    paper_count: int,
    relevant_count: int,
    saved_count: int,
    max_show: int = 5,
) -> str:
    """完整 WeChat 简报

    max_show: 展开卡片数（默认 5，手机一屏刚好）
    超出部分折叠为索引列表
    """
    if not papers:
        return wechat_daily_empty()

    parts = [wechat_daily_header(paper_count, relevant_count), ""]

    # 展开前 N 篇
    for i, p in enumerate(papers[:max_show], 1):
        parts.append(paper_card(p, i))
        parts.append("")

    # 折叠剩余
    if len(papers) > max_show:
        remaining = papers[max_show:]
        parts.append(f"*…还有 {len(remaining)} 篇已存 inbox*")
        for i, p in enumerate(remaining, max_show + 1):
            arxiv_id = p.get("arxiv_id", "")
            t = p["title"][:55]
            parts.append(f"  {i}. {t}{'…' if len(p['title'])>55 else ''}  `{arxiv_id}`")
        parts.append("")

    parts.append(wechat_daily_footer(saved_count))
    return "\n".join(parts)


# ─── HTML 邮件模板 ────────────────────────────────────────

EMAIL_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: #f7f7f8;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
    color: #1a1a2e;
    -webkit-font-smoothing: antialiased;
}
.wrapper { max-width: 520px; margin: 0 auto; padding: 24px 16px; }
.card {
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04);
    margin-bottom: 20px;
}

/* header */
.header {
    background: #1a1a2e;
    color: #fff;
    padding: 28px 24px;
    text-align: center;
}
.header .brand {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.header .date {
    font-size: 13px;
    opacity: 0.65;
    margin-top: 6px;
}

/* stats */
.stats-row {
    display: flex;
    padding: 20px 24px;
    gap: 16px;
}
.stat-box {
    flex: 1;
    background: #f7f7f8;
    border-radius: 10px;
    padding: 14px 12px;
    text-align: center;
}
.stat-box .num {
    font-size: 26px;
    font-weight: 700;
    color: #1a1a2e;
}
.stat-box .label {
    font-size: 11px;
    color: #888;
    margin-top: 4px;
    letter-spacing: 0.3px;
}

/* papers */
.paper-list { padding: 0 24px 16px 24px; }
.paper-item {
    padding: 14px 0;
    border-bottom: 1px solid #f0f0f2;
}
.paper-item:last-child { border: none; }
.paper-item .idx {
    font-size: 11px;
    font-weight: 600;
    color: #aaa;
    margin-bottom: 4px;
}
.paper-item .title {
    font-size: 15px;
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: 6px;
}
.paper-item .title a {
    color: #1a1a2e;
    text-decoration: none;
}
.paper-item .title a:hover { color: #4f46e5; }
.paper-item .meta {
    font-size: 12px;
    color: #999;
    margin-bottom: 6px;
    line-height: 1.5;
}
.paper-item .meta code {
    background: #f0f0f2;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 11px;
    color: #666;
}
.signal-tag {
    display: inline-block;
    font-size: 11px;
    color: #4f46e5;
    background: #eef0ff;
    padding: 2px 8px;
    border-radius: 10px;
    margin-right: 4px;
    margin-bottom: 3px;
    font-weight: 500;
}

/* footer */
.footer {
    padding: 16px 24px;
    background: #fafafa;
    text-align: center;
    font-size: 11px;
    color: #bbb;
    line-height: 1.6;
}
.footer a { color: #999; text-decoration: none; }

/* empty */
.empty-note {
    text-align: center;
    padding: 40px 24px;
    color: #bbb;
    font-size: 14px;
    line-height: 1.8;
}
.empty-note .empty-icon { font-size: 40px; margin-bottom: 8px; }

/* folded note */
.folded-note {
    text-align: center;
    font-size: 12px;
    color: #aaa;
    padding: 8px 0 14px 0;
    border-bottom: 1px solid #f0f0f2;
}
.folded-list {
    padding: 8px 0 0 0;
    font-size: 12px;
    color: #999;
    line-height: 1.8;
}
.folded-list code {
    background: #f0f0f2;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 10px;
    color: #888;
}
"""


def email_paper_card(paper: dict, idx: int) -> str:
    """单篇论文 — HTML"""
    title = paper["title"].strip()
    arxiv_id = paper.get("arxiv_id", "")
    authors = ", ".join(paper.get("authors", [])[:3])
    cats = ", ".join(paper.get("categories", [])[:2])
    url = paper.get("url", f"https://arxiv.org/abs/{arxiv_id}")
    signals = _extract_signals(paper)

    signal_html = ""
    if signals:
        tags = [s.replace("▸ ", "") for s in signals.split("  ")]
        signal_html = "".join(
            f'<span class="signal-tag">{t}</span>' for t in tags if t
        )

    return f"""\
<div class="paper-item">
    <div class="idx">NO. {idx}</div>
    <div class="title"><a href="{url}">{title}</a></div>
    <div class="meta">
        <code>{arxiv_id}</code> · {cats}<br>
        {authors}
    </div>
    {signal_html}
</div>"""


def email_daily_full(
    papers: list[dict],
    paper_count: int,
    relevant_count: int,
    max_show: int = 8,
) -> str:
    """完整 HTML 邮件"""
    today = datetime.now(timezone(timedelta(hours=8)))
    date_str = f"{today.month}月{today.day}日 · 星期{WEEKDAYS[today.weekday()]}"

    if papers:
        paper_html = ""
        for i, p in enumerate(papers[:max_show], 1):
            paper_html += email_paper_card(p, i)

        if len(papers) > max_show:
            remaining = len(papers) - max_show
            paper_html += f"""\
<div class="folded-note">还有 {remaining} 篇已存入本地</div>
<div class="folded-list">
"""
            for i, p in enumerate(papers[max_show:], max_show + 1):
                t = p["title"][:55]
                aid = p.get("arxiv_id", "")
                paper_html += (
                    f"{i}. {t}{'…' if len(p['title'])>55 else ''}  "
                    f"<code>{aid}</code><br>"
                )
            paper_html += "</div>"
    else:
        paper_html = f"""\
<div class="empty-note">
    <div class="empty-icon">📭</div>
    今天没有符合关键词的新论文<br>
    存量阅读日 📖
</div>"""

    return f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>arXiv Daily — {date_str}</title>
<style>{EMAIL_CSS}</style>
</head>
<body>
<div class="wrapper">
  <div class="card">
    <div class="header">
      <div class="brand">arXiv Daily</div>
      <div class="date">{date_str}</div>
    </div>
    <div class="stats-row">
      <div class="stat-box">
        <div class="num">{paper_count}</div>
        <div class="label">检索论文</div>
      </div>
      <div class="stat-box">
        <div class="num">{relevant_count}</div>
        <div class="label">产品相关</div>
      </div>
    </div>
    <div class="paper-list">{paper_html}</div>
    <div class="footer">
      Paper2Product · 每日自动生成<br>
      <a href="https://github.com/graceruowenwang/paper2product">
        github.com/graceruowenwang/paper2product
      </a>
    </div>
  </div>
</div>
</body>
</html>"""


# ─── 邮箱配置 ─────────────────────────────────────────────

SMTP_CONFIG = {
    "yeah": {
        "host": "smtp.yeah.net",
        "port": 465,
        "use_ssl": True,
        "sender": "Product Lens <ruowenwang@yeah.net>",
    },
    "wukong": {
        "host": "smtp.exmail.qq.com",
        "port": 587,
        "sender": "Product Lens <account@wukong-editor.com>",
    },
}
