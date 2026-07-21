---
name: update-master-talks-html
description: Update MasterTalks course sales-page copy in static HTML from a Notion GTD task. Use when the user links a Notion Step/文案 task, asks to change 學習目標 or curriculum text on 台股看盤 pages, or modify curriculumData objectives in 台股看盤_盯盤系統_260610.html.
---

# Update MasterTalks HTML Copy

## When to use

Apply when the user provides a **Notion GTD task** or asks to change **課程網頁文案** for MasterTalks static HTML in this repo.

Primary file:

```
台股看盤_盯盤系統_260610.html
```

## Workflow

```
Task Progress:
- [ ] Step 1: Read Notion task requirements
- [ ] Step 2: Locate the target copy in HTML (usually curriculumData)
- [ ] Step 3: Apply the exact wording from Notion
- [ ] Step 4: Verify desktop + mobile modal display
```

### Step 1: Read Notion task

Prefer **Notion MCP** when authenticated. If MCP is unavailable, use the public `loadPageChunk` API:

```bash
PAGE_ID="7aace276-6f0c-4091-b44c-49e2c26282a2"  # from Notion URL
curl -sL -A "Mozilla/5.0" "https://www.notion.so/api/v3/loadPageChunk" \
  -H "Content-Type: application/json" \
  -d "{\"page\":{\"id\":\"$PAGE_ID\"},\"limit\":100,\"cursor\":{\"stack\":[]},\"chunkNumber\":0,\"verticalColumns\":false}" \
  -o /tmp/notion-page.json
```

Extract page ID from URLs like:

- `https://app.notion.com/p/.../GTD-Master-Talks-Step23-7aace2766f0c4091b44c49e2c26282a2`
- `https://www.notion.so/GTD-...-<32-char-hex-id>`

Parse checklist items and quoted copy from the JSON `recordMap.block` entries (look for `to_do`, `quote`, `bulleted_list` blocks).

Use the **exact** Chinese copy from Notion — do not paraphrase.

### Step 2: Locate copy in HTML

Course steps live in the `curriculumData` JavaScript array near the bottom of the HTML file:

```javascript
const curriculumData = [
  { id: 23, title: "...", desc: "...", objective: "本節學習目標文案" },
  // ...
];
```

| Field | Shown in UI as |
|-------|----------------|
| `title` | Modal title + card heading |
| `desc` | 單元簡介 |
| `objective` | 本節學習目標 (purple box in modal) |

Find the step by `id` (e.g. Step 23 → `id: 23`).

### Step 3: Edit

Change only the requested fields. Keep punctuation and wording identical to the Notion spec.

Example (Step 23 objective):

```javascript
objective: "學習串接 Email API，撰寫警示條件判斷邏輯，滿足買賣訊息時的自動化推播。"
```

### Step 4: Verify

1. **Text match** — grep or a short Python assert on the `id` + `objective` string.
2. **Modal display** — start the server (see `host-static-html` skill), open the page, click the step card or run:

```javascript
openModal(curriculumData.find(c => c.id === 23));
```

3. **Responsive** — capture modal at desktop (1280×900) and mobile (390×844) if copy length changed; confirm line breaks and punctuation look correct. Modal uses `textContent`, so wrapping is automatic.

Reference screenshots from Notion (if attached) can be fetched via:

```bash
curl -sL -A "Mozilla/5.0" "https://www.notion.so/api/v3/getSignedFileUrls" \
  -H "Content-Type: application/json" \
  -d '{"urls":[{"url":"attachment:<file-id>:image.png","permissionRecord":{"table":"block","id":"<block-id>","spaceId":"<space-id>"},"useS3Url":true}]}'
```

## Conventions

- One HTML file per course demo; filename may include date suffix (e.g. `_260610`).
- Do not load the entire HTML into context for unrelated edits — search for `curriculumData` or the step `id` instead.
- After copy changes, commit with a clear message and open/update a PR if working in Cloud Agent mode.

## Related skills

- `host-static-html` — serve and share the page for preview
- `extract-html-data-uri-images` — externalize embedded base64 images when HTML is too large
