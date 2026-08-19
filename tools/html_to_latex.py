#!/usr/bin/env python3
"""Convert the self-contained HTML lessons into chapter-ready LaTeX fragments.

The HTML remains the editable source of truth. Re-running this script refreshes
the generated files in latex/chapters without changing the source lessons.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from lxml import etree
from lxml import html as lxml_html


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "lessons"
OUTPUT_DIR = ROOT / "latex" / "chapters"

LESSONS = [
    "0001-open-closed-by-balls.html",
    "0002-cluster-closure-boundary.html",
    "0007-2-definite-integral-properties.html",
    "0007-3-fundamental-theorem-calculus.html",
    "0007-4-geometric-applications-definite-integrals.html",
    "0008-1-improper-integrals-concept-computation.html",
    "0008-2-improper-integral-tests.html",
    "0009-1-numerical-series-convergence.html",
    "0009-2-upper-lower-limits.html",
    "0009-3-positive-series.html",
    "0009-4-arbitrary-series.html",
    "0009-5-infinite-products.html",
    "0011-1-euclidean-space-basic-theorems.html",
    "0011-2-multivariable-continuous-functions.html",
    "0011-3-continuous-function-properties.html",
    "0012-1-partial-derivatives-total-differential.html",
    "0012-2-chain-rule-multivariable.html",
    "0012-3-mean-value-taylor.html",
    "0012-4-implicit-functions.html",
]

MATH_PATTERN = re.compile(r"(\\\[.*?\\\]|\\\(.*?\\\))", re.S)
PLACEHOLDER_PATTERN = re.compile(r"MATHPLACEHOLDER(\d+)END")


def protect_math(source: str) -> tuple[str, list[str]]:
    math_chunks: list[str] = []

    def replace(match: re.Match[str]) -> str:
        value = html.unescape(match.group(0))
        # MathJax accepts these aliases, while standard LaTeX does not.
        value = value.replace(r"\lt", "<").replace(r"\gt", ">")
        value = value.replace("≤", r"\le ").replace("≥", r"\ge ")
        value = normalize_chinese_in_math(value)
        math_chunks.append(value)
        return f"MATHPLACEHOLDER{len(math_chunks) - 1}END"

    return MATH_PATTERN.sub(replace, source), math_chunks


def normalize_chinese_in_math(value: str) -> str:
    """Wrap bare Chinese words in \text while preserving existing \text groups."""
    protected: list[str] = []

    def hold(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"TEXTGROUPPLACEHOLDER{len(protected) - 1}END"

    value = re.sub(r"\\text\{[^{}]*\}", hold, value)
    value = re.sub(r"[\u4e00-\u9fff]+", lambda match: rf"\text{{{match.group(0)}}}", value)
    for index, group in enumerate(protected):
        value = value.replace(f"TEXTGROUPPLACEHOLDER{index}END", group)
    return value


def latex_escape(value: str, math_chunks: list[str]) -> str:
    parts: list[str] = []
    cursor = 0
    for match in PLACEHOLDER_PATTERN.finditer(value):
        parts.append(escape_plain(value[cursor : match.start()]))
        parts.append(math_chunks[int(match.group(1))])
        cursor = match.end()
    parts.append(escape_plain(value[cursor:]))
    return "".join(parts)


def escape_plain(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "≤": r"\(\le\)",
        "≥": r"\(\ge\)",
    }
    return "".join(replacements.get(char, char) for char in value)


def text_content(node: etree._Element, math_chunks: list[str]) -> str:
    return latex_escape("".join(node.itertext()), math_chunks).strip()


class Converter:
    def __init__(self, math_chunks: list[str]) -> None:
        self.math_chunks = math_chunks

    def children(self, node: etree._Element) -> str:
        result = latex_escape(node.text or "", self.math_chunks)
        for child in node:
            result += self.convert(child)
            result += latex_escape(child.tail or "", self.math_chunks)
        return result

    def convert(self, node: etree._Element) -> str:
        tag = node.tag.lower() if isinstance(node.tag, str) else ""
        classes = set((node.get("class") or "").split())

        if tag in {"script", "style", "button"} or "choices" in classes or "feedback" in classes:
            return ""
        if tag in {"main", "header", "section", "thead", "tbody"}:
            return self.children(node)
        if tag == "h1":
            return ""
        if tag == "h2":
            return f"\n\\subsection*{{{text_content(node, self.math_chunks)}}}\n"
        if tag == "h3":
            return f"\n\\subsubsection*{{{text_content(node, self.math_chunks)}}}\n"
        if tag == "h4":
            return f"\n\\paragraph*{{{text_content(node, self.math_chunks)}}}\n"
        if tag == "p":
            body = self.children(node).strip()
            return f"\n{body}\n\n" if body else ""
        if tag == "br":
            return r"\\ "
        if tag in {"strong", "b"}:
            return f"\\textbf{{{self.children(node).strip()}}}"
        if tag in {"em", "i"}:
            return f"\\emph{{{self.children(node).strip()}}}"
        if tag == "a":
            label = self.children(node).strip()
            href = node.get("href", "")
            if href.startswith(("http://", "https://")):
                return f"\\href{{{href}}}{{{label}}}"
            return label
        if tag in {"ul", "ol"}:
            environment = "itemize" if tag == "ul" else "enumerate"
            return f"\n\\begin{{{environment}}}\n{self.children(node)}\\end{{{environment}}}\n"
        if tag == "li":
            return f"\\item {self.children(node).strip()}\n"
        if tag == "table":
            return self.convert_table(node)
        if tag == "details":
            content = "".join(
                self.convert(child) + latex_escape(child.tail or "", self.math_chunks)
                for child in node
                if child.tag.lower() != "summary"
            ).strip()
            return f"\n\\begin{{hintbox}}\n{content}\n\\end{{hintbox}}\n"
        if tag == "summary":
            return ""
        if tag == "div":
            if "quiz-card" in classes:
                question_nodes = node.xpath("./div[contains(concat(' ', normalize-space(@class), ' '), ' question ')]")
                question = self.children(question_nodes[0]).strip() if question_nodes else ""
                answer = latex_escape(node.get("data-answer", ""), self.math_chunks)
                explain = latex_escape(node.get("data-explain", ""), self.math_chunks)
                solution = f"\\textbf{{答案：}}{answer}"
                if explain:
                    solution += f"。{explain}"
                return (
                    "\n\\begin{quickcheck}\n"
                    f"{question}\n\n\\tcblower\n{solution}\n"
                    "\\end{quickcheck}\n"
                )
            body = self.children(node).strip()
            if not body:
                return ""
            if "note" in classes:
                return f"\n\\begin{{notebox}}\n{body}\n\\end{{notebox}}\n"
            if "exercise" in classes:
                return f"\n\\begin{{exercisebox}}\n{body}\n\\end{{exercisebox}}\n"
            if "exercise-title" in classes:
                return f"\\textbf{{{body}}}\n"
            if "tag" in classes:
                return f"\\badge{{{body}}}"
            if classes.intersection({"box", "card", "step"}):
                return f"\n\\begin{{conceptbox}}\n{body}\n\\end{{conceptbox}}\n"
            return f"\n{body}\n"
        if tag == "span":
            body = self.children(node).strip()
            if "tag" in classes:
                return f"\\badge{{{body}}}"
            return body
        return self.children(node)

    def convert_table(self, node: etree._Element) -> str:
        rows = node.xpath(".//tr")
        if not rows:
            return ""
        column_count = max(len(row.xpath("./th|./td")) for row in rows)
        if column_count == 3:
            columns = (
                ">{\\raggedright\\arraybackslash}p{0.18\\linewidth}|"
                ">{\\raggedright\\arraybackslash}p{0.42\\linewidth}|"
                ">{\\raggedright\\arraybackslash}X"
            )
        else:
            columns = "|".join([">{\\raggedright\\arraybackslash}X"] * column_count)
        output = [f"\n\\begin{{center}}\n\\small\n\\begin{{tabularx}}{{\\linewidth}}{{|{columns}|}}\n\\hline\n"]
        for row in rows:
            cells = row.xpath("./th|./td")
            rendered: list[str] = []
            for cell in cells:
                content = self.children(cell).strip()
                content = re.sub(r"\\\[\s*", r"\\(\\displaystyle ", content)
                content = re.sub(r"\s*\\\]", r"\\)", content)
                if cell.tag.lower() == "th":
                    content = f"\\textbf{{{content}}}"
                rendered.append(content)
            rendered.extend([""] * (column_count - len(rendered)))
            output.append(" & ".join(rendered) + r" \\ \hline" + "\n")
        output.append("\\end{tabularx}\n\\end{center}\n")
        return "".join(output)


def convert_lesson(path: Path) -> str:
    source, math_chunks = protect_math(path.read_text(encoding="utf-8"))
    document = lxml_html.fromstring(source)
    main = document.xpath("//main")[0]
    title_nodes = main.xpath("./header/h1")
    title = text_content(title_nodes[0], math_chunks) if title_nodes else path.stem
    converter = Converter(math_chunks)

    content = ""
    for child in main:
        if child.tag.lower() == "header":
            for header_child in child:
                if header_child.tag.lower() not in {"h1"} and "kicker" not in (header_child.get("class") or ""):
                    content += converter.convert(header_child)
        else:
            content += converter.convert(child)

    content = re.sub(r"[ \t]+\n", "\n", content)
    content = re.sub(r"\n{3,}", "\n\n", content).strip()
    source_name = latex_escape(path.name, math_chunks)
    return (
        f"% Generated from lessons/{source_name}; edit the HTML source, then rerun the converter.\n"
        f"\\section{{{title}}}\n"
        f"\\lessonmark{{{title}}}\n\n"
        f"{content}\n"
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename in LESSONS:
        source = SOURCE_DIR / filename
        output = OUTPUT_DIR / f"{source.stem}.tex"
        output.write_text(convert_lesson(source), encoding="utf-8")
        print(f"generated {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
