# 工程工作流总手册

## 目标

- 建立一套可复制、可审计、可追踪的企业级执行流程
- 统一环境安装、依赖安装、开发、归档、校验、审核、发布、复盘
- 将“算法联盟最高权限”落实为标准化操作，而不是临时口头约定
- 保证任何成员接手项目时，都能按同一份手册完成全流程操作

## 适用范围

- 仓库：`ggmbook`
- 站点类型：VitePress 多语言内容站
- 内容类型：书籍首页、课程讲义、研究论文、专题文稿、自动归档文章、图片、视频、音频
- 自动化目录：`scripts/archives/`
- 规范文档目录：`project_docs/`

## 执行原则

1. 单一事实源
   - 目录、命令、流程、审核规则统一以 `project_docs/` 为准
   - 站点内容只放在 `docs/`
   - 自动化脚本只放在 `scripts/archives/`

2. 先规范后修改
   - 先确定内容归属、目录位置、页面职责
   - 再执行脚本、页面或样式修改

3. 先生成后验证
   - 任何归档、重建、图片本地化都必须经过构建验证
   - 未经过 `pnpm build` 的结果，不视为完成

4. 先自检后审核
   - 自动化自检完成后，才进入“乖乖老师”审核环节
   - 审核前必须确保 404、错链、明显格式错误已处理

5. 先记录后发布
   - 发布前记录变更范围、执行命令、风险点、遗留问题
   - 发布后记录复盘与下一步优化项

## 环境基线

当前仓库已验证环境：

- Node.js：`v22.11.0`
- pnpm：`9.15.3`
- Python：`3.8.8`

推荐最低基线：

- Node.js：`20+`
- pnpm：`9+`
- Python：`3.8+`

## 安装流程

### 1. 获取代码

```bash
git clone <仓库地址>
cd ggmbook
```

### 2. 安装 Node.js

要求：

- 必须安装 Node.js
- 推荐使用 LTS 或当前已验证版本附近的大版本

验证：

```bash
node -v
```

### 3. 安装 pnpm

若本机未安装：

```bash
npm install -g pnpm
```

验证：

```bash
pnpm -v
```

### 4. 安装 Python

要求：

- 用于运行归档、重建、图片本地化脚本
- 建议加入系统 PATH

验证：

```bash
python --version
```

### 5. 安装 ffmpeg

要求：

- 处理视频下载、转码、封面提取时必须安装
- 建议加入系统 PATH

验证：

```bash
ffmpeg -version
```

### 6. 安装项目依赖

```bash
pnpm install
```

### 7. 安装后自检

按顺序执行：

```bash
pnpm build
pnpm run archive:build --help
pnpm run archive:rebuild --help
pnpm run archive:localize-images --help
pnpm run archive:verify-media --help
```

通过标准：

- 依赖安装无中断
- `pnpm build` 可完成
- 归档命令可显示帮助或正常执行

## 目录职责

- `docs/`：站点内容与 VitePress 配置
- `docs/zh/`：中文主内容
- `docs/en/`：英文镜像入口层
- `docs/.vitepress/`：站点配置、主题、组件、样式
- `scripts/archives/`：归档正式脚本
- `scripts/archives/legacy/`：废弃或一次性脚本，仅保留参考
- `project_docs/`：工程规范、流程、合规文档
- `reports/`：分析输出、报告类文件
- `tmp/`：构建日志与临时文件

## 标准命令矩阵

### 站点开发

```bash
pnpm dev --host 127.0.0.1 --port 8081
pnpm build
pnpm preview
```

### 归档构建

```bash
pnpm run archive:build
pnpm run archive:build:clean
pnpm run archive:rebuild
pnpm run archive:localize-images
pnpm run archive:verify-images
pnpm run archive:verify-media
```

### 精准修复

```bash
python scripts/archives/build_csdn_archives.py --only-id <文章ID>
python scripts/archives/archive_localize_images.py <目标目录或文件> --purge-assets
python scripts/archives/archive_prepare_video.py <source> <output_dir>
```

## 全流程工作流

### 阶段 1：任务受理

- 明确任务是：
  - 新增书籍页
  - 优化书籍布局
  - 接入归档文章
  - 修复 404 / 图片 / 样式 / 导航
  - 文档规范化
- 明确影响范围：
  - `docs/`
  - `scripts/archives/`
  - `project_docs/`

输出物：

- 目标页面清单
- 目标脚本清单
- 预期验收标准

### 阶段 2：结构判定

- 先确定内容归属书籍：
  - `math`
  - `goldbach`
  - `shushu`
  - `course`
- 再确定承载方式：
  - 首页
  - 归档页
  - 卷页
  - 单篇文章页
- 再确定是否需要同步：
  - 元信息组件
  - 文章卡片
  - 图片本地化
  - 视频与音频媒体
  - 导航与侧边栏

### 阶段 3：实施开发

执行顺序建议：

1. 修改结构与文档
2. 修改脚本与生成逻辑
3. 修改页面与样式
4. 执行重建
5. 执行本地化

实施规则：

- 新增页面必须使用真实 `index.md`
- 所有内部链接必须使用相对路径
- 文章与论文页统一使用结构化 frontmatter
- 远程图片必须下载并改写为本地 `./assets/...`
- `ArticlePaperMeta` 内的 `cover` 也必须同步改写为本地相对路径
- 图片处理完成后，必须执行远程残留扫描，不能只靠抽样目视判断
- 视频与音频必须落在页面同级 `assets/` 目录下，并使用相对路径引用
- 视频优先统一转码为 `mp4`，封面统一抽取为本地 `poster.jpg`

### 阶段 4：自动化执行

#### 场景 A：全量重建

```bash
pnpm run archive:build:clean
```

适用：

- 首次大规模接入
- 规则变更后全站重建
- 目录结构重构后重建

#### 场景 B：模板重建

```bash
pnpm run archive:rebuild
```

适用：

- 文章模板、文章元信息、卡片样式更新后
- 需要让已有文章全部重新套用新结构时

#### 场景 C：图片本地化

```bash
pnpm run archive:localize-images
```

适用：

- 修复远程图片回退
- 新增历史页面图片本地化
- 重建后确认资源回归本地目录

#### 场景 D：远程图片验收

```bash
pnpm run archive:verify-images
```

适用：

- 发布前确认是否仍有远程图片残留
- 检查 `cover`、Markdown 图片、HTML 图片、引用式图片是否全部本地化
- 作为图片整改后的强制验收步骤

#### 图片本地化黄金闭环

标准顺序必须固定为：

```bash
pnpm run archive:build:clean
pnpm run archive:localize-images
pnpm run archive:verify-images
pnpm build
```

说明：

- `archive:build:clean` 负责按最新规则生成文章页，并尽量在生成时完成图片落盘
- `archive:localize-images` 负责兜底处理历史页面、封面 `cover` 与残留远程图
- `archive:verify-images` 负责扫描并阻断远程图片残留进入发布环节
- `pnpm build` 负责确认站点层面没有 Markdown、组件或链接错误

禁止直接以“重建成功”视为图片问题已解决，必须跑完整闭环

#### 场景 E：远程媒体验收

```bash
pnpm run archive:verify-media
```

适用：

- 发布前确认是否仍有远程视频、音频、封面残留
- 检查 `video src`、`audio src`、`source src`、`poster`、`cover`
- 作为媒体整改后的强制验收步骤

### 阶段 5：自检

必须检查：

- 页面是否存在 404
- 文章页是否存在远程图片残留
- `ArticlePaperMeta` 的 `cover` 是否仍指向远程地址
- 页面中的视频、音频、封面是否仍引用远程地址
- 归档页是否显示为卡片化展示
- 书籍首页是否保留统一入口风格
- 卷页、课程页、归档页是否职责清晰

建议命令：

```bash
pnpm build
```

必要时结合：

- `tmp/archive_build.log`
- 编辑器诊断
- 站点预览
- `pnpm run archive:verify-images`
- `pnpm run archive:verify-media`

### 阶段 6：本地预览

```bash
pnpm dev --host 127.0.0.1 --port 8081
```

检查重点：

- 首页首屏结构是否正常
- 文章卡片是否布局稳定
- 数学公式是否渲染正常
- 文章详情页元信息区是否完整
- 中英文入口是否没有明显断链

### 阶段 7：老师审核

发布前必须经过“乖乖老师”审核。

审核清单：

1. 404 检查
2. 公式渲染检查
3. 错别字检查
4. 文章归类是否正确
5. 卷页状态是否真实
6. 图片是否全部本地化
7. 是否存在“入口可点但内容不符合预期”的误导情况

### 阶段 8：发布记录

每次发布至少记录：

- 变更页面范围
- 变更脚本范围
- 执行命令
- 审核结果
- 已知遗留问题
- 下一步优化方向

推荐记录位置：

- `project_docs/`
- 对应专题 workflow 文档
- 项目记忆与会话总结

### 阶段 9：复盘优化

复盘时统一从以下维度分析：

- 目录是否更清晰
- 命令是否更少、更稳定
- 样式是否更统一
- 图片是否更稳定
- 生成链路是否存在重复步骤
- 用户是否能更快找到文章和论文

## 安装到发布的完整执行示例

### 首次接手项目

```bash
git clone <仓库地址>
cd ggmbook
pnpm install
pnpm build
pnpm dev --host 127.0.0.1 --port 8081
```

### 处理归档文章并上线

```bash
pnpm run archive:build:clean
pnpm run archive:localize-images
pnpm run archive:verify-images
pnpm build
pnpm dev --host 127.0.0.1 --port 8081
```

### 样式或文章模板升级后刷新全站

```bash
pnpm run archive:rebuild
pnpm build
```

### 修复图片本地化

```bash
pnpm run archive:localize-images
pnpm run archive:verify-images
pnpm build
```

### 新增本地视频并上线

```bash
python scripts/archives/archive_prepare_video.py <source> <output_dir>
pnpm run archive:verify-media
pnpm build
```

## 全流程跟踪清单

每轮任务按以下顺序打钩：

1. 环境可用
2. 目录归属已判定
3. 页面职责已确认
4. 脚本入口已确认
5. 修改已完成
6. 归档或重建已执行
7. 图片本地化已确认
8. 视频与音频路径已确认
9. `pnpm build` 已通过
10. 本地预览已检查
11. 老师审核已完成
12. 发布记录已补齐
13. 优化项已写入文档

## 常见故障与处理

### 1. 页面 404

排查顺序：

- 是否缺少 `index.md`
- 首页链接是否指向真实目录
- 相对路径是否写错

### 2. 图片变回远程链接

排查顺序：

- 是否执行过 `archive:rebuild` 但未重新本地化
- 当前 `archive:rebuild` 是否为最新版本
- 目标文章目录下是否存在 `assets/`

处理：

```bash
pnpm run archive:localize-images
pnpm run archive:verify-images
pnpm build
```

补充排查：

- 已生成页面中的正文图片也许已改成本地，但 `ArticlePaperMeta` 的 `cover` 仍可能残留远程地址
- 若只执行过重建，未执行本地化与验收，不能认定图片流程闭环完成
- 若验收脚本仍报错，必须继续整改直到 `archive:verify-images` 返回通过

### 3. 视频或音频仍是远程地址

排查顺序：

- 页面是否直接写了远程 `video src` 或 `audio src`
- `poster` 是否仍是远程地址
- 是否跳过了 `archive:verify-media`
- 视频资源是否实际落在页面同级 `assets/` 下

处理：

```bash
python scripts/archives/archive_prepare_video.py <source> <output_dir>
pnpm run archive:verify-media
pnpm build
```

### 4. 构建失败

排查顺序：

- Markdown 结构是否损坏
- VitePress 配置是否引用了错误文件
- 组件名或样式类是否写错

### 5. 文章分类错误

排查顺序：

- 文章标题和正文关键词是否命中错误分类
- 分类规则是否需要扩展
- 是否需要单篇定向重建

## 持续优化策略

建议长期执行以下优化：

- 将高频页面布局进一步组件化
- 将文章推荐、上一篇/下一篇纳入统一模板
- 将侧边栏数据进一步从内容页自动生成
- 对远程图片残留做定期扫描
- 对 404、死链、无效锚点做周期性巡检
- 将每轮经验写回 `project_docs/`

## 关联文档

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [MEDIA_WORKFLOW.md](./MEDIA_WORKFLOW.md)
- [SHUSHU_WORKFLOW.md](./SHUSHU_WORKFLOW.md)
- [OPEN_SOURCE.md](./OPEN_SOURCE.md)
