#!/usr/bin/env node
// evo-note.mjs — 口味/机制台账唯一读写入口(参照 lizi review-pr 的 evolution-note.mjs)。
// evolution/ledger.json 是事实源;EVOLUTION.md 由本脚本再生成,手改会被覆盖。
// 每次写盘后自动 git commit+push 台账两个文件(只 add 这两个,绝不裹挟;--no-sync 跳过;
// 推送失败不报错退出——同步是 best-effort,绝不阻塞主流程)。
//
// tier 三档:
//   taste     口味规则(用户毙卡/改写/点名的偏好)。同指纹 occurrences>=2 才允许升级进
//             taste-rules.json(升级时把 landedIn 填上并 set-status adopted)。
//   mechanism 机制缺口(取数/闸门/派工/上下文等确定性问题)。可当轮落地,改脚本必须过 node --check。
//   judgment  需用户拍板的判断类。永不自动落地,只留提案。拿不准算哪类=judgment。
//
// 用法:
//   add        --fingerprint <slug> --tier <taste|mechanism|judgment> --title "…"
//              [--quote "用户原话"] [--detail "…"] [--proposal "…"] [--landed-in "…"] [--no-sync]
//   set-status --fingerprint <slug> --status <open|adopted|landed|rejected> [--note "…"] [--no-sync]
//   render     只重新生成 EVOLUTION.md(不 push)
// 同指纹重复 add → 只自增 occurrences 并更新 lastSeen(isNew=false),不要重复分析。

import { readFileSync, writeFileSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const LEDGER = join(ROOT, 'evolution', 'ledger.json');
const MD = join(ROOT, 'EVOLUTION.md');
const TIERS = ['taste', 'mechanism', 'judgment'];
const STATUSES = ['open', 'adopted', 'landed', 'rejected', 'archived'];
const today = () => new Date().toISOString().slice(0, 10);

const arg = (n) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 && process.argv[i + 1] != null ? process.argv[i + 1] : null; };
const readLedger = () => JSON.parse(readFileSync(LEDGER, 'utf8'));

function renderMd(ledger) {
  const groups = [
    ['taste', '## 口味台账(用户的每一次否决/改写/拍板;≥2 次同指纹才升级为硬规则)'],
    ['mechanism', '## 机制缺口(确定性问题;可当轮落地,改脚本须过 node --check)'],
    ['judgment', '## 待拍板(判断类,永不自动落地)'],
  ];
  let out = `# idea-outline 自进化台账\n\n自动生成:由 scripts/evo-note.mjs 从 evolution/ledger.json 再生成,**手改本文件会被覆盖**。\n进化目标:让 选题/中心思想/提纲 的提炼越来越符合口味——严谨的 AI 实战干货分享。\n`;
  for (const [tier, heading] of groups) {
    const es = ledger.entries.filter((e) => e.tier === tier && e.status !== 'rejected' && e.status !== 'archived');
    if (!es.length) continue;
    out += `\n${heading}\n\n`;
    for (const e of es) {
      out += `- \`${e.fingerprint}\` **${e.title}** — 出现 ${e.occurrences} 次,首见 ${e.firstSeen},最近 ${e.lastSeen},status: ${e.status}${e.landedIn ? `,落于 ${e.landedIn}` : ''}\n`;
      if (e.quote) out += `  - 原话:「${e.quote}」\n`;
      if (e.detail) out += `  - 现象:${e.detail}\n`;
      if (e.proposal) out += `  - 提案:${e.proposal}\n`;
      if (e.note) out += `  - 备注:${e.note}\n`;
    }
  }
  const rejected = ledger.entries.filter((e) => e.status === 'rejected');
  if (rejected.length) {
    out += `\n## 已否决(留档防止重复提出)\n\n`;
    for (const e of rejected) out += `- \`${e.fingerprint}\` ${e.title}${e.note ? ` — ${e.note}` : ''}\n`;
  }
  const archived = ledger.entries.filter((e) => e.status === 'archived');
  if (archived.length) {
    out += `\n## 已归档(45 天未再触发,默认已吸收;留档防止重复提出)\n\n`;
    for (const e of archived) out += `- \`${e.fingerprint}\` ${e.title}(x${e.occurrences},最近 ${e.lastSeen})${e.note ? ` — ${e.note}` : ''}\n`;
  }
  return out;
}

function writeAll(ledger) {
  writeFileSync(LEDGER, JSON.stringify(ledger, null, 2) + '\n');
  writeFileSync(MD, renderMd(ledger));
}

function sync(message) {
  if (process.argv.includes('--no-sync')) return { skipped: 'no-sync' };
  try {
    execSync(`git -C "${ROOT}" add evolution/ledger.json EVOLUTION.md`, { stdio: 'pipe' });
    execSync(`git -C "${ROOT}" commit -m ${JSON.stringify(message)}`, { stdio: 'pipe' });
    execSync(`git -C "${ROOT}" push`, { stdio: 'pipe', timeout: 30000 });
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e).slice(0, 200) };
  }
}

const cmd = process.argv[2];
if (cmd === 'render') {
  writeAll(readLedger());
  console.log(JSON.stringify({ ok: true, rendered: MD }));
} else if (cmd === 'add') {
  const fp = arg('fingerprint');
  if (!fp || !/^[a-z0-9-]{3,64}$/.test(fp)) throw new Error('缺少或不合法的 --fingerprint(小写字母/数字/连字符,3-64 位)');
  const ledger = readLedger();
  let entry = ledger.entries.find((e) => e.fingerprint === fp);
  let isNew = false;
  if (entry) {
    entry.occurrences += 1;
    entry.lastSeen = today();
    if (arg('detail')) entry.detail = arg('detail');
  } else {
    const tier = arg('tier');
    if (!TIERS.includes(tier)) throw new Error(`--tier 必须是 ${TIERS.join('|')}`);
    if (!arg('title')) throw new Error('缺少 --title(一句话)');
    entry = {
      fingerprint: fp, tier, title: arg('title'),
      quote: arg('quote') || undefined, detail: arg('detail') || undefined,
      proposal: arg('proposal') || undefined, landedIn: arg('landed-in') || undefined,
      status: 'open', occurrences: 1, firstSeen: today(), lastSeen: today(),
    };
    ledger.entries.push(entry);
    isNew = true;
  }
  writeAll(ledger);
  const s = sync(`evo: ${fp} (${entry.tier}, x${entry.occurrences})`);
  console.log(JSON.stringify({ ok: true, isNew, fingerprint: fp, occurrences: entry.occurrences, canPromote: entry.tier === 'taste' && entry.occurrences >= 2 && entry.status === 'open', sync: s }));
} else if (cmd === 'set-status') {
  const fp = arg('fingerprint'); const status = arg('status');
  if (!STATUSES.includes(status)) throw new Error(`--status 必须是 ${STATUSES.join('|')}`);
  const ledger = readLedger();
  const entry = ledger.entries.find((e) => e.fingerprint === fp);
  if (!entry) throw new Error(`指纹不存在: ${fp}`);
  entry.status = status;
  if (arg('note')) entry.note = arg('note');
  if (arg('landed-in')) entry.landedIn = arg('landed-in');
  writeAll(ledger);
  const s = sync(`evo: ${fp} -> ${status}`);
  console.log(JSON.stringify({ ok: true, fingerprint: fp, status, sync: s }));
} else {
  console.error('用法见文件头注释: add | set-status | render');
  process.exit(1);
}
