# 本科专业第二批扩展核验

核验日期：2026-09-12。范围：原24项基础上增加6校各2项，完成12校36项；96校/22国家地区及QS2027原始排名规则不变。

## 新增范围与事实边界

- Imperial：Computing BEng、Mechanical Engineering MEng。后者是本科入口四年本硕连读；2027国际费明确Not set，£45,500仅2026/27参考。TMUA、ESAT及中国大陆/港澳考场日期来自UAT-UK当期页。就业比例为院系范围，标2023/24届与2026发布，不冒称单一课程或大陆生比例。
- UCL：Computer Science BSc、Economics BSc (Econ)。2027分别TARA、TMUA；国际年费£48,600、£40,800。China资格在两门2027课程页实际使用Chrome选择后读取：认可中国大学两年本科、加权90%、相关科目；不解释为高考直录或插班。Global Undergraduate Scholarship仍按2026/27已截止批次展示。语言依据及统计样本缺口在条目内保留。
- HKU、CUHK：计算机与经济方向；逐项区分高考招生大类、学位及入学后分流。2026大陆招生章程、2026/27学费与已取得的2027国际课程申请安排分开记录，不移植年份或申请类别。
- Melbourne：BSc内Computing and Software Systems主修，BCom内Economics主修。实际Chrome逐页选择International/2027及IB、A-level读取条件，费用页单独切换国际生，避免国内补贴学费。2027首年所属学位区间分别A$55,556–65,344、A$56,451–62,464，不能当作主修固定价。高考不直录；IB31/34、A-level BBB/ABB均为参考且须先修。国际本科奖学金国家清单已实读，不含中国。
- Sydney：BAC内Computer Science主修、2027新版BCom。2027国际招生指南p.60/62/68–71提供高考80%/85%、IB34/38、首年A$63,600/59,100等；两门课程实际Chrome选择International/2027后再次确认：BAC A$63,600、4年、CRICOS093855E；BCom A$59,100、3年、CRICOS012849G，使用新版course URL `bachelor-of-commerce0.html`。BAC2027培养计划明确处于复核，ACS2027认证未取得完成证明。

完整官方链接、适用口径和每一事实的引用位于对应 `data/catalog/*.json`；生成网页与索引同源。此次仅记录当前可核事实，不因条目数量要求填补无证据数字。

## 现有项目补证

NUS电气工程、NTU电气电子工程、NTU经济学补入MOE data.gov.sg官方2024届统计，2025仍待核。源数据字段精确匹配year/university/degree，读取gross median而非basic median或25百分位。选中行保存在 `program-batch2-ges2024-evidence.json`。

官方数据集：<https://data.gov.sg/datasets/d_3c55210de27fcccda2ed0c63fdd2b352/view>。
官方API：<https://data.gov.sg/api/action/datastore_search?resource_id=d_3c55210de27fcccda2ed0c63fdd2b352&limit=10000>。
本轮完整1550条返回数据范围2013–2024，页面更新时间不能当成毕业年份。原始响应SHA256：`aa68aa6e5a52f531d4fd12d4bd98bbe08a6c33bf3bad2dcbc37fdcef03a8882d`。

| 专业 | 2024全职长期就业率 | 经常性税前月薪中位 | 原始_id |
| --- | ---: | ---: | ---: |
| NUS Electrical Engineering | 86.0% | S$5,000 | 1424 |
| NTU Electrical and Electronic Engineering | 76.1% | S$4,800 | 1454 |
| NTU Economics | 79.4% | S$4,325 | 1463 |

调查分母、全职定义、工资组别和缺少国际生/大陆生样本均在详情保留。谢菲尔德2027/28 Overseas费用查询UI本轮只返回牙科1行，仍未取得4目标项目准确报价；不推断所有官方渠道均未公布，也不填校级区间为专业价格。NTU无TG学科分类亦未擅自补全。

## 验收记录

内容交叉复核：UK关键2027考试、费用、截止日期及UCL China动态资格已由第二人复核，未发现实质错误；AU主修/资格/申请日期独立复核通过，并补齐悉尼奖学金续领条件。

浏览器初检：Chrome中实际查看墨尔本经济学主修页与费用章节，正文无横向溢出，依据链接准确跳转来源记录；通过分享URL恢复澳洲/墨尔本2项筛选，再点英国卡片自动清空不兼容学校并显示英国12项。待HK集成后记录最终结构、搜索和部署检查。


最终本地验收（2026-09-12）：

- 36个项目、12所覆盖大学、627条事实、356个项目内来源记录（169个唯一官方URL）。计算机12、工程8、经济10、商科6；英国12、澳大利亚12、新加坡8、中国香港4。
- `render_catalog.py --check`：源数据、生成页面和索引一致，QS102条原始记录/96校选择及哈希检查通过。
- 来源登记检查、7项预算/目录测试、2项版本资产测试、MkDocs严格构建通过。
- 全站166个HTML页、36,085个内部引用与1,335项搜索索引验证通过；实际搜索引擎通过24组中英查询及无结果查询，含6所新增学校各一项专业查询。
- Chrome完成香港卡片大学5项/专业4项联动，再点取消恢复36项，香港+计算机+CUHK交叉筛选得到唯一正确项目。墨尔本经济、Imperial机械、CUHK计算机详情实际截图检查无横向溢出；章节和依据锚点可用。
- HK独立复核确认旧文件名高考PDF实际有2026日期/费用；CUHK最低控制线、奖学金630/600及前0.5%逻辑、HKU2027国际申请日期与来源一致。未用文件名代替文内年份。
- GitHub Pages部署及新12条页面/版本资产的线上核验在提交后执行；机器回执保存在本地`scratch/program-batch2-deployment.json`。
