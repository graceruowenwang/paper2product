#!/usr/bin/env python3
"""
Paper2Product — 邮件摘要发送器
生成当天的 arXiv HTML 邮件并通过 SMTP 发送
"""

import argparse
import os
import smtplib
import sys
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# 确保能 import 同目录的 templates
sys.path.insert(0, str(Path(__file__).resolve().parent))

from templates import email_daily_full, SMTP_CONFIG


def send_email(
    html_content: str,
    to: str,
    subject: str,
    smtp_config: dict,
    username: str,
    password: str,
) -> bool:
    """通过 SMTP 发送 HTML 邮件（支持 SSL 和 STARTTLS）"""
    import ssl

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_config["sender"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        use_ssl = smtp_config.get("use_ssl", False)
        if use_ssl:
            ctx = ssl.create_default_context()
            server = smtplib.SMTP_SSL(
                smtp_config["host"], smtp_config["port"],
                timeout=30, context=ctx
            )
        else:
            server = smtplib.SMTP(
                smtp_config["host"], smtp_config["port"], timeout=30
            )
            server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="arXiv 邮件摘要")
    parser.add_argument(
        "--to", default="ruowenwang@yeah.net",
        help="收件人邮箱",
    )
    parser.add_argument(
        "--provider", choices=["yeah", "wukong"], default="yeah",
        help="SMTP 服务商",
    )
    parser.add_argument(
        "--html-file",
        help="已有 HTML 文件路径（可选，不传则搜 papers/digests/）",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只生成 HTML，不发送",
    )
    parser.add_argument(
        "--papers-dir",
        default=None,
        help="papers/inbox/ 路径（用于重新生成邮件）",
    )
    args = parser.parse_args()

    # ─── 获取密码 ───
    password = os.environ.get("SMTP_PASSWORD")
    if not password and not args.dry_run:
        print("❌ 请设置环境变量 SMTP_PASSWORD", file=sys.stderr)
        print("   export SMTP_PASSWORD='your-app-password'", file=sys.stderr)
        sys.exit(1)

    smtp_config = SMTP_CONFIG.get(args.provider, SMTP_CONFIG["yeah"])
    username = smtp_config["sender"].split("<")[-1].rstrip(">") if "<" in smtp_config["sender"] else smtp_config["sender"]

    # ─── 获取 HTML 内容 ───
    html_content = None

    if args.html_file:
        html_path = Path(args.html_file)
        if html_path.exists():
            html_content = html_path.read_text(encoding="utf-8")
            print(f"📄 使用已有文件: {html_path}")
        else:
            print(f"❌ 文件不存在: {html_path}", file=sys.stderr)
            sys.exit(1)
    else:
        # 自动找今天的 digest
        today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
        digest_dir = Path(__file__).resolve().parent.parent / "papers" / "digests"
        digest_file = digest_dir / f"arxiv-digest-{today}.html"

        if digest_file.exists():
            html_content = digest_file.read_text(encoding="utf-8")
            print(f"📄 使用今日摘要: {digest_file}")
        else:
            print(f"⚠️  今日无摘要文件 ({digest_file})", file=sys.stderr)
            # 尝试重新生成
            print("   尝试从 papers/inbox/ 重新生成...")
            # 直接输出空模板
            html_content = email_daily_full(papers=[], paper_count=0, relevant_count=0)

            # 保存
            digest_dir.mkdir(parents=True, exist_ok=True)
            digest_file.write_text(html_content, encoding="utf-8")
            print(f"   已保存: {digest_file}")

    if not html_content:
        print("❌ 无法生成邮件内容", file=sys.stderr)
        sys.exit(1)

    # ─── 发送或保存 ───
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%m/%d")
    subject = f"Product Lens 双周洞察 — {today}"

    if args.dry_run:
        out_path = Path("/tmp/arxiv-email-preview.html")
        out_path.write_text(html_content, encoding="utf-8")
        print(f"🔍 Dry run — HTML 已保存: {out_path}")
        print(f"   收件人: {args.to}")
        print(f"   主题: {subject}")
        return

    print(f"📧 发送中 → {args.to}...")
    success = send_email(
        html_content=html_content,
        to=args.to,
        subject=subject,
        smtp_config=smtp_config,
        username=username,
        password=password,
    )

    if success:
        print("✅ 邮件已发送")
    else:
        print(f"💡 提示: yeah.net 需要应用专用密码（非登录密码）", file=sys.stderr)
        print(f"   在网易邮箱设置 → POP3/SMTP → 生成授权码", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
