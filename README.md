# 海外大学留学手册 · 大学与专业查询

面向中国大陆学生，按 **国家 → 大学 → 专业** 查询本科入学条件、国际生学费和毕业生情况。

**[打开大学与专业目录 →](https://garylauchina.github.io/study-abroad-handbook/)**

## 当前收录

大学清单采用 **QS World University Rankings 2027 官方名次 ≤ 100**，保留并列及官方更正，剔除中国大陆 6 所后收录 **22 个国家和地区、96 所大学**。每校有中英文名称、所在地、QS 2027 名次、排名来源与官网链接。

首页可切换大学清单与已收录专业；国家／地区卡片直接筛选下方结果，再次点击取消。支持中文、英文与常用简称查询，大学默认按 QS 原始名次排序。

详细专业资料覆盖英国、澳大利亚、新加坡和中国香港 12 所大学的 36 个本科项目。其余学校标注“专业详情待收录”。资料核验：2026-09-12。本批新增帝国理工、UCL、香港大学、香港中文大学、墨尔本大学和悉尼大学，每校 2 个项目；原有 6 校各 4 个项目继续保留。详情页含校区、授课语言、入学条件、申请渠道与截止日期、学费与资助、毕业生情况。入学年、学费年、申请批次、毕业调查年分别记录；缺少的资料不推算。QS 名次规则和覆盖范围见[数据说明](docs/about/catalog-data.md)。

[预算计算器](https://garylauchina.github.io/study-abroad-handbook/tools/budget/)、[申请准备](docs/start/undergraduate.md)、[英国申请指南](docs/destinations/uk.md)和[比较模板](docs/tools/compare.md)在网站“申请工具”中。

## 数据与本地维护

使用 Python 3.12、Node.js 24、Material for MkDocs。大学与专业数据源为 `data/catalog/*.json`，QS 来源及原始名次提取为 `data/rankings/qs-2027.json`，每条专业说明引用同一记录内的官方来源。生成器产出首页、国家页、大学页、专业页和小型筛选索引。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/render_catalog.py
.venv/bin/python scripts/render_catalog.py --check
.venv/bin/python scripts/render_sources.py --check
node --test scripts/budget.test.mjs scripts/catalog.test.mjs
.venv/bin/python scripts/version_assets_test.py
.venv/bin/mkdocs build --strict
.venv/bin/python scripts/validate_site.py site
node scripts/validate_search.mjs site
.venv/bin/mkdocs serve
```

构建时自动为自定义 CSS、JavaScript 和目录数据生成内容哈希文件名，页面引用同一批资源，避免更新后浏览器缓存旧样式；同时保留上一提交的公共资源，供发布期间缓存的旧 HTML 继续加载。CI 获取两层 Git 历史以完成该过渡。

修改目录请先更新结构化记录，再运行生成器；生成页中的注释指出对应维护入口。英国申请指南的来源另保存在 `.maintenance/uk-sources.json`，通过 `scripts/render_sources.py` 生成来源页。生成与结构检查不会自动复核官方事实。

提交 `main` 后，GitHub Actions 检查数据、生成结果、预算、筛选、构建、站内链接与全文搜索，通过后发布 GitHub Pages；Pull Request 只检查。

[执行方案](PROJECT_PLAN.md) · [收录与更新](docs/about/roadmap.md) · [提交纠错](https://github.com/Garylauchina/study-abroad-handbook/issues)

公开仓库仅保存公共资料和编辑内容，不包含个人成绩单、护照或账户凭据。虚构预算案例保留虚构标识，毕业收入不作为基础预算的确定资金来源。
