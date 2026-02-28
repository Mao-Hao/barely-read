---
name: br-init
description: "Initialize BR environment: guided setup for research profile, directories, and MCP detection"
disable-model-invocation: false
argument-hint: ""
---

# /br-init — 首次使用引导

## Input

- 无参数。交互式引导。
- 如果 `config/user.yaml` 已存在，提示用户选择：重新配置 / 保留现有。

## Steps

### 1. 欢迎 + 研究 Profile

向用户询问以下信息（逐项，不要一次全问）：

```
欢迎使用 Barely Read!

请告诉我你的研究方向：
> [用户输入]

你最关注的具体 topics（逗号分隔）：
> [用户输入]

常用搜索关键词（逗号分隔）：
> [用户输入]

你目前的阶段：
  1. 本科生
  2. 硕士
  3. 博士 (默认)
  4. 博后
  5. 教职
  6. 业界
```

### 2. 解释偏好

```
论文讲解的详细程度：
  1. 简要（要点即可）
  2. 标准
  3. 详细（含推导过程）(默认)

是否包含数学公式？ [Y/n]

首选语言：
  1. English (default)
  2. 中文
  3. Mixed
```

### 3. 创建目录结构

检查并创建以下目录（如不存在）：

```
library/papers/
library/notes/
memory/
config/
```

### 4. 检测 MCP Servers

依次检测以下 MCP servers 的可用性：

- **arxiv** — 尝试调用 `search_papers` 搜索 "test"
- **semantic-scholar** — 尝试调用 `search_paper` 搜索 "test"
- **zotero** — 尝试调用 `zotero_search_items` 搜索 "test"

输出检测结果：

```
MCP Servers 检测：
  arxiv            ✓ 可用
  semantic-scholar ✓ 可用
  zotero           ✓ 可用 / ✗ 不可用（非必需）
```

### 5. 生成配置文件

读取 `src/config/defaults.yaml` 作为模板，用用户输入填充字段，写入 `config/user.yaml`。

### 6. 输出欢迎摘要

```
BR 初始化完成！

研究方向: {area}
关注领域: {topics}
解释偏好: {depth}, {language}

可用命令：
  /br-search [query]     搜索论文
  /br-download [paper]   下载论文
  /br-read [paper]       深度阅读
  /br-explain [concept]  概念讲解

开始试试：/br-search "{第一个 keyword}"
```

## Output

- `config/user.yaml` — 用户配置文件
- 终端输出：欢迎摘要 + 可用命令

## Error Handling

- MCP server 不可用 → 警告但不阻塞初始化（标记不可用，相关 skill 会降级处理）
- `config/user.yaml` 已存在 → 询问是否覆盖
- 用户跳过某项 → 使用 defaults.yaml 中的默认值
