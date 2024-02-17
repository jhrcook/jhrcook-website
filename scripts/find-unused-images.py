#!/usr/bin/env python3

from pathlib import Path
from typing import Annotated, Final, Generator

from rich.console import Console
from typer import Option, Typer

app = Typer()

POSTS_DIR: Final[Path] = Path("./content/posts/")
IMAGE_SUFFIXES: Final[set[str]] = {".jpeg", ".jpg", ".png", ".svg"}
console = Console()


def get_text(post_dir: Path) -> str | None:
    index_file = post_dir / "index.md"
    if not index_file.exists():
        return None
    with open(index_file) as fh:
        text = "\n".join(fh.readlines())
    return text


def iter_images(post_dir: Path) -> Generator[Path, None, None]:
    for file in post_dir.rglob("*"):
        if file.suffix in IMAGE_SUFFIXES:
            yield file


@app.command()
def main(
    delete: Annotated[
        bool, Option("-d", "--delete", help="Delete unused images.", is_flag=True)
    ] = False,
) -> None:
    for post_dir in POSTS_DIR.iterdir():
        if not post_dir.is_dir():
            continue
        console.log(f"Post: {post_dir.name}")
        if (text := get_text(post_dir)) is None:
            console.log("No index file.")
            continue
        for img in iter_images(post_dir):
            if img.name.startswith("featured.") or img.name.startswith("background."):
                continue
            if img.name not in text:
                _img_path = img.relative_to(post_dir)
                console.log(f"Unused image: {_img_path}")
                if delete:
                    img.unlink()


if __name__ == "__main__":
    app()
