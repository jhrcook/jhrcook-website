#!/usr/bin/env python3

from pathlib import Path
from typing import Annotated, Final, Generator

from PIL import Image
from rich.console import Console
from typer import Option, Typer

app = Typer()

POSTS_DIR: Final[Path] = Path("./content/posts/")
IMAGE_SUFFIXES: Final[set[str]] = {
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".gif",
    ".webp",
    ".jp2",
}
console = Console()


def get_text(post_dir: Path) -> str | None:
    index_file = post_dir / "index.md"
    if not index_file.exists():
        return None
    with open(index_file) as fh:
        text = "".join(fh.readlines())
    return text


def iter_images(post_dir: Path) -> Generator[Path, None, None]:
    for file in post_dir.rglob("*"):
        if file.suffix in IMAGE_SUFFIXES:
            yield file


def iter_post_dirs() -> Generator[Path, None, None]:
    """Iterate over blog post directories."""
    for post_dir in POSTS_DIR.iterdir():
        if post_dir.is_dir():
            yield post_dir


@app.command()
def rm_unused_images(
    delete: Annotated[
        bool, Option("-d", "--delete", help="Delete unused images.", is_flag=True)
    ] = False,
) -> None:
    """Find (and optionally remove) unused images in post dirs."""
    for post_dir in iter_post_dirs():
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


def fsize_mb(fpath: Path) -> float:
    return fpath.stat().st_size / 10**6


def convert_png_to_webp(post_dir: Path, png_path: Path, webp_quality: int) -> float:
    """Convert an PNG to WebP, returning the amount of space saved."""
    console.log(f"Converting {png_path} to WebP.")
    png_size = fsize_mb(png_path)
    webp_path = png_path.with_suffix(".webp")
    Image.open(png_path).save(webp_path, lossless=True, quality=webp_quality)
    webp_size = fsize_mb(webp_path)
    console.log(f"  new file size: {fsize_mb(webp_path):0.1f} MB")
    size_diff = png_size - webp_size
    png_path.unlink()

    text = get_text(post_dir)
    if text is None:
        console.log(f"Cannot find text for post '{post_dir.name}'.")
    else:
        text = text.replace(png_path.name, webp_path.name)
        with open(post_dir / "index.md", "w") as fh:
            fh.write(text)
    return size_diff


@app.command()
def large_assets(
    threshold: Annotated[float, Option(help="File size threshold.")] = 2,
    png_to_webp: Annotated[
        bool, Option("-w", "--png-to-webp", help="Convert PNG to WebP.", is_flag=True)
    ] = False,
    webp_quality: Annotated[
        int,
        Option(
            "-c",
            "--webp-compression",
            help="WebP compression. 0 is the fastest, but gives larger files compared to the slowest, but best, 100.",
            min=0,
            max=100,
        ),
    ] = 80,
) -> None:
    """Find large assets in posts."""
    space_saved = 0.0
    for post_dir in iter_post_dirs():
        console.log(f"Post: {post_dir.name}")

        for file in post_dir.rglob("*"):
            if file.name == "index.md":
                continue
            fsize = fsize_mb(file)
            if fsize < threshold:
                continue
            _fpath = file.relative_to(post_dir)
            console.log(f" -> {_fpath} - {fsize:0.1f} MB")
            if png_to_webp and file.suffix == ".png":
                space_saved += convert_png_to_webp(
                    post_dir, file, webp_quality=webp_quality
                )
    if png_to_webp:
        console.log(f"Total space saved: {space_saved:0.1f} MB")


if __name__ == "__main__":
    app()
