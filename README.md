# 海外大学留学手册

面向中国大陆学生及家长，从自身条件、专业目标和家庭预算出发，逐步完成大学选择、申请准备和入学安排。

**[阅读网站 →](https://garylauchina.github.io/study-abroad-handbook/)**

## 当前内容

首批样章围绕大陆普高学生的本科申请展开：

- [本科申请从这里开始](docs/start/undergraduate.md)
- [英国本科样章：Sheffield 与 Manchester 计算机本科实例](docs/destinations/uk.md)
- [全程预算计算器](https://garylauchina.github.io/study-abroad-handbook/tools/budget/)与[填写指南](docs/tools/budget-guide.md)
- [大学项目比较模板](docs/tools/compare.md)、个人条件与付款日历文本模板
- [两个虚构家庭的预算演练](docs/start/cases.md)
- [来源与核验范围](docs/about/sources.md)

当前仅覆盖一个目的地样章，部分 2027 费用及资格细则存在明确缺口。其他目的地、硕士、博士和完整个案审查尚未展开。核验日期统一在网站首页和来源台账展示；网站构建与链接检查不替代政策核验。

[项目推进方案](PROJECT_PLAN.md) · [后续路线](docs/about/roadmap.md) · [提交纠错或建议](https://github.com/Garylauchina/study-abroad-handbook/issues)

## 本地维护

使用 Python 3.12 和 Node.js 24。内容为 Markdown，网站通过 Material for MkDocs 生成。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/render_sources.py --check
node --test scripts/budget.test.mjs
.venv/bin/mkdocs build --strict
.venv/bin/python scripts/validate_site.py site
node scripts/validate_search.mjs site
.venv/bin/mkdocs serve
```

修改 `.maintenance/uk-sources.json` 后，先运行 `python scripts/render_sources.py` 更新公开来源页；这一步只生成记录，不会自动核验网页事实。直接依赖见 `requirements.txt`，完整版本锁定见 `requirements.lock.txt`。

提交到 `main` 后，GitHub Actions 执行来源字段检查、预算测试、严格构建、站内链接检查和中英文实际搜索测试，通过后发布到 GitHub Pages。Pull Request 只检查，不部署。

## 内容与隐私

具体规则引用对应年度的官方来源；区分已核实事实、编辑建议、估算和虚构演练。基础预算不依赖尚未落实的奖学金、兼职或毕业收入。

公开仓库仅放公共资料和编辑内容。请勿在文件或 Issue 中提交护照、成绩单、账户凭据及其他个人申请材料。
