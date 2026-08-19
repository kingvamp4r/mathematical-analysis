# Mathematical Analysis Notes

个人数学分析学习笔记，包含可独立阅读的 HTML 讲义和由其生成的 LaTeX 版本。

## 内容

- `lessons/`：按课程章节组织的 HTML 笔记。
- `latex/`：可使用 XeLaTeX 编译的完整笔记工程。
- `tools/html_to_latex.py`：将 HTML 内容同步到 LaTeX 分节文件。
- `output/pdf/数学分析笔记.pdf`：已编译的 PDF 版本。
- `reference/`：复习路线、速查表和错题整理。

## 更新与编译

修改 HTML 后，在仓库根目录运行：

```sh
python3 tools/html_to_latex.py
```

随后进入 `latex` 目录编译：

```sh
latexmk -xelatex -interaction=nonstopmode main.tex
```
