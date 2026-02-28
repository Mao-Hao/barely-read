---
name: br-search
description: "Search academic papers across arxiv and Semantic Scholar, rank by relevance to user's research"
disable-model-invocation: false
argument-hint: "[query]"
---

# /br-search — 论文搜索

## Input

- `$ARGUMENTS`: 自然语言查询（如 "symbolic regression for physics"）
- `config/user.yaml`: 用户研究方向和搜索偏好

## Steps

### 1. 解析查询意图

从用户的自然语言查询中提取：
- **关键词**: 核心搜索词
- **时间范围**: 如提及 "recent" / "2024" 等，映射为日期过滤；否则使用 `config/user.yaml` 中 `search.default_years_back`
- **领域**: 如提及具体领域，根据用户输入推断对应的 arxiv categories（如 physics.comp-ph, q-bio.BM, econ.TH 等，不限于 CS）

如果 $ARGUMENTS 为空，提示用户输入查询。

### 2. 并行搜索

同时调用两个 MCP server：

**arxiv MCP** (`search_papers`):
- query: 提取的关键词，使用引号括住核心短语
- categories: 如有领域信息则过滤
- date_from: 按时间范围设置
- max_results: `search.max_results` 的一半（默认 10）
- sort_by: "relevance"

**Semantic Scholar MCP** (`search_paper`):
- query: 自然语言查询
- limit: `search.max_results` 的一半（默认 10）
- year: 按时间范围设置
- fields: "paperId,title,abstract,authors,year,citationCount,url,externalIds"

### 3. 合并去重 + 排序

1. **去重**: 基于 arxiv ID 或 DOI 匹配，保留信息更丰富的条目
2. **排序**: 综合以下信号
   - 与用户 `research.topics` 和 `research.keywords` 的语义相关性
   - 引用数（来自 Semantic Scholar）
   - 发表时间（近期加权，如用户偏好 prefer_recent）
3. **相关性说明**: 对每篇论文生成一句话说明为何与用户研究相关

### 4. 输出结果

格式化为编号表格：

```
搜索: "{query}"
来源: arxiv + Semantic Scholar
结果: N 篇（去重后）

| # | 标题 | 作者 | 年份 | 引用 | 相关性 |
|---|------|------|------|------|--------|
| 1 | ... | ... | 2025 | 142 | 与你的 SR 研究直接相关：... |
| 2 | ... | ... | 2024 | 89  | 方法可借鉴：... |
| ... |

接下来你可以说：
  "下载 #3"         下载第 3 篇
  "#5 讲讲"         看第 5 篇的详细信息
  "换个关键词"       重新搜索
```

每个结果编号在本次会话中有效，用户可直接引用。

### 5. 详情查询（可选）

如果用户请求某篇论文的详情：
- 调用 Semantic Scholar MCP (`get_paper`) 获取完整信息
- 展示：完整摘要、所有作者、发表 venue、引用/被引数、PDF 链接

## Output

- 终端输出：编号结果表
- 无文件写入（搜索是只读操作）

## Error Handling

- arxiv MCP 不可用 → 仅用 Semantic Scholar，提示用户
- Semantic Scholar MCP 不可用 → 仅用 arxiv，提示用户
- 两者都不可用 → 回退到 WebSearch 搜索 arxiv.org，提示功能受限
- 无结果 → 建议调整关键词或放宽时间范围
- config/user.yaml 不存在 → 跳过个性化排序，搜索完后建议先配置 profile

ARGUMENTS: $ARGUMENTS
