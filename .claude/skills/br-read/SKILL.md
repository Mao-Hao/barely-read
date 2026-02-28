---
name: br-read
description: "Deep-read a paper PDF and generate structured notes following the paper-note template"
disable-model-invocation: false
argument-hint: "[arxiv_id | paper_path]"
---

# /br-read — 深度阅读

## Input

- `$ARGUMENTS`: 以下任一格式
  - arxiv ID: `2401.12345`（从 `library/index.yaml` 查找 PDF 路径）
  - 文件路径: `library/papers/2401.12345.pdf`
- `config/user.yaml`: 用户研究方向（用于"与我的研究关联" section）
- `src/templates/paper-note.md`: 笔记模板

## Steps

### 1. 定位论文

从 $ARGUMENTS 确定 PDF 路径：
- 如果是 arxiv ID → 查 `library/index.yaml` 获取 `pdf_path`
- 如果是文件路径 → 直接使用
- 如果 PDF 不存在 → 提示先 `/br-download`
- 如果 $ARGUMENTS 为空 → 列出最近下载但未读的论文，让用户选择

### 2. 读取 PDF

使用 Claude 原生 Read 工具读取 PDF 文件。

如果论文很长（超过 Read 工具限制），分段读取：
- 先读前 20 页获取 abstract、intro、method
- 再读后续部分获取 results、conclusion

### 3. 加载上下文

- 读取 `config/user.yaml` 中的研究方向和关键词
- 读取已有的 stub 笔记（如有）获取已填充的元数据

### 4. 生成结构化笔记

按 `src/templates/paper-note.md` 的 section 结构生成笔记：

**Frontmatter**: 保留 stub 中已有的元数据，更新：
- status: `read`
- read_date: 当前日期
- tags: 从论文内容提取 3-5 个标签

**Sections**（每个 section 的写作指南）：

| Section | 指南 |
|---------|------|
| Summary | 2-3 句话概括核心贡献，非专业人士也能理解 |
| Problem | 这篇论文要解决什么问题？为什么重要？ |
| Method | 关键技术方法。如果有重要公式，用 LaTeX 写出 |
| Results | 主要发现，与 baseline 的对比 |
| Strengths | 论文做得好的地方 |
| Limitations | 弱点、假设、适用范围 |
| Relevance to My Research | **结合 config/user.yaml 中的研究方向**，说明与用户研究的关联 |
| Key Takeaways | 3-5 个要点，最值得记住的东西 |

### 5. 写入笔记

将生成的笔记写入 `library/notes/{arxiv_id}.md`（覆盖 stub）。

### 6. 更新 Index

更新 `library/index.yaml`：
- status: `read`
- read_date: 当前日期
- tags: 添加从论文提取的标签

可使用：`uv run src/tools/update_index.py status {arxiv_id} --status read --tags "tag1,tag2"`

### 7. 输出摘要

```
已完成深度阅读: {title}

Key Takeaways:
1. ...
2. ...
3. ...

与你的研究关联: {一句话总结}

笔记已保存: library/notes/{arxiv_id}.md

下一步：
  /br-explain [概念]     讲解论文中的某个概念
  /br-read [另一篇]      继续阅读下一篇
  /br-search [相关查询]  搜索相关论文
```

## Output

- `library/notes/{arxiv_id}.md` — 完整结构化笔记
- `library/index.yaml` — 更新后的索引
- 终端输出：Key Takeaways + 研究关联

## Error Handling

- PDF 不存在 → 提示下载
- PDF 无法读取（损坏/加密）→ 报错，建议重新下载
- index.yaml 中无该论文 → 创建新条目
- config/user.yaml 不存在 → 跳过 "Relevance to My Research"，提示运行 /br-init

ARGUMENTS: $ARGUMENTS
