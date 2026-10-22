#!/usr/bin/env node
// sync-skill-repo.mjs — skill 仓自同步:执行前 pull 到最新,进化落地后 push 回个人仓。
// 同步失败 ok=false 但 exit 0(best-effort,绝不阻塞主流程);只有参数错误 exit 1。
//
// 用法: node sync-skill-repo.mjs <pull|push> [--message "…"]
//   pull  git pull --ff-only(每次 skill 开跑前先调,保证用的是最新规则)
//   push  提交 skill 目录下未提交改动并推送(仅当前分支==main 才推)

import { execSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const git = (args, opts = {}) => execSync(`git -C "${ROOT}" ${args}`, { stdio: 'pipe', timeout: 30000, ...opts }).toString().trim();
const arg = (n) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 && process.argv[i + 1] != null ? process.argv[i + 1] : null; };

const cmd = process.argv[2];
try {
  if (cmd === 'pull') {
    const out = git('pull --ff-only');
    console.log(JSON.stringify({ ok: true, out: out.slice(0, 200) }));
  } else if (cmd === 'push') {
    const branch = git('rev-parse --abbrev-ref HEAD');
    if (branch !== 'main') { console.log(JSON.stringify({ ok: false, error: `当前分支 ${branch} != main,不推送` })); process.exit(0); }
    const dirty = git('status --porcelain');
    if (dirty) {
      git('add -A');
      git(`commit -m ${JSON.stringify(arg('message') || 'evo: sync skill state')}`);
    }
    git('push');
    console.log(JSON.stringify({ ok: true, committed: Boolean(dirty) }));
  } else {
    console.error('用法: sync-skill-repo.mjs <pull|push> [--message "…"]');
    process.exit(1);
  }
} catch (e) {
  console.log(JSON.stringify({ ok: false, error: String(e.message || e).slice(0, 200) }));
}
