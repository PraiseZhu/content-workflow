#!/usr/bin/env python3
"""
Humanness scoring for WeWrite articles.

2026-10-12 upgrade (de-AI research, see writing-guide.md「去AI味」):
the target is now "reads like a careful human author" (reader perception),
NOT "evades AI detectors". Checks that rewarded performed humanness
(one-line "嗯。" paragraphs, fake self-correction, word-temperature quotas,
negative-emotion floor) are REPORT-ONLY: still computed and shown, never scored.

  Tier 1  (Statistical): sentence-length stddev/range, paragraph variance,
          vocabulary richness (no temperature bonus), adverb density.
  Tier 2  (Pattern):     tiered banned words (hard-ban / once-per-article /
          sentence-start-only / 2+-per-paragraph cluster), real sources.
  Tier 2b (De-AI lint):  ~20 structure/phrasing checks merged from deai_lint.py
          (contrast frames, essence anchors, signposts, aphorisms, parallel pairs,
          triads, bold-label lists, staccato runs, CJK-Latin spaces, ...).
          English drafts use the EN set; --en-gate also gained these checks.
  Tier 3  (LLM): agent score via --tier3.
  Report-only: negative_emotion_ratio, broken_sentences, word_temperature_mix,
          self_correction, style_baseline (distance from the author's own samples).

Weights: with --tier3  T1 40% / T2 20% / T2b 20% / T3 20%
         standalone    T1 50% / T2 25% / T2b 25%

Usage (unchanged CLI, all old flags still work):
    python3 humanness_score.py article.md                    # single score
    python3 humanness_score.py article.md --verbose          # detailed report
    python3 humanness_score.py article.md --json             # full JSON
    python3 humanness_score.py article.md --json --tier3 0.7 # with agent score
    python3 humanness_score.py article.md --en-gate          # English HOW gate (exit 2 = fail)
    python3 humanness_score.py article.md --baseline path.yaml  # optional: other baseline config
"""

import argparse
import difflib
import json
import os
import re
import sys
from pathlib import Path


# ============================================================
# Constants
# ============================================================

# ---- Banned words, tiered (2026-10-12) ----
# Hard ban: any occurrence is a finding.
HARD_BAN_WORDS = [
    # 讲义腔 / 总结句
    "综上所述", "总而言之", "总的来说", "综合来看", "由此可见", "不难发现",
    "通过以上分析", "正如我们所看到的", "值得注意的是", "需要指出的是",
    "不可否认", "毋庸置疑", "众所周知", "显而易见", "不言而喻", "从某种意义上说",
    "与此同时", "不仅如此", "更重要的是", "在此基础上", "作为一个",
    # 空洞拔高
    "非常重要", "至关重要", "具有重要意义", "发挥着重要作用", "意义深远", "影响深远",
    "引发了广泛关注", "引起了热烈讨论",
    # 路标 / 结尾 / 假互动
    "让我们", "话不多说", "本文将", "未来可期", "拭目以待", "这只是开始",
    "希望对你有帮助", "希望对大家有帮助", "你觉得呢", "抛砖引玉",
    # 黑话
    "赋能", "抓手", "颗粒度", "深耕", "老兵", "破局", "双轮驱动",
]
# Only banned at sentence/clause start ("最后一公里""另外两个服务" are fine).
SENTENCE_START_BAN = [
    "首先", "其次", "再者", "最后", "总之", "此外", "另外", "事实上", "可以说",
]
AMBIGUOUS_START_WORDS = {"最后", "另外", "再者"}
# Allowed at most once per article.
ONCE_PER_ARTICLE = [
    "说白了", "说实话", "讲真", "坦白讲", "老实说", "说穿了", "其实吧", "不得不说",
    "有一说一", "本质上", "说到底", "归根结底", "换句话说", "一句话",
    "真正的问题", "核心在于", "关键在于",
]
# Flag only when 2+ of these appear in the same paragraph (engineering terms are
# normal in R&D articles; a cluster is the tell).
PARAGRAPH_CLUSTER_WORDS = [
    "闭环", "链路", "全链路", "托住", "托底", "接住", "兜底", "对齐", "拉齐", "沉淀",
    "落地", "收口", "范式", "重塑", "心智", "底层逻辑", "护城河", "飞轮", "一站式",
    "降本增效", "生态位", "击穿", "打穿",
]
# Backward compatible flat list (other scripts may import BANNED_WORDS).
BANNED_WORDS = HARD_BAN_WORDS + SENTENCE_START_BAN

REAL_SOURCE_PATTERNS = [
    r'[A-Z][a-z]+\s+[A-Z][a-z]+',
    r'[\u4e00-\u9fff]{2,4}(?:表示|指出|认为|写道|提到|说过)',
    r'(?:据|根据|来自)\s*[\u4e00-\u9fff]+(?:报告|数据|研究|调查)',
    r'20[12]\d\s*年',
    r'\d+(?:\.\d+)?%',
    r'(?:亿|万)\s*(?:美元|元|人民币)',
]

NEGATIVE_MARKERS = [
    # 直接负面情绪
    "失望", "糟糕", "扯", "坑", "烂", "差劲", "崩溃", "吐槽", "骂",
    "怒", "烦", "焦虑", "担忧", "不满", "恶心", "可怕", "可悲", "可笑",
    "离谱", "尴尬", "无语", "蠢", "惨", "亏", "危",
    # 绝望/迷茫
    "绝望", "迷茫", "心累", "丧", "后悔", "后怕", "心寒",
    # 欺骗/操控（隐性负面）
    "骗", "忽悠", "割韭菜", "套路", "画大饼", "洗脑",
    # 失败/徒劳
    "白费", "白搭", "没戏", "黄了", "凉了", "废了",
    # 自嘲/自贬
    "傻", "天真", "吃亏", "自嗨", "打脸",
    # 讽刺/反语
    "呵呵", "好吧", "行吧", "真服了",
    # 短语
    "太扯了", "说实话我很失望", "搞什么", "不靠谱", "受不了",
    "受够了", "想哭", "伤心", "苦哈哈", "得过且过",
]

COMMON_ADVERBS = [
    "非常", "十分", "极其", "特别", "相当", "尤其", "格外",
    "更加", "越来越", "逐渐", "不断", "始终", "一直",
    "已经", "正在", "将要", "可能", "大概", "或许",
    "似乎", "显然", "明显", "确实", "果然", "居然",
    "竟然", "简直", "几乎", "完全", "绝对", "必然",
]

COLD_WORDS = [
    "边际", "认知负荷", "信息不对称", "路径依赖", "商业模式", "生态系统", "增量",
    "技术栈", "标准化", "结构性", "规模化", "护城河", "飞轮", "闭环",
    "赛道", "壁垒", "方法论", "底层逻辑", "第一性原理", "杠杆", "复利",
    "ROI", "PMF", "代运营", "供给侧", "需求侧",
]
# 2026-10-12: 说白了/讲真/说实话/坦白讲/老实说/其实吧/这么说吧/懂的都懂 removed —
# they are 假坦诚口头禅 (limited by ONCE_PER_ARTICLE), not a bonus. Temperature
# bands are report-only now.
WARM_WORDS = [
    "怎么说呢", "你想啊", "别急", "慢慢来",
    "有意思的是", "好玩的是", "巧的是", "说来话长", "话说回来",
]
HOT_WORDS = [
    "DNA动了", "格局打开", "遥遥领先", "卷", "内卷", "炸了", "杀疯了", "吃灰",
    "凡尔赛", "标题党", "躺平", "摆烂", "破防", "上头", "内耗",
    "蒸发", "出圈", "降维打击", "弯道超车",
]
WILD_WORDS = [
    "整挺好", "不靠谱", "瞎折腾", "搁这儿", "糊弄", "扯", "嗯",
    "苦哈哈", "傻乎乎", "稀里糊涂", "得了吧", "算了吧",
    "摔了跤", "交学费", "踩坑", "翻车", "栽了",
]

SELF_CORRECTION_PATTERNS = [
    r'不对[，,]', r'准确说', r'算了', r'说错了',
    r'其实不是', r'我记混了', r'应该说', r'更准确地说',
    r'（[^）]{4,}）',  # Chinese parenthetical insertion (≥4 chars)
]

BROKEN_SENTENCE_PATTERNS = [
    r'——(?!.*[，。！？])',
    r'\.{3,}|…',
    r'不对[，,]',
    r'算了',
]

EN_BANNED_WORDS = [
    "delve", "moreover", "furthermore", "in conclusion",
    "it is important to note", "it's important to note",
    "in today's", "let's dive", "tapestry", "landscape of",
    "realm of", "multifaceted", "groundbreaking",
    "this piece is", "this article will", "this post will",
    "in summary", "to summarize", "as an ai",
    # 2026-10-12 additions
    "here's the thing", "let that sink in", "make no mistake", "without further ado",
    "game-changer", "game changer", "ever-evolving", "unlock the",
]

EN_NEGATIVE_MARKERS = [
    "wasted", "empty", "broke", "failed", "silent", "mistake",
    "no one", "thin is", "more expensive", "never hit",
    "lost", "wrong", "cheap part",
]

EN_ADVERBS = [
    "very", "really", "extremely", "particularly", "especially",
    "increasingly", "clearly", "obviously", "simply", "actually",
    "basically", "essentially", "literally", "inherently",
]

EN_SELF_CORRECTION_PATTERNS = [
    r'\bwait[,—]', r"\bthat's not quite", r'\bno[,:] I',
    r'\bmore precisely', r'\bI mean\b', r'\bscratch that',
]

EN_SYLLABUS_RE = re.compile(
    r"\bThis (?:piece|article|post) (?:is|covers|will cover) .{0,60}?(?:things|parts|sections)\b",
    re.I,
)
EN_SPECTATOR_RE = re.compile(
    r"\bI recently watched\b|\bI watched a\b|\bI observed a\b",
    re.I,
)
EN_NEGATIVE_PARALLEL_RES = [
    re.compile(r"\bIt is not\.\s+It is\b", re.I),
    re.compile(r"\bit looks like .+\. It is not\b", re.I),
    re.compile(r"\bwas never .+\. It was\b", re.I),
    re.compile(r"\bnot after .+\.\s+After\b", re.I),
]
EN_BRIEF_RE = re.compile(r"\bthin brief\b|\ba thin brief\b", re.I)
EN_HISTORICAL_MESS_RE = re.compile(r"\bhistorical mess\b", re.I)
EN_LITERARY_DOUBLE_RE = re.compile(
    r"\blost in silence,\s*lost into\b",
    re.I,
)


# ============================================================
# Helpers
# ============================================================

def _detect_lang(text):
    """zh if enough CJK; otherwise treat as English."""
    cjk = len(re.findall(r"[一-鿿]", text))
    return "zh" if cjk >= 20 else "en"


def _clean_article_text(text):
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    text = re.sub(r"^#+\s+.*$", "", text, flags=re.MULTILINE)
    return text.strip()


def _split_sentences(text):
    """Split by language-appropriate sentence endings."""
    if _detect_lang(text) == "en":
        sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 1]
    sentences = re.split(r"[。！？\n]", text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 1]


def _split_paragraphs(text):
    """Split text into paragraphs, excluding headings."""
    return [p.strip() for p in text.split('\n\n')
            if p.strip() and not p.strip().startswith('#')]


def _make_result(score, detail, param=None):
    """Create a check result dict."""
    r = {"score": round(max(0.0, min(1.0, score)), 4), "detail": detail}
    if param is not None:
        r["param"] = param
    else:
        r["param"] = None
    return r


# ============================================================
# Tier 1: Statistical Checks (weight 50%)
# ============================================================

def score_sentence_length_stddev(text):
    """[1.1] Sentence length standard deviation. → sentence_variance"""
    sentences = _split_sentences(text)
    if len(sentences) < 5:
        return _make_result(0.5, "too few sentences to measure", "sentence_variance")
    lengths = [len(s) for s in sentences]
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    stddev = variance ** 0.5
    score = min(1.0, stddev / 25.0)
    return _make_result(score, f"stddev={stddev:.1f} (target ≥15)", "sentence_variance")


def score_sentence_length_range(text):
    """[1.1] Sentence length range (max - min). → sentence_variance"""
    sentences = _split_sentences(text)
    if len(sentences) < 5:
        return _make_result(0.5, "too few sentences", "sentence_variance")
    lengths = [len(s) for s in sentences]
    rng = max(lengths) - min(lengths)
    range_score = min(1.0, rng / 40.0)
    # 2026-10-12: one-line short paragraphs are no longer rewarded (staccato tell).
    lines = text.split('\n')
    short_limit = 24 if _detect_lang(text) == "en" else 5
    short_paras = sum(1 for l in lines if l.strip() and 1 <= len(l.strip()) <= short_limit
                      and not l.strip().startswith('#'))
    return _make_result(range_score, f"range={rng} (target ≥30), short_paras={short_paras} (info only)", "sentence_variance")


def score_paragraph_length_variance(text):
    """[1.3] Paragraph length variance. → paragraph_rhythm"""
    paragraphs = _split_paragraphs(text)
    if len(paragraphs) < 3:
        return _make_result(0.5, "too few paragraphs", "paragraph_rhythm")
    total_pairs = len(paragraphs) - 1
    similar = sum(1 for i in range(total_pairs)
                  if abs(len(paragraphs[i]) - len(paragraphs[i + 1])) <= 20)
    score = 1.0 - (similar / total_pairs) if total_pairs > 0 else 0.5
    return _make_result(score, f"{similar}/{total_pairs} consecutive similar-length pairs", "paragraph_rhythm")


def score_vocabulary_richness(text):
    """[1.2] Type-token ratio + temperature mix. → word_temperature_bias"""
    if _detect_lang(text) == "en":
        words = re.findall(r"[A-Za-z']+", text.lower())
        if len(words) < 50:
            return _make_result(0.5, "too few English words", "word_temperature_bias")
        ttr = len(set(words)) / len(words)
        ttr_score = min(1.0, ttr / 0.55)
        return _make_result(ttr_score, f"word_ttr={ttr:.3f}", None)
    cjk_chars = re.findall(r'[\u4e00-\u9fff]', text)
    if len(cjk_chars) < 20:
        return _make_result(0.5, "too few CJK characters", "word_temperature_bias")
    bigrams = [cjk_chars[i] + cjk_chars[i + 1] for i in range(len(cjk_chars) - 1)]
    ttr = len(set(bigrams)) / len(bigrams) if bigrams else 0
    ttr_score = min(1.0, ttr / 0.7)
    # 2026-10-12: temperature-band bonus removed (it rewarded slang quotas).
    return _make_result(ttr_score, f"bigram_ttr={ttr:.3f}", None)


def score_negative_emotion_ratio(text):
    """[1.4] Negative emotion ratio. → emotional_arc"""
    sentences = _split_sentences(text)
    if not sentences:
        return _make_result(0.5, "no sentences", "emotional_arc")
    markers = EN_NEGATIVE_MARKERS if _detect_lang(text) == "en" else NEGATIVE_MARKERS
    negative_count = sum(1 for s in sentences
                         if any(m in s.lower() if _detect_lang(text) == "en" else m in s for m in markers))
    ratio = negative_count / len(sentences)
    score = min(1.0, ratio / 0.25)
    return _make_result(score, f"negative={negative_count}/{len(sentences)} ({ratio:.0%}, target ≥20%)", "emotional_arc")


def score_adverb_density(text):
    """[1.5] Adverb density control. → adverb_max_per_100"""
    char_count = len(text)
    if char_count < 50:
        return _make_result(0.5, "text too short", "adverb_max_per_100")
    adverbs = EN_ADVERBS if _detect_lang(text) == "en" else COMMON_ADVERBS
    hay = text.lower() if _detect_lang(text) == "en" else text
    total_adverbs = sum(hay.count(adv) for adv in adverbs)
    density = total_adverbs / char_count * 100
    sentences = _split_sentences(text)
    consecutive_adverb_starts = 0
    for i in range(len(sentences) - 1):
        a_starts = any(sentences[i].lower().startswith(adv) for adv in adverbs)
        b_starts = any(sentences[i + 1].lower().startswith(adv) for adv in adverbs)
        if a_starts and b_starts:
            consecutive_adverb_starts += 1
    score = 1.0
    if density > 3.0:
        score -= min(0.5, (density - 3.0) * 0.1)
    score -= consecutive_adverb_starts * 0.3
    return _make_result(score, f"density={density:.1f}/100chars, consecutive_starts={consecutive_adverb_starts}", "adverb_max_per_100")


# ============================================================
# Tier 2: Pattern Checks (weight 30%)
# ============================================================

def _sentence_start_hits(text, words):
    """Words at the start of a sentence/clause/line (after 。！？；：\n or list marker)."""
    hits = []
    for w in words:
        # 最后/另外 are ambiguous without a comma ("最后一公里""另外两个服务")
        tail = r'(?:\*\*)?[，,、：:]' if w in AMBIGUOUS_START_WORDS else ''
        pat = r'(?:^|[。！？；：!?;:\n]|^\s*[-*>]\s*)\s*(?:\*\*)?' + re.escape(w) + tail
        for m in re.finditer(pat, text, flags=re.M):
            hits.append(w)
    return hits


def banned_word_findings(text):
    """Tiered banned-word findings (zh). Returns dict of lists."""
    hard = [w for w in HARD_BAN_WORDS if w in text]
    start = _sentence_start_hits(text, SENTENCE_START_BAN)
    once = [f"{w}×{text.count(w)}" for w in ONCE_PER_ARTICLE if text.count(w) > 1]
    clusters = []
    for i, p in enumerate(_split_paragraphs(text)):
        found = [w for w in PARAGRAPH_CLUSTER_WORDS if w in p]
        # 全链路 contains 链路; count distinct surface words only once
        if "全链路" in found and "链路" in found:
            found.remove("链路")
        if len(found) >= 2:
            clusters.append(f"P{i+1}:{'/'.join(found)}")
    return {"hard": hard, "sentence_start": start, "once_exceeded": once, "para_cluster": clusters}


def score_banned_words(text):
    """[2.1] Tiered banned words. → null (hard rule, no config param)"""
    if _detect_lang(text) == "en":
        lower = text.lower()
        found = [w for w in EN_BANNED_WORDS if w in lower]
        score = max(0.0, 1.0 - len(found) * 0.2)
        detail = "0 banned words" if not found else f"{len(found)} found: {found[:5]}"
        return _make_result(score, detail, None)
    f = banned_word_findings(text)
    penalty = (len(f["hard"]) * 0.2 + len(f["sentence_start"]) * 0.15
               + len(f["once_exceeded"]) * 0.15 + len(f["para_cluster"]) * 0.1)
    score = max(0.0, 1.0 - penalty)
    parts = [f"{k}={v[:5]}" for k, v in f.items() if v]
    detail = "0 banned words" if not parts else "; ".join(parts)
    r = _make_result(score, detail, None)
    r["findings"] = f
    return r


def score_broken_sentences(text):
    """[2.2] Broken/incomplete sentence patterns. → broken_sentence_rate"""
    count = 0
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for p in BROKEN_SENTENCE_PATTERNS:
            count += len(re.findall(p, line))
        if 1 <= len(line) <= 10 and not line.startswith('#'):
            count += 1
    char_count = len(text)
    expected = max(3, char_count / 500 * 3)
    score = min(1.0, count / expected)
    return _make_result(score, f"{count} broken structures (expected ≥{expected:.0f})", "broken_sentence_rate")


def score_real_sources(text):
    """[3.1] Real external source indicators. → real_data_density"""
    count = 0
    for pattern in REAL_SOURCE_PATTERNS:
        count += len(re.findall(pattern, text))
    score = min(1.0, count / 5.0)
    return _make_result(score, f"{count} real-source indicators (target ≥5)", "real_data_density")


def score_word_temperature_mix(text):
    """[1.2] Word temperature band coverage. → word_temperature_bias"""
    if _detect_lang(text) == "en":
        return _make_result(0.5, "skipped for English (CJK temperature bands)", "word_temperature_bias")
    found_temps = sum([
        any(w in text for w in COLD_WORDS),
        any(w in text for w in WARM_WORDS),
        any(w in text for w in HOT_WORDS),
        any(w in text for w in WILD_WORDS),
    ])
    score = max(0.0, (found_temps - 1) / 3.0)
    return _make_result(score, f"{found_temps}/4 temperature bands", "word_temperature_bias")


def score_self_correction(text):
    """[2.2] Self-correction and parenthetical patterns. → self_correction_rate"""
    patterns = EN_SELF_CORRECTION_PATTERNS if _detect_lang(text) == "en" else SELF_CORRECTION_PATTERNS
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text, flags=re.I if _detect_lang(text) == "en" else 0))
    score = min(1.0, count / 3.0)
    return _make_result(score, f"{count} self-corrections/insertions (target ≥3)", "self_correction_rate")


# ============================================================
# Tier 2b: De-AI lint (merged from deai_lint.py, 2026-10-12)
# ============================================================
# Each check returns hits; a hit beyond its limit is one "violation".
# These are prompts for a human re-read, not authorship verdicts.

ZH_LINT_PATTERNS = {
    # 字面「不是…而是」: 作者的固定偏好，全文 0
    "not_x_but_y": r"不是[^。！？\n]{1,30}[，,]?\s*而是",
    # 其它对照骨架变体：全文 ≤1，且两端须是实词
    "contrast_frame": r"不在于[^。\n]{1,30}而在于|不仅仅?是[^。\n]{1,30}(?:更|还|也)是|与其说?[^。\n]{1,30}不如|问题不在[^。\n]{1,20}[，,]?(?:而)?在|(?:不|没)值钱[^。\n]{0,12}值钱的是|变得廉价[^。\n]{0,12}变得稀缺|只说中了|看似[^。\n]{1,20}(?:实则|本质)|表面上?[^。\n]{1,20}背后",
    "essence_anchor": r"本质上|本质是|核心在于|关键在于|说到底|归根结底|究其根本|真正(?:的)?(?:问题|难点|价值|决定)|真正[^。\n]{0,8}的是",
    "signpost": r"下面(?:先|我们|来|就)?(?:讲|说|看|聊|拆)|接下来(?:我们|我)?(?:看|讲|聊)|本文(?:将|会)|话不多说|让我们|我们来看|再看全貌|逐段拆|划重点|敲黑板",
    "aphorism": r"的尽头是|是新的(?:货币|石油|护城河)|才是(?:真正的|核心|关键)|一切[^。\n]{1,6}皆|好[^。\n]{1,6}比好[^。\n]{1,6}更",
    "fake_candor": r"说白了|说实话|讲真|坦白讲|老实说|这么说吧|说穿了|其实吧|懂的都懂|不得不说|有一说一",
    "fake_engage": r"你觉得呢|欢迎(?:在)?评论|评论区见|你有没有[^。\n]{0,15}(?:经历|过)？|点赞|在看|转发给",
    "generic_close": r"未来可期|拭目以待|相信在不久|展望未来|任重道远|值得期待|这既是挑战|只是开始",
    "false_agency": r"(?:组织|流程|系统|机制|数据|市场|趋势|行业|时代|代码)(?:自己|会自己|开始|正在)?(?:进化|生长|说话|告诉我们|做出选择|在奖励|在惩罚|学会)",
    "translationese": r"进行(?:了)?[\u4e00-\u9fff]{2}|作出|予以|加以|被[^。，\n]{1,12}所|将被|在[^。，\n]{1,15}的情况下|对于[^。\n]{1,12}而言",
    "ai_disclaimer": r"AI辅助(?:创作|写作|生成)|由AI(?:生成|辅助)|人工智能辅助创作|本文(?:由|为)[^。\n]{0,10}AI",
    "heading_numeral": r"^#{1,6}\s*(?:[一二三四五六七八九十]+[、.．:：\s]|第[一二三四五六七八九十]+[章节部分]|§)",
    "cjk_latin_space": r"[\u4e00-\u9fff][ \t]+[A-Za-z0-9]|[A-Za-z0-9][ \t]+[\u4e00-\u9fff]",
}
ZH_LINT_LIMITS = {
    "not_x_but_y": 0, "contrast_frame": 1, "essence_anchor": 2, "signpost": 0,
    "aphorism": 0, "fake_candor": 1, "fake_engage": 0, "generic_close": 0,
    "false_agency": 0, "translationese": 4, "ai_disclaimer": 0, "heading_numeral": 0,
    "cjk_latin_space": 0,
}

EN_LINT_PATTERNS = {
    "negative_parallel": r"\b(?:not|isn't|wasn't|aren't|doesn't|don't)\b[^.!?\n]{1,60}?(?:,|;|:|—|–|\.)\s*(?:it's|it is|but|they're|that's|this is)\b|\bnot just\b|\bnot only\b[^.]{1,60}\bbut\b|\b(?:isn't|wasn't) the (?:problem|point|question)\b",
    "rather_than": r"\brather than\b",
    "hook_phrase": r"here's the thing|here's why|here's what|the truth is|let that sink in|make no mistake|the kicker|plot twist|but here's|the real (?:question|problem|story)|what most people (?:miss|don't)",
    "ing_tail": r",\s*(?:highlighting|underscoring|showcasing|reflecting|emphasizing|ensuring|fostering|demonstrating|signaling)\b",
    "copula_avoid": r"\b(?:serves as|stands as|acts as|functions as|boasts|represents a|marks a)\b",
    "ai_vocab": r"\b(?:delve|tapestry|testament|pivotal|crucial|underscore[sd]?|showcas\w+|landscape|realm|seamless\w*|robust|leverage[sd]?|multifaceted|foster\w*|quietly|navigate|unlock\w*|game[- ]changer|paradigm|intricate|vibrant|meticulous\w*|ever-evolving|prioritiz\w+|dependable)\b",
    "signpost": r"\b(?:let's (?:dive|explore|look)|in this (?:article|piece|post|section)|now that we've|as mentioned (?:earlier|above)|in conclusion|in summary|to sum up|without further ado)\b",
    "real_inflation": r"\b(?:genuinely|truly)\b",
    "false_agency": r"\b(?:the data|the market|the system|the org(?:anization)?|the culture|the decision) (?:tells|rewards|decides|shifts|emerges|wants|knows)\b",
    "generic_close": r"\b(?:the future (?:is|belongs)|only time will tell|one thing is (?:clear|certain)|the question is no longer|it's just the beginning)\b",
    "ai_disclaimer": r"\b(?:written|drafted|created) with (?:the help of )?AI\b|\bAI[- ]assist(?:ed|ance)\b",
}
EN_LINT_LIMITS = {
    "negative_parallel": 1, "rather_than": 2, "hook_phrase": 0, "ing_tail": 1,
    "copula_avoid": 1, "ai_vocab": 3, "signpost": 0, "real_inflation": 2,
    "false_agency": 0, "generic_close": 0, "ai_disclaimer": 0,
}


def _keep_lines(m):
    return "\n" * m.group(0).count("\n")


def _line_preserving_body(text):
    """Frontmatter and headings blanked but line count kept, so lint line
    numbers match the source file."""
    t = re.sub(r"^---\n.*?\n---\n", _keep_lines, text, count=1, flags=re.DOTALL)
    return t


def _strip_for_lint(text):
    t = re.sub(r"```.*?```", _keep_lines, text, flags=re.S)
    t = re.sub(r"`[^`\n]*`", "", t)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"\]\([^)]*\)", "]", t)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"<!--.*?-->", _keep_lines, t, flags=re.S)
    t = re.sub(r"^[ \t]*\|.*\|[ \t]*$", "", t, flags=re.M)  # tables
    return t


def _lineno(text, idx):
    return text.count("\n", 0, idx) + 1


def de_ai_lint(text, raw_text=None):
    """Run the de-AI lint. `text` = cleaned body; `raw_text` keeps headings
    (for heading checks). Returns {"lang", "hits", "violations", "structure"}."""
    lang = _detect_lang(text)
    body = _strip_for_lint(text)
    head_src = _strip_for_lint(raw_text) if raw_text is not None else body
    pats, limits = (EN_LINT_PATTERNS, EN_LINT_LIMITS) if lang == "en" else (ZH_LINT_PATTERNS, ZH_LINT_LIMITS)
    hits = {}
    for k, p in pats.items():
        src_t = head_src if k == "heading_numeral" else body
        flags = re.M | (re.I if lang == "en" else 0)
        hits[k] = [(_lineno(src_t, m.start()), m.group(0)[:40]) for m in re.finditer(p, src_t, flags)]
    violations = {k: len(v) - limits[k] for k, v in hits.items() if k in limits and len(v) > limits[k]}

    # ---- structural checks ----
    S = _split_sentences(body)
    P = _split_paragraphs(body)
    L = (lambda s: len(s.split())) if lang == "en" else (lambda s: len(re.sub(r"\s", "", s)))
    st = {}
    short = 5 if lang == "en" else 8
    runs, cur = [], []
    for s in S + ["x" * 100]:
        if L(s) <= short:
            cur.append(s)
        else:
            if len(cur) >= 3:
                runs.append(" / ".join(cur)[:60])
            cur = []
    st["staccato_runs"] = runs
    head = (lambda s: " ".join(s.lower().split()[:2])) if lang == "en" else (lambda s: re.sub(r"[\s*#>\-]", "", s)[:2])
    st["same_opener_x3"] = sorted({head(S[i]) for i in range(len(S) - 2)
                                   if head(S[i]) and head(S[i]) == head(S[i + 1]) == head(S[i + 2])})
    lines = body.splitlines()
    bold_items = sum(1 for l in lines if re.match(r"\s*(?:[-*]|\d+\.)\s*\*\*[^*]{1,30}\*\*", l))
    list_items = sum(1 for l in lines if re.match(r"\s*(?:[-*]|\d+\.)\s+", l))
    st["bold_label_list"] = {"bold_label_items": bold_items, "list_items": list_items}
    if lang == "zh":
        tri = re.findall(r"[：:][^。；\n]{1,40}?、[^。；\n]{1,40}?(?:、|和|与|及)[^。；、\n]{1,40}[。；\n]", body)
        num3 = re.findall(r"三(?:件事|个(?:问题|层面|维度|方面)|大(?:原因|趋势|变化))", body)
    else:
        tri = re.findall(r"\b\w+(?: \w+){0,3}, \w+(?: \w+){0,3},? and \w+(?: \w+){0,3}\b", body)
        num3 = re.findall(r"\bthree (?:things|ways|reasons|lessons)\b", body, re.I)
    st["triads"] = {"list_of_three": len(tri), "three_label": len(num3)}
    pairs = []
    if lang == "zh":
        for s in S:
            cl = [c for c in re.split(r"[，；,;]", s) if len(c) >= 4]
            for a, b in zip(cl, cl[1:]):
                if abs(len(a) - len(b)) <= 1 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.4:
                    pairs.append(f"{a}｜{b}")
    st["parallel_pairs"] = pairs[:8]
    stamp_re = r"(这说明|这意味着|换句话说|也就是说|所以说|可见|一句话)[^。]{0,40}。?$" if lang == "zh" else \
               r"^(?:This means|In other words|That's why|The lesson)\b"
    stamp = sum(1 for p in P if re.search(stamp_re, p.split("\n")[-1].strip(), re.M))
    st["stamp_para_ratio"] = round(stamp / len(P), 2) if P else 0
    n = max(1, len(re.sub(r"\s", "", body)) if lang == "zh" else len(body.split()))
    per = 1000 / n
    if lang == "zh":
        st["dash_per_k"] = round(body.count("——") * per, 2)
        st["colon_per_k"] = round(body.count("：") * per, 2)
        st["scare_quotes_per_k"] = round(len(re.findall(r"[“「][^”」]{1,4}[”」]", body)) * per, 2)
        st["formal_conj_per_k"] = round(len(re.findall(
            r"以及|并且|而且|因此|然而|同时|此外|从而|进而|因而|不仅", body)) * per, 2)
        st["de_chain"] = [c.strip()[:30] for c in re.split(r"[，。；：！？,\n]", body) if c.count("的") >= 3][:6]
        hedge = r"可能|或许|也许|一定程度上|某种程度上|往往|通常|大概率"
        st["hedge_stack"] = [s[:40] for s in S if len(re.findall(hedge, s)) >= 2][:6]
    else:
        st["dash_per_k"] = round((body.count("—") + body.count("–") + body.count(" -- ")) * per, 2)

    # structural violations
    sv = {}
    if runs:
        sv["staccato_runs"] = len(runs)
    if st["same_opener_x3"]:
        sv["same_opener_x3"] = len(st["same_opener_x3"])
    if bold_items > 6 and list_items and bold_items / list_items > 0.5:
        sv["bold_label_list"] = 1
    if len(pairs) > 1:
        sv["parallel_pairs"] = len(pairs) - 1
    if st["triads"]["list_of_three"] > max(2, n / 1000 * 2):
        sv["triads"] = 1
    if st["stamp_para_ratio"] > 0.15:
        sv["stamp_para_ratio"] = 1
    if lang == "zh":
        if st["formal_conj_per_k"] > 4:
            sv["formal_conj_per_k"] = 1
        if st["de_chain"]:
            sv["de_chain"] = len(st["de_chain"])
        if st["hedge_stack"]:
            sv["hedge_stack"] = len(st["hedge_stack"])
    elif st["dash_per_k"] > 2:  # roughly >2 em dashes per 1000 words
        sv["dash_per_k"] = 1
    violations.update({f"struct:{k}": v for k, v in sv.items()})
    return {"lang": lang, "hits": {k: v for k, v in hits.items() if v},
            "violations": violations, "structure": st}


def score_de_ai_lint(text, raw_text=None):
    """[2b] De-AI lint as a 0-1 score: each violation unit costs 0.08."""
    lint = de_ai_lint(text, raw_text)
    units = sum(lint["violations"].values())
    score = max(0.0, 1.0 - units * 0.08)
    detail = "no violations" if not units else \
        f"{units} violation units: " + ", ".join(f"{k}+{v}" for k, v in sorted(lint["violations"].items()))
    r = _make_result(score, detail, None)
    r["lint"] = lint
    return r


# ============================================================
# Style baseline (distance from the author's own past articles)
# ============================================================
DEFAULT_BASELINE_CONFIG = Path(__file__).resolve().parent.parent / "references" / "style-baseline.yaml"


def _load_baseline_config(path):
    path = Path(path)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # pyyaml is in requirements.txt
        return yaml.safe_load(text) or {}
    except ImportError:
        # minimal fallback: only "samples:" list of "- path" lines
        samples, in_s = [], False
        for line in text.splitlines():
            if re.match(r"^samples:\s*(\[\s*\])?\s*$", line):
                in_s = True
                continue
            if in_s and re.match(r"^\s*-\s+", line):
                samples.append(line.split("-", 1)[1].strip().strip('"\''))
            elif in_s and line.strip() and not line.startswith(" "):
                in_s = False
        return {"samples": samples}


def style_metrics(text):
    """Distribution-level metrics used for baseline comparison."""
    clean = _clean_article_text(text)
    body = _strip_for_lint(clean)
    lang = _detect_lang(body)
    S = _split_sentences(body)
    P = _split_paragraphs(body)
    L = (lambda s: len(s.split())) if lang == "en" else (lambda s: len(re.sub(r"\s", "", s)))
    sl = [L(s) for s in S] or [0]
    pl = [L(p) for p in P] or [0]
    mean = lambda xs: sum(xs) / len(xs)
    sd = lambda xs: (sum((x - mean(xs)) ** 2 for x in xs) / len(xs)) ** 0.5
    n = max(1, sum(pl))
    lines = body.splitlines()
    list_items = sum(1 for l in lines if re.match(r"\s*(?:[-*]|\d+\.)\s+", l))
    return {
        "avg_sentence_len": round(mean(sl), 2),
        "sentence_len_sd": round(sd(sl), 2),
        "paragraph_cv": round(sd(pl) / mean(pl), 3) if mean(pl) else 0,
        "colon_per_k": round((body.count("：") + body.count(":")) * 1000 / n, 2),
        "dash_per_k": round((body.count("——") + body.count("—")) * 1000 / n, 2),
        "bold_per_k": round(body.count("**") / 2 * 1000 / n, 2),
        "list_line_ratio": round(list_items / max(1, len([l for l in lines if l.strip()])), 3),
        "formal_conj_per_k": round(len(re.findall(r"以及|并且|而且|因此|然而|同时|此外|从而|进而|因而", body)) * 1000 / n, 2),
    }


def style_baseline_report(text, config_path=None):
    """Compare the article with the author's own samples (report-only).
    Returns None when no samples are configured (TODO: 作者 picks 3-5)."""
    cfg = _load_baseline_config(config_path or DEFAULT_BASELINE_CONFIG)
    if not cfg or not cfg.get("samples"):
        return {"status": "not_configured",
                "note": "TODO: add 3-5 of the author's own past articles to references/style-baseline.yaml"}
    base_dir = Path(config_path or DEFAULT_BASELINE_CONFIG).resolve().parent
    z_limit = float(cfg.get("z_threshold", 1.5))
    rows, missing = [], []
    for s in cfg["samples"]:
        p = Path(os.path.expanduser(str(s)))
        if not p.is_absolute():
            p = base_dir / p
        if p.exists():
            rows.append(style_metrics(p.read_text(encoding="utf-8")))
        else:
            missing.append(str(s))
    if len(rows) < 2:
        return {"status": "too_few_samples", "found": len(rows), "missing": missing}
    art = style_metrics(text)
    out = {}
    for k, v in art.items():
        xs = [r[k] for r in rows]
        m = sum(xs) / len(xs)
        sd = (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5
        z = (v - m) / sd if sd > 1e-9 else (0.0 if abs(v - m) < 1e-9 else float("inf"))
        out[k] = {"article": v, "baseline_mean": round(m, 3), "baseline_sd": round(sd, 3),
                  "z": round(z, 2) if z != float("inf") else "inf"}
    off = [k for k, d in out.items() if d["z"] == "inf" or abs(d["z"]) > z_limit]
    return {"status": "ok", "samples": len(rows), "missing": missing,
            "z_threshold": z_limit, "metrics": out, "off_baseline": off}


# ============================================================
# Tier Runners
# ============================================================

TIER1_CHECKS = [
    ("sentence_length_stddev", score_sentence_length_stddev),
    ("sentence_length_range", score_sentence_length_range),
    ("paragraph_length_variance", score_paragraph_length_variance),
    ("vocabulary_richness", score_vocabulary_richness),
    ("negative_emotion_ratio", score_negative_emotion_ratio),
    ("adverb_density", score_adverb_density),
]

TIER2_CHECKS = [
    ("banned_words", score_banned_words),
    ("broken_sentences", score_broken_sentences),
    ("real_sources", score_real_sources),
    ("word_temperature_mix", score_word_temperature_mix),
    ("self_correction", score_self_correction),
]

# Computed and shown, but excluded from means, composite and param_scores.
# They rewarded performed humanness (playbook R001; writing-guide 去AI味).
REPORT_ONLY_CHECKS = {
    "negative_emotion_ratio", "broken_sentences", "word_temperature_mix", "self_correction",
}


def _tier_summary(results, n_checks):
    scores = [d["score"] for k, d in results.items()
              if not k.startswith("_") and not d.get("report_only")]
    return {
        "count": n_checks,
        "scored_count": len(scores),
        "mean_score": round(sum(scores) / len(scores), 4) if scores else 0,
        "scores": [round(s, 4) for s in scores],
    }


def run_tier(checks, text):
    """Run a tier of checks. Returns dict keyed by check name + _summary."""
    results = {}
    for name, fn in checks:
        r = fn(text)
        if name in REPORT_ONLY_CHECKS:
            r["report_only"] = True
            r["detail"] += " [report-only, not scored]"
        results[name] = r
    results["_summary"] = _tier_summary(results, len(checks))
    return results


# ============================================================
# Calibration (bell-curve + over-optimization penalty)
# ============================================================

# Human article baselines (from 15 example articles, 2026-03-30).
# 2026-10-12: banned_words removed (a clean article scored 0 under the curve);
# broken_sentences/self_correction are report-only. Overshoot penalty softened:
# exceeding the human average now costs at most 30% instead of 100%.
_BELL_CURVE_CHECKS = {
    # sentence_length_range dropped: its 0.71 center was calibrated on the old
    # range+short-paragraph blend, which no longer exists.
    "paragraph_length_variance": 0.52,
}
_BELL_OVERSHOOT_MAX_PENALTY = 0.3


def _bell_curve(raw_score, center):
    """Below center: linear rise. Above center: soft quadratic penalty (≤30%)."""
    if center <= 0:
        return raw_score
    if raw_score <= center:
        return raw_score / center
    overshoot = (raw_score - center) / (1.0 - center) if center < 1 else 0
    return max(0.0, 1.0 - _BELL_OVERSHOOT_MAX_PENALTY * overshoot * overshoot)


def calibrate_tiers(tier1, tier2):
    """Apply bell-curve calibration and over-optimization penalty in-place."""
    for tier in [tier1, tier2]:
        for name, data in tier.items():
            if name.startswith("_") or data.get("report_only"):
                continue
            if name in _BELL_CURVE_CHECKS:
                raw = data["score"]
                center = _BELL_CURVE_CHECKS[name]
                calibrated = round(max(0.0, min(1.0, _bell_curve(raw, center))), 4)
                data["raw_score"] = raw
                data["score"] = calibrated
                data["detail"] += f" [calibrated from {raw:.2f}, center={center}]"

    all_scores = [d["score"] for tier in [tier1, tier2] for n, d in tier.items()
                  if not n.startswith("_") and not d.get("report_only")]
    high_count = sum(1 for s in all_scores if s > 0.8)
    over_opt_ratio = high_count / len(all_scores) if all_scores else 0
    # 2026-10-12: only statistical over-polish triggers this; clean pattern
    # checks (banned words, lint) are the goal, not suspicious.
    stat_scores = [d["score"] for n, d in tier1.items()
                   if not n.startswith("_") and not d.get("report_only")]
    stat_high = sum(1 for s in stat_scores if s > 0.95) / len(stat_scores) if stat_scores else 0
    penalty = 0.85 if (over_opt_ratio >= 0.6 and stat_high >= 0.75) else 1.0
    if penalty < 1.0:
        for tier in [tier1, tier2]:
            for name, data in tier.items():
                if not name.startswith("_") and not data.get("report_only"):
                    data["score"] = round(data["score"] * penalty, 4)

    for tier, n in [(tier1, len(TIER1_CHECKS)), (tier2, len(TIER2_CHECKS))]:
        tier["_summary"] = _tier_summary(tier, n)
    return penalty


# ============================================================
# Composite Score
# ============================================================

def compute_composite(tier1, tier2, tier3_score=None, tier2b=None):
    """Compute composite score (0=human, 100=AI).

    With tier3:  T1=40%, T2=20%, T2b=20%, T3=20%
    Without:     T1=50%, T2=25%, T2b=25%
    (Legacy call without tier2b keeps the old 50/30/20 and 62.5/37.5 weights.)
    """
    t1_mean = tier1["_summary"]["mean_score"]
    t2_mean = tier2["_summary"]["mean_score"]
    if tier2b is None:
        if tier3_score is not None:
            humanness = t1_mean * 0.50 + t2_mean * 0.30 + tier3_score * 0.20
            weights = {"tier1": 0.50, "tier2": 0.30, "tier3": 0.20}
        else:
            humanness = t1_mean * 0.625 + t2_mean * 0.375
            weights = {"tier1": 0.625, "tier2": 0.375}
    else:
        t2b = tier2b["_summary"]["mean_score"]
        if tier3_score is not None:
            humanness = t1_mean * 0.40 + t2_mean * 0.20 + t2b * 0.20 + tier3_score * 0.20
            weights = {"tier1": 0.40, "tier2": 0.20, "tier2b": 0.20, "tier3": 0.20}
        else:
            humanness = t1_mean * 0.50 + t2_mean * 0.25 + t2b * 0.25
            weights = {"tier1": 0.50, "tier2": 0.25, "tier2b": 0.25}
    composite = round((1 - humanness) * 100, 2)
    return composite, weights


def build_param_scores(tier1, tier2):
    """Flat param→score map for optimization (report-only checks excluded)."""
    param_map = {}
    for tier in [tier1, tier2]:
        for name, data in tier.items():
            if name.startswith("_") or data.get("report_only"):
                continue
            param = data.get("param")
            if param is None:
                continue
            param_map.setdefault(param, []).append(data["score"])
    return {p: round(sum(s) / len(s), 4) for p, s in param_map.items()}


# ============================================================
# Main API
# ============================================================

# Generalized negative parallelism (2026-10-12) — counted together with the
# original four fingerprints toward max_negative_parallel.
EN_NEGATIVE_PARALLEL_GENERAL_RE = re.compile(EN_LINT_PATTERNS["negative_parallel"], re.I)
EN_GATE_HARD = ["hook_phrase", "signpost", "generic_close"]
EN_GATE_WARN = ["ing_tail", "copula_avoid", "ai_vocab", "real_inflation", "false_agency",
                "rather_than", "ai_disclaimer"]


def english_how_gate(text, max_emdash=5, max_negative_parallel=2, return_warnings=False):
    """Fail-closed HOW checks for English X drafts. Returns (ok, findings)
    (or (ok, findings, warnings) when return_warnings=True).

    Hard failures: 2026-08-20 fingerprints (syllabus TOC, spectator voice,
    em-dash abuse, HR 'brief', literary doubling, CJK in body) plus, since
    2026-10-12, generalized negative parallelism, hook phrases, signposting,
    generic future closers. Warnings (non-blocking): -ing tails, copula
    avoidance, AI vocabulary over limit, real/truly inflation, false agency,
    AI disclaimer.
    """
    body = _clean_article_text(text)
    lint_body = _strip_for_lint(body)
    findings, warnings = [], []
    emdash = body.count("—") + body.count("–")
    if emdash > max_emdash:
        findings.append(f"emdash={emdash} (max {max_emdash})")
    if EN_SYLLABUS_RE.search(body):
        findings.append("syllabus_toc: 'This piece is N things'")
    if EN_SPECTATOR_RE.search(body):
        findings.append("spectator_voice: watched/observed instead of lived")
    np_hits = sum(len(p.findall(body)) for p in EN_NEGATIVE_PARALLEL_RES)
    np_general = len(EN_NEGATIVE_PARALLEL_GENERAL_RE.findall(lint_body))
    np_total = max(np_hits, np_general)
    if np_total > max_negative_parallel:
        findings.append(f"negative_parallel={np_total} (max {max_negative_parallel})")
    if EN_BRIEF_RE.search(body):
        findings.append("hr_brief: 'thin brief' — use handoff")
    if EN_HISTORICAL_MESS_RE.search(body):
        findings.append("flattened_baggage: 'historical mess' — use old baggage / legacy constraints")
    if EN_LITERARY_DOUBLE_RE.search(body):
        findings.append("literary_double: 'lost in silence, lost into'")
    if re.search(r"[一-鿿]", body):
        findings.append("cjk_in_english_body")
    for k in EN_GATE_HARD + EN_GATE_WARN:
        ms = [m.group(0) for m in re.finditer(EN_LINT_PATTERNS[k], lint_body, re.I | re.M)]
        if len(ms) > EN_LINT_LIMITS[k]:
            msg = f"{k}={len(ms)} (max {EN_LINT_LIMITS[k]}): {ms[:4]}"
            (findings if k in EN_GATE_HARD else warnings).append(msg)
    if return_warnings:
        return (not findings, findings, warnings)
    return (not findings, findings)


# Lint keys that block push regardless of composite (the author's standing rules).
DE_AI_BLOCKING = ["not_x_but_y", "signpost", "aphorism", "generic_close", "fake_engage",
                  "ai_disclaimer", "heading_numeral", "cjk_latin_space"]


def score_article(text, verbose=False, tier3_score=None, baseline_config=None):
    """Score an article. Returns full results dict."""
    clean = _clean_article_text(text)
    lang = _detect_lang(clean)

    tier1 = run_tier(TIER1_CHECKS, clean)
    tier2 = run_tier(TIER2_CHECKS, clean)
    over_opt_penalty = calibrate_tiers(tier1, tier2)
    lp = _line_preserving_body(text)
    lint_body = re.sub(r"^#+\s+.*$", "", lp, flags=re.MULTILINE)
    lint_result = score_de_ai_lint(lint_body, lp)
    tier2b = {"de_ai_lint": lint_result}
    tier2b["_summary"] = {"count": 1, "scored_count": 1,
                          "mean_score": lint_result["score"], "scores": [lint_result["score"]]}
    composite, weights = compute_composite(tier1, tier2, tier3_score, tier2b=tier2b)
    param_scores = build_param_scores(tier1, tier2)

    result = {
        "composite_score": composite,
        "tier1": tier1,
        "tier2": tier2,
        "tier2b": tier2b,
        "tier3": {
            "score": tier3_score,
            "source": "agent" if tier3_score is not None else "not_available",
        },
        "weights": weights,
        "param_scores": param_scores,
        "report_only": sorted(REPORT_ONLY_CHECKS),
        "over_optimization_penalty": over_opt_penalty,
        "style_baseline": style_baseline_report(text, baseline_config),
        "char_count": len(clean),
        "lang": lang,
    }
    # Blocking de-AI gate (zh): composite < 30 alone is not enough to push.
    if lang == "zh":
        v = lint_result["lint"]["violations"]
        blocking = [f"{k}+{v[k]}" for k in DE_AI_BLOCKING if k in v]
        hard = tier2["banned_words"].get("findings", {}).get("hard", [])
        if hard:
            blocking.append(f"hard_banned={hard}")
        result["de_ai_gate"] = {"ok": not blocking, "blocking": blocking}
    if lang == "en":
        ok, findings, warns = english_how_gate(text, return_warnings=True)
        result["en_gate"] = {"ok": ok, "findings": findings, "warnings": warns}

    if verbose:
        _print_verbose(result)

    return result


def _bar(score):
    return "█" * int(score * 10) + "░" * (10 - int(score * 10))


def _print_verbose(result):
    """Print a human-readable report."""
    composite = result["composite_score"]
    print(f"\n{'=' * 60}")
    print(f"HUMANNESS SCORE: {composite:.1f}/100 (lower = more human)")
    print(f"{'=' * 60}")

    for tier_name, tier_label in [("tier1", "Tier 1 — Statistical"), ("tier2", "Tier 2 — Pattern")]:
        tier = result[tier_name]
        summary = tier["_summary"]
        weight = result["weights"].get(tier_name, 0)
        print(f"\n{tier_label} (weight {weight:.0%}, mean {summary['mean_score']:.2f})")
        for name, data in tier.items():
            if name.startswith("_"):
                continue
            tag = " (report-only)" if data.get("report_only") else ""
            param_tag = f" [{data['param']}]" if data.get("param") and not data.get("report_only") else ""
            print(f"  {_bar(data['score'])} {data['score']:.2f}  {name}{param_tag}{tag}")
            print(f"         {data['detail']}")

    lint = result["tier2b"]["de_ai_lint"]
    print(f"\nTier 2b — De-AI lint (weight {result['weights'].get('tier2b', 0):.0%})")
    print(f"  {_bar(lint['score'])} {lint['score']:.2f}  de_ai_lint")
    print(f"         {lint['detail']}")
    for k, v in lint["lint"]["hits"].items():
        print(f"    - {k} ×{len(v)}: " + "; ".join(f"L{a}「{b}」" for a, b in v[:5]))
    for k, v in lint["lint"]["structure"].items():
        print(f"    · {k}: {v}")

    t3 = result["tier3"]
    if t3["score"] is not None:
        print(f"\nTier 3 — LLM (weight {result['weights'].get('tier3', 0):.0%})")
        print(f"  Score: {t3['score']:.2f} (source: {t3['source']})")
    else:
        print(f"\nTier 3 — LLM: not available (standalone mode)")

    sb = result.get("style_baseline") or {}
    print(f"\nStyle baseline: {sb.get('status')}", end="")
    if sb.get("status") == "ok":
        print(f" ({sb['samples']} samples) off-baseline: {sb['off_baseline'] or 'none'}")
    else:
        print(f" — {sb.get('note') or sb}")

    if result.get("de_ai_gate"):
        g = result["de_ai_gate"]
        print(f"\nDe-AI gate (blocking): {'PASS' if g['ok'] else 'FAIL'} {g['blocking']}")
    if result.get("en_gate"):
        g = result["en_gate"]
        print(f"\nEN gate: {'PASS' if g['ok'] else 'FAIL'} findings={g['findings']} warnings={g['warnings']}")

    print(f"\nComposite: {composite:.1f} (0=完美人类, 100=明显AI)")
    print(f"Weights: {result['weights']}")

    param_scores = result["param_scores"]
    if param_scores:
        sorted_params = sorted(param_scores.items(), key=lambda x: x[1])
        print(f"\nLowest-scoring parameters (optimize these first):")
        for param, score in sorted_params[:3]:
            print(f"  {param}: {score:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Score article humanness (0=human, 100=AI)")
    parser.add_argument("input", help="Markdown article file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Detailed report")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--tier3", type=float, default=None,
                        help="Tier 3 LLM score (0-1), passed by agent from SKILL.md")
    parser.add_argument("--en-gate", action="store_true",
                        help="Run English HOW gate; exit 2 on fail. Do not treat CJK composite as English quality.")
    parser.add_argument("--baseline", default=None,
                        help="Style-baseline config (default: references/style-baseline.yaml)")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    result = score_article(text, verbose=args.verbose, tier3_score=args.tier3,
                           baseline_config=args.baseline)

    if args.en_gate:
        gate = result.get("en_gate")
        if gate is None:
            ok, findings, warns = english_how_gate(text, return_warnings=True)
            gate = {"ok": ok, "findings": findings, "warnings": warns}
        if not gate.get("ok", False):
            print("EN GATE FAIL")
            for item in gate.get("findings", []):
                print(f"- {item}")
            for item in gate.get("warnings", []):
                print(f"- (warn) {item}")
            sys.exit(2)
        print("EN GATE PASS")
        for item in gate.get("warnings", []):
            print(f"- (warn) {item}")
        if not args.json and not args.verbose:
            return

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif not args.verbose:
        print(f"{result['composite_score']:.1f}")


if __name__ == "__main__":
    main()
