#!/usr/bin/python3
# -*- coding: utf-8 -*-
# <swiftbar.title>Claude API Cost Today</swiftbar.title>
# <swiftbar.version>v1.0</swiftbar.version>
# <swiftbar.author>Brandon</swiftbar.author>
# <swiftbar.desc>Shows today's Anthropic API spend from the Admin Cost Report API</swiftbar.desc>
# <swiftbar.dependencies>python3</swiftbar.dependencies>
# <swiftbar.refreshOnOpen>true</swiftbar.refreshOnOpen>
# <swiftbar.hideSwiftBar>true</swiftbar.hideSwiftBar>

import json
import os
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone, timedelta

CONFIG_FILE = os.path.expanduser("~/.config/claude-cost/admin_key")
API_BASE = "https://api.anthropic.com"


def get_api_key():
    key = os.environ.get("ANTHROPIC_ADMIN_KEY", "").strip()
    if key:
        return key
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return f.read().strip()
    return None


def fetch_cost(api_key):
    now_local = datetime.now().astimezone()
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    starting_at = today_start.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ending_at = today_end.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = urllib.parse.urlencode([
        ("starting_at", starting_at),
        ("ending_at", ending_at),
        ("bucket_width", "1d"),
        ("group_by[]", "description"),
    ])
    url = f"{API_BASE}/v1/organizations/cost_report?{params}"

    req = urllib.request.Request(url, headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "User-Agent": "ClaudeUsageMeter/1.0",
    })

    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def shorten_model(model):
    """Turn e.g. 'claude-opus-4-6' into 'Opus 4.6'"""
    name = model.lower()
    name = name.replace("claude-", "")
    # Normalize version separators: last two dash-separated segments that are
    # digits form the version (e.g. "4-6" -> "4.6", "3-5" -> "3.5")
    parts = name.split("-")
    version_parts = []
    while parts and parts[-1].isdigit():
        version_parts.insert(0, parts.pop())
    version = ".".join(version_parts) if version_parts else ""
    family = " ".join(p.capitalize() for p in parts)
    return f"{family} {version}".strip() if version else family.strip()


def main():
    api_key = get_api_key()
    if not api_key:
        print("claude ⚠")
        print("---")
        print("No Admin API key found")
        print("---")
        print(f"Create config file:")
        print(f"mkdir -p ~/.config/claude-cost")
        print(f"echo 'sk-ant-admin...' > {CONFIG_FILE}")
        print(f"chmod 600 {CONFIG_FILE}")
        return

    try:
        data = fetch_cost(api_key)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print("claude ⚠")
        print("---")
        print(f"API error {e.code}")
        try:
            msg = json.loads(body).get("error", {}).get("message", body[:120])
        except Exception:
            msg = body[:120]
        print(msg)
        return
    except urllib.error.URLError as e:
        print("claude ⚠")
        print("---")
        print(f"Network error: {e.reason}")
        return
    except Exception as e:
        print("claude ⚠")
        print("---")
        print(str(e))
        return

    # Sum totals and build per-model breakdown
    total_cents = 0.0
    by_model = {}

    for bucket in data.get("data", []):
        for result in bucket.get("results", []):
            cents = float(result.get("amount", "0"))
            total_cents += cents
            model = result.get("model") or "Other"
            by_model[model] = by_model.get(model, 0.0) + cents

    total_usd = total_cents / 100.0

    # Menu bar title
    print(f"${total_usd:.2f}")
    print("---")
    print(f"Today's Claude API Cost")
    print("---")

    if by_model:
        for model, cents in sorted(by_model.items(), key=lambda x: -x[1]):
            usd = cents / 100.0
            if usd >= 0.001:
                name = shorten_model(model)
                print(f"${usd:.4f}  {name}")
    else:
        print("No usage recorded yet today")

    print("---")
    print(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    print("Refresh | refresh=true")
    print("Open Console | href=https://console.anthropic.com/cost")


if __name__ == "__main__":
    main()
