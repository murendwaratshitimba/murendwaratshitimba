#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.request

DEFAULT_CHANNEL_ID = "UCm3moBxexOnsaGSMoquscHg"


def format_count(value: int) -> str:
    if value >= 1_000_000_000:
        num = f"{value/1_000_000_000:.2f}".rstrip("0").rstrip(".")
        return f"{num}B"
    if value >= 1_000_000:
        num = f"{value/1_000_000:.2f}".rstrip("0").rstrip(".")
        return f"{num}M"
    if value >= 1_000:
        num = f"{value/1_000:.1f}".rstrip("0").rstrip(".")
        return f"{num}K"
    return str(value)


def fetch_stats(api_key: str, channel_id: str) -> tuple[int, int]:
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        f"?part=statistics&id={channel_id}&key={api_key}"
    )
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    items = data.get("items", [])
    if not items:
        raise RuntimeError("No channel statistics returned. Check channel ID and API key.")

    stats = items[0].get("statistics", {})
    subs = int(stats.get("subscriberCount", 0))
    views = int(stats.get("viewCount", 0))
    return subs, views


def replace_text_by_id(path: str, element_id: str, value: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = (
        rf'(<text[^>]*id="{re.escape(element_id)}"[^>]*>)(.*?)(</text>)'
    )
    if not re.search(pattern, content, flags=re.DOTALL):
        raise RuntimeError(f'Text element with id="{element_id}" not found in {path}')

    updated = re.sub(pattern, rf"\\1{value}\\3", content, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)


def main() -> int:
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY is required", file=sys.stderr)
        return 1

    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID", DEFAULT_CHANNEL_ID)

    subs, views = fetch_stats(api_key, channel_id)

    subs_display = format_count(subs)
    views_display = format_count(views)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    subs_svg = os.path.join(repo_root, "youtube-subs.svg")
    views_svg = os.path.join(repo_root, "youtube-views.svg")

    replace_text_by_id(subs_svg, "subs-count", subs_display)
    replace_text_by_id(views_svg, "views-count", views_display)

    print(f"Updated counts: subscribers={subs_display}, views={views_display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
