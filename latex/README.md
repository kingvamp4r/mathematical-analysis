# 数学分析 LaTeX 笔记

本目录是由项目现有 `lessons/*.html` 内容生成的可维护 LaTeX 工程。

## 编译

在 `latex` 目录运行：

```sh
latexmk -xelatex -interaction=nonstopmode main.tex
```

生成文件为 `main.pdf`。

## 从 HTML 更新

在项目根目录运行：

```sh
python3 tools/html_to_latex.py
```

该命令会重建 `latex/chapters/*.tex`。请在 HTML 中修改正文；`main.tex` 和 `preamble.tex` 分别负责章节编排与全局样式，不会被转换脚本覆盖。
