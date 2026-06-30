# 架构规范（目录规范与全自动流程）

## 目标

- 维护一个可持续迭代的数学知识站点（VitePress）
- 将历史 CSDN 文章备份自动归档到站内可读路径
- 将文章中的远程图片下载到本项目并改写为本地相对路径，保证离线可读与长期可用
- 形成“生成 → 校验 → 老师审核 → 发布”的闭环

## 目录结构（规范）

### 站点根目录

- `docs/`：VitePress 站点内容根目录
- `docs/.vitepress/`：站点配置与主题
  - `config.ts`：站点配置（多语言、导航、KaTeX、构建排除）
  - `theme/`：主题扩展
- `docs/zh/`：中文站点内容
- `docs/en/`：英文站点内容（目前主要是入口与镜像结构）
- `scripts/archives/`：归档自动化正式脚本目录
- `scripts/archives/legacy/`：已废弃或一次性迁移脚本，仅保留参考
- `project_docs/`：项目治理与流程文档唯一规范目录

### 内容分层（推荐保持不变）

- `docs/zh/books/<book>/index.md`：每本书的首页
- `docs/zh/books/<book>/articles/index.md`：该书 CSDN 归档入口页
- `docs/zh/books/<book>/articles/<articleId>/index.md`：单篇文章页（目录式页面）
- `docs/zh/books/<book>/articles/<articleId>/assets/`：该文章的图片资产（文章子目录内）

其中 `<book>` 为：

- `math`：全域数学
- `goldbach`：哥德巴赫猜想
- `shushu`：数术工坊
- `course`：文明进阶200讲

### 原始备份（不参与编译、不建议提交）

- `docs/aa/`：原始备份与临时数据目录
  - 已在 `docs/.vitepress/config.ts` 通过 `srcExclude: ['aa/**']` 排除构建
  - 已在 `.gitignore` 忽略（避免嵌套仓库/巨量文件影响主仓库）

## 图片资产规范（企业级）

### 存放位置

每篇文章独立目录，图片放在文章子目录内，保证可移动、可归档、可增量更新：

`docs/zh/books/<book>/articles/<articleId>/assets/<host>/<ext>/<file>`

### 分类维度

- `<host>`：来源域名分类（当前实现）
  - `csdnimg`：CSDN/博客图床相关域名
  - `external`：其它外部域名
- `<ext>`：按实际格式分层（例如 `jpg`/`png`/`gif`/`webp`/`svg`）
- `<file>`：稳定哈希命名（以 URL 计算，便于去重与增量生成）

### 链接改写范围

自动处理以下图片写法：

- Markdown 行内图片：`![alt](https://...)`
- HTML 图片：`<img src="https://..." />`
- Markdown 引用式链接：`[id]: https://...`

## 自动化流程（全自动处理）

### 1）归档生成（含图片下载与路径改写）

```bash
python scripts/archives/build_csdn_archives.py --purge
```

可选参数：

- `--limit N`：只处理前 N 篇（调试用）
- `--only-id <id>`：只重建指定文章（修单篇用，可重复传参）
- `--no-download-images`：只改写结构不下载图片（调试/离线环境）
- `--progress-every N`：每 N 篇写一次进度到 `tmp/archive_build.log`

标准命令入口：

```bash
pnpm run archive:build
pnpm run archive:build:clean
pnpm run archive:rebuild
pnpm run archive:localize-images
```

### 2）构建验证

```bash
pnpm build
```

### 3）本地预览

```bash
pnpm dev --host 127.0.0.1 --port 8081
```

## 审核闭环（乖乖数学老师审核）

建议流程：

- 生成并自检（归档生成 + build）
- 提交待审核清单（重点内容/问题列表/变更摘要）
- 老师审核：按“文章入口页 → 重点目录 → 逐篇抽检”方式验收
- 修复后再次 build 验证，再进入下一轮迭代

## 目录是否规范（当前结论与建议）

当前目录结构已具备“可长期维护”的核心要素：

- 构建目录与原始备份分离（`srcExclude` + `.gitignore`）
- 文章采用目录式页面（`articles/<id>/index.md`），利于同目录携带 assets
- 图片资产落地到文章子目录，并进行来源/格式分层，利于治理与迁移

建议补强（不破坏现有结构）：

- 统一用 `pnpm`，禁止混用 `package-lock.json`
- 需要“自动更新 sidebar/目录”的话，建议基于 `docs/zh/books/*/articles/index.md` 自动生成，而不是修改 `config.ts`
