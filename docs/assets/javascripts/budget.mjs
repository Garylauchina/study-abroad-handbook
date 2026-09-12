export const exampleBudget = Object.freeze({
  tuitionAnnual: 20000, livingMonthly: 1000, years: 3, studyMonthsPerYear: 12,
  annualFees: 1000, oneOff: 3000, confirmedAidTotal: 10000,
  refundableDeposit: 1500, exchangeRate: 9, contingencyPercent: 10,
  familyBudgetCny: 1000000,
});

export function calculateBudget(input) {
  const fields = ['tuitionAnnual', 'livingMonthly', 'years', 'studyMonthsPerYear',
    'annualFees', 'oneOff', 'confirmedAidTotal', 'refundableDeposit', 'exchangeRate', 'contingencyPercent'];
  for (const field of fields) {
    if (typeof input[field] !== 'number' || !Number.isFinite(input[field]) || input[field] < 0) {
      throw new RangeError(`Invalid budget field: ${field}`);
    }
  }
  if (input.years <= 0 || input.studyMonthsPerYear <= 0 || input.studyMonthsPerYear > 12 || input.exchangeRate <= 0) {
    throw new RangeError('Years, months and exchange rate must be within their valid range');
  }
  const familyBudget = input.familyBudgetCny ?? null;
  if (familyBudget !== null && (typeof familyBudget !== 'number' || !Number.isFinite(familyBudget) || familyBudget < 0)) {
    throw new RangeError('Invalid family budget');
  }
  const baseCost = (input.tuitionAnnual + input.livingMonthly * input.studyMonthsPerYear + input.annualFees) * input.years + input.oneOff;
  const contingency = baseCost * input.contingencyPercent / 100;
  const netCost = Math.max(0, baseCost + contingency - input.confirmedAidTotal);
  const fundsLocal = netCost + input.refundableDeposit;
  const fundsCny = fundsLocal * input.exchangeRate;
  if (![baseCost, contingency, netCost, fundsLocal, fundsCny].every(Number.isFinite)) throw new RangeError('Budget exceeds supported range');
  return { baseCost, contingency, netCost, refundableDeposit: input.refundableDeposit,
    fundsLocal, fundsCny, balanceCny: familyBudget === null ? null : familyBudget - fundsCny,
    aidExceedsCost: input.confirmedAidTotal > baseCost + contingency };
}

const labels = {
  tuitionAnnual: '年学费（原币）', livingMonthly: '月生活费（原币）', years: '学制（年）',
  studyMonthsPerYear: '每年计入月数', annualFees: '年其他费用（原币）', oneOff: '全程一次性支出（原币）',
  confirmedAidTotal: '全程已落实资助（原币）', refundableDeposit: '额外可退押金（原币）',
  exchangeRate: '1 原币折合人民币', contingencyPercent: '预备金比例（%）', familyBudgetCny: '家庭可投入资金（人民币）',
};

if (typeof document !== 'undefined') {
  const form = document.querySelector('#budget-form');
  if (form) {
    const resultBox = document.querySelector('#budget-result');
    const status = document.querySelector('#budget-status');
    const comparison = document.querySelector('#budget-comparison');
    const money = new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    let current = null;
    let demo = false;
    let exampleEdited = false;
    const read = () => Object.fromEntries(Object.keys(labels).map(key => {
      const value = form.elements.namedItem(key).value.trim();
      return [key, value === '' ? (key === 'familyBudgetCny' ? null : NaN) : Number(value)];
    }));
    const render = () => {
      if (!form.checkValidity()) { resultBox.hidden = true; current = null; return; }
      try {
        const input = read();
        const result = calculateBudget(input);
        current = { input, result, demo, exampleEdited };
        for (const element of resultBox.querySelectorAll('[data-result]')) element.textContent = money.format(result[element.dataset.result]);
        comparison.classList.toggle('budget-warning', result.balanceCny !== null && result.balanceCny < 0);
        comparison.textContent = result.balanceCny === null ? '可填写家庭可投入资金，继续查看差额。'
          : result.balanceCny < 0 ? `按当前输入，资金缺口为人民币 ${money.format(-result.balanceCny)} 元。先缩小支出或落实额外资金，再作付款决定。`
          : `按当前输入，家庭资金扣除总资金参考后剩余人民币 ${money.format(result.balanceCny)} 元。还需检查付款节点。`;
        if (result.aidExceedsCost) comparison.textContent += ' 输入的资助超过支出，净成本已按零计；超额部分不计作收入。';
        status.textContent = demo ? (exampleEdited ? '基于虚构示例修改，仍含未核实的演练数据。实际决策前请逐项替换。' : '当前为完全虚构示例，仅演示计算方法。') : '已按当前输入计算。请记录原币名称、汇率日期和各项费用来源。';
        resultBox.hidden = false;
      } catch {
        current = null; resultBox.hidden = true;
        status.textContent = '数值超出可计算范围，请检查输入。';
      }
    };
    form.addEventListener('submit', event => { event.preventDefault(); render(); });
    form.addEventListener('input', () => {
      if (demo) exampleEdited = true;
      if (current) render();
      if (!current) status.textContent = '输入已更改，请补齐有效数值后计算。';
    });
    form.addEventListener('reset', () => { current = null; demo = false; exampleEdited = false; resultBox.hidden = true; status.textContent = '已清空重填。预备金比例和计入月数恢复默认值。'; });
    document.querySelector('#load-example').addEventListener('click', () => {
      for (const [key, value] of Object.entries(exampleBudget)) form.elements.namedItem(key).value = value;
      demo = true; exampleEdited = false; render();
    });
    document.querySelector('#print-budget').addEventListener('click', () => window.print());
    document.querySelector('#save-budget').addEventListener('click', () => {
      if (!current) return;
      const { input, result } = current;
      const lines = ['海外大学留学手册 · 全程预算记录', `生成时间：${new Date().toLocaleString('zh-CN')}`,
        current.demo ? (current.exampleEdited ? '数据性质：基于虚构示例修改，仍含未核实演练数据；不得作为已确认的实际费用。' : '数据性质：完全虚构，仅用于演练，非任何国家的实际费用或汇率。') : '数据性质：用户自行填写，金额与来源需自行复核。',
        '原币名称：____________', '汇率参考日期：____________', '费用来源与适用学年：____________', '',
        ...Object.entries(labels).map(([key, label]) => `${label}：${input[key] ?? '未填写'}`), '',
        `基础支出（原币）：${money.format(result.baseCost)}`, `预备金（原币）：${money.format(result.contingency)}`,
        `净成本（原币）：${money.format(result.netCost)}`, `含押金总资金参考（人民币）：${money.format(result.fundsCny)}`,
        result.balanceCny === null ? '家庭资金差额：未计算' : `家庭资金减总资金参考（人民币；负数为缺口）：${money.format(result.balanceCny)}`, '',
        '这是全程资金参考，不是逐月峰值或签证资金证明金额。学费上涨、分段学制与资助到账时间需另列付款日历。',
        '预备金作用于扣除资助前的基础支出；可退押金只计资金占用；超额资助不视为自由收入。',
        '手册：https://garylauchina.github.io/study-abroad-handbook/tools/budget/'];
      const url = URL.createObjectURL(new Blob(['\uFEFF' + lines.join('\n')], { type: 'text/plain;charset=utf-8' }));
      const link = document.createElement('a'); link.href = url; link.download = '留学全程预算记录.txt'; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  }
}
