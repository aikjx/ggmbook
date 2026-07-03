from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "archives"))


def cmd_build(args: argparse.Namespace) -> int:
    from build_csdn_archives import build_archives
    build_archives(
        limit=args.limit,
        only_ids=args.only_id or [],
        download_images=not args.no_download_images,
        purge=args.purge,
        progress_every=args.progress_every,
    )
    return 0


def cmd_localize(args: argparse.Namespace) -> int:
    from archive_localize_images import main as localize_main
    import argparse as localize_argparse
    localize_args = localize_argparse.Namespace(
        targets=args.targets,
        timeout=args.timeout,
        retries=args.retries,
        purge_assets=args.purge_assets,
    )
    localize_main(localize_args)
    return 0


def cmd_video(args: argparse.Namespace) -> int:
    from archive_prepare_video import main as video_main
    import argparse as video_argparse
    video_args = video_argparse.Namespace(
        source=args.source,
        output_dir=args.output_dir,
        slug=args.slug,
        video_name=args.video_name,
        poster_name=args.poster_name,
        poster_at=args.poster_at,
        skip_poster=args.skip_poster,
        overwrite=args.overwrite,
        ffmpeg_bin=args.ffmpeg_bin,
    )
    video_main(video_args)
    return 0


def cmd_rebuild(args: argparse.Namespace) -> int:
    from archive_rebuild import main as rebuild_main
    rebuild_main()
    return 0


def cmd_verify_images(args: argparse.Namespace) -> int:
    from archive_verify_remote_images import main as verify_images_main
    import argparse as verify_argparse
    verify_args = verify_argparse.Namespace(
        targets=args.targets,
        allow_nonzero=args.allow_nonzero,
    )
    verify_images_main(verify_args)
    return 0


def cmd_verify_media(args: argparse.Namespace) -> int:
    from archive_verify_remote_media import main as verify_media_main
    import argparse as verify_argparse
    verify_args = verify_argparse.Namespace(
        targets=args.targets,
        allow_nonzero=args.allow_nonzero,
    )
    verify_media_main(verify_args)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.archives.main",
        description="ggmbook 归档管理工具 - 统一入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
业务架构映射：
├── build      → CSDN博文归档构建（分类、转换、本地化）
├── localize   → 图片本地化处理（远程→本地）
├── video      → 视频标准化处理（下载、转码、封面）
├── rebuild    → 增量重建（模板更新）
├── verify-images → 图片资源验收
└── verify-media  → 全媒体验收（图片/视频/音频）
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    build_parser = subparsers.add_parser("build", help="构建CSDN博文归档")
    build_parser.add_argument("--limit", type=int, default=None, help="限制处理数量")
    build_parser.add_argument("--only-id", action="append", default=[], help="指定文章ID")
    build_parser.add_argument("--no-download-images", action="store_true", help="不下载图片")
    build_parser.add_argument("--purge", action="store_true", help="清理现有归档")
    build_parser.add_argument("--progress-every", type=int, default=25, help="进度输出间隔")
    build_parser.set_defaults(func=cmd_build)

    localize_parser = subparsers.add_parser("localize", help="本地化页面图片")
    localize_parser.add_argument("targets", nargs="*", help="目标目录或文件")
    localize_parser.add_argument("--timeout", type=int, default=20, help="超时时间")
    localize_parser.add_argument("--retries", type=int, default=2, help="重试次数")
    localize_parser.add_argument("--purge-assets", action="store_true", help="清理现有assets")
    localize_parser.set_defaults(func=cmd_localize)

    video_parser = subparsers.add_parser("video", help="视频标准化处理")
    video_parser.add_argument("source", help="视频源路径或URL")
    video_parser.add_argument("output_dir", help="输出目录")
    video_parser.add_argument("--slug", help="媒体标识")
    video_parser.add_argument("--video-name", default="video.mp4", help="输出视频名")
    video_parser.add_argument("--poster-name", default="poster.jpg", help="输出封面名")
    video_parser.add_argument("--poster-at", default="00:00:01", help="封面时刻")
    video_parser.add_argument("--skip-poster", action="store_true", help="跳过封面")
    video_parser.add_argument("--overwrite", action="store_true", help="覆盖已存在")
    video_parser.add_argument("--ffmpeg-bin", default="ffmpeg", help="ffmpeg路径")
    video_parser.set_defaults(func=cmd_video)

    subparsers.add_parser("rebuild", help="增量重建归档").set_defaults(func=cmd_rebuild)

    verify_images_parser = subparsers.add_parser("verify-images", help="验收远程图片")
    verify_images_parser.add_argument("targets", nargs="*", help="目标目录或文件")
    verify_images_parser.add_argument("--allow-nonzero", action="store_true", help="允许非零返回")
    verify_images_parser.set_defaults(func=cmd_verify_images)

    verify_media_parser = subparsers.add_parser("verify-media", help="验收远程媒体")
    verify_media_parser.add_argument("targets", nargs="*", help="目标目录或文件")
    verify_media_parser.add_argument("--allow-nonzero", action="store_true", help="允许非零返回")
    verify_media_parser.set_defaults(func=cmd_verify_media)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())