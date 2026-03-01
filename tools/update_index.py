"""Update library/index.yaml with a new paper entry or status change.

Usage:
    uv run tools/update_index.py add <paper_id> --title "..." --authors "A,B" --year 2025
    uv run tools/update_index.py status <paper_id> --status read
"""

import argparse
import logging
from datetime import date
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

INDEX_PATH = Path("library/index.yaml")

# Valid status values in lifecycle order
VALID_STATUSES = ("stub", "pending_pdf", "downloaded", "read", "annotated")

# Type alias for the index structure
IndexData = dict[str, Any]


def sanitize_paper_id(paper_id: str) -> str:
    """Make paper_id safe for use in file paths. DOIs contain '/' which must be replaced."""
    return paper_id.replace("/", "_")


def _default_index() -> IndexData:
    return {"papers": {}}


def load_index() -> IndexData:
    """Load index from YAML file, or return empty index."""
    if INDEX_PATH.exists():
        try:
            with INDEX_PATH.open() as f:
                data: Any = yaml.safe_load(f)
        except yaml.YAMLError:
            logger.warning("Failed to parse %s, using empty index", INDEX_PATH)
            return _default_index()
        if isinstance(data, dict) and "papers" in data:
            # Handle papers: (empty value) → None in YAML
            if data["papers"] is None:
                data["papers"] = {}
            return data  # type: ignore[no-any-return]
    return _default_index()


def save_index(data: IndexData) -> None:
    """Save index to YAML file."""
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def add_paper(
    paper_id: str,
    *,
    title: str,
    authors: list[str],
    year: int,
    doi: str = "",
    url: str = "",
    tags: list[str] | None = None,
    status: str = "downloaded",
) -> None:
    """Add a new paper entry to the index. Merges with existing entry if present.

    Merge strategy: existing entry is the base; new values overlay non-empty fields.
    This preserves user-customized paths, custom fields, and advanced status.
    """
    index = load_index()
    safe_id = sanitize_paper_id(paper_id)

    new_fields: dict[str, Any] = {
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "url": url or f"https://arxiv.org/abs/{paper_id}",
        "tags": tags or [],
        "status": status,
        "pdf_path": f"library/papers/{safe_id}.pdf",
        "note_path": f"library/notes/{safe_id}.md",
        "added_date": date.today().isoformat(),
        "read_date": "",
    }

    if paper_id in index["papers"]:
        logger.warning("Paper %s already exists in index, merging", paper_id)
        existing = index["papers"][paper_id]
        # Existing entry is the base — preserve all fields (including custom ones)
        merged = dict(existing)
        # Overlay metadata that may have been updated
        for key in ("title", "authors", "year", "doi", "url"):
            if new_fields.get(key):
                merged[key] = new_fields[key]
        # Merge tags (union)
        if tags:
            merged["tags"] = sorted(set(existing.get("tags", []) + tags))
        # Don't regress status: keep the more advanced one
        if VALID_STATUSES.index(existing.get("status", "stub")) > VALID_STATUSES.index(status):
            pass  # keep existing status
        else:
            merged["status"] = status
        # Preserve existing dates and paths (user may have customized)
        index["papers"][paper_id] = merged
    else:
        index["papers"][paper_id] = new_fields

    save_index(index)
    logger.info("Added paper %s to index", paper_id)


def update_status(paper_id: str, *, status: str, tags: list[str] | None = None) -> None:
    """Update the status of a paper in the index."""
    index = load_index()

    if paper_id not in index["papers"]:
        raise KeyError(f"Paper {paper_id} not found in index")

    index["papers"][paper_id]["status"] = status
    if status == "read":
        index["papers"][paper_id]["read_date"] = date.today().isoformat()
    elif status in ("stub", "pending_pdf", "downloaded"):
        # Clear read_date on status regression to avoid stale data
        index["papers"][paper_id]["read_date"] = ""
    if tags is not None:
        existing = index["papers"][paper_id].get("tags", [])
        index["papers"][paper_id]["tags"] = sorted(set(existing + tags))

    save_index(index)
    logger.info("Updated paper %s status to %s", paper_id, status)


def main() -> None:
    """CLI entry point."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Update library index")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a paper to the index")
    add_parser.add_argument("paper_id", help="Paper ID (e.g., 2401.12345)")
    add_parser.add_argument("--title", required=True, help="Paper title")
    add_parser.add_argument("--authors", required=True, help="Comma-separated authors")
    add_parser.add_argument("--year", required=True, type=int, help="Publication year")
    add_parser.add_argument("--doi", default="", help="DOI")
    add_parser.add_argument("--url", default="", help="Paper URL")
    add_parser.add_argument("--tags", default="", help="Comma-separated tags")
    add_parser.add_argument(
        "--status",
        default="downloaded",
        choices=list(VALID_STATUSES),
        help="Initial status (default: downloaded)",
    )

    # status command
    status_parser = subparsers.add_parser("status", help="Update paper status")
    status_parser.add_argument("paper_id", help="Paper ID")
    status_parser.add_argument(
        "--status",
        required=True,
        choices=list(VALID_STATUSES),
    )
    status_parser.add_argument("--tags", default="", help="Comma-separated tags to add")

    args = parser.parse_args()

    if args.command == "add":
        authors = [a.strip() for a in args.authors.split(",")]
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        add_paper(
            args.paper_id,
            title=args.title,
            authors=authors,
            year=args.year,
            doi=args.doi,
            url=args.url,
            tags=tags,
            status=args.status,
        )
    elif args.command == "status":
        status_tags: list[str] | None = (
            [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
        )
        try:
            update_status(args.paper_id, status=args.status, tags=status_tags)
        except KeyError as e:
            logger.error("%s", e)
            raise SystemExit(1) from None


if __name__ == "__main__":
    main()
