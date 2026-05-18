#!/usr/bin/env python3
"""
Paper2Product — 论文摘要生成器
读取 papers/inbox/ 中的论文，调用 LLM 提取关键信息，写入 papers/reading/
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INBOX = PROJECT_ROOT / "papers" / "inbox"
READING = PROJECT_ROOT / "papers" / "reading"
PROMPT_FILE = PROJECT_ROOT / "prompts" / "extract-key-info.md"


def load_prompt() -> str:
    """加载 extract-key-info prompt"""
    text = PROMPT_FILE.read_text(encoding="utf-8")
    # 提取 prompt 代码块
    in_block = False
    lines = []
    for line in text.split("\n"):
        if line.strip() == "```" and not in_block:
            in_block = True
            continue
        if line.strip() == "```" and in_block:
            break
        if in_block:
            lines.append(line)
    return "\n".join(lines)


def read_paper(filepath: Path) -> dict:
    """读取 inbox 论文文件，提取标题和摘要"""
    text = filepath.read_text(encoding="utf-8")
    title = ""
    summary = ""
    
    for line in text.split("\n"):
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        if line.startswith("## 摘要"):
            # 收集摘要内容
            in_summary = True
            continue
        if in_summary:
            if line.startswith("---") or line.startswith("*自动收录"):
                break
            if line.strip():
                summary += line.strip() + " "
    
    return {
        "filepath": filepath,
        "arxiv_id": filepath.stem.split("_", 1)[-1] if "_" in filepath.stem else filepath.stem,
        "title": title,
        "summary": summary.strip(),
    }


def generate_reading_note(paper: dict, prompt_template: str) -> str:
    """生成阅读笔记模板（人工 + AI 协作）"""
    return f"""# {paper['title']}

- **arXiv**: [{paper['arxiv_id']}](https://arxiv.org/abs/{paper['arxiv_id']})
- **状态**: 阅读中
- **开始阅读**: {datetime.now().strftime('%Y-%m-%d')}

## 原始摘要

{paper['summary']}

---

## 快速判断（人工填写）

- [ ] 值得精读？
- [ ] 有开源代码？
- [ ] 产品化潜力：高 / 中 / 低
- [ ] 选题优先级：P0 / P1 / P2

## AI 提取关键信息

> 将以下内容粘贴到 LLM 中，使用 `prompts/extract-key-info.md`

### 论文内容
```
{paper['summary']}
```

---

## 产品化分析（人工填写）

### 一句话产品化判断
> [这篇论文最值得做的一个产品方向是什么？为什么？]

### 可执行的产品方案
1. 
2. 

### 技术可行性
- 实现难度: 
- 所需资源: 
- 时间估算: 

---
*迁移自 inbox → reading | {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""


def main():
    parser = argparse.ArgumentParser(description="论文摘要生成器")
    parser.add_argument("paper", nargs="?", help="指定论文文件名（可选，默认处理 inbox 中所有新论文）")
    parser.add_argument("--move", action="store_true", help="处理后将论文从 inbox 移到 reading")
    args = parser.parse_args()

    prompt = load_prompt()
    print(f"📋 已加载 prompt ({len(prompt)} 字符)")

    if args.paper:
        files = [INBOX / args.paper]
    else:
        files = sorted(INBOX.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)

    if not files:
        print("📭 papers/inbox/ 中没有论文")
        return

    print(f"📄 处理 {len(files)} 篇论文\n")

    for fp in files[:10]:  # 一次最多 10 篇
        paper = read_paper(fp)
        print(f"→ {paper['title'][:80]}...")

        note = generate_reading_note(paper, prompt)
        out_path = READING / fp.name
        READING.mkdir(parents=True, exist_ok=True)
        out_path.write_text(note, encoding="utf-8")
        print(f"  ✅ → reading/{fp.name}")

        if args.move:
            fp.unlink()
            print(f"  🗑️  已从 inbox 移除")

    print(f"\n💡 下一步: 打开 papers/reading/ 中的文件，将 AI 分析结果填入")


if __name__ == "__main__":
    main()
