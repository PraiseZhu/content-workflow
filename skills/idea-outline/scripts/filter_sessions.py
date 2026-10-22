# filter_sessions.py — 会话机械过滤(2026-07-25 真实数据 200→27 验证通过,勿凭感觉重写)。
# 用法: python3 filter_sessions.py <list_sessions落盘.json> <输出.json>
# 剔除: scheduler 来源 / Worker · 前缀 / messageCount<10 / 纯功能词标题(>500 条降权保留)
import json, sys, re

d = json.load(open(sys.argv[1])); s = d["sessions"]
FUNC = re.compile(r'^(hello|hi|test|收工|开工|qa\d*|\[fork\]\s*qa\d*)$', re.I)

def base(w):
    w = w or ""
    return "DIALOGUE" if "dialogues" in w else (w.rstrip("/").split("/")[-1] or "?")

kept = []
for x in s:
    t = (x.get("title") or "").strip(); m = x.get("messageCount") or 0
    if x.get("source") == "scheduler": continue
    if t.startswith("Worker ·"): continue
    if m < 10: continue
    if FUNC.match(t) and m <= 500: continue   # 纯功能词剔除,大体量降权保留
    kept.append({"title": t, "project": base(x.get("workingDir")), "msgs": m,
                 "model": x.get("model"), "date": (x.get("createdAt") or "")[:10],
                 "downweight": bool(FUNC.match(t))})

json.dump({"window": d.get("query", {}).get("from", "?") + ".." + d.get("query", {}).get("to", "?"),
           "total_raw": len(s), "kept": len(kept), "sessions": kept},
          open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print("raw:", len(s), "→ kept:", len(kept))
