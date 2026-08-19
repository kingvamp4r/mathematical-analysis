# Course State: 数学分析讲义生成入口

这个文件是后续生成讲义时的优先入口。除非用户明确要求检查全工作区，否则不要先全量扫描文件；先读本文件，再只读当前章节需要的上一节 HTML、教材页截图或 PDF。

## 生成契约

- 一节教材对应一个 `lessons/*.html` 文件。
- HTML 必须自足：默认用户不翻原教材。
- 公式统一用 LaTeX/MathJax 渲染。
- 每节至少包含：本节主线、重要定义、重要定理、证明思路、考试用法、即时练习、完整课后题。
- 题目题面要完整保留；提示只给入口，不替代学生独立做题。
- 偏导数优先写成 `\frac{\partial f}{\partial x}`、`\frac{\partial^2 f}{\partial x\partial y}`，少用 `f_x,f_y` 作主记号。
- 用户做题后，先批改已做部分；不要默认展开全部答案。

## 当前课程位置

当前打开并完成到：

- `lessons/0009-3-positive-series.html`：第九章 §3 正项级数

已生成待学习：

- `lessons/0009-4-arbitrary-series.html`：第九章 §4 任意项级数
- `lessons/0009-5-infinite-products.html`：第九章 §5 无穷乘积

下一节按顺序应从：

- 第十章 §1 函数项级数的一致收敛性（建议先学完 §4、§5 后再推进）
- 建议文件名：`lessons/0010-1-uniform-convergence.html`

## 已有讲义

### 第七章 定积分

- `lessons/0007-2-definite-integral-properties.html`
- `lessons/0007-3-fundamental-theorem-calculus.html`
- `lessons/0007-4-geometric-applications-definite-integrals.html`

### 第八章 反常积分

- `lessons/0008-1-improper-integrals-concept-computation.html`
- `lessons/0008-2-improper-integral-tests.html`

### 第九章 数项级数

- `lessons/0009-1-numerical-series-convergence.html`
- `lessons/0009-2-upper-lower-limits.html`
- `lessons/0009-3-positive-series.html`
- `lessons/0009-4-arbitrary-series.html`（已生成，待学习）
- `lessons/0009-5-infinite-products.html`（已生成，待学习）

### 第十一章 Euclid 空间上的极限和连续

- `lessons/0011-1-euclidean-space-basic-theorems.html`
- `lessons/0011-2-multivariable-continuous-functions.html`
- `lessons/0011-3-continuous-function-properties.html`

### 第十二章 多元函数微分学

- `lessons/0012-1-partial-derivatives-total-differential.html`
- `lessons/0012-2-chain-rule-multivariable.html`
- `lessons/0012-3-mean-value-taylor.html`
- `lessons/0012-4-implicit-functions.html`

### 早期点集入门

- `lessons/0001-open-closed-by-balls.html`
- `lessons/0002-cluster-closure-boundary.html`

## 教材与来源

教材 PDF：

- 上册：`数学分析 陈纪修 第三版 上 (陈纪修,于崇华,金路) (z-library.sk, 1lib.sk, z-lib.sk).pdf`
- 下册：`数学分析 陈纪修 第三版 下 (陈纪修,于崇华,金路) (z-library.sk, 1lib.sk, z-lib.sk).pdf`

已渲染/截取过的第九章相关材料：

- `tmp/lower-ch9/pages/`
- `tmp/lower-ch9-s2/pages/`
- `tmp/lower-ch9-s3/`
- `tmp/upper-ch9/pages/`
- `tmp/upper-ch9-calib/`

第九章 §3 正项级数已使用 `tmp/lower-ch9-s3/pdf-034.png` 至 `pdf-045.png`；`pdf-046.png` 起进入下一节内容。

## 推荐工作流

1. 读本文件确认当前进度和下一节文件名。
2. 读同章上一节 HTML 作为样式模板。
3. 只打开下一节对应教材截图/PDF页，不全量扫描工作区。
4. 生成或修改 HTML。
5. 用 `rg` 定点检查标题、MathJax、定理编号、课后题数量。
6. 若用户要求打开浏览器，再用浏览器工具查看；否则给出文件路径。

## 避免的无效动作

- 不要每次先 `rg --files` 全量列工作区。
- 不要每次重新读取所有 `lessons/*.html`。
- 不要重新扫描所有教材页。
- 不要把旧的欧氏空间 `MISSION.md` 当作当前唯一课程范围；当前实际范围已扩展到第七、八、九、十一、十二章。
