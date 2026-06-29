# ggmbook

全域数学·VitePress 文档站点工程。

## 快速开始

```bash
pnpm install
pnpm dev --host 127.0.0.1 --port 8081
```

构建与预览：

```bash
pnpm build
pnpm serve
```

## 一键归档（CSDN 备份 → 站内可读）

将 `docs/aa/CSDN博文备份/*.md` 自动分类到四本书的归档目录，并进行图片本地化（下载到文章子目录并重写路径）：

```bash
python docs/books/build_csdn_archives.py --purge
```

也可以走脚本封装（Windows 下建议使用 `pnpm run`）：

```bash
pnpm run archive:purge
```

## 项目文档

目录规范、自动化流程、审核流程见 [PROJECT.md](file:///d:/a10/aikjx/gitcode/ggbook/PROJECT.md)。

