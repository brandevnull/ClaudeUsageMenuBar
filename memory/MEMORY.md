# ClaudeUsageMeter — Project Memory

## What This Is
A SwiftBar plugin (`claude-cost.5m.py`) that displays today's Anthropic API spend in the macOS menu bar. Refreshes every 5 minutes.

## Key Files
- `claude-cost.5m.py` — the SwiftBar plugin script (Python, no third-party deps)
- `PLAN.md` — original implementation plan

## Setup
- SwiftBar: `brew install swiftbar`; on first launch point Plugin Folder at this repo dir
- Admin API key: `~/.config/claude-cost/admin_key` (or `ANTHROPIC_ADMIN_KEY` env var)
- Must be an **Admin key** (`sk-ant-admin...`), not a regular API key
- Admin API requires an **Organization** set up in the Claude Console (not individual accounts)
- Python: uses `/usr/bin/python3` (system 3.9.6) — `/usr/local/bin/python3` is a broken stale Python 3.6 symlink from 2018, do not use

## Anthropic Cost Report API — Learned Behaviors
- Endpoint: `GET https://api.anthropic.com/v1/organizations/cost_report`
- Only supports `bucket_width=1d` (daily granularity)
- **Only returns completed UTC day buckets** — the current in-progress day is never included
- `ending_at` must not be in the future — use `datetime.now(timezone.utc)` not end-of-day
- URL must be built with f-strings (literal `[]` in `group_by[]=description`) — `urllib.parse.urlencode` encodes `[` as `%5B` and `:` as `%3A`, which the API rejects
- Amounts are in **cents** as decimal strings (e.g. `"245.85"` = $2.46) — divide by 100 for USD
- Data freshness: typically within 5 minutes of API call completion

## Date Range Strategy
Request last 2 days with `ending_at=now_utc`; take the most recent returned bucket. This always yields the last completed UTC day regardless of local timezone.

## Model Name Formatting
Model names like `claude-haiku-4-5-20251001` contain an 8-digit date stamp suffix. Strip it before collecting version digits. Pattern: strip trailing 8-digit segments, then collect trailing 1-2 digit segments as the version number.
