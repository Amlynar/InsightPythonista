# Insight (Pythonista)

A single-screen Pythonista 3 (iOS) dashboard that answers: *"after I pay what I owe this month, what do I actually have left?"*

It reads from the InsightBE backend (`GET /api/v1/accounts`), shows cached data immediately on launch, refreshes in the background, and degrades gracefully on network failure or Plaid reauth issues.

## Features

- **Dashboard** with three cards:
  - **Net Position** = Total Cash - Total Liability (most prominent)
  - **Total Cash** and **Total Liability**
  - "Last updated: 2h ago" label with a small refresh spinner
- **Cache-first launch**: renders from `Documents/insight_cache.json`, then refreshes automatically.
- **Refresh failure banner**: inline, non-modal; cached totals stay on screen.
- **Reauth banner**: shown when `hasStaleData` is true, naming each institution in `linksNeedingReauth`. Display only; totals are never withheld.
- **Refresh** (left nav-bar icon): re-runs `GET /accounts` on demand.
- **Sync Now** (button below the cards): `POST /api/v1/sync`, polls `/api/v1/sync/status` every 2s for up to 60s, then does a plain Refresh. If still running after 60s, an inline banner says so.
- **Settings** screen (gear button): Base URL and API Key, saved to `Documents/insight_settings.json`. Save pops back to the Dashboard and refreshes immediately.

Out of scope: per-account lists, reauth/Plaid Link flow, savings goals, history, pull-to-refresh, notifications.

## Classification rules

Implemented as a pure function in `src/common/insight_totals.py`:

| Total | Accounts included (sum of `balance`) |
|---|---|
| Total Liability | `type == "credit"` |
| Total Cash | `type == "depository"`, or `type == "investment"` with `balanceField == "AVAILABLE"` |
| Net Position | Total Cash - Total Liability |

Other account types (e.g. loans) are excluded from both totals. `balance` is trusted as-is and never re-derived from `current`/`available`.

## Requirements

- Pythonista 3 on iOS (Python 3.10+).
- PocketRepo's shared `framework` package installed in `Documents/site-packages-3/framework` (use PocketRepo's **Export Framework**).
- For `*.home.arpa` backends: the home-lab CA certificate downloaded via PocketRepo's **Download CA Certificate** button. If it is missing, the refresh banner shows the framework's error message verbatim.
- A running InsightBE and its API key.

## Setup

1. Install the framework and CA certificate via PocketRepo (see above).
2. Copy/install this project's `src/` into Pythonista and run `src/main.py`.
3. Tap the gear icon, enter Base URL (e.g. `https://insight.home.arpa`) and API Key, then Save.
4. Save returns to the Dashboard and refreshes with the new values.

## Project structure

```
src/
  main.py                      entry point
  application/insight_app.py   PYIApp subclass, route -> controller mapping
  core/app_module.py           injector module (theme)
  navigation/routes.py         Dashboard / Settings routes
  screens/
    dashboard/                 model, view, controller
    settings/                  model, view, controller
  common/
    insight_totals.py          pure classification/aggregation
    insight_client.py          GET /accounts via PYIHomeLabSession
    insight_cache.py           insight_cache.json read/write
    insight_settings.py        insight_settings.json read/write
    time_utils.py              ISO parsing, relative time
    palette.py                 Insight-specific colors
    paths.py                   Documents file paths
tests/                         desktop unit tests (pure logic)
```

The app follows PocketRepo's framework conventions: MVC screens (`PYIScreen`, `PYIController`), `PYIRoute` navigation, `PYITheme` styling and `injector` DI.

## Local files

| File | Contents |
|---|---|
| `Documents/insight_cache.json` | `{"cachedAt": ISO-8601, "response": <raw /accounts body>}` |
| `Documents/insight_settings.json` | `{"baseUrl": "...", "apiKey": "..."}` |

Both are gitignored. The API key is stored in plain text on the device.

## Development

The pure logic can be tested on a desktop (UI modules need Pythonista's `ui`):

```
python -m pytest
```

For editor/IDE support, `.opencode/opencode.json` and `.vscode/settings.json` point at PocketRepo's `src/framework`. Both are gitignored.

