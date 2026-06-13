#!/usr/bin/env python3
"""Extract data:image/* base64 URIs from HTML img src and save as local files."""

from __future__ import annotations

import argparse
import base64
import re
import sys
from pathlib import Path
from urllib.parse import unquote

DATA_URI_RE = re.compile(
    r"data:image/([^;]+);base64,([A-Za-z0-9+/=]+)",
    re.IGNORECASE,
)
IMG_TAG_RE = re.compile(r"<img\b([^>]*?)>", re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(
    r"""(\w+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""",
    re.IGNORECASE,
)

EXT_BY_MIME = {
    "jpeg": "jpg",
    "jpg": "jpg",
    "png": "png",
    "gif": "gif",
    "webp": "webp",
    "svg+xml": "svg",
    "bmp": "bmp",
    "avif": "avif",
}


def parse_attrs(tag_inner: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in ATTR_RE.finditer(tag_inner):
        key = match.group(1).lower()
        value = next(v for v in match.groups()[1:] if v is not None)
        attrs[key] = unquote(value)
    return attrs


def slugify_filename(text: str, fallback: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff\-]+", "-", text.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    return cleaned or fallback


def mime_to_ext(mime: str) -> str:
    mime = mime.lower().strip()
    if mime in EXT_BY_MIME:
        return EXT_BY_MIME[mime]
    if "/" in mime:
        mime = mime.split("/", 1)[1]
    return EXT_BY_MIME.get(mime, mime.replace("+xml", "").replace("+", "-") or "bin")


def rel_path(from_file: Path, to_file: Path) -> str:
    return Path(
        Path(
            Path(to_file).resolve().relative_to(from_file.parent.resolve()).as_posix()
        )
    ).as_posix()


def extract_images(html_path: Path, output_dir: Path | None, dry_run: bool) -> int:
    html_text = html_path.read_text(encoding="utf-8")
    if output_dir is None:
        output_dir = html_path.parent / "images" / html_path.stem

    output_dir = output_dir.resolve()
    replacements: list[tuple[str, str]] = []
    saved = 0

    for index, img_match in enumerate(IMG_TAG_RE.finditer(html_text), start=1):
        attrs = parse_attrs(img_match.group(1))
        src = attrs.get("src", "")
        data_match = DATA_URI_RE.fullmatch(src.strip())
        if not data_match:
            continue

        mime, b64_data = data_match.groups()
        ext = mime_to_ext(mime)
        alt = attrs.get("alt", "")
        stem = slugify_filename(alt, f"image-{index:02d}")
        filename = f"{index:02d}-{stem}.{ext}"
        out_file = output_dir / filename

        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
            out_file.write_bytes(base64.b64decode(b64_data))

        new_src = rel_path(html_path, out_file)
        replacements.append((src, new_src))
        saved += 1
        print(f"[{index:02d}] {filename}  ({mime})")

    if not replacements:
        print("No data:image URIs found in <img src>.", file=sys.stderr)
        return 0

    new_html = html_text
    for old, new in replacements:
        if old not in new_html:
            raise RuntimeError("Failed to locate data URI for replacement.")
        new_html = new_html.replace(old, new, 1)

    if dry_run:
        print(f"\nDry run: would save {saved} image(s) to {output_dir}")
        print(f"Dry run: would update {html_path}")
        return saved

    html_path.write_text(new_html, encoding="utf-8")
    print(f"\nSaved {saved} image(s) to {output_dir}")
    print(f"Updated {html_path}")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract data:image base64 URIs from HTML and replace with local paths."
    )
    parser.add_argument(
        "html",
        help="HTML file to process",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for extracted images (default: images/<html-stem>/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be extracted without writing files",
    )
    args = parser.parse_args()

    html_path = Path(args.html).expanduser().resolve()
    if not html_path.is_file():
        print(f"HTML file not found: {html_path}", file=sys.stderr)
        return 1

    try:
        extract_images(html_path, args.output_dir, args.dry_run)
    except Exception as exc:  # noqa: BLE001 - CLI entrypoint
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
