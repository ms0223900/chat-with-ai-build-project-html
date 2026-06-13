---
name: extract-html-data-uri-images
description: Extracts data:image base64 URIs from HTML img src, saves images locally under images/, and replaces src with relative paths. Use when the user asks to externalize embedded images, extract data URIs, shrink HTML file size, or replace inline base64 images with local asset links in sales pages or static HTML.
---

# Extract HTML Data-URI Images

## When to use

Apply when HTML contains `<img src="data:image/...;base64,...">` and the user wants local image files plus updated relative `src` links.

Do **not** read the entire HTML into context. Run the bundled script instead.

## Workflow

```
Task Progress:
- [ ] Step 1: Dry-run to preview extraction
- [ ] Step 2: Run extraction (writes images + updates HTML in place)
- [ ] Step 3: Verify no data:image remains
```

### Step 1: Dry-run

From the project root (directory containing the target HTML):

```bash
python3 .cursor/skills/extract-html-data-uri-images/scripts/extract_data_uri_images.py --dry-run "path/to/page.html"
```

Confirm output filenames and `images/<html-stem>/` target directory.

### Step 2: Extract and replace

```bash
python3 .cursor/skills/extract-html-data-uri-images/scripts/extract_data_uri_images.py "path/to/page.html"
```

Optional custom output directory:

```bash
python3 .cursor/skills/extract-html-data-uri-images/scripts/extract_data_uri_images.py "path/to/page.html" -o images/custom-folder
```

### Step 3: Verify

```bash
python3 -c "
import re
from pathlib import Path
html = Path('path/to/page.html').read_text(encoding='utf-8')
print('data:image remaining:', len(re.findall(r'data:image/', html)))
print('img tags:', len(re.findall(r'<img\b', html, re.I)))
"
```

Expected: `data:image remaining: 0`. Image count should match `<img>` tags that previously used data URIs.

## Conventions

| Item | Default |
|------|---------|
| Image output dir | `images/<html-filename-without-ext>/` next to the HTML file |
| Filename format | `{index:02d}-{slug-from-alt}.{ext}` |
| Fallback name | `image-{index:02d}` when `alt` is empty |
| HTML update | In-place overwrite of the source HTML |
| Supported MIME | jpeg, png, gif, webp, svg+xml, bmp, avif |

Example result:

```html
<img src="images/不要賭_銷售頁_260613/01-王采元伏案手繪施工圖.jpg" alt="王采元伏案手繪施工圖">
```

## Notes

- Only processes `<img src="data:image/...">`; CSS `url(data:image/...)` is out of scope.
- Requires Python 3 stdlib only (no pip packages).
- For very large HTML, the script streams via regex on the full file — do not manually open the HTML in the editor for inspection.
