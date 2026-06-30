# ggbook

全域数学·VitePress 文档站点工程。

## 开源协议与版权

- License：MIT（见 [LICENSE](LICENSE)）
- 版权主体：乖乖数学团队
- 开源说明与合规提示：见 [OPEN_SOURCE.md](project_docs/OPEN_SOURCE.md)

## 快速开始

```bash
pnpm install
pnpm dev --host 127.0.0.1 --port 8081
```

构建与预览：

```bash
pnpm build
pnpm preview
```

## 一键归档（CSDN 备份 → 站内可读）

将 `docs/aa/CSDN博文备份/*.md` 自动分类到四本书的归档目录，并进行图片本地化（下载到文章子目录并重写路径）：

```bash
python scripts/archives/build_csdn_archives.py --purge
```

推荐使用标准化命令入口：

```bash
pnpm run archive:build:clean
pnpm run archive:rebuild
pnpm run archive:localize-images
```

## 项目文档

固定目录：`project_docs/`。

- 文档索引：[INDEX.md](project_docs/INDEX.md)
- 架构主文档：[ARCHITECTURE.md](project_docs/ARCHITECTURE.md)
- 开源与合规：[OPEN_SOURCE.md](project_docs/OPEN_SOURCE.md)

