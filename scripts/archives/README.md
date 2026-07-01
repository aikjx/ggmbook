# ggbook 归档管理脚本

## 概述

本目录包含 ggbook 项目的核心自动化脚本，用于文章归档、媒体处理和质量验收。

## 业务架构映射

| 命令 | 对应脚本 | 业务职责 |
|-----|---------|---------|
| `build` | `build_csdn_archives.py` | CSDN博文归档构建（分类、转换、本地化） |
| `localize` | `archive_localize_images.py` | 图片本地化处理（远程→本地） |
| `video` | `archive_prepare_video.py` | 视频标准化处理（下载、转码、封面） |
| `rebuild` | `archive_rebuild.py` | 增量重建（模板更新） |
| `verify-images` | `archive_verify_remote_images.py` | 图片资源验收 |
| `verify-media` | `archive_verify_remote_media.py` | 全媒体验收 |

## 统一入口

### 基本用法

```bash
# 显示帮助
python scripts/archives/main.py --help

# 构建CSDN博文归档
python scripts/archives/main.py build

# 本地化页面图片
python scripts/archives/main.py localize

# 处理视频
python scripts/archives/main.py video <source> <output_dir>

# 增量重建
python scripts/archives/main.py rebuild

# 验收远程图片
python scripts/archives/main.py verify-images

# 验收全媒体
python scripts/archives/main.py verify-media
```

## 四大书籍分类体系

| 分类 | 中文名称 | 关键词示例 |
|-----|---------|-----------|
| `math` | 全域数学 | 全域数学、统一场论、光速螺旋、量子、黑洞 |
| `goldbach` | 哥德巴赫猜想 | 哥德巴赫、孪生素数、素数、数论 |
| `shushu` | 数术工坊 | 易经、河图洛书、太极、五行、道德经 |
| `course` | 文明进阶200讲 | 全域数学vs传统数学、第X讲 |

## 工作流程

### 1. 完整归档构建

```bash
# 全量构建（含图片下载）
python scripts/archives/main.py build

# 增量构建（仅指定ID）
python scripts/archives/main.py build --only-id 123456 --only-id 789012

# 仅重建模板（不下载图片）
python scripts/archives/main.py build --no-download-images
```

### 2. 图片本地化

```bash
# 处理指定目录
python scripts/archives/main.py localize docs/zh/books/math

# 处理单个文件
python scripts/archives/main.py localize docs/zh/books/math/index.md

# 清理现有assets后重新下载
python scripts/archives/main.py localize --purge-assets
```

### 3. 视频处理

```bash
# 本地视频转码
python scripts/archives/main.py video input.mp4 assets/video/lesson01

# 远程视频下载并转码
python scripts/archives/main.py video https://example.com/video.mp4 assets/video/lesson01

# 跳过封面生成
python scripts/archives/main.py video input.mp4 assets/video/lesson01 --skip-poster
```

### 4. 质量验收

```bash
# 检查远程图片引用
python scripts/archives/main.py verify-images

# 检查全部远程媒体
python scripts/archives/main.py verify-media

# 仅统计，不报错
python scripts/archives/main.py verify-media --allow-nonzero
```

## 目录结构

```
scripts/archives/
├── main.py                          # 统一入口
├── build_csdn_archives.py           # 核心归档构建器
├── archive_localize_images.py       # 图片本地化工具
├── archive_prepare_video.py         # 视频标准化处理
├── archive_rebuild.py               # 增量重建工具
├── archive_verify_remote_images.py  # 图片验收
├── archive_verify_remote_media.py   # 全媒体验收
└── legacy/                          # 废弃脚本（保留参考）
```

## 技术规范

### 路径常量

- `REPO_ROOT`: 项目根目录
- `DOCS_DIR`: 文档根目录 (`docs/`)
- `SOURCE_DIR`: CSDN备份源 (`docs/aa/CSDN博文备份`)
- `ZH_BOOKS_DIR`: 中文书籍目录 (`docs/zh/books`)
- `EN_BOOKS_DIR`: 英文书籍目录 (`docs/en/books`)

### 媒体资源组织

```
article_dir/
├── index.md              # 文章内容
└── assets/
    ├── csdnimg/          # CSDN来源图片
    │   ├── png/
    │   └── jpg/
    └── external/         # 外部来源图片
        ├── png/
        └── jpg/
```

## 废弃脚本

`legacy/` 目录存放已废弃的一次性迁移脚本，仅保留参考，不作为正式生产入口。