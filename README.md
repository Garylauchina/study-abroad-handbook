# 海外大学留学手册 · 大学与专业查询

面向中国大陆学生，按 **国家 → 大学 → 专业** 查询本科入学条件、国际生学费和毕业生情况。

**[打开大学与专业目录 →](https://garylauchina.github.io/study-abroad-handbook/)**

## 当前收录

英国、澳大利亚、新加坡，共 6 所大学、12 个本科专业：

- 英国：谢菲尔德大学、曼彻斯特大学。
- 澳大利亚：蒙纳士大学、新南威尔士大学。
- 新加坡：新加坡国立大学、南洋理工大学。

首批聚焦计算机与商科相关专业。首页支持中文／英文名称搜索，以及国家、大学、专业方向的联合筛选。国家页和大学页也能直接逐级浏览，每个专业有独立网址和官方依据。

资料核验：2026-09-12。入学年度、学费年度和毕业调查年份分别记录；精确费用或毕业数据不足时会标出缺口。该目录尚未覆盖全部国家、院校与专业。详见[数据说明](docs/about/catalog-data.md)。

[预算计算器](https://garylauchina.github.io/study-abroad-handbook/tools/budget/)、[申请准备](docs/start/undergraduate.md)、[英国申请指南](docs/destinations/uk.md)和[比较模板](docs/tools/compare.md)在网站“申请工具”中。

## 数据与本地维护

使用 Python 3.12、Node.js 24、Material for MkDocs。数据源为 `data/catalog/*.json`，每条专业说明引用同一记录内的官方来源。生成器产出首页、国家页、大学页、专业页和小型筛选索引。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/render_catalog.py
.venv/bin/python scripts/render_catalog.py --check
.venv/bin/python scripts/render_sources.py --check
node --test scripts/budget.test.mjs scripts/catalog.test.mjs
.venv/bin/mkdocs build --strict
.venv/bin/python scripts/validate_site.py site
node scripts/validate_search.mjs site
.venv/bin/mkdocs serve
```

修改目录请先更新结构化记录，再运行生成器；生成页中的注释指出对应维护入口。英国申请指南的来源另保存在 `.maintenance/uk-sources.json`，通过 `scripts/render_sources.py` 生成来源页。生成与结构检查不会自动复核官方事实。

提交 `main` 后，GitHub Actions 检查数据、生成结果、预算、筛选、构建、站内链接与全文搜索，通过后发布 GitHub Pages；Pull Request 只检查。

[执行方案](PROJECT_PLAN.md) · [收录与更新](docs/about/roadmap.md) · [提交纠错](https://github.com/Garylauchina/study-abroad-handbook/issues)

公开仓库仅保存公共资料和编辑内容，不包含个人成绩单、护照或账户凭据。虚构预算案例保留虚构标识，毕业收入不作为基础预算的确定资金来源。
