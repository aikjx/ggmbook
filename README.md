# ggbook

全域数学·VitePress 文档站点工程。

## 开源协议与版权

本项目采用 **MIT License** 开源。

### 版权信息

- **版权主体**：乖乖数学团队
- **版权年份**：2024-2026
- **License 文件**：[LICENSE](LICENSE)

### 授权范围

MIT 许可证授予您以下权利：
- 使用：以任何目的使用本软件
- 复制：复制本软件的副本
- 修改：修改本软件
- 合并：将本软件与其他软件合并
- 发布：发布本软件的修改版本
- 分发：分发本软件的副本
- 再许可：以不同的条款重新许可本软件
- 销售：销售本软件的副本

### 义务要求

在所有副本或实质性部分中必须保留版权声明和许可声明。

### 免责声明

本软件按"原样"提供，不提供任何明示或暗示的保证。在任何情况下，作者或版权所有者均不对任何索赔、损害赔偿或其他责任承担责任。

### 合规提示

- 详细的开源说明与合规指南：[OPEN_SOURCE.md](project_docs/OPEN_SOURCE.md)
- 网站法律声明页面：[法律声明](docs/zh/legal.md)
- 第三方内容：仓库中包含的第三方内容（如引用、截图等）著作权归原权利人所有

## 快速开始

环境要求：

- Node.js `20+`
- pnpm `9+`
- Python `3.8+`

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
- 总工作流：[ENGINEERING_WORKFLOW.md](project_docs/ENGINEERING_WORKFLOW.md)
- 媒体规范：[MEDIA_WORKFLOW.md](project_docs/MEDIA_WORKFLOW.md)
- 开源与合规：[OPEN_SOURCE.md](project_docs/OPEN_SOURCE.md)

