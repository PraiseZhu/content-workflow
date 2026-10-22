#!/usr/bin/env python3
"""deai_lint.py — rule-file driven de-AI checker. No rules live in this file.

Subcommands
  lint FILE [--lang zh|en] [--x] [--article article.yaml] [--json]   hard-ban + warn hits
  gate FILE --stage outline|draft|final|author_final [--rubric R.json] [--article A.yaml] [--x] [--out OUT.json] [--no-legacy]
  legacy FILE [--json]                old deai_lint.py report, byte-identical (acceptance step 1)
  test                                run tests/<lang>/<rule>.json (hit/miss samples)
  calibrate [--add-pass P] [--add-fail P]   pass rate / catch rate / per-rule FP rate, writes calibration/last-run.json
  profile                             style-profile.json from calibration pass set
  rubric-prompt FILE [--article A]    print the reviewer prompt (fresh context, flag only)
  rubric-check FILE RUBRIC.json       validate reviewer output (evidence must be in FILE; void otherwise)

Env / flags: --rules DIR (default $DEAI_RULES or deai-rules),
  --names FILE, --glossary FILE (default from personal.json data_defaults).
"""
import re, sys, os, json, difflib, subprocess, datetime

RULES_DIR = os.environ.get("DEAI_RULES", "deai-rules")
LEGACY_SCORE = os.environ.get("DEAI_LEGACY_SCORE", "")
LEGACY_CANDIDATES = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skill", "wewrite", "scripts", "humanness_score.py"),
                     os.path.expandvars("${WEWRITE_DIR}/scripts/humanness_score.py")]

def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else default

def load(name):
    return json.load(open(os.path.join(arg("--rules", RULES_DIR), name + ".json"), encoding="utf-8"))

# ---------------- legacy (verbatim behaviour of the old script) ----------------
def clean(t):
    t = re.sub(r"^\s*\|.*\|\s*$", "", t, flags=re.M)
    t = re.sub(r"^---\n.*?\n---\n", "", t, count=1, flags=re.S)
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    return t

def lang(t, zh=None):
    zh = zh or load("zh")
    d = zh["detect"]
    n_zh = len(re.findall(d["script"], t)); n_en = len(re.findall(r"[A-Za-z]+", t))
    return "zh" if n_zh >= d["min_chars"] or n_zh > n_en else "en"

def paras(t): return [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip() and not p.strip().startswith("#")]
def sents_zh(t): return [s.strip() for s in re.split(r"(?<=[。！？!?])|\n", t) if len(s.strip()) > 1]
def sents_en(t): return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", t) if len(s.strip()) > 1]
def lineno(text, idx): return text.count("\n", 0, idx) + 1

def legacy_scan(text, pats, icase):
    flags = re.M | (re.I if icase else 0)
    return {k: [(lineno(text, m.start()), m.group(0)[:40]) for m in re.finditer(p, text, flags)] for k, p in pats.items()}

def structural(text, lg, ZH):
    S = sents_zh(text) if lg == "zh" else sents_en(text)
    P = paras(text); f = {}
    L = (lambda s: len(re.sub(r"\s", "", s))) if lg == "zh" else (lambda s: len(s.split()))
    short = 8 if lg == "zh" else 5
    runs, cur = [], []
    for s in S:
        if L(s) <= short: cur.append(s)
        else:
            if len(cur) >= 3: runs.append(" / ".join(cur)[:60])
            cur = []
    if len(cur) >= 3: runs.append(" / ".join(cur)[:60])
    f["staccato_runs"] = runs
    head = (lambda s: re.sub(r"[\s*#>\-]", "", s)[:2]) if lg == "zh" else (lambda s: " ".join(s.lower().split()[:2]))
    reps = []
    for i in range(len(S) - 2):
        h = head(S[i])
        if h and h == head(S[i+1]) == head(S[i+2]): reps.append(h)
    f["same_opener_x3"] = sorted(set(reps))
    lines = text.splitlines()
    bl = [l for l in lines if re.match(r"\s*(?:[-*]|\d+\.)\s*\*\*[^*]{1,30}\*\*", l)]
    li = [l for l in lines if re.match(r"\s*(?:[-*]|\d+\.)\s+", l)]
    f["bold_label_list"] = {"bold_label_items": len(bl), "list_items": len(li)}
    tri = re.findall(r"[：:][^。；\n]{1,40}?、[^。；\n]{1,40}?(?:、|和|与|及)[^。；、\n]{1,40}[。；\n]", text) if lg == "zh" else \
          re.findall(r"\b\w+(?: \w+){0,3}, \w+(?: \w+){0,3},? and \w+(?: \w+){0,3}\b", text)
    num3 = re.findall(r"三(?:件事|个(?:问题|层|维度|方面)|层|大|点)", text) if lg == "zh" else re.findall(r"\bthree (?:things|ways|reasons|lessons)\b", text, re.I)
    f["triads"] = {"list_of_three": len(tri), "three_label": len(num3)}
    pairs = []
    if lg == "zh":
        for s in S:
            cl = [c for c in re.split(r"[，；,;]", s) if len(c) >= 4]
            for a, b in zip(cl, cl[1:]):
                if abs(len(a) - len(b)) <= 1 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.4:
                    pairs.append(f"{a}｜{b}")
    f["parallel_pairs"] = pairs[:8]
    stamp = sum(1 for p in P if re.search(r"(这说明|这意味着|换句话说|也就是说|所以|可见|因此|说白了|一句话)[^。]{0,40}。?$", p.split("\n")[-1]))
    lens = [L(p) for p in P]
    if lens:
        m = sum(lens)/len(lens); sd = (sum((x-m)**2 for x in lens)/len(lens))**.5
        f["paragraph_cv"] = round(sd/m, 2) if m else 0
    f["stamp_para_ratio"] = round(stamp/len(P), 2) if P else 0
    n = max(1, len(re.sub(r"\s", "", text)) if lg == "zh" else len(text.split()))
    per = 1000/n
    f["dash_per_k"] = round((text.count("——") + text.count("—") - 2*text.count("——") + text.count("——")) * per, 2) if lg=="zh" else round((text.count("—")+text.count("–")+text.count(" -- "))*per, 2)
    if lg == "zh":
        f["scare_quotes_per_k"] = round(len(re.findall(r"[“\"「][^”\"」]{1,4}[”\"」]", text))*per, 2)
        f["colon_per_k"] = round(text.count("：")*per, 2)
        f["formal_conj_per_k"] = round(len(re.findall(r"以及|并且|而且|因此|然而|同时|此外|从而|进而|因而|与此同时|不仅", text))*per, 2)
        f["de_chain"] = [c[:30] for c in re.split(r"[，。；：！？,]", text) if c.count("的") >= 3][:6]
        f["hedge_stack"] = [s[:40] for s in S if len(re.findall(ZH["hedge"], s)) >= 2][:6]
        f["abstract_cluster_paras"] = [p[:30] for p in P if len(re.findall(ZH["abstract_verbs"], p)) >= 2][:6]
        sp = len(re.findall(r"[\u4e00-\u9fff] [A-Za-z0-9]|[A-Za-z0-9] [\u4e00-\u9fff]", text))
        nsp = len(re.findall(r"[\u4e00-\u9fff][A-Za-z0-9]|[A-Za-z0-9][\u4e00-\u9fff]", text))
        f["cjk_latin_spacing"] = {"spaced": sp, "unspaced": nsp}
        f["halfwidth_punct_in_zh"] = len(re.findall(r"[\u4e00-\u9fff][,.;:!?](?=[\u4e00-\u9fff\s])", text))
    if P: f["last_para"] = P[-1][:80]
    return f

def legacy_report(path):
    zh, en = load("zh"), load("en")
    raw = open(path, encoding="utf-8").read(); t = clean(raw); lg = lang(t, zh)
    src = zh if lg == "zh" else en
    pats, lim = src["legacy"]["patterns"], src["legacy"]["limits"]
    hits = legacy_scan(t, pats, src["legacy"].get("flags") == "i")
    st = structural(t, lg, zh["legacy"]["patterns"])
    if lg == "zh": hits["hedge"] = []
    over = {k: len(v) for k, v in hits.items() if k in lim and len(v) > lim[k]}
    return {"file": path, "lang": lg, "over_limit": over, "pattern_hits": {k: v for k, v in hits.items() if v}, "structure": st}

def legacy_print(res, as_json):
    if as_json: print(json.dumps(res, ensure_ascii=False, indent=1)); return
    print(f"# {res['file']}  [{res['lang']}]\n超限: {res['over_limit'] or '无'}")
    for k, v in res["pattern_hits"].items():
        print(f"- {k} ×{len(v)}: " + "; ".join(f"L{a}「{b}」" for a, b in v[:6]))
    print("结构:"); [print(f"  {k}: {v}") for k, v in res["structure"].items()]

# ---------------- new lint ----------------
def mask_keep_lines(text, pat, flags=0):
    """blank out matches but keep newlines, so line numbers stay valid"""
    return re.sub(pat, lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=flags)

def read_article_meta(path):
    """minimal article.yaml reader: only the `locked:` list (- "line") is needed"""
    if not path or not os.path.exists(path): return {"locked": []}
    locked, on = [], False
    for ln in open(path, encoding="utf-8"):
        if re.match(r"^locked:\s*$", ln): on = True; continue
        if on:
            m = re.match(r"^\s+-\s+(.*)$", ln)
            if m: locked.append(m.group(1).strip().strip("'\"")); continue
            if ln.strip() and not ln.startswith(" "): on = False
    return {"locked": locked}

def prepare(raw):
    """returns dict of views, all with identical line numbering"""
    t = raw
    fm = re.match(r"^---\n.*?\n---\n", t, flags=re.S)
    if fm: t = re.sub(r"[^\n]", " ", fm.group(0)) + t[fm.end():]
    t = mask_keep_lines(t, r"```.*?```", re.S)
    t = mask_keep_lines(t, r"<!--.*?-->", re.S)
    t = mask_keep_lines(t, r"!\[[^\]]*\]\([^)]*\)")
    t = mask_keep_lines(t, r"^\s*\|.*\|\s*$", re.M)          # tables
    all_ = t
    t = mask_keep_lines(t, r"`[^`\n]+`")                     # inline code
    noquote = mask_keep_lines(t, r"“[^”\n]{1,200}”|「[^」\n]{1,200}」|\"[^\"\n]{1,200}\"")
    heading = "\n".join(l if re.match(r"^#{1,6}\s", l) else "" for l in t.split("\n"))
    body = "\n".join("" if re.match(r"^#{1,6}\s", l) else l for l in noquote.split("\n"))
    return {"all": all_, "body": body, "heading": heading, "x_body": t, "raw": raw}

def hit(rule, line, text, note=None):
    h = {"rule": rule["id"], "severity": rule["severity"], "line": line, "text": text[:60], "fix": rule["fix"]}
    if note: h["note"] = note
    return h

def run_rule(r, V, ctx):
    k = r["kind"]; scope = V.get(r.get("scope", "body"), V["body"]); flags = re.M | (re.I if r.get("flags") == "i" else 0)
    out = []
    if k in ("regex", "count", "count_per_k"):
        ms = list(re.finditer(r["pattern"], scope, flags))
        ms = [m for m in ms if not any(a in scope[max(0, m.start()-10):m.end()+10] for a in r.get("allow", []))]
        if k == "regex":
            return [hit(r, lineno(scope, m.start()), m.group(0)) for m in ms][: None] if len(ms) > r.get("limit", 0) else []
        if k == "count":
            return [hit(r, lineno(scope, ms[0].start()), f"{len(ms)} 处（上限 {r['limit']}）")] if len(ms) > r["limit"] else []
        n = max(1, len(re.sub(r"\s", "", scope))); perk = len(ms) * 1000 / n
        return [hit(r, lineno(scope, ms[0].start()), f"每千字 {perk:.1f}（上限 {r['limit']}）：" + "、".join(m.group(0) for m in ms[:4]))] if perk > r["limit"] else []
    if k == "cluster_in_para":
        for m in re.finditer(r"(?:[^\n]+\n?)+", scope):
            p = m.group(0); hs = re.findall(r["pattern"], p)
            if len(hs) > r["limit"] and not p.lstrip().startswith("#"):
                out.append(hit(r, lineno(scope, m.start()), "同段：" + "、".join(hs) + " ｜ " + p.strip()[:30]))
        return out
    if k == "bold_label_list":
        lines = V["all"].splitlines()
        bl = [(i+1, l) for i, l in enumerate(lines) if re.match(r"\s*(?:[-*]|\d+\.)\s*\*\*[^*]{1,30}\*\*", l)]
        li = [l for l in lines if re.match(r"\s*(?:[-*]|\d+\.)\s+", l)]
        if li and len(bl) >= r["min_items"] and len(bl) / len(li) > r["ratio"]:
            out.append(hit(r, bl[0][0], f"{len(bl)}/{len(li)} 个列表项是粗体标签"))
        return out
    if k == "bold_count":
        ms = list(re.finditer(r"\*\*[^*\n]+\*\*", V["x_body"]))
        return [hit(r, lineno(V["x_body"], ms[0].start()), f"{len(ms)} 处粗体（上限 {r['limit']}）")] if len(ms) > r["limit"] else []
    if k == "parallel_pair":
        for i, l in enumerate(scope.split("\n")):
            for s in re.split(r"(?<=[。！？])", l):
                cl = [c for c in re.split(r"[，；,;]", s) if len(c) >= 4]
                for a, b in zip(cl, cl[1:]):
                    if abs(len(a) - len(b)) <= 1 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.4:
                        out.append(hit(r, i+1, f"{a.strip()}｜{b.strip()}"))
        return out
    if k == "loose_layout":
        for m in re.finditer(r"\n(?:[ \t]*\n){%d,}" % (r["max_blank"] + 1), ctx["raw_body"]):
            out.append(hit(r, lineno(ctx["raw_body"], m.start()) + 1, "段间空行过多"))
        ps = [(m.start(), m.group(0).strip()) for m in re.finditer(r"(?:[^\n]+\n?)+", scope) if m.group(0).strip()]
        run = []
        for st, p in ps + [(None, "")]:
            single = p and "\n" not in p and not re.match(r"^(?:[-*>]|\d+\.)", p) and len(re.findall(r"[。！？.!?]", p)) <= 1 and (not r.get("single_needs_end_punct") or re.search(r"[。！？.!?][”」）)]?$", p))
            if single: run.append(st)
            else:
                if len(run) >= r["single_run"]: out.append(hit(r, lineno(scope, run[0]), f"连续 {len(run)} 个单句段"))
                run = []
        return out
    if k == "staccato":
        S = [(i+1, s.strip()) for i, l in enumerate(scope.split("\n")) for s in re.split(r"(?<=[.!?])\s+", l) if len(s.strip()) > 1]
        cur = []
        for ln, s in S + [(0, "x " * 20)]:
            if len(s.split()) <= 5: cur.append((ln, s))
            else:
                if len(cur) >= 3: out.append(hit(r, cur[0][0], " / ".join(x for _, x in cur)))
                cur = []
        return out
    if k == "title_case":
        small = {"a","an","the","and","or","but","of","to","in","on","for","at","by","with","vs","is","are","it","as","from"}
        for i, l in enumerate(scope.split("\n")):
            m = re.match(r"^#{1,6}\s+(.*)$", l)
            if not m: continue
            w = [x for x in re.findall(r"[A-Za-z][A-Za-z'-]*", m.group(1))]
            sig = [x for x in w[1:] if x.lower() not in small]
            if len(sig) >= 2 and all(x[0].isupper() for x in sig) and not all(x.isupper() for x in sig):
                out.append(hit(r, i+1, m.group(1)))
        return out
    if k == "names":
        for n in ctx["names"]:
            for m in re.finditer(re.escape(n), V["all"], re.I if n.isascii() else 0):
                out.append(hit(r, lineno(V["all"], m.start()), m.group(0)))
        return out
    if k == "jargon":
        for g in ctx["glossary"]:
            term = g["term"]; pat = r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])"
            m = re.search(pat, V["body"])
            if not m: continue
            w = r.get("window", 30); win = V["raw"][max(0, m.start()-w):m.end()+w] if False else V["body"][max(0, m.start()-w):m.end()+w]
            explained = re.search(r"[（(]|也就是|即|指的是|叫做|就是", win) or any(a in win for a in g.get("explain", []))
            if not explained: out.append(hit(r, lineno(V["body"], m.start()), f"{term} 首次出现未解释"))
        return out
    if k == "locked":
        return []  # handled in lint()
    raise SystemExit(f"unknown rule kind {k} in {r['id']}")

def load_names(path):
    if not path or not os.path.exists(path): return []
    return [l.strip() for l in open(path, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]

def lint(path, lg=None, x=False, article=None, names=None, glossary=None, text=None):
    raw = text if text is not None else open(path, encoding="utf-8").read()
    zh = load("zh"); pe = load("personal")
    lg = lg or lang(clean(raw), zh)
    src = zh if lg == "zh" else load("en")
    V = prepare(raw)
    raw_body = re.sub(r"^---\n.*?\n---\n", lambda m: re.sub(r"[^\n]+", "fm", m.group(0)).replace("\n\n", "\nfm\n"), raw, count=1, flags=re.S)
    dd = pe.get("data_defaults", {})
    ctx = {"raw_body": raw_body,
           "names": load_names(names or arg("--names", dd.get("names"))),
           "glossary": json.load(open(glossary or arg("--glossary", dd.get("glossary")), encoding="utf-8")).get("terms", []) if os.path.exists(glossary or arg("--glossary", dd.get("glossary")) or "") else []}
    meta = read_article_meta(article)
    locked = meta["locked"]
    rules = [r for r in src["rules"] if r.get("scope") != "x_body" or x] + [r for r in pe["rules"] if lg == "zh" or r["id"] != "p.jargon_first_use"]
    hits = []
    for r in rules: hits += run_rule(r, V, ctx)
    # lock exemption: hits inside a locked line become warn
    lines = raw.split("\n")
    for h in hits:
        if h["severity"] == "ban" and locked and h["rule"] != "p.leak.names":
            ln = lines[h["line"]-1] if 0 < h["line"] <= len(lines) else ""
            if any(L and L in ln for L in locked):
                h["severity"] = "warn"; h["note"] = "在锁定行内，只提示不改"
    locked_res = {"ok": True, "missing": []}
    for L in locked:
        if L not in raw:
            locked_res["ok"] = False; locked_res["missing"].append(L)
            hits.append({"rule": "p.locked_lines", "severity": "ban", "line": 0, "text": L[:60], "fix": "locked_line_modified：恢复原句", "note": "locked_line_modified"})
    return {"file": path, "lang": lg,
            "rules_version": f"{lg}@{src['version']}, personal@{pe['version']}",
            "hard_bans": [h for h in hits if h["severity"] == "ban"],
            "warnings": [h for h in hits if h["severity"] == "warn"],
            "locked_lines": locked_res}

# ---------------- legacy humanness score (report only) ----------------
def legacy_score(path):
    if "--no-legacy" in sys.argv: return None
    exe = LEGACY_SCORE or next((p for p in LEGACY_CANDIDATES if os.path.exists(p)), None)
    if not exe: return {"error": "humanness_score.py not found"}
    try:
        o = subprocess.run([sys.executable, exe, path, "--json"], capture_output=True, text=True, timeout=120)
        d = json.loads(o.stdout); return {"composite_score": d.get("composite_score"), "script": exe, "note": "report only, not a gate"}
    except Exception as e:
        return {"error": str(e)[:200]}

# ---------------- rubric ----------------
def norm(s): return re.sub(r"[\s*_`>#]+", "", s or "")

def rubric_check(path, rpath):
    draft = norm(open(path, encoding="utf-8").read()); rub = load("rubric")
    data = json.load(open(rpath, encoding="utf-8"))
    items = data["rubric"] if isinstance(data, dict) else data
    dims = {d["id"] for d in rub["dimensions"]}
    out, voided, needs = [], [], []
    for it in items:
        d = it.get("dim")
        if d not in dims: voided.append({**it, "void_reason": "unknown dim"}); continue
        res = it.get("result")
        if res == "needs_author": needs.append(f"{d}: {it.get('where', it.get('evidence',''))}"); out.append(it); continue
        if res == "fail":
            ev, rw = it.get("evidence"), it.get("rewrite")
            if not ev or not rw: voided.append({**it, "void_reason": "missing evidence or rewrite"}); it = {**it, "result": "pass", "voided": True}
            elif norm(ev) not in draft: voided.append({**it, "void_reason": "evidence not found in draft"}); it = {**it, "result": "pass", "voided": True}
        out.append(it)
    seen = {i["dim"] for i in out}
    missing = sorted(dims - seen)
    return {"rubric_version": rub["version"], "rubric": out, "voided": voided, "needs_author": needs, "missing_dims": missing,
            "rubric_fail": [i["dim"] for i in out if i.get("result") == "fail"]}

def rubric_prompt(path, article=None, stage="draft"):
    rub = load("rubric"); dims = rub["dimensions"]
    if stage == "outline": dims = [d for d in dims if d["id"] in rub.get("outline_dims", [])]
    anchors = rub.get("voice_anchors_path"); anc = open(anchors, encoding="utf-8").read() if anchors and os.path.exists(anchors) else "(暂无作者终稿锚点：R7 只检查有没有明显的模板化手法)"
    locked = read_article_meta(article)["locked"]
    lines = [rub["instructions"], "", "## 维度"]
    for d in dims: lines.append(f"- {d['id']}：{d['question']}｜pass：{d['pass']}｜证据：{d['evidence']}")
    lines += ["", "## 锁定行（不得建议改写）", *(f"- {l}" for l in locked or ["(无)"]), "", "## 风格锚点", anc, "", "## 输出格式（只输出 JSON）", rub["output_schema"], "", "## 稿子", open(path, encoding="utf-8").read()]
    return "\n".join(lines)

# ---------------- gate ----------------
def gate(path, stage, rubric=None, article=None, x=False, lg=None):
    L = lint(path, lg=lg, x=x, article=article)
    if stage == "outline":
        keep = {"p.leak.names", "p.locked_lines"} | {r["id"] for src in ("zh", "en", "personal") for r in load(src)["rules"] if r.get("outline")}
        L["hard_bans"] = [h for h in L["hard_bans"] if h["rule"] in keep]
    if stage == "author_final": rubric = None
    R = rubric_check(path, rubric) if rubric else None
    rub_req = stage in ("outline", "draft", "final")
    rub_ok = (R is not None and not R["rubric_fail"] and not R["missing_dims"]) if rub_req else True
    if R and stage == "outline":
        need = set(load("rubric").get("outline_dims", [])); rub_ok = not R["rubric_fail"] and need <= {i["dim"] for i in R["rubric"]}
    g = {"pass": (len(L["hard_bans"]) == 0) and rub_ok and L["locked_lines"]["ok"],
         "hard_ban_hits": len(L["hard_bans"]),
         "rubric_fail": R["rubric_fail"] if R else ([] if not rub_req else ["<rubric not run>"]),
         "needs_author": R["needs_author"] if R else []}
    rep = {"rules_version": L["rules_version"], "rubric_version": load("rubric")["version"], "stage": stage, "lang": L["lang"],
           "file": path, "gate": g, "hard_bans": L["hard_bans"], "rubric": R["rubric"] if R else [],
           "rubric_voided": R["voided"] if R else [], "warnings": L["warnings"], "locked_lines": L["locked_lines"],
           "legacy": legacy_score(path), "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
    return rep

def summary(rep):
    g = rep["gate"]
    s1 = f"门槛：{'通过' if g['pass'] else '未通过'}（硬禁 {g['hard_ban_hits']} 条；评审 fail：{', '.join(g['rubric_fail']) or '无'}；锁定行 {'OK' if rep['locked_lines']['ok'] else '被改'}）"
    fx = [f"L{h['line']} {h['rule']}「{h['text'][:20]}」→{h['fix']}" for h in rep["hard_bans"][:6]] + \
         [f"{i['dim']}「{i.get('evidence','')[:20]}」→{i.get('rewrite','')}" for i in rep["rubric"] if i.get("result") == "fail"][:4]
    s2 = "要改：" + ("；".join(fx) if fx else "无")
    s3 = "要你补的料：" + ("；".join(g["needs_author"]) if g["needs_author"] else "无")
    return "\n".join([s1, s2, s3])

# ---------------- tests / calibration / profile ----------------
def run_tests():
    base = os.path.join(arg("--rules", RULES_DIR), "tests"); fails = 0; n = 0
    allrules = {r["id"]: (lg, r) for lg in ("zh", "en") for r in load(lg)["rules"]} | {r["id"]: ("zh", r) for r in load("personal")["rules"]}
    covered = set()
    for sub in sorted(os.listdir(base)):
        for fn in sorted(os.listdir(os.path.join(base, sub))):
            if not fn.endswith(".json"): continue
            T = json.load(open(os.path.join(base, sub, fn), encoding="utf-8"))
            if "rule" not in T: continue  # fixture
            rid = T["rule"]; covered.add(rid)
            lg = allrules[rid][0] if rid in allrules else sub
            for kind in ("hit", "miss"):
                for s in T.get(kind, []):
                    n += 1
                    res = lint(f"<test:{rid}>", lg=T.get("lang", lg), x=T.get("x", False), article=T.get("article"),
                               names=T.get("names"), glossary=T.get("glossary"), text=s)
                    got = any(h["rule"] == rid for h in res["hard_bans"] + res["warnings"])
                    if got != (kind == "hit"):
                        fails += 1; print(f"FAIL {rid} [{kind}] {s[:60]!r}")
    unc = sorted(set(allrules) - covered)
    print(f"tests: {n - fails}/{n} passed; rules without tests: {unc or 'none'}")
    return fails == 0 and not unc

def read_list(p):
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.exists(p) else []

def calibrate():
    cdir = os.path.join(arg("--rules", RULES_DIR), "calibration")
    for flag, fn in (("--add-pass", "pass.txt"), ("--add-fail", "fail.txt")):
        p = arg(flag)
        if p:
            p = os.path.abspath(p); lst = read_list(os.path.join(cdir, fn))
            if p not in lst:
                with open(os.path.join(cdir, fn), "a", encoding="utf-8") as f: f.write(p + "\n")
    P, F = read_list(os.path.join(cdir, "pass.txt")), read_list(os.path.join(cdir, "fail.txt"))
    per_rule = {}; rows = []
    def tally(path, side):
        L = lint(path, x=path.endswith(".x.md"))
        for h in L["hard_bans"] + L["warnings"]:
            d = per_rule.setdefault(h["rule"], {"severity": h["severity"], "pass_hits": 0, "fail_hits": 0}); d[side + "_hits"] += 1
        rows.append({"file": path, "set": side, "lang": L["lang"], "hard_bans": len(L["hard_bans"]),
                     "rules": sorted({h["rule"] for h in L["hard_bans"]}), "gate_pass_lint": not L["hard_bans"]})
    for p in P: tally(p, "pass")
    for p in F: tally(p, "fail")
    for d in per_rule.values():
        tot = d["pass_hits"] + d["fail_hits"]; d["fp_rate"] = round(d["pass_hits"] / tot, 2) if tot else 0
        d["flag"] = "降为 warn 候选（FP>20%）" if d["fp_rate"] > 0.2 and d["severity"] == "ban" else ""
    pr = [r for r in rows if r["set"] == "pass"]; fr = [r for r in rows if r["set"] == "fail"]
    res = {"run_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "rules_version": {k: load(k)["version"] for k in ("zh", "en", "personal")},
           "pass_set_n": len(pr), "fail_set_n": len(fr),
           "pass_rate": round(sum(r["gate_pass_lint"] for r in pr) / len(pr), 3) if pr else None,
           "catch_rate": round(sum(not r["gate_pass_lint"] for r in fr) / len(fr), 3) if fr else None,
           "fail_min2_bans": all(r["hard_bans"] >= 2 for r in fr) if fr else None,
           "targets": {"pass_rate": 1.0, "catch_rate": 0.9, "status": "PROVISIONAL"},
           "rows": rows, "per_rule": per_rule}
    ok = (res["pass_rate"] in (None, 1.0)) and (res["catch_rate"] or 0) >= 0.9
    res["meets_line"] = ok
    if not pr: res["note"] = "pass 集为空：作者尚未指定满意终稿/人写文章，通过率无法测，只验证了拦截率"
    json.dump(res, open(os.path.join(cdir, "last-run.json"), "w"), ensure_ascii=False, indent=1)
    print(f"pass set {len(pr)}: pass_rate={res['pass_rate']}   fail set {len(fr)}: catch_rate={res['catch_rate']}  each≥2 bans={res['fail_min2_bans']}  meets provisional line={ok}")
    for r in rows: print(f"  [{r['set']}] {r['hard_bans']:>3} bans  {os.path.basename(r['file'])}  {','.join(r['rules'])[:110]}")
    for k, d in sorted(per_rule.items()):
        if d["pass_hits"]: print(f"  FP {k}: pass_hits={d['pass_hits']} fail_hits={d['fail_hits']} fp_rate={d['fp_rate']} {d['flag']}")
    if res.get("note"): print("NOTE:", res["note"])
    return ok

def profile():
    cdir = os.path.join(arg("--rules", RULES_DIR), "calibration"); P = read_list(os.path.join(cdir, "pass.txt"))
    out = arg("--out", "config/style-profile.json"); zhp = load("zh")["legacy"]["patterns"]
    per = []
    for p in P:
        t = clean(open(p, encoding="utf-8").read()); lg = lang(t)
        if lg != "zh": continue
        st = structural(t, lg, zhp); S = sents_zh(t); n = max(1, len(re.sub(r"\s", "", t)))
        sl = [len(re.sub(r"\s", "", s)) for s in S] or [0]; m = sum(sl)/len(sl)
        lines = t.splitlines(); li = [l for l in lines if re.match(r"\s*(?:[-*]|\d+\.)\s+", l)]
        per.append({"file": p, "paragraph_cv": st.get("paragraph_cv", 0), "sent_len_mean": round(m, 1),
                    "sent_len_sd": round((sum((x-m)**2 for x in sl)/len(sl))**.5, 1),
                    "colon_per_k": st["colon_per_k"], "bold_per_k": round(len(re.findall(r"\*\*[^*]+\*\*", t))*1000/n, 2),
                    "list_per_k": round(len(li)*1000/n, 2), "formal_conj_per_k": st["formal_conj_per_k"],
                    "bold_label_ratio": round(st["bold_label_list"]["bold_label_items"]/max(1, st["bold_label_list"]["list_items"]), 2)})
    agg = {}
    for k in (per[0].keys() if per else []):
        if k == "file": continue
        v = [x[k] for x in per]; m = sum(v)/len(v); agg[k] = {"mean": round(m, 3), "sd": round((sum((x-m)**2 for x in v)/len(v))**.5, 3)}
    res = {"version": datetime.date.today().isoformat(), "source": "calibration/pass.txt only", "n": len(per), "metrics": agg, "per_file": per,
           "use": "偏离均值 >1.5σ 记 warn，作为 R7 输入；不进门槛",
           "status": "EMPTY — 作者尚未指定满意文章" if not per else "ok"}
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1); print(f"profile: n={len(per)} -> {out}")

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "legacy": legacy_print(legacy_report(sys.argv[2]), "--json" in sys.argv); return
    if cmd == "lint":
        r = lint(sys.argv[2], lg=arg("--lang"), x="--x" in sys.argv, article=arg("--article"))
        if "--json" in sys.argv: print(json.dumps(r, ensure_ascii=False, indent=1)); return
        print(f"# {r['file']} [{r['lang']}] {r['rules_version']}  ban={len(r['hard_bans'])} warn={len(r['warnings'])}")
        for h in r["hard_bans"] + r["warnings"]: print(f"  {h['severity']:4} L{h['line']:<4} {h['rule']:28} 「{h['text']}」→ {h['fix']}" + (f" ({h['note']})" if h.get("note") else ""))
        sys.exit(2 if r["hard_bans"] else 0)
    if cmd == "gate":
        rep = gate(sys.argv[2], arg("--stage", "draft"), arg("--rubric"), arg("--article"), "--x" in sys.argv, arg("--lang"))
        out = arg("--out")
        if out: os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); json.dump(rep, open(out, "w"), ensure_ascii=False, indent=1)
        if "--json" in sys.argv: print(json.dumps(rep, ensure_ascii=False, indent=1))
        print(summary(rep)); sys.exit(0 if rep["gate"]["pass"] else 2)
    if cmd == "test": sys.exit(0 if run_tests() else 1)
    if cmd == "calibrate":
        ok = calibrate()
        if "--no-profile" not in sys.argv: profile()
        sys.exit(0 if ok else 1)
    if cmd == "profile": profile(); return
    if cmd == "rubric-prompt": print(rubric_prompt(sys.argv[2], arg("--article"), arg("--stage", "draft"))); return
    if cmd == "rubric-check": print(json.dumps(rubric_check(sys.argv[2], sys.argv[3]), ensure_ascii=False, indent=1)); return
    print(__doc__); sys.exit(1)

if __name__ == "__main__": main()
