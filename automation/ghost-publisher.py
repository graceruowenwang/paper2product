#!/usr/bin/env python3
"""
Product Lens — Ghost 发布器
使用 Ghost Admin API 创建/发布文章到 https://lens.ruowenwang.site

JWT 认证：Admin API Key (id:secret) → HS256 JWT → Ghost Admin API
"""

import argparse
import hashlib
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

import jwt  # PyJWT

# ─── 配置 ─────────────────────────────────────────────

GHOST_URL = "https://lens.ruowenwang.site"
ADMIN_API_KEY = "6a0b1c65f7042a75ef005bcc:f1be9dfcf0bc1f63050342e82efaa5a38eeaa532058fdcb2fa17e548edee3a89"


def get_jwt() -> str:
    """生成 Ghost Admin API JWT token（5 分钟有效）"""
    kid, secret = ADMIN_API_KEY.split(":", 1)
    iat = int(time.time())
    return jwt.encode(
        {"iat": iat, "exp": iat + 300, "aud": "/admin/"},
        bytes.fromhex(secret),
        algorithm="HS256",
        headers={"kid": kid},
    )


def api_request(method: str, path: str, data: dict | None = None) -> dict:
    """Ghost Admin API 请求"""
    token = get_jwt()
    url = f"{GHOST_URL}/ghost/api/admin/{path}"

    body = None
    if data:
        body = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Ghost {token}",
            "Content-Type": "application/json",
            "Accept-Version": "v5.0",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")[:500]
        raise RuntimeError(f"Ghost API {e.code}: {err_body}") from e


def create_post(
    title: str,
    html: str,
    status: str = "draft",
    tags: list[str] | None = None,
    feature_image: str | None = None,
    publish_now: bool = False,
) -> dict:
    """创建文章"""
    post_data: dict = {
        "title": title,
        "html": html,
        "status": status,
    }

    if tags:
        post_data["tags"] = [{"name": t} for t in tags]
    if feature_image:
        post_data["feature_image"] = feature_image
    if publish_now and status == "published":
        post_data["email_recipient_filter"] = "all"

    result = api_request("POST", "posts/?source=html", {"posts": [post_data]})
    return result["posts"][0]


def update_post(post_id: str, **kwargs) -> dict:
    """更新已有文章"""
    result = api_request("PUT", f"posts/{post_id}/?source=html", {"posts": [kwargs]})
    return result["posts"][0]


def list_posts(limit: int = 10, status: str = "all") -> list[dict]:
    """列出文章"""
    result = api_request("GET", f"posts/?limit={limit}&formats=html")
    return result.get("posts", [])


# ─── Pipeline 集成 ─────────────────────────────────────

def from_email_html(html_path: str, title: str, tags: list[str] | None = None) -> dict:
    """从现有 HTML 邮件内容创建 Ghost 文章"""
    html_content = Path(html_path).read_text(encoding="utf-8")
    return create_post(title=title, html=html_content, tags=tags, status="draft")


# ─── Main ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Product Lens Ghost 发布器")
    sub = parser.add_subparsers(dest="cmd")

    # create
    p_create = sub.add_parser("create", help="创建新文章")
    p_create.add_argument("--title", required=True, help="文章标题")
    p_create.add_argument("--html-file", help="HTML 文件路径")
    p_create.add_argument("--html", help="HTML 内容（直接传入）")
    p_create.add_argument("--tags", nargs="*", help="标签列表")
    p_create.add_argument("--publish", action="store_true", help="直接发布（默认草稿）")

    # list
    p_list = sub.add_parser("list", help="列出文章")
    p_list.add_argument("--limit", type=int, default=10)

    # update
    p_update = sub.add_parser("update", help="更新文章")
    p_update.add_argument("--id", required=True, help="文章 ID")
    p_update.add_argument("--title", help="新标题")
    p_update.add_argument("--html-file", help="新 HTML 文件")
    p_update.add_argument("--publish", action="store_true", help="发布")

    args = parser.parse_args()

    if args.cmd == "create":
        html = None
        if args.html_file:
            html = Path(args.html_file).read_text(encoding="utf-8")
        elif args.html:
            html = args.html
        else:
            print("❌ 需要 --html-file 或 --html", file=sys.stderr)
            sys.exit(1)

        status = "published" if args.publish else "draft"
        post = create_post(
            title=args.title,
            html=html,
            status=status,
            tags=args.tags,
            publish_now=args.publish,
        )
        print(f"✅ 文章已创建: {post['url']}")
        print(f"   ID: {post['id']}")
        print(f"   状态: {post['status']}")

    elif args.cmd == "list":
        posts = list_posts(limit=args.limit)
        for p in posts:
            print(f"  [{p['status']}] {p['title'][:60]}  {p['url']}")

    elif args.cmd == "update":
        kwargs = {}
        if args.title:
            kwargs["title"] = args.title
        if args.html_file:
            kwargs["html"] = Path(args.html_file).read_text(encoding="utf-8")
        if args.publish:
            kwargs["status"] = "published"

        post = update_post(args.id, **kwargs)
        print(f"✅ 文章已更新: {post['url']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
