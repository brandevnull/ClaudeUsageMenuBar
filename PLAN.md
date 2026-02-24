# Plan: Claude API Cost Menu Bar Plugin

## Context

The goal is a macOS menu bar item that shows today's Anthropic API spend, refreshing automatically. The user has an Admin API key and prefers the SwiftBar approach (a simple Python script) over a full native Swift app. This avoids Xcode entirely while still integrating natively into the macOS menu bar. SwiftBar is chosen over xbar for its active maintenance and Homebrew availability.

## Prerequisites (user actions before we code)

1. Install **SwiftBar**: `brew install swiftbar`
2. On first launch, SwiftBar prompts for a Plugin Folder — point it at this repo (`/Users/brandon/workspace/ClaudeUsageMeter`) or a dedicated folder; if using a separate folder, a symlink is needed (see below)
3. Store the Admin API key in a config file:
   ```
   mkdir -p ~/.config/claude-cost
   echo 'sk-ant-admin...' > ~/.config/claude-cost/admin_key
   chmod 600 ~/.config/claude-cost/admin_key
   ```

## Files to Create

### Primary: `claude-cost.5m.py`

The plugin script. The `5m` in the filename tells xbar to refresh every 5 minutes.

**What it does:**
- Reads Admin API key from `~/.config/claude-cost/admin_key` (falls back to `ANTHROPIC_ADMIN_KEY` env var)
- Calls `GET https://api.anthropic.com/v1/organizations/cost_report` with today's local-time date range (converted to UTC), `bucket_width=1d`, and `group_by[]=description` for per-model breakdown
- Parses response: amounts are in cents as decimal strings → divide by 100 for USD
- Outputs xbar-formatted text:
  - Line 1: `$X.XX` — shown as the menu bar title
  - `---` separator
  - Per-model cost breakdown, sorted descending
  - Timestamp + manual Refresh link + link to open Console

**No third-party dependencies** — uses only Python stdlib (`urllib`, `json`, `datetime`, `os`).

**SwiftBar-specific metadata** (in script header comments):
- `swiftbar.refreshOnOpen=true` — refreshes data before showing the dropdown
- `swiftbar.hideSwiftBar=true` — hides the "Open SwiftBar" clutter item from the menu

**Error states** (shown in menu bar):
- `⚠ No key` — config file missing, with setup instructions in dropdown
- `⚠ API Error` — HTTP error with status code shown in dropdown
- `⚠ Network` — timeout or connection failure

### Pointing SwiftBar at this repo (preferred)

The simplest setup: on first SwiftBar launch, set the Plugin Folder directly to this repo directory. No symlink needed.

If the plugin folder is already set elsewhere, symlink instead:
```bash
chmod +x claude-cost.5m.py
ln -sf "$PWD/claude-cost.5m.py" /path/to/swiftbar-plugins/claude-cost.5m.py
```

## API Details

- **Endpoint:** `GET https://api.anthropic.com/v1/organizations/cost_report`
- **Key params:**
  - `starting_at` — local midnight converted to UTC RFC 3339
  - `ending_at` — local midnight+1d converted to UTC RFC 3339
  - `bucket_width=1d`
  - `group_by[]=description` (gives model-level breakdown)
- **Auth headers:** `x-api-key: sk-ant-admin...`, `anthropic-version: 2023-06-01`
- **Response amounts:** cents as decimal strings, e.g. `"123.45"` = $1.23
- **Data freshness:** typically within 5 minutes of API call completion

## xbar Plugin Output Format

```
$1.23                          ← menu bar title (line 1)
---
Today's Claude API Cost
---
$0.89  opus-4-6               ← per-model lines
$0.34  sonnet-4-6
---
Updated: 14:32:01
Refresh | refresh=true
Open Console | href=https://console.anthropic.com/cost
```

## Timezone Handling

The script uses Python's `datetime.now().astimezone()` to get the local timezone offset, then converts local midnight to UTC for the API call. This ensures "today" reflects the user's local calendar day, not UTC day.

## Verification

1. Run the script directly to test output: `python3 claude-cost.5m.py`
2. Verify menu bar title appears correctly (expect `$X.XX` or an error icon)
3. Click the menu bar item to see the cost breakdown dropdown
4. Click "Refresh" to force an immediate re-fetch
5. Click "Open Console" to verify the numbers match the Anthropic Console cost page
6. Wait 5 minutes to confirm auto-refresh works
