---
name: br-read
description: "Interactive paper walkthrough — AI explains the paper to you, saves notes as byproduct"
disable-model-invocation: false
argument-hint: "[arxiv_id | paper_path]"
---

# /br-read — 论文讲解

## Input

- `$ARGUMENTS`: arxiv ID (`2401.12345`) 或文件路径
- `config/user.yaml`: 用户研究方向和讲解偏好
- `templates/paper-note.md`: 笔记模板（用于保存）

## Steps

### 1. 定位论文

从 $ARGUMENTS 确定 PDF 路径：
- 如果是 arxiv ID → 查 `library/index.yaml` 获取 `pdf_path`
- 如果是文件路径 → 直接使用
- 如果 PDF 不存在 → 提示："这篇论文还没下载，要我帮你下载吗？"
- 如果 $ARGUMENTS 为空 → 列出最近下载但未读的论文，用编号让用户选

### 2. 选择讲解方式

```
这篇论文：{title}
作者：{authors} ({year})

选择讲解方式：
  1. 速览 — 核心结论，1-2 分钟
  2. 标准 — 问题+方法+结果，5 分钟（默认）
  3. 深入 — 含技术细节和推导，适合精读
```

默认使用 `config/user.yaml` 中 `explanation.depth` 对应的选项。用户输入编号选择。

### 3. 读取 PDF + 加载上下文

- 使用 Claude 原生 Read 工具读取 PDF
- 如果论文很长，分段读取（先 abstract+intro+method，再 results+conclusion）
- 读取 `config/user.yaml` 中的研究方向和关键词

### 4. 讲解论文（交互式）

根据选择的颗粒度讲解。**用对话语气讲，不是写学术摘要。**

**速览模式**：
```
## 一句话总结
[用直觉语言概括]

## 核心发现
- [3-5 个要点]

## 跟你的研究有什么关系
[结合用户研究方向]
```

**标准模式**：
```
## 这篇论文要解决什么问题？
[用直觉语言，为什么这个问题重要]

## 他们怎么做的？
[关键方法，用用户能理解的语言]

## 主要发现
[结果 + 和之前工作的对比]

## 亮点和不足
[strengths + limitations]

## 跟你的研究有什么关系
[结合用户研究方向，可以借鉴什么]
```

**深入模式**：
标准模式的所有内容，加上：
```
## 技术细节
[关键公式/算法，用 LaTeX 写出，配有直觉解释]

## 实验设计
[数据集、baseline、评估指标的细节]

## 开放问题
[论文没解决的、后续可以做的]
```

### 5. 等待用户反馈

讲完后提示（自然语言，不要用斜杠命令）：

```
---
有什么想深入了解的吗？比如：
  "方法部分再详细讲讲"
  "XX 是什么意思？"
  "跟 [另一篇论文] 比呢？"
  "保存笔记"
  "换一篇"
```

用户可以：
- 追问任何部分 → AI 直接在当前上下文中回答
- 说"保存笔记" → 执行 Step 6
- 说"换一篇" / 给新 paper ID → 从 Step 1 重新开始
- 直接开始下一个话题 → 自然退出

### 6. 保存笔记（用户请求时）

当用户说"保存笔记"、"存一下"等：

1. 将讲解内容整理为 `templates/paper-note.md` 格式
2. 填充 frontmatter（paper_id, title, authors, year, status: read, tags）
3. 写入 `library/notes/{arxiv_id}.md`
4. 更新 `library/index.yaml`（status: read, read_date, tags）
5. 确认："笔记已保存到 library/notes/{arxiv_id}.md"

## Output

- 终端输出：交互式论文讲解
- `library/notes/{arxiv_id}.md` — 笔记（仅用户请求时保存）
- `library/index.yaml` — 更新（仅保存笔记时）

## Error Handling

- PDF 不存在 → 提议帮用户下载（自然语言）
- PDF 无法读取 → 报错，建议重新下载
- config/user.yaml 不存在 → 使用默认偏好，讲完后建议配置 profile

ARGUMENTS: $ARGUMENTS
