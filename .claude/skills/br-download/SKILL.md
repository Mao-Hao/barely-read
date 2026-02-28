---
name: br-download
description: "Download a paper PDF and add it to the library with stub note and index entry"
disable-model-invocation: false
argument-hint: "[arxiv_id | arxiv_url | #search_result_number]"
---

# /br-download — 论文下载入库

## Input

- `$ARGUMENTS`: 以下任一格式
  - arxiv ID: `2401.12345`
  - arxiv URL: `https://arxiv.org/abs/2401.12345`
  - 搜索结果编号: `#3`（引用上次 /br-search 的结果）
- `config/user.yaml`: 用户配置（可选，用于笔记模板填充）

## Steps

### 1. 解析 paper ID

从 $ARGUMENTS 提取 arxiv ID：
- 如果是 URL，提取 ID 部分
- 如果是 `#N`，从上次搜索结果中查找对应论文
- 如果为空，提示用户输入

### 2. 检查是否已下载

读取 `library/index.yaml`（如存在），检查该 paper_id 是否已存在：
- 已存在 → 提示用户，询问是否重新下载
- 不存在 → 继续

### 3. 获取元数据

调用 arxiv MCP (`search_papers`) 或 Semantic Scholar MCP (`get_paper`) 获取论文元数据：
- title, authors, year, abstract, doi, url

### 4. 下载 PDF

调用 arxiv MCP (`download_paper`) 下载论文。

MCP 会将文件存储在其管理目录中。下载完成后，使用 Bash 工具将 PDF 复制到 `library/papers/{arxiv_id}.pdf`：

```bash
cp .claude/papers/{arxiv_id}.pdf library/papers/{arxiv_id}.pdf
```

如果 MCP 下载失败，尝试直接用 Bash 下载：
```bash
curl -L -o library/papers/{arxiv_id}.pdf https://arxiv.org/pdf/{arxiv_id}.pdf
```

### 5. 创建 Stub 笔记

读取 `src/templates/paper-note.md` 模板，填充已知元数据字段：
- paper_id, title, authors, year, url, doi
- status: stub
- created: 当前日期
- tags: 从 abstract 中提取 2-3 个关键词

写入 `library/notes/{arxiv_id}.md`。

### 6. 更新 Index

调用 `uv run src/tools/update_index.py` 更新 `library/index.yaml`，或直接用 Read + Write 工具操作 YAML：

添加条目：
```yaml
papers:
  "{arxiv_id}":
    title: "..."
    authors: [...]
    year: 2025
    doi: "..."
    url: "https://arxiv.org/abs/{arxiv_id}"
    tags: [...]
    status: downloaded
    pdf_path: "library/papers/{arxiv_id}.pdf"
    note_path: "library/notes/{arxiv_id}.md"
    added_date: "2026-02-28"
    read_date: ""
```

### 7. 输出确认

```
已下载: {title}
作者: {authors}
PDF: library/papers/{arxiv_id}.pdf

要我讲讲这篇论文吗？或者继续下载其他的。
```

## Output

- `library/papers/{arxiv_id}.pdf` — 论文 PDF
- `library/notes/{arxiv_id}.md` — stub 笔记（元数据已填，内容待 deep-read）
- `library/index.yaml` — 更新的索引

## Error Handling

- arxiv MCP 不可用 → 回退到 curl 直接下载
- PDF 下载失败 → 报错，不创建 index 条目
- paper 已存在 → 询问是否覆盖
- index.yaml 不存在 → 创建新文件
- $ARGUMENTS 无法解析为 paper ID → 提示用法

ARGUMENTS: $ARGUMENTS
