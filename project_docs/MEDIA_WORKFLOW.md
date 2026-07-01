# 媒体资产工作流

## 目标

- 将图片、视频、音频、封面统一纳入正式工程规范
- 建立“下载 / 转码 / 落盘 / 引用 / 验收 / 构建”闭环
- 避免页面直接引用远程媒体，保证长期可读、可迁移、可审计

## 适用资产

- 图片：`png`、`jpg`、`jpeg`、`gif`、`webp`、`svg`
- 视频：`mp4`、`mov`、`m4v`、`webm`、`avi`、`mkv`
- 音频：`mp3`、`wav`、`ogg`、`m4a`
- 封面：文章 `cover`、视频 `poster`

## 核心原则

1. 所有媒体必须优先本地化
   - 页面禁止依赖远程图片、远程视频、远程音频、远程封面
   - 所有媒体引用都必须落到页面同级 `assets/` 子目录

2. 路径必须使用相对路径
   - 图片示例：`./assets/csdnimg/jpg/example.jpg`
   - 视频示例：`./assets/video/lecture-01/video.mp4`
   - 封面示例：`./assets/video/lecture-01/poster.jpg`

3. 视频必须标准化转码
   - 发布格式统一优先 `mp4`
   - 编码统一优先 `H.264 + AAC`
   - 封面统一生成 `poster.jpg`

4. 媒体整改后必须验收
   - 图片整改后至少执行 `archive:verify-images`
   - 涉及视频、音频、封面时必须执行 `archive:verify-media`

## 目录规范

### 图片

每篇文章目录：

`docs/zh/books/<book>/articles/<articleId>/assets/<host>/<ext>/<file>`

### 视频与音频

建议按页面同级再细分媒体类型：

- 视频：`docs/zh/books/<book>/<page>/assets/video/<slug>/`
- 音频：`docs/zh/books/<book>/<page>/assets/audio/<slug>/`

推荐文件结构：

- `video.mp4`
- `poster.jpg`
- `audio.mp3`

## 图片工作流

### 1. 归档生成

```bash
pnpm run archive:build:clean
```

作用：

- 按最新规则生成文章页
- 尽量在生成阶段下载图片并改写路径

### 2. 图片本地化兜底

```bash
pnpm run archive:localize-images
```

作用：

- 处理历史页面残留
- 处理正文图片与 `cover`
- 修复模板重建后的远程图片回退

### 3. 图片验收

```bash
pnpm run archive:verify-images
```

作用：

- 扫描 Markdown 图片、HTML 图片、引用式图片
- 扫描 `cover` 与 `poster` 远程残留
- 发现命中时返回非零状态，阻断发布

## 视频工作流

## 环境要求

- Python `3.8+`
- `ffmpeg` 已安装并位于 PATH

验证：

```bash
ffmpeg -version
```

当前仓库环境已验证存在 `ffmpeg` 可执行程序。

### 标准目录

建议目标目录：

`docs/zh/books/<book>/<page>/assets/video/<slug>/`

示例：

`docs/zh/books/course/assets/video/lecture-01/`

### 视频准备脚本

正式脚本：

`scripts/archives/archive_prepare_video.py`

作用：

- 接收本地视频文件或可直链下载的视频 URL
- 统一转码为站内发布用 `mp4`
- 自动提取 `poster.jpg`
- 输出可直接粘贴到 Markdown 页面中的 HTML 片段

### 使用方式

#### 场景 A：本地视频转码

```bash
python scripts/archives/archive_prepare_video.py ^
  D:\source\lecture-01.mov ^
  docs\zh\books\course\assets\video\lecture-01
```

#### 场景 B：远程视频下载并转码

```bash
python scripts/archives/archive_prepare_video.py ^
  https://example.com/video/lecture-01.mp4 ^
  docs\zh\books\course\assets\video\lecture-01
```

#### 场景 C：指定封面时间点

```bash
python scripts/archives/archive_prepare_video.py ^
  D:\source\lecture-01.mov ^
  docs\zh\books\course\assets\video\lecture-01 ^
  --poster-at 00:00:03
```

### 脚本输出

脚本会输出：

- `video_output`
- `video_relative`
- `poster_output`
- `poster_relative`
- `html_snippet`

推荐引用：

```html
<video controls preload="metadata" poster="./assets/video/lecture-01/poster.jpg">
  <source src="./assets/video/lecture-01/video.mp4" type="video/mp4" />
</video>
```

### 视频转码规范

- 视频输出名默认：`video.mp4`
- 封面输出名默认：`poster.jpg`
- 视频编码：`libx264`
- 像素格式：`yuv420p`
- 音频编码：`aac`
- 开启：`+faststart`

### 不建议的做法

- 直接在页面里写远程 `video src`
- 直接把第三方平台临时地址写进 `poster`
- 把视频文件直接堆在 `docs/` 根层
- 页面里混用绝对路径和相对路径

## 音频工作流

当前仓库尚未接入独立音频准备脚本，但规范与视频一致：

- 优先本地落盘
- 放在 `assets/audio/<slug>/`
- 页面引用使用相对路径
- 发布前纳入 `archive:verify-media`

示例：

```html
<audio controls preload="metadata">
  <source src="./assets/audio/lecture-01/audio.mp3" type="audio/mpeg" />
</audio>
```

## 验收工作流

### 图片验收

```bash
pnpm run archive:verify-images
```

### 媒体验收

```bash
pnpm run archive:verify-media
```

媒体验收覆盖：

- 远程 `img src`
- 远程 `video src`
- 远程 `audio src`
- 远程 `source src`
- 远程 `cover`
- 远程 `poster`
- 远程媒体直链 Markdown 链接

## 媒体黄金闭环

### 图片闭环

```bash
pnpm run archive:build:clean
pnpm run archive:localize-images
pnpm run archive:verify-images
pnpm build
```

### 视频闭环

```bash
python scripts/archives/archive_prepare_video.py <source> <output_dir>
pnpm run archive:verify-media
pnpm build
```

### 图文视频混合页闭环

```bash
pnpm run archive:build:clean
pnpm run archive:localize-images
python scripts/archives/archive_prepare_video.py <source> <output_dir>
pnpm run archive:verify-images
pnpm run archive:verify-media
pnpm build
```

## 发布前检查

必须确认：

1. 图片全部为本地相对路径
2. `cover` 与 `poster` 全部为本地相对路径
3. 视频与音频文件存在于页面同级 `assets/` 下
4. `archive:verify-images` 返回通过
5. `archive:verify-media` 返回通过
6. `pnpm build` 返回通过

## 常见问题

### 1. 视频能播放但不能发布

原因通常是：

- 使用了远程 `video src`
- `poster` 仍然是远程地址
- 媒体验收脚本命中远程链接

### 2. 视频转码失败

排查顺序：

- `ffmpeg` 是否已安装
- 输入文件路径是否正确
- 输出目录是否已存在同名文件且未开启 `--overwrite`

### 3. 图片都改好了但验收仍失败

优先排查：

- `ArticlePaperMeta` 的 `cover`
- HTML `<img>` 标签
- 引用式图片
- 页面里是否还存在远程 `poster`

## 关联文档

- [ENGINEERING_WORKFLOW.md](./ENGINEERING_WORKFLOW.md)
- [ARCHITECTURE.md](./ARCHITECTURE.md)
