# Claude Usage Meter

A [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin that shows your Anthropic API spend in the macOS menu bar, updated every 5 minutes.

```
$2.46
├── Sonnet 4.6   $2.37
└── Haiku 4.5    $0.09
```

## Requirements

- macOS
- [SwiftBar](https://github.com/swiftbar/SwiftBar)
- An Anthropic **Admin API key** (`sk-ant-admin...`)
- Your Anthropic account must be set up as an **Organization** (Console → Settings → Organization) — individual accounts don't have access to the Cost Report API

## Installation

**1. Install SwiftBar**

```bash
brew install swiftbar
```

**2. Clone this repo**

```bash
git clone https://github.com/brandevnull/ClaudeUsageMenuBar.git
```

**3. Point SwiftBar at the repo**

On first launch, SwiftBar will ask you to choose a Plugin Folder. Select the cloned repo directory. SwiftBar will pick up `claude-cost.5m.py` automatically.

> If SwiftBar is already running with a different plugin folder, symlink the script instead:
> ```bash
> ln -sf /path/to/ClaudeUsageMenuBar/claude-cost.5m.py \
>   /path/to/your/swiftbar/plugins/claude-cost.5m.py
> ```

**4. Add your Admin API key**

```bash
mkdir -p ~/.config/claude-cost
echo 'sk-ant-admin...' > ~/.config/claude-cost/admin_key
chmod 600 ~/.config/claude-cost/admin_key
```

Generate an Admin API key at [console.anthropic.com/settings/admin-keys](https://console.anthropic.com/settings/admin-keys).

That's it — the menu bar item will appear within seconds.

## Usage

| Menu item | What it does |
|---|---|
| `$2.46` (title) | Total spend for the most recent completed UTC day |
| Per-model lines | Cost breakdown sorted by spend |
| **Refresh** | Force an immediate data fetch |
| **Open Console** | Jump to the Anthropic Console cost page |

## A note on data freshness

The Anthropic Cost Report API only returns **completed UTC days** — the current in-progress day isn't available until it rolls over at midnight UTC. The plugin always shows the last fully completed UTC day, labeled with its date (e.g. `2026-02-23 UTC`). Data is typically available within 5 minutes of API call completion.

## Configuration

The plugin reads your Admin API key from `~/.config/claude-cost/admin_key` by default. You can also set it via environment variable:

```bash
export ANTHROPIC_ADMIN_KEY="sk-ant-admin..."
```

## Troubleshooting

| Menu bar shows | Cause | Fix |
|---|---|---|
| `claude ⚠` + "No Admin API key found" | Config file missing | Follow step 4 above |
| `claude ⚠` + "API error 401" | Wrong key type | Make sure you're using an **Admin** key, not a regular API key |
| `claude ⚠` + "API error 403" | No organization set up | Set up an org at Console → Settings → Organization |
| `claude ⚠` + "Network error" | No internet / Anthropic outage | Check your connection |

## License

MIT
