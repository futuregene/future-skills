---
version: 1.0.3
name: future-web
description: Search the public web for current information. Returns page titles, URLs, and content snippets from search results. Pair with fetch_url to retrieve full page content — if fetch_url returns empty or fails (e.g. JS-rendered pages, WeChat articles, anti-bot walls), automatically fall back to browser (command: open + snapshot). Use for fact-checking, news, documentation, and any information beyond your knowledge cutoff.
allowed-tools: Bash(future:*)
category: tools
---

> **Authentication is automatic.** The `future` CLI reads your credentials from `~/.future/agent/auth.json`. You do NOT need to find, configure, or pass API keys — just call the tools below.

> **Tip:** use `future tools describe <tool>` to see all available arguments for any tool.
# Web Search

## When to use this skill

Load this skill when the user asks to:
- Search the web or look up current information
- Find documentation, news, or recent events
- Fetch content from a specific URL
- Fact-check or verify claims
- 搜索网页 / 查资料 / 网上搜索 / 打开链接 / 查最新信息

**If the user mentions any of the above, stop what you're doing and use this skill.** Do not explore the filesystem or use curl directly — use the tools below.

## How to use

All tools are called via the `future` CLI using the `bash` tool:

```bash
# Search the web
future tools call web_search --query "BRCA1 variant classification guidelines 2025" --count 5

# Fetch a specific page (preferred first attempt)
future tools call fetch_url --url "https://en.wikipedia.org/wiki/BRCA1" ```

## Available tools

### web_search
Search the public web for a query. Returns a ranked list of results with page titles, URLs, and text snippets. Supports pagination.

Arguments: `--query "..." --count "..." --offset "..."`

### fetch_url
Download and extract the main text content from a web page. Strips navigation, ads, and boilerplate. Returns the page title and clean article text.

Arguments: `--url "..."`

**⚠️ Limitations:** `fetch_url` is a lightweight HTTP fetcher. It will return empty or fail on:
- Pages that require JavaScript rendering (SPAs, React/Vue apps)
- Pages with anti-bot verification (WeChat MP articles, Cloudflare challenges)
- Paywalled or login-gated content

**When `fetch_url` returns empty content, errors, or clearly incomplete text, you MUST fall back to the browser workflow below — do NOT give up or tell the user the page is inaccessible.**

## 🚨 Fallback: Browser-based page reading

When `fetch_url` fails, use the browser tools to open the page in a real Chrome/Edge browser and read its content:

```bash
# Step 1: Open the URL in the browser (auto-starts a browser if none is running)
future tools call browser --command "open" --url "https://mp.weixin.qq.com/s/RimhDV1PqVqzv3twoaxnOg" # Step 2: Wait briefly for JS to render, then get the page snapshot (DOM text content)
future tools call browser --command "snapshot" --limit 120 # Step 3 (optional): If the snapshot text is truncated or the page has important images/charts
future tools call browser --command "screenshot" --fullPage true # Step 4 (optional): Check for JS errors that might indicate blocked content
future tools call browser --command "console" --level "error" ```

**Important:** After `browser` with `command: "open"`, always wait a moment for the page to fully render (especially for JS-heavy sites like WeChat) before calling `command: "snapshot"`. If the first snapshot doesn't show the full article text, try increasing `limit` or scrolling.

## Decision flowchart

```
User asks to open/summarize a URL
        │
        ▼
  future tools call fetch_url --url <url>
        │
        ├─ ✅ Got full content → use it
        │
        ├─ ❌ Empty / error → browser (command: open) → browser (command: snapshot)
        │
        └─ ⚠️ Partial / truncated → browser (command: open) → browser (command: snapshot) (or screenshot for images)
```
