#!/usr/bin/env python3
"""check_spec.py — render sizes.json as a table and check every slot against SPEC.md.
For each slot: the SPEC.md table row whose first cell is `spec_row` must contain "<w>×<h>".
Retired slots must be mentioned as 停用 in that row. Exit 1 on any mismatch."""
import json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(D, "sizes.json"), encoding="utf-8"))
rows = [l for l in open(os.path.join(D, S["doc"]), encoding="utf-8") if l.startswith("|")]
bad = 0
print(f"sizes.json version {S['version']}\n")
print("| id | status | lang | size | safe | SPEC row |\n|---|---|---|---|---|---|")
for k, v in S["slots"].items():
    size = f"{v['w']}×{v['h']}"
    row = next((r for r in rows if r.split("|")[1].strip() == v["spec_row"]), None)
    ok = row is not None and size in row
    if v["status"] == "retired": ok = ok and "停用" in row
    bad += not ok
    print(f"| {k} | {v['status']} | {v['lang']} | {size} | {v.get('safe','-')} | {'OK' if ok else 'MISMATCH'} |")
sys.exit(1 if bad else 0)
