# 全程预算计算器

把整个学位的成本算清楚，再检查家庭资金是否能够按时到位。下面的输入统一使用同一种原币，结果同时换算成人民币。

**先查到金额，再填写。** 学费、生活费和汇率均留空；“载入虚构示例”只演示计算方法，不代表任何国家、大学的费用或实时汇率。

<form id="budget-form" class="budget-form">
  <fieldset>
    <legend>学制和日常支出</legend>
    <div class="budget-fields">
      <label>每学年学费（原币）<input name="tuitionAnnual" type="number" min="0" step="0.01" required inputmode="decimal"></label>
      <label>每月生活费（原币）<input name="livingMonthly" type="number" min="0" step="0.01" required inputmode="decimal"><span class="field-note">含住宿、吃饭、交通等；已包含的项目不重复填写。</span></label>
      <label>学制（年）<input name="years" type="number" min="0.5" max="15" step="0.5" required inputmode="decimal"></label>
      <label>每年生活费计入月数<input name="studyMonthsPerYear" type="number" min="1" max="12" step="1" value="12" required inputmode="numeric"><span class="field-note">假期仍需付租金等支出时，不应仅按上课月份算。</span></label>
      <label>每学年其他必付费用（原币）<input name="annualFees" type="number" min="0" step="0.01" value="0" required inputmode="decimal"><span class="field-note">已计入学费或生活费的保险、注册费不要重复计入。</span></label>
      <label>全程一次性支出合计（原币）<input name="oneOff" type="number" min="0" step="0.01" value="0" required inputmode="decimal"><span class="field-note">先汇总考试、申请、翻译、签证、交通等；往返多次按全程次数计入。</span></label>
    </div>
  </fieldset>
  <fieldset>
    <legend>资助、预备金和家庭资金</legend>
    <div class="budget-fields">
      <label>全程已落实资助（原币）<input name="confirmedAidTotal" type="number" min="0" step="0.01" value="0" required inputmode="decimal"><span class="field-note">有待竞争、续领或批准的部分暂不计入。</span></label>
      <label>可退押金现金占用（原币）<input name="refundableDeposit" type="number" min="0" step="0.01" value="0" required inputmode="decimal"><span class="field-note">只填支出以外的可退押金；抵扣学费的订金不能重复计算。</span></label>
      <label>汇率：1 原币折合人民币<input name="exchangeRate" type="number" min="0.000001" step="any" required inputmode="decimal"><span class="field-note">自行填写预算汇率并记录日期；可提高汇率观察压力情景。</span></label>
      <label>预备金比例（%）<input name="contingencyPercent" type="number" min="0" max="100" step="0.1" value="10" required inputmode="decimal"><span class="field-note">10%仅是可修改的演练起点，不代表足够覆盖所有风险。</span></label>
      <label>家庭可投入资金（人民币，可不填）<input name="familyBudgetCny" type="number" min="0" step="0.01" inputmode="decimal"><span class="field-note">先保留家庭必要支出与应急资金，再填写留学可用部分。</span></label>
    </div>
  </fieldset>
  <div class="budget-actions">
    <button type="submit">计算全程预算</button>
    <button type="button" id="load-example">载入虚构示例</button>
    <button type="reset">清空重填</button>
  </div>
  <p id="budget-status" class="budget-status" role="status">填写后计算。内容只在当前页面使用，刷新后清空。</p>
</form>

<section id="budget-result" class="budget-result" aria-live="polite" aria-label="预算计算结果" hidden>
  <h2>你的全程预算</h2>
  <dl>
    <dt>基础支出（原币）</dt><dd data-result="baseCost"></dd>
    <dt>预备金（原币）</dt><dd data-result="contingency"></dd>
    <dt>扣除已落实资助后的净成本（原币）</dt><dd data-result="netCost"></dd>
    <dt>额外可退押金（原币）</dt><dd data-result="refundableDeposit"></dd>
    <dt class="total">含押金的总资金参考（人民币）</dt><dd class="total" data-result="fundsCny"></dd>
  </dl>
  <p id="budget-comparison"></p>
  <p>这是全程资金参考，不是某个月的资金峰值，也不是签证资金证明金额。资助到账和退押金可能晚于付款，仍需单独安排付款日历。</p>
  <div class="budget-actions"><button type="button" id="save-budget">保存预算记录</button><button type="button" id="print-budget">打印本页</button></div>
</section>

<noscript>你的浏览器没有启用 JavaScript，可按下方公式手工计算，并使用预算填写指南。</noscript>

## 计算口径

```text
基础支出 =（年学费 + 月生活费 × 每年计入月数 + 年其他费用）× 学制 + 一次性支出
预备金 = 基础支出 × 输入的预备金比例 ÷ 100
净成本 = max(0, 基础支出 + 预备金 − 全程已落实资助)
总资金参考 =（净成本 + 额外可退押金）× 人民币汇率
```

这一简化模型假设各学年的费用相同、每年计入的生活费月数相同、全程使用同一个预算汇率。**学费逐年上涨、先读预科、不同年份资助不同或中途更换国家时，应分段计算并合并付款日历。** 它不自动预测涨价或汇率。

输入 0.5、1.5 等非整数年时，模型会将年学费和年度费用按比例计算。只有学校确实按该比例收费时才这样填写；否则按实际计费阶段单独核算。

毕业收入、尚未获得的奖学金和计划中的兼职收入，不计入基础预算。资助超过总支出时净成本按零显示，超额部分不视为可自由使用的收入。

## 下一步

- [阅读预算填写指南](budget-guide.md)，补齐支出项目与退款条件。
- [看两个虚构家庭怎样处理预算结果](../start/cases.md)。
- [把费用和来源放进大学项目比较表](compare.md)。
