#!/usr/bin/env node
// check-gates.mjs — 人话闸门 + 口味硬规则的机械校验。
// 规则全部来自 config/taste-rules.json(数据),本脚本只做确定性检查,不做判断。
//
// 用法: node check-gates.mjs <选题文件.md> [--json]
// 退出码: 0=全过 / 1=有命中(明细在输出) / 2=参数或读文件错误
//
// 检查项:
//   jargon      行业黑话(命中即打回)
//   abstract    抽象名词化词表(命中→人工判断主宾语,非具体即重写)
//   cliche      套话(命中即打回)
//   regex       抽象对抽象句式等(命中→人工判断两端是否具体物)
//   length      中心思想/选题主张 超长(直接重写)
// 注意: 中文长度按 [一-鿿] 计汉字数,标点和空格不计。

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const rules = JSON.parse(readFileSync(join(ROOT, 'config', 'taste-rules.json'), 'utf8'));

const file = process.argv[2];
if (!file) { console.error('用法: node check-gates.mjs <选题文件.md> [--json]'); process.exit(2); }
let text;
try { text = readFileSync(file, 'utf8'); } catch (e) { console.error(`读文件失败: ${e.message}`); process.exit(2); }

const lines = text.split('\n');
const findings = [];
const push = (rule, lineNo, hit, note) =>
  findings.push({ rule, line: lineNo + 1, hit, text: lines[lineNo].trim().slice(0, 90), note });

const hanLen = (s) => (s.match(/[一-鿿]/g) || []).length;

lines.forEach((line, i) => {
  for (const w of rules.bannedJargon) if (line.includes(w)) push('jargon', i, w, '黑话,打回重写');
  for (const w of rules.bannedAbstractNouns.patterns) if (line.includes(w)) push('abstract', i, w, '抽象名词化,人工判断主宾语');
  for (const w of rules.bannedCliches) if (line.includes(w)) push('cliche', i, w, '套话,打回重写');
  for (const r of rules.bannedRegex) {
    const m = line.match(new RegExp(r.pattern));
    if (m) push(`regex:${r.name}`, i, m[0], r.note);
  }
  // 长度检查:匹配「中心思想」「选题主张」的字段行,取冒号后内容
  const fm = line.match(/\*{0,2}(中心思想|选题主张)\*{0,2}[:：](.+)/);
  if (fm) {
    const body = fm[2].replace(/\*/g, '');
    const limit = fm[1] === '中心思想' ? rules.lengths.centralIdeaMaxChars : rules.lengths.claimMaxChars;
    const n = hanLen(body);
    if (n > limit) push('length', i, `${fm[1]}=${n}字>${limit}`, '超长,直接重写');
  }
});

const summary = {
  file,
  pass: findings.length === 0,
  counts: findings.reduce((a, f) => ((a[f.rule.split(':')[0]] = (a[f.rule.split(':')[0]] || 0) + 1), a), {}),
  findings,
};

if (process.argv.includes('--json')) {
  console.log(JSON.stringify(summary, null, 2));
} else {
  console.log(summary.pass ? `✅ 全过: ${file}` : `❌ 命中 ${findings.length} 处: ${file}`);
  for (const f of findings) console.log(`  L${f.line} [${f.rule}] "${f.hit}" — ${f.note}\n      ${f.text}`);
}
process.exit(summary.pass ? 0 : 1);
