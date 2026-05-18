#!/usr/bin/env python3
"""
PM 视角生成器 — 调用 DeepSeek API 为每篇论文生成具体的产品化角度

不输出泛泛的"PM视角"，而是具体的一句判断：
  - "公共事业SaaS" 而不是 "PM视角"
  - "企业知识库替代方案" 而不是 "产品机会"
"""

import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional


def get_deepseek_key() -> str:
    """从 Hermes 配置读取 DeepSeek API key"""
    env_file = Path.home() / ".hermes" / ".env"
    for line in env_file.read_text().split("\n"):
        if line.startswith("DEEPSEEK_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("DEEPSEEK_API_KEY not found in ~/.hermes/.env")


def generate_pm_angle(title: str, abstract: str, api_key: str) -> str:
    """用 DeepSeek 生成一句话产品化角度（10 字以内）"""

    prompt = (
        "你是一个 AI 产品经理。读出论文的产品机会，用 10 字以内中文一句话总结。\n"
        "规则：\n"
        "- 不要说「产品机会」「PM视角」这种废话\n"
        "- 直接说具体是什么产品/场景\n"
        "- 例如：「公共事业SaaS」「企业知识库引擎」「开发者工具」「C端内容生成」\n"
        "- 只输出结果，不要解释\n"
        f"\n标题：{title}\n摘要：{abstract[:400]}\n\n产品角度："
    )

    data = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 20,
        "temperature": 0.3,
    }).encode()

    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read())
        result = body["choices"][0]["message"]["content"].strip()
        # 清理引号和废话前缀
        for prefix in ["产品机会：", "产品角度：", "产品机会:", "产品角度:"]:
            result = result.removeprefix(prefix).strip()
        return result.strip('"\'""''')[:15]


def batch_generate(papers: list[dict], api_key: Optional[str] = None) -> list[dict]:
    """批量生成 PM 视角，返回更新后的论文列表"""
    if api_key is None:
        api_key = get_deepseek_key()

    for i, p in enumerate(papers):
        title = p.get("title", "")
        abstract = p.get("summary", "")
        try:
            angle = generate_pm_angle(title, abstract, api_key)
            p["pm_angle"] = angle
            print(f"  [{i+1}/{len(papers)}] {angle}", file=sys.stderr)
        except Exception as e:
            p["pm_angle"] = ""
            print(f"  [{i+1}/{len(papers)}] FAILED: {e}", file=sys.stderr)

    return papers


# CLI entry point
if __name__ == "__main__":
    # 测试模式：从命令行参数或 stdin 读取标题和摘要
    if len(sys.argv) >= 3:
        title, abstract = sys.argv[1], sys.argv[2]
        key = get_deepseek_key()
        print(generate_pm_angle(title, abstract, key))
    else:
        print("Usage: python pm_angle_generator.py <title> <abstract>")
