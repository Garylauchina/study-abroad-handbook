# 海外大学留学手册 · 大学与专业查询

面向中国大陆学生，按 **国家 → 大学 → 专业** 查询本科入学条件、国际生学费和毕业生情况。

**[打开大学与专业目录 →](https://garylauchina.github.io/study-abroad-handbook/)**

## 当前收录

大学清单采用 **QS World University Rankings 2027 官方名次 ≤ 100**，保留并列及官方更正，剔除中国大陆 6 所后收录 **22 个国家和地区、96 所大学**。每校有中英文名称、所在地、QS 2027 名次、排名来源与官网链接。

首页可切换大学清单与已收录专业；国家／地区卡片直接筛选下方结果，再次点击取消。支持中文、英文与常用简称查询，大学默认按 QS 原始名次排序。

96 所大学均已收录官方本科目录，范围扩展至医学、法律、人文、艺术等全部学科。各校页面注明目录范围、完整性证据及尚待核查的分支。条目包括独立学位、主修、联合培养、第二学位和校区／学制变体，不能将总条目数解释为独立招生学位数。

原有 36 条详细专业资料保留；新批次逐步补充课程内容、申请资格、费用和毕业去向，并在页面区分“含详细资料”“部分专业资料已核实”“仅补学校共用资料”和“目录已核对”。**全量详情尚在收录，目录覆盖不等于每项入学条件、学费与毕业信息已经核实。** 最新数量以网站筛选区和学校页为准，核验日期为 2026-09-12。

[预算计算器](https://garylauchina.github.io/study-abroad-handbook/tools/budget/)、[申请准备](docs/start/undergraduate.md)、[英国申请指南](docs/destinations/uk.md)和[比较模板](docs/tools/compare.md)在网站“申请工具”中。

## 数据与本地维护

使用 Python 3.12、Node.js 24、Material for MkDocs。原有详细资料及学校身份为 `data/catalog/*.json`；全校专业目录为 `data/program-index/*.json`，新核实的学校规则与专业事实为 `data/program-research/*.json`；QS 来源及原始名次提取为 `data/rankings/qs-2027.json`，每条专业说明引用同一记录内的官方来源。生成器产出首页、国家页、大学页、专业页和分页筛选索引。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/render_catalog.py
.venv/bin/python scripts/render_catalog.py --check
.venv/bin/python scripts/render_sources.py --check
.venv/bin/python scripts/catalog_research_test.py
node --test scripts/budget.test.mjs scripts/catalog.test.mjs
.venv/bin/python scripts/version_assets_test.py
.venv/bin/mkdocs build --strict
.venv/bin/python scripts/validate_site.py site
node scripts/validate_search.mjs site
.venv/bin/mkdocs serve
```

构建时自动为自定义 CSS、JavaScript 和目录数据生成内容哈希文件名，页面引用同一批资源，避免更新后浏览器缓存旧样式；同时保留上一提交的公共资源，供发布期间缓存的旧 HTML 继续加载。CI 获取两层 Git 历史以完成该过渡。

修改目录请先更新结构化记录，再运行生成器；研究批次可通过 `scripts/import_catalog_research.py <批次目录>` 验证原文 SHA-256 后导入，原文保留在被忽略的 `scratch/`，公开来源记录保存在 `.maintenance/research-evidence/`。生成页中的注释指出对应维护入口。英国申请指南的来源另保存在 `.maintenance/uk-sources.json`，通过 `scripts/render_sources.py` 生成来源页。生成与结构检查不会自动复核官方事实。

提交 `main` 后，GitHub Actions 检查数据、生成结果、预算、筛选、构建、站内链接与全文搜索，通过后发布 GitHub Pages；Pull Request 只检查。

[执行方案](PROJECT_PLAN.md) · [收录与更新](docs/about/roadmap.md) · [提交纠错](https://github.com/Garylauchina/study-abroad-handbook/issues)

公开仓库仅保存公共资料和编辑内容，不包含个人成绩单、护照或账户凭据。虚构预算案例保留虚构标识，毕业收入不作为基础预算的确定资金来源。
