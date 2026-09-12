# 本科专业第 1 批扩展与验收

核验日：2026-09-12。范围为已授权的六校本科首批扩展；保留原 12 项，新增 12 项，共 24 项，每校 4 项。学校清单仍为 QS 2027 的 96 校、22 个国家和地区。

## 收录结果

| 学校 | 新增课程 |
| --- | --- |
| Sheffield | Mechanical Engineering BEng；Electrical and Electronic Engineering BEng |
| Manchester | BEng Mechanical Engineering；BSc Economics |
| Monash | Engineering (Honours) 内 Mechanical engineering 方向；Bachelor of Economics |
| UNSW | Engineering (Honours) (Mechanical Engineering)；Bachelor of Economics |
| NUS | Electrical Engineering；Economics（CHS Humanities and Sciences 共同入口） |
| NTU | Electrical and Electronic Engineering；Economics |

学科合计：计算机 6、商科 5、工程 7、经济 6。全部补充校区、授课语言、申请安排与资助条件；详情页增加申请章节导航。结构化库有 405 条有来源事实、237 个课程内来源记录，合并为 97 个不同 URL。来源、适用年度与核验日保存在 data/catalog/*.json。

## 独立复核和已修正项目

- 三地区研究分别完成，并交叉审查关键录取与奖学金条件；主任务复核全部新增课程文字及旧课程补充项。
- Chrome 实读 Monash B2031 与 B2001 国际生视图，确认两项 2027 学费均为 A$59,140/48 学分。B2031 高考 70%、IB 31、GCE A-level 校方积分 11、IELTS 6.5/单项 6.0；高考数学 60% 另由 2027 官方高考表支持。B2001 11 月入学不提供精算方向。未使用默认国内生视图的 A$38,740。
- NUS 新生收费表第 2 页经图像复核：其他国际生含 GST，EE 有 TG/无 TG 为 S$21,400/39,700；Humanities and Sciences 为 S$21,400/36,650。TG 的三年服务义务与奖学金资格保留。
- UCAS 2027 普通本科平等考虑截止为 2027-01-13 英国 18:00；不称其为绝对最终截止。
- Sheffield 专用 2027 奖学金条款优先于课程页残留的 2026 广告：£2,500/年、2027-06-02 英国 16:00 前 firm 或 insurance、续领成绩及学分条件；明确外部资助禁止叠加及须全部偿还贷款的例外。
- Manchester 2027 课程学费尚未确定；独立复核机械 2026/27 £35,700、经济 £33,100，仅作上一年度参考。补充所修 Science A-level 实验考核要求及机械课程 GCSE 基础。Global Futures 按居住地区判断，不能按国籍一概排除。
- UNSW 非 ISA 本科 T1 2027 的 2026-09-24 申请轮计划 11-19 发 offer。Scientia 通常要求 10-30 前已有合资格 offer，未将两者写成可直接衔接；保留高中最终成绩待定及 UAC 的原页例外。
- NUS 下一轮国际资格及 IB 申请为 2026-12-16 至 2027-02-17，与本页 2026/27 课程/费用分开。NTU 2027 起凭实际高考成绩筛选面试、放榜三日内补交、七月面试；不继续套用高一高二成绩决定面试的旧流程。
- NTU 奖学金须在对应资格的入学截止前另交表，不能等 offer；补充短文与教师评价时限。

## 保留的事实边界

- 新增课程未取得充分可核验的专业就业率或薪资统计，提供官方职业方向及明确缺口；不以全校、院系或其他学位结果填补。NUS 社会科学汇总不等于 Economics 单专业。
- NTU 无 TG 实验/非实验收费分类没有取得 CS、EEE、Economics 的明确课程对应，未凭学科常识定价。NTU 2027 完整申请期、部分学校 2027 项目学费等仍标明未取得。
- Sheffield 授课语言采用合作大学 UOW 的官方院校资料；UNSW 明确语言声明来自官方 2021 交换生资料。页面说明资料层级/年份，没有沿用其旧申请、费用规则。
- 入学年、费用年、下一轮申请日及毕业调查届次分别标注。所有达到最低门槛、职业方向、奖学金摘要均不当作录取、就业或获奖保证。

## 验收

- 来源表与目录生成一致性检查通过；405 条事实的引用闭合、HTTPS、来源核验日通过。
- 7 项预算/筛选/大学目录测试通过；2 项内容哈希与前版资源保留测试通过。
- MkDocs strict 构建通过；全站 HTML、内部链接/章节、实际搜索 worker 通过。新增六校课程均有真实搜索查询覆盖。
- Chrome 实测：澳洲 8 项 → 工程 2 项；英国工程 3 项 → Sheffield 2 项；切到新加坡自动清除不兼容学校，工程 2 项、经济 2 项；清除恢复 24 项。大学模式新加坡仍为 2 校；NUS 专业模式为 4 项。
- Chrome 查看首页、Monash Economics 详情和申请章节，布局无横向溢出、章节跳转正常；NUS Economics 的共同入口与费用年度显示正确。本批没有更改响应式样式，也没有另做移动端尺寸测试。

发布沿用 GitHub Pages 工作流；CI 会在发布提交上重新执行校验，随后对公开站点及带哈希目录资源作部署复核。
