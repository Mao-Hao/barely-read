---
name: br-explain
description: "Explain an academic concept tailored to user's research background and preferences"
disable-model-invocation: false
argument-hint: "[concept or term]"
---

# /br-explain — 概念讲解

## Input

- `$ARGUMENTS`: 要讲解的概念、术语或方法名
- `config/user.yaml`: 用户背景和讲解偏好
- `library/notes/`: 已有论文笔记（可选，用于关联具体论文）

## Steps

### 1. 加载用户上下文

读取 `config/user.yaml`：
- `explanation.depth`: 讲解详细程度（brief / standard / detailed）
- `explanation.include_math`: 是否包含数学公式
- `explanation.level`: 假设的知识水平
- `explanation.language`: 输出语言
- `research.area`: 研究方向（用于关联说明）

如果 config 不存在，使用默认值（detailed, include_math, graduate, zh）。

### 2. 搜索 Library 关联

在 `library/notes/` 中搜索与该概念相关的论文笔记：
- 使用 Grep 工具搜索 $ARGUMENTS 关键词
- 如果找到相关论文，记录 paper_id 和相关段落

### 3. 生成讲解

根据用户偏好生成讲解，结构如下：

**Brief 模式**（~100 字）：
```
## {概念}
一段话定义 + 核心直觉。
```

**Standard 模式**（~300 字）：
```
## {概念}

### 直觉
用类比或日常语言解释核心思想。

### 定义
精确的定义。如果 include_math=true，包含数学表达。

### 为什么重要
在用户研究领域中的意义。
```

**Detailed 模式**（~500+ 字）：
```
## {概念}

### 直觉
用类比或日常语言解释核心思想。

### 形式化定义
精确定义 + 数学表达（如适用）。

### 关键性质
重要特征、定理、或推论。

### 与相关概念的关系
与相近/相对概念的对比。

### 在你的研究中
结合用户的研究方向，说明该概念如何与其研究相关。

### 参考论文
列出 library 中涉及该概念的论文（如有）。
```

### 4. 关联已有论文

如果 Step 2 找到了相关笔记，在讲解中引用：

```
### 参考论文（来自你的 Library）
- [{title}](library/notes/{id}.md): {该论文如何使用/讨论这个概念}
```

### 5. 输出

直接输出讲解内容到终端（不写入文件）。

末尾提示：
```
---
想深入了解？
  "更详细"         切换到 detailed 模式重新讲解
  "举个例子"       用具体例子说明
  /br-search "{概念}" 搜索相关论文
```

## Output

- 终端输出：结构化讲解
- 无文件写入（讲解是即时操作）

## Error Handling

- $ARGUMENTS 为空 → 提示输入要讲解的概念
- 概念过于宽泛 → 询问用户想了解哪个方面
- config 不存在 → 使用默认偏好，提示运行 /br-init

ARGUMENTS: $ARGUMENTS
