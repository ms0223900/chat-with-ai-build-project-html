---
name: host-static-html
description: Serve static HTML demo pages from this repo with a local HTTP server and a public preview tunnel. Use when the user asks to run, preview, host, open, or share an HTML file (e.g. 台股看盤_盯盤系統_260610.html) from the browser.
---

# Host Static HTML

## When to use

Apply when the user wants to **preview or share** a static `.html` file in this repository. Typical targets:

| File | Purpose |
|------|---------|
| `台股看盤_盯盤系統_260610.html` | MasterTalks 台股盯盤課程銷售頁 |
| `index_modified_260514.html` | 其他課程 demo 頁 |
| `codex-seo.html` | SEO demo 頁 |

Do **not** assume the user can reach `127.0.0.1` in a Cloud Agent environment — always provide a **public tunnel URL** when hosting remotely.

## Workflow

```
Task Progress:
- [ ] Step 1: Start HTTP server (tmux, bind 0.0.0.0)
- [ ] Step 2: Start public tunnel (localtunnel)
- [ ] Step 3: Verify with curl and share the full file URL
```

### Step 1: HTTP server

Run from the **project root** (`/workspace` or repo root). Use **tmux** so the server keeps running:

```bash
SESSION_NAME="static-html-server"
tmux -f /exec-daemon/tmux.portal.conf has-session -t "=$SESSION_NAME" 2>/dev/null \
  || tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION_NAME" -c "/workspace" -- "${SHELL:-zsh}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_NAME:0.0" \
  'python3 -m http.server 8080 --bind 0.0.0.0' C-m
```

Verify locally:

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" "http://127.0.0.1:8080/"
```

If port `8080` is taken, pick another (e.g. `8765`) and use the same port for the tunnel in Step 2.

### Step 2: Public tunnel

```bash
SESSION_NAME="static-html-tunnel"
tmux -f /exec-daemon/tmux.portal.conf has-session -t "=$SESSION_NAME" 2>/dev/null \
  || tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$SESSION_NAME" -c "/workspace" -- "${SHELL:-zsh}" -l
tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$SESSION_NAME:0.0" \
  'npx --yes localtunnel --port 8080' C-m
```

Wait a few seconds, then read the tunnel URL from tmux output:

```bash
sleep 5
tmux -f /exec-daemon/tmux.portal.conf capture-pane -t "static-html-tunnel:0.0" -p -S -30
```

The URL looks like `https://<subdomain>.loca.lt`.

### Step 3: Build and verify the file URL

Chinese filenames must be **URL-encoded** in the link. Example for the 台股 page:

```
https://<subdomain>.loca.lt/%E5%8F%B0%E8%82%A1%E7%9C%8B%E7%9B%A4_%E7%9B%AF%E7%9B%A4%E7%B3%BB%E7%B5%B1_260610.html
```

Quick encode in shell:

```bash
python3 -c "import urllib.parse; print(urllib.parse.quote('台股看盤_盯盤系統_260610.html'))"
```

Verify the tunnel serves the page (not just the directory listing):

```bash
curl -s -o /dev/null -w "FILE %{http_code}\n" \
  -H "Bypass-Tunnel-Reminder: true" \
  "https://<subdomain>.loca.lt/<url-encoded-filename>"
```

Share the **full file URL** with the user. Mention that loca.lt may show a reminder page — click Continue to proceed.

## Local-only preview (user's machine)

If the user runs this on their own computer (not Cloud Agent):

```bash
cd /path/to/repo
python3 -m http.server 8080
```

Then open `http://127.0.0.1:8080/<filename>.html` in a browser, or double-click the `.html` file directly (no server needed for simple static pages).

## Notes

- **Stack**: Python `http.server` + `localtunnel` via `npx`. No Nginx, Docker, or build step.
- **Persistence**: Servers live in tmux sessions; reuse an existing session if one is already running for the same port.
- **Egress**: Cloud Agent environments typically allow outbound network for `npx localtunnel`.
- **Screenshots**: For modal/UI checks, use `playwright-core` with system Chrome if available.
