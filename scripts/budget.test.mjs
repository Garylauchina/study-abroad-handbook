import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateBudget, exampleBudget } from '../docs/assets/javascripts/budget.mjs';

test('full-degree example includes one-off fees once and refundable deposit only in funds', () => {
  const r = calculateBudget(exampleBudget);
  assert.equal(r.baseCost, 102000);
  assert.equal(r.contingency, 10200);
  assert.equal(r.netCost, 102200);
  assert.equal(r.fundsLocal, 103700);
  assert.equal(r.fundsCny, 933300);
  assert.equal(r.balanceCny, 66700);
  const withoutDeposit = calculateBudget({ ...exampleBudget, refundableDeposit: 0 });
  assert.equal(withoutDeposit.netCost, r.netCost);
  assert.equal(r.fundsCny - withoutDeposit.fundsCny, 13500);
});
test('a funding gap is visible; missing family funds is not zero', () => {
  assert.equal(calculateBudget({ ...exampleBudget, familyBudgetCny: 700000 }).balanceCny, -233300);
  assert.equal(calculateBudget({ ...exampleBudget, familyBudgetCny: null }).balanceCny, null);
  assert.ok(Math.abs(calculateBudget({ ...exampleBudget, exchangeRate: 9.45 }).fundsCny - 979965) < .001);
  const alternative = calculateBudget({ ...exampleBudget, tuitionAnnual: 10000, livingMonthly: 700, confirmedAidTotal: 0 });
  assert.equal(alternative.fundsCny, 619380);
});
test('invalid values do not silently become zero or produce plausible totals', () => {
  for (const change of [{tuitionAnnual: NaN}, {years: 0}, {studyMonthsPerYear: 13}, {exchangeRate: 0}, {oneOff: -1}, {familyBudgetCny: -1}, {years: Infinity}, {tuitionAnnual: ''}]) {
    assert.throws(() => calculateBudget({ ...exampleBudget, ...change }), RangeError);
  }
});
test('half-year scenarios and grant surplus keep the documented cost boundaries', () => {
  const short = calculateBudget({ ...exampleBudget, years: .5, contingencyPercent: 0, confirmedAidTotal: 0 });
  assert.equal(short.baseCost, 19500);
  const funded = calculateBudget({ ...exampleBudget, confirmedAidTotal: 200000 });
  assert.equal(funded.netCost, 0);
  assert.equal(funded.fundsCny, 13500);
  assert.equal(funded.aidExceedsCost, true);
});
