"""Update library/index.yaml with a new paper entry or status change.

Usage:
    uv run src/tools/update_index.py add <paper_id> --title "..." --authors "A,B" --year 2025
    uv run src/tools/update_index.py status <paper_id> --status read
"""

import argparse
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

INDEX_PATH = Path("library/index.yaml")

# Type alias for the index structure
IndexData = dict[str, Any]


def _default_index() -> IndexData:
    return {"papers": {}}


def load_index() -> IndexData:
    """Load index from YAML file, or return empty index."""
    if INDEX_PATH.exists():
        with INDEX_PATH.open() as f:
            data: Any = yaml.safe_load(f)
        if isinstance(data, dict) and "papers" in data:
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
) -> None:
    """Add a new paper entry to the index."""
    index = load_index()

    if paper_id in index["papers"]:
        logger.warning("Paper %s already exists in index, updating", paper_id)

    index["papers"][paper_id] = {
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "url": url or f"https://arxiv.org/abs/{paper_id}",
        "tags": tags or [],
        "status": "downloaded",
        "pdf_path": f"library/papers/{paper_id}.pdf",
        "note_path": f"library/notes/{paper_id}.md",
        "added_date": date.today().isoformat(),
        "read_date": "",
    }

    save_index(index)
    logger.info("Added paper %s to index", paper_id)


def update_status(paper_id: str, *, status: str, tags: list[str] | None = None) -> None:
    """Update the status of a paper in the index."""
    index = load_index()

    if paper_id not in index["papers"]:
        logger.error("Paper %s not found in index", paper_id)
        sys.exit(1)

    index["papers"][paper_id]["status"] = status
    if status == "read":
        index["papers"][paper_id]["read_date"] = date.today().isoformat()
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

    # status command
    status_parser = subparsers.add_parser("status", help="Update paper status")
    status_parser.add_argument("paper_id", help="Paper ID")
    status_parser.add_argument(
        "--status", required=True, choices=["downloaded", "read", "annotated"]
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
        )
    elif args.command == "status":
        status_tags: list[str] | None = (
            [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None
        )
        update_status(args.paper_id, status=args.status, tags=status_tags)


if __name__ == "__main__":
    main()
