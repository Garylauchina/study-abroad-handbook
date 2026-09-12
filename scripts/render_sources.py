"""Render the public evidence register from reviewed source records; no live policy check."""
from collections import Counter
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
STATUS = {"verified": "已核实", "partial": "部分待核实", "gap": "核心证据缺口"}


def render():
    records = json.loads((ROOT / ".maintenance/uk-sources.json").read_text())
    seen = set()
    required = {"id", "claim", "url", "title", "applicant_scope", "intake_year", "checked_at", "status", "location", "limitations", "page"}
    for record in records:
        assert required <= record.keys(), record.get("id")
        assert record["id"] not in seen, record["id"]
        seen.add(record["id"])
        assert record["status"] in STATUS
        assert record["url"].startswith("https://")
        assert (ROOT / record["page"]).is_file()
    counts = Counter(r["status"] for r in records)
    dates = sorted(set(r["checked_at"] for r in records))
    lines = ["# 来源与核验范围", "",
        "本手册将具体事实、编辑方法和虚构演练分开。下列记录只覆盖英国首个样章；它不是对全世界大学或某位申请者资格的完整核验。", "",
        f"集中核验日期：**{'、'.join(dates)}**。本批共 **{len(records)} 条事实或入口记录**：" + "、".join(f"{STATUS[s]} {counts[s]} 条" for s in STATUS) + "。", "",
        "“已核实”表示这条有明确适用范围的陈述得到所列官方页面支持；并不表示申请人已经满足所有条件。未公布金额、未能取得的信息，以及跨年度适用性仍有缺口时，不作补值。", "",
        "## 优先解决的缺口", "",
        "- 两个计算机本科项目的 2027 国际生精确学费：Manchester 明确未定，Sheffield 本次未取得项目金额，不能用校级范围代替报价。",
        "- 未按入学年度标注的中国资格规则，以及 Manchester 计算机系 2027 具体学历组合。",
        "- 本科录取对应的押金、退款条款和个人回复期限。",
        "- 本人的预科选择、完整学术资格、签证材料、注册及住宿安排，仍需按具体情况核实。", "",
        "## 如何使用这些记录", "",
        "正文在结论旁放来源链接；这里保留适用对象、年度、原文位置和限制。预算工具及两个家庭案例使用编辑定义的模型与虚构数据，没有把演练价格当作官方费用。", "",
        "具体政策变化以有权发布该项规则的官方机构为准。链接检查和网站构建通过，不等于政策已经重新核验。", "",
        "[阅读英国样章](../destinations/uk.md) · [查看原始结构化记录](https://github.com/Garylauchina/study-abroad-handbook/blob/main/.maintenance/uk-sources.json)", "",
        "## 逐项记录", ""]
    for r in records:
        lines += [f"### {r['id']} · {STATUS[r['status']]}", "", r["claim"], "",
            f"- 官方来源：[{r['title']}]({r['url']})；位置：{r['location']}。",
            f"- 适用范围：{r['applicant_scope']}；年度：{r['intake_year']}。",
            f"- 限制或缺口：{r['limitations']}", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "docs/about/sources.md"
    output = render()
    if args.check:
        assert path.read_text() == output, "Source register is out of date; run python scripts/render_sources.py"
        print("Source register and required record fields match")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output)
        print("Rendered public source register")
