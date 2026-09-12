# 全量本科收录工作检查点

用户已明确授权：96校全部本科专业逐项收录，覆盖医学、法律、人文、艺术等全部学科；同一GitHub Pages发布授权持续有效。名称清单不代表全量详情完成。

## 已发布的首批

首批提交4e239f0已推送main；Actions34695695982 build/deploy均success。线上资源catalog.1ccedb57e4f2.mjs与16,410条目一致，Chrome线上MIT55条分页正常。

## 第二批已通过本地验收，准备发布

- 96校、22国家地区、16,488专业条目；36原详细记录保留；8,119条含部分专业事实，5,448条仅补学校共用规则，2,885条仅目录。
- 73校有研究资料：英国16、澳洲9、欧洲13、瑞士3、美国26、加拿大2（UBC/Alberta）、亚洲4（HKUST/NTU/Malaya/KAIST）。
- Columbia新增83条College/GS目录身份，保留原有稳定ID；研究182条。CMU同名同URL但BA/BS必须按inventory_id和学位区分。
- 排除5条错误本科条目并保留原URL更正页：Lund高年级工程完成段、Trinity Science四个入口总览、Alberta证书及两条商科minor。
- UBC192专业、Alberta348专业已补；UBC120份明确类别学费；Alberta292个精确项目代码的国际费用模型，均明确2026参考，不冒充2027定价。
- Alberta DDS国际生可以竞争最多3个非阿尔伯塔席位；GPA3.3只用于资格，不作排名。医学/放射治疗不套普通国际入学。DDS学院未标年度费用与Fall2026计算器冲突明确保留。
- 卡片展示具体学位，区分普通/荣誉/第二学位；有项目2027日期依据的Alberta条目标2027。
- Strict最终构建222.65秒；16,623 HTML、803,479内部引用及18,299搜索条目验收通过；逻辑站点442.3MB。
- 8个Node测试、4个研究适用性测试、2个资源版本测试通过；生成一致性、来源登记及真实中英搜索worker通过。
- Chrome桌面Alberta348筛选、普通/荣誉卡片、DDS具体资格/费用页，以及390px窄屏布局已目视检查；资源catalog.349c76df1340.mjs。
- 公开来源原文哈希已核对；Columbia身份来源的本机绝对路径已从公开文件移除，原证据留在本地忽略目录。首次发现的5条更正页外链拼接错误已修复并经全站链接复验。

## 下一增量研究

- uk_sample：欧洲14校全部草稿已完成，UCD151归档中11个BSc仅minor须排除，140有效；修正清单保存旧ID/原文SHA，尚未导入。正研究法国4校。
- research_au_catalog：香港5校；最新稳定HKUST47/HKU135/CUHK84，后两校尚未导入；CityU/PolyU进行中。随后接力Toronto316及DDS/JD/PharmD目录缺口，root已将来源和边界写入scratch/full-catalog/root/toronto-handoff.md。
- research_uk_catalog：亚洲12校（香港外）；NTU/Malaya/KAIST已导入，其余韩日台及NUS进行中。KAIST2027新增AI学院4方向待补目录。
- root：Toronto199唯一页面中198已取、44段中文摘要已写并交接；改做McGill392、Auckland189、UBA101、KFUPM54及整合发布。

## 未完成的验收范围

1. 所有16,488条目的全字段实质收录仍未完成，继续补学校和专业条件、准确费用、申请安排和毕业证据。
2. 目录口径目前65校完整、31校部分；继续逐院系闭合，不能把该口径叫全量详情完成。
3. 费用必须区分年度、年/学分/整个项目及申请者身份；职业方向不等于实际毕业去向或就业率。尚未核实不代表未公布。
4. 已知展示待补：Alberta DDS正文已证4年，顶部学制仍待同步；其他明确学制与语言逐项补充，不由费用模型推断完整先修年限。

## 操作边界

工作分支codex/full-undergraduate-catalog；首批线上基准4e239f089ad274f5aa1735926f665afed54f78ae。
scratch忽略且不提交；data/.maintenance只保存可公开事实、来源链接和哈希。git status用--untracked-files=no或计数；提交使用quiet避免数万生成文件输出。发布后继续已授权全量任务。
