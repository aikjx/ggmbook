from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import urlretrieve


VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".avi", ".mkv"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="下载或接收本地视频源，统一转码为站内可引用的 mp4，并可选生成封面图。"
    )
    parser.add_argument("source", help="本地视频文件路径或可直接下载的视频 URL。")
    parser.add_argument(
        "output_dir",
        help="输出目录，建议指向文章或页面同级的 assets/video/<slug> 目录。",
    )
    parser.add_argument("--slug", help="媒体标识，仅用于命名提示与日志输出。")
    parser.add_argument("--video-name", default="video.mp4", help="输出视频文件名，默认 video.mp4。")
    parser.add_argument("--poster-name", default="poster.jpg", help="输出封面文件名，默认 poster.jpg。")
    parser.add_argument(
        "--poster-at",
        default="00:00:01",
        help="提取封面时刻，格式示例 00:00:01，默认 00:00:01。",
    )
    parser.add_argument("--skip-poster", action="store_true", help="只转码视频，不生成封面。")
    parser.add_argument("--overwrite", action="store_true", help="允许覆盖已存在的产物。")
    parser.add_argument("--ffmpeg-bin", default="ffmpeg", help="ffmpeg 可执行文件名或绝对路径。")
    return parser.parse_args()


def ensure_ffmpeg(ffmpeg_bin: str) -> str:
    resolved = shutil.which(ffmpeg_bin) if Path(ffmpeg_bin).name == ffmpeg_bin else ffmpeg_bin
    if not resolved:
        raise SystemExit("未找到 ffmpeg，请先安装 ffmpeg 并确保其位于 PATH 中。")
    return resolved


def ensure_output_paths(output_dir: Path, video_name: str, poster_name: str, overwrite: bool) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    video_path = output_dir / video_name
    poster_path = output_dir / poster_name
    if not overwrite and video_path.exists():
        raise SystemExit(f"输出视频已存在：{video_path}")
    if not overwrite and poster_path.exists():
        raise SystemExit(f"输出封面已存在：{poster_path}")
    return video_path, poster_path


def download_source_if_needed(source: str, temp_dir: Path) -> Path:
    if source.startswith("http://") or source.startswith("https://"):
        parsed = urlparse(source)
        suffix = Path(parsed.path).suffix.lower()
        if suffix not in VIDEO_EXTENSIONS:
            suffix = ".mp4"
        temp_path = temp_dir / f"downloaded_source{suffix}"
        urlretrieve(source, temp_path)
        return temp_path
    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"未找到输入视频：{path}")
    return path


def run_ffmpeg(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            "ffmpeg 执行失败：\n"
            f"command={' '.join(command)}\n"
            f"stdout={result.stdout}\n"
            f"stderr={result.stderr}"
        )


def main(args: argparse.Namespace | None = None) -> None:
    if args is None:
        args = parse_args()
    ffmpeg_bin = ensure_ffmpeg(args.ffmpeg_bin)
    output_dir = Path(args.output_dir).expanduser().resolve()
    video_path, poster_path = ensure_output_paths(output_dir, args.video_name, args.poster_name, args.overwrite)

    with tempfile.TemporaryDirectory(prefix="ggmbook-video-") as temp_dir_raw:
        temp_dir = Path(temp_dir_raw)
        source_path = download_source_if_needed(args.source, temp_dir)

        video_command = [
            ffmpeg_bin,
            "-y",
            "-i",
            str(source_path),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(video_path),
        ]
        run_ffmpeg(video_command)

        if not args.skip_poster:
            poster_command = [
                ffmpeg_bin,
                "-y",
                "-ss",
                args.poster_at,
                "-i",
                str(source_path),
                "-frames:v",
                "1",
                str(poster_path),
            ]
            run_ffmpeg(poster_command)

    relative_video = f"./{video_path.name}"
    print(f"video_output={video_path}")
    print(f"video_relative={relative_video}")
    if not args.skip_poster:
        relative_poster = f"./{poster_path.name}"
        print(f"poster_output={poster_path}")
        print(f"poster_relative={relative_poster}")
        print(
            "html_snippet="
            f"<video controls preload=\"metadata\" poster=\"{relative_poster}\">\n"
            f"  <source src=\"{relative_video}\" type=\"video/mp4\" />\n"
            "</video>"
        )
    else:
        print(
            "html_snippet="
            f"<video controls preload=\"metadata\">\n"
            f"  <source src=\"{relative_video}\" type=\"video/mp4\" />\n"
            "</video>"
        )


if __name__ == "__main__":
    main()
