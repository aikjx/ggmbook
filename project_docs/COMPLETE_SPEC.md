# 全域数学书籍项目 - 企业级规范标准

## 一、项目概述

### 1.1 项目定位

本项目是一个基于 **VitePress** 构建的多语言数学知识站点，核心目标包括：

- 维护可持续迭代的数学知识体系
- 将历史 CSDN 文章自动归档到站内可读路径
- 将远程图片下载到本地，保证离线可读与长期可用
- 形成"生成 → 校验 → 审核 → 发布"的企业级闭环流程

### 1.2 适用范围

| 类别 | 说明 |
|------|------|
| 仓库 | `ggbook` |
| 站点类型 | VitePress 多语言内容站 |
| 内容类型 | 书籍首页、课程讲义、研究论文、专题文稿、自动归档文章 |
| 媒体类型 | 图片、视频、音频、封面 |

---

## 二、目录结构规范

### 2.1 根目录结构

```
ggbook/
├── docs/                    # VitePress 站点内容根目录
│   ├── .vitepress/          # 站点配置与主题
│   │   ├── config.ts        # 站点配置（多语言、导航、KaTeX）
│   │   ├── theme/           # 主题扩展
│   │   │   ├── index.ts     # 主题入口
│   │   │   ├── style.css    # 全局样式（含KaTeX）
│   │   │   └── katex-render.js  # KaTeX客户端渲染
│   │   └── dist/            # 构建产物（自动生成）
│   ├── zh/                  # 中文站点内容
│   ├── en/                  # 英文站点内容
│   └── aa/                  # 原始备份与临时数据（不参与编译）
├── scripts/
│   └── archives/            # 归档自动化正式脚本目录
│       └── legacy/          # 已废弃脚本（仅保留参考）
├── project_docs/            # 项目治理与流程文档
├── reports/                 # 分析输出、报告类文件
├── tmp/                     # 构建日志与临时文件
├── package.json             # 项目依赖配置
└── .gitignore               # Git忽略配置
```

### 2.2 内容分层规范

| 层级 | 路径模式 | 职责说明 |
|------|----------|----------|
| 书籍首页 | `docs/zh/books/<book>/index.md` | 每本书的主入口页 |
| 归档入口 | `docs/zh/books/<book>/articles/index.md` | CSDN归档文章列表页 |
| 单篇文章 | `docs/zh/books/<book>/articles/<articleId>/index.md` | 目录式文章页面 |
| 文章资源 | `docs/zh/books/<book>/articles/<articleId>/assets/` | 文章图片资产 |

### 2.3 书籍分类体系

| 书籍标识 | 书籍名称 | 职责定位 |
|----------|----------|----------|
| `math` | 全域数学 | 核心数学理论与公式典藏 |
| `goldbach` | 哥德巴赫猜想 | 数论专题研究 |
| `shushu` | 数术工坊 | 传统数术与现代数学融合 |
| `course` | 文明进阶200讲 | 数学与文明对比课程 |

### 2.4 图片资产规范

**存放路径**：
```
docs/zh/books/<book>/articles/<articleId>/assets/<host>/<ext>/<file>
```

**分类维度**：

| 维度 | 说明 | 示例 |
|------|------|------|
| `<host>` | 来源域名分类 | `csdnimg`、`external` |
| `<ext>` | 文件格式分层 | `jpg`、`png`、`gif`、`webp`、`svg` |
| `<file>` | 稳定哈希命名 | 基于URL计算，便于去重 |

---

## 三、技术栈规范

### 3.1 环境基线

| 工具 | 已验证版本 | 最低要求 |
|------|-----------|----------|
| Node.js | `v22.11.0` | `20+` |
| pnpm | `9.15.3` | `9+` |
| Python | `3.8.8` | `3.8+` |
| ffmpeg | 系统安装 | 视频处理必需 |

### 3.2 核心依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| `vitepress` | `1.0.0-alpha.28` | 站点框架 |
| `vue` | `3.4.21` | 前端框架 |
| `katex` | `^0.17.0` | LaTeX公式渲染 |
| `@iktakahiro/markdown-it-katex` | 最新 | Markdown公式支持 |

---

## 四、工程工作流规范

### 4.1 执行原则

1. **单一事实源**：目录、命令、流程统一以 `project_docs/` 为准
2. **先规范后修改**：先确定内容归属、目录位置、页面职责
3. **先生成后验证**：任何归档、重建都必须经过 `pnpm build`
4. **先自检后审核**：自动化自检完成后，才进入审核环节
5. **先记录后发布**：发布前记录变更范围、风险点、遗留问题

### 4.2 全流程阶段

| 阶段 | 名称 | 核心任务 | 输出物 |
|------|------|----------|--------|
| 1 | 任务受理 | 明确任务类型与影响范围 | 目标页面/脚本清单 |
| 2 | 结构判定 | 确定内容归属与承载方式 | 目录归属判定 |
| 3 | 实施开发 | 修改结构、脚本、页面 | 代码变更 |
| 4 | 自动化执行 | 重建、本地化、验收 | 处理结果 |
| 5 | 自检 | 404、远程资源、构建验证 | 自检报告 |
| 6 | 本地预览 | 页面、公式、导航检查 | 预览确认 |
| 7 | 老师审核 | 内容、状态、入口审核 | 审核通过 |
| 8 | 发布记录 | 记录变更与遗留问题 | 发布文档 |
| 9 | 复盘优化 | 分析流程与体验问题 | 优化方案 |

### 4.3 标准命令矩阵

#### 站点开发

```bash
pnpm dev --host 127.0.0.1 --port 8081    # 开发服务器
pnpm build                               # 构建验证
pnpm preview                             # 预览构建结果
```

#### 归档构建

```bash
pnpm run archive:build                   # 归档生成
pnpm run archive:build:clean             # 全量重建（含清理）
pnpm run archive:rebuild                 # 模板重建
pnpm run archive:localize-images         # 图片本地化
pnpm run archive:verify-images           # 图片验收
pnpm run archive:verify-media            # 媒体验收
```

#### 精准修复

```bash
python scripts/archives/build_csdn_archives.py --only-id <文章ID>
python scripts/archives/archive_localize_images.py <目标目录> --purge-assets
python scripts/archives/archive_prepare_video.py <source> <output_dir>
```

### 4.4 黄金闭环流程

#### 图片本地化闭环

```bash
pnpm run archive:build:clean      # 1. 全量重建
pnpm run archive:localize-images  # 2. 图片本地化
pnpm run archive:verify-images    # 3. 图片验收
pnpm build                        # 4. 构建验证
```

#### 视频处理闭环

```bash
python scripts/archives/archive_prepare_video.py <source> <output_dir>
pnpm run archive:verify-media
pnpm build
```

---

## 五、页面规范

### 5.1 页面职责矩阵

| 页面 | 主职责 | 可承载内容 | 不应承担 |
|------|--------|------------|----------|
| `shushu/index.md` | 数术工坊总入口 | 状态、入口、主题摘要 | 长正文主发布 |
| `shushu/volX/index.md` | 单卷稳定入口 | 状态、跳转、独立正文 | 其它卷内容 |
| `math/articles/<id>/` | 阶段性合集承载 | 已上线正文与锚点 | 永久替代卷页入口 |
| `shushu/articles/index.md` | 归档补充 | 自动分类文章 | 数术八卷主内容 |

### 5.2 卷页状态模型

| 状态 | 定义 | 说明 |
|------|------|------|
| `已上线` | 正文已可读 | 独立卷页或合集页均可 |
| `合集承载` | 正文存在但未拆卷 | 技术状态，首页展示为"已上线" |
| `待上线` | 卷页入口已补齐 | 仅有落点和说明，不伪装成已上线 |
| `归档为空` | 无自动分类文章 | 归档页专用状态 |

### 5.3 页面展示规范

#### 首页规范
- 必须前置统计信息
- 必须前置卷册入口
- 必须展示每卷状态
- 必须区分"合集页"和"归档页"

#### 卷页规范
- 必须包含当前状态
- 必须包含当前载体
- 必须包含正文入口或后续说明
- 必须包含返回首页入口

#### 归档页规范
- 有文章时显示列表
- 无文章时显示空状态说明
- 不允许只有标题没有说明

---

## 六、媒体资产规范

### 6.1 核心原则

1. **所有媒体必须优先本地化**：禁止依赖远程资源
2. **路径必须使用相对路径**：`./assets/...`
3. **视频必须标准化转码**：优先 `mp4` + `H.264 + AAC`
4. **媒体整改后必须验收**：执行验证脚本

### 6.2 视频转码规范

| 属性 | 标准值 |
|------|--------|
| 输出格式 | `video.mp4` |
| 封面格式 | `poster.jpg` |
| 视频编码 | `libx264` |
| 像素格式 | `yuv420p` |
| 音频编码 | `aac` |
| 优化选项 | `+faststart` |

### 6.3 视频准备脚本

```bash
# 本地视频转码
python scripts/archives/archive_prepare_video.py ^
  D:\source\lecture-01.mov ^
  docs\zh\books\course\assets\video\lecture-01

# 远程视频下载并转码
python scripts/archives/archive_prepare_video.py ^
  https://example.com/video.mp4 ^
  docs\zh\books\course\assets\video\lecture-01

# 指定封面时间点
python scripts/archives/archive_prepare_video.py ^
  D:\source\lecture-01.mov ^
  docs\zh\books\course\assets\video\lecture-01 ^
  --poster-at 00:00:03
```

### 6.4 推荐视频引用格式

```html
<video controls preload="metadata" poster="./assets/video/lecture-01/poster.jpg">
  <source src="./assets/video/lecture-01/video.mp4" type="video/mp4" />
</video>
```

---

## 七、审核规范

### 7.1 审核清单

| 检查项 | 说明 |
|--------|------|
| 404 检查 | 所有入口是否可访问 |
| 公式渲染 | KaTeX公式是否正常显示 |
| 错别字检查 | 文案正确性 |
| 文章归类 | 是否归属正确书籍 |
| 卷页状态 | 状态是否真实反映内容 |
| 图片本地化 | 是否存在远程图片残留 |
| 入口误导 | 是否存在"可点但内容不符预期" |

### 7.2 发布前检查

必须确认：
1. ✅ 图片全部为本地相对路径
2. ✅ `cover` 与 `poster` 全部为本地相对路径
3. ✅ 视频与音频文件存在于同级 `assets/` 下
4. ✅ `archive:verify-images` 返回通过
5. ✅ `archive:verify-media` 返回通过
6. ✅ `pnpm build` 返回通过

---

## 八、常见故障排查

### 8.1 页面 404

排查顺序：
1. 是否缺少 `index.md`
2. 首页链接是否指向真实目录
3. 相对路径是否写错

### 8.2 图片变回远程链接

排查顺序：
1. 是否执行过 `archive:rebuild` 但未重新本地化
2. 当前 `archive:rebuild` 是否为最新版本
3. 目标文章目录下是否存在 `assets/`

处理命令：
```bash
pnpm run archive:localize-images
pnpm run archive:verify-images
pnpm build
```

### 8.3 视频或音频仍是远程地址

排查顺序：
1. 页面是否直接写了远程 `video src` 或 `audio src`
2. `poster` 是否仍是远程地址
3. 是否跳过了 `archive:verify-media`

### 8.4 构建失败

排查顺序：
1. Markdown 结构是否损坏
2. VitePress 配置是否引用了错误文件
3. 组件名或样式类是否写错

---

## 九、持续优化策略

| 优化方向 | 说明 |
|----------|------|
| 组件化 | 将高频页面布局进一步组件化 |
| 模板统一 | 将文章推荐、上下篇纳入统一模板 |
| 自动生成 | 侧边栏数据从内容页自动生成 |
| 定期扫描 | 远程图片残留定期扫描 |
| 周期性巡检 | 404、死链、无效锚点巡检 |
| 文档沉淀 | 将每轮经验写回 `project_docs/` |

---

## 十、文档索引

| 文档 | 路径 | 职责 |
|------|------|------|
| 项目索引 | `project_docs/INDEX.md` | 文档总索引 |
| 架构规范 | `project_docs/ARCHITECTURE.md` | 目录规范与自动化流程 |
| 工程工作流 | `project_docs/ENGINEERING_WORKFLOW.md` | 环境、命令、审核、发布 |
| 媒体工作流 | `project_docs/MEDIA_WORKFLOW.md` | 图片、视频、音频规范 |
| 数术工坊流程 | `project_docs/SHUSHU_WORKFLOW.md` | 卷页与状态治理 |
| 开源合规 | `project_docs/OPEN_SOURCE.md` | 开源协议与版权 |

---

**文档版本**：v1.0  
**最后更新**：2026年7月  
**适用范围**：ggbook 项目全体成员