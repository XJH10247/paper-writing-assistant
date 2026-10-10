#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摘要字数统计与自检工具（abstract 模块用）

解决两个问题：
  1. 字数口径歧义 —— "300-400 字"到底按什么算？中英文差异巨大，必须显式约定并同时报出多个口径。
  2. 中英双语一致性 —— 程序化比对中英摘要里的数值/单位/百分比，避免人工漏检。

仅使用 Python 标准库。

终端编码：脚本把 stdout/stderr 切到 UTF-8 后输出中文结论。若宿主用管道捕获（如 PowerShell 5.1 的
`… | Select-Object`）会按 GBK 解码这些字节，中文看着乱码但**退出码与 --output 落盘的 JSON 不受影响**；
需要人读结论时优先用 --output 写文件再读。

用法：
  # 统计中文字数（默认口径 + 全口径）
  python word_count.py --input abstract_zh.md

  # 指定统计口径与区间，超限返回非零退出码
  python word_count.py --input abstract_en.md --lang en --min 200 --max 250

  # 单边限制也支持（不给 --max 即不限上限）
  python word_count.py --input abstract_zh.md --min 300

  # 双语一致性比对（数值、单位、术语）
  python word_count.py --zh abstract_zh.md --en abstract_en.md

  # 术语一致性检查（需显式给出中英对照，如 "卷积神经网络=convolutional neural network"）
  python word_count.py --zh abstract_zh.md --en abstract_en.md \
         --terms "卷积神经网络=convolutional neural network"

  # 查看版本（与 CHANGELOG.md 中的版本号一致）
  python word_count.py --version

退出码：
  0  主口径在区间内，且（双语场景）中英数值一致
  1  保留，当前不使用
  2  字数越界，或用法/输入错误（如 --min 大于 --max、输入文件不存在）
  3  中英数值数量不一致（双语模式）

  双语模式下若字数越界与数值不一致同时发生，返回 3（数值不一致属实质性信息差，
  严重度高于字数越界；两者都需在交付说明中交代）。

字数默认区间（未给 --min/--max 时）：
  中文 han_chars 300-500；英文 words_en 200-300（与 SKILL.md、references/abstract-guide.md 一致）

输出 JSON 报告：
  {
    "lang": "zh",
    "counts": {
      "han_chars": 321,          # 纯汉字个数
      "word_msword": 397,        # Word「字数」口径（中文字符+英文单词）
      "chars_no_space": 536,     # 字符数(不含空格)
      "words_en": 0              # 英文分词数（中文文本恒为 0）
    },
    "primary_metric": "han_chars",
    "primary_count": 321,
    "primary_range": [300, 500],
    "primary_range_text": "300-500",
    "within_range": true,
    "alternative_metrics_out_of_range": [{"word_msword": 356}],
    "bilingual": {...}
  }

字数口径约定（与 SKILL.md「模块一」一致）：
  中文摘要主口径 = han_chars（纯汉字个数，不含标点、数字、英文词）
    ·理由：中文期刊/学位论文的"字数"要求通常指汉字数，标点不计入
  中文摘要副报 = word_msword（Word「字数」统计口径 = 汉字 + 英文单词 + 数字串）
  英文摘要主口径 = words_en（按空白/连字符切分的词数）
  无论主口径是否达标，只要存在另一口径越界，必须在交付说明中显式声明歧义。

仅使用 Python 标准库（Python 3.8+），无需安装依赖。
"""

import argparse
import json
import re
import sys

__version__ = "1.0.0"


def _force_utf8_console():
    """Windows 简体中文环境的默认控制台编码是 GBK，直接 print 含中文的结论行
    可能抛 UnicodeEncodeError。这里统一把 stdout/stderr 切到 UTF-8，失败则静默降级。
    用户侧也可用环境变量 PYTHONIOENCODING=utf-8 达到同样效果。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


_force_utf8_console()

INF = float("inf")
# 未给 --min/--max 时的默认区间（与 SKILL.md、references/abstract-guide.md 保持一致）
DEFAULT_RANGES = {"zh": (300, 500), "en": (200, 300)}

# 汉字（含扩展区基本汉字与常用扩展）
HAN_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
# 英文单词与数字串
WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*|\d+(?:\.\d+)?%?")

# 数值（含限定词前缀、百分号与单位）；前缀用选择而非字符集，避免"减少25%"被抽成"少25%"
NUM_RE = re.compile(
    r"(?:(?:±|∓|~|约|近|超过|至少|低于|高于)\s*)?"
    r"(?<![A-Za-z0-9.])"
    r"\d+(?:\.\d+)?"
    r"(?:\s*(?:[%％]|pp|percentage points?|"
    r"ms|min|h|mm|cm|kg|mg|GB|MB|TB|KB|Hz|kHz|dB|"
    r"epochs?|iters?|steps?|runs?|seeds?|layers?|heads?|params?|FLOPs?|billion|million|"
    r"(?:[MBKG])(?![A-Za-z])|"
    r"元|万元|倍|个|次|天|小时|分钟|年|月|日|万|亿))?",
    re.IGNORECASE,
)

# 需要排除的 Markdown/结构噪声
_MD_NOISE = re.compile(r"^\s*(#{1,6}\s*|[-*+]\s*|\d+\.\s*|>\s*)", re.MULTILINE)
_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")            # [文字](url) → 保留文字
_KEYWORD_LINE = re.compile(r"^\s*(关键词|Keywords?|Key\s*words?)\s*[:：].*$", re.MULTILINE | re.IGNORECASE)
_ABSTRACT_LABEL = re.compile(r"^\s*(?:摘\s*要|abstract)\s*[:：]\s*", re.MULTILINE | re.IGNORECASE)
_ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def clean_text(raw: str) -> str:
    """剥离 Markdown 结构噪声、摘要/关键词标签行，保留正文。"""
    t = _ZERO_WIDTH.sub("", raw)
    t = t.replace("\ufeff", "")
    t = _CODE_FENCE.sub("", t)                 # 先去代码块，避免围栏内的符号被当成正文
    t = _MD_LINK.sub(r"\1", t)                 # 去掉链接 URL，只留链接文字
    t = _KEYWORD_LINE.sub("", t)               # 关键词行不计入摘要字数
    t = _ABSTRACT_LABEL.sub("", t)             # "摘要：/Abstract:" 前缀不计入
    t = _MD_NOISE.sub("", t)
    t = re.sub(r"[*_`]+", "", t)               # 去掉强调/代码符号（保留 # 以外的结构已处理）
    return t.strip()


def counts_of(text: str, lang: str) -> dict:
    han = len(HAN_RE.findall(text))
    en_words = len(WORD_RE.findall(text))
    # Word「字数」：汉字 + 西文单词 + 数字串
    msword = han + len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", text)) + \
        len(re.findall(r"\d+(?:\.\d+)?", text))
    return {
        "han_chars": han,
        "word_msword": msword,
        "chars_no_space": len(re.sub(r"\s", "", text)),
        "chars_with_space": len(text),
        "words_en": en_words if lang == "en" else 0,
    }


def extract_numbers(text: str):
    """抽取所有数值表达，归一化后用于中英比对。"""
    out = []
    for m in NUM_RE.finditer(text):
        raw = re.sub(r"\s+", "", m.group(0))
        raw = raw.replace("％", "%")
        if not re.search(r"\d", raw):
            continue
        out.append(raw)
    return out


def numeric_core(s: str) -> str:
    """抽取数值"内核"（纯数字部分），用于跨语言比较时忽略单位差异。

    中英摘要里同一个量常写成 "5 次" vs "5 times"、"19.5%" vs "19.5 %"，
    数值内核一致即视为同一数值，单位差异另行提示。
    """
    m = re.search(r"\d+(?:\.\d+)?", s)
    return m.group(0) if m else ""


def compare_bilingual(zh: str, en: str, terms=None):
    """比对中英文摘要的数值集合与术语表。"""
    zh_nums = extract_numbers(zh)
    en_nums = extract_numbers(en)
    zh_set, en_set = set(zh_nums), set(en_nums)
    zh_core = {numeric_core(x) for x in zh_set if numeric_core(x)}
    en_core = {numeric_core(x) for x in en_set if numeric_core(x)}

    # 数值内核一致的算"数量匹配"；仅单位写法不同不算错误
    core_diff_zh = sorted(zh_core - en_core)
    core_diff_en = sorted(en_core - zh_core)
    # 写法差异（内核一致但原字符串不同）—— 提示核对，不算错误
    literal_diff_zh = sorted(zh_set - en_set)
    literal_diff_en = sorted(en_set - zh_set)

    term_issues = []
    for pair in (terms or []):
        if "=" not in pair:
            continue
        zh_term, en_term = [t.strip() for t in pair.split("=", 1)]
        in_zh, in_en = zh_term in zh, en_term.lower() in en.lower()
        if in_zh != in_en:
            term_issues.append({
                "pair": f"{zh_term} = {en_term}",
                "in_zh": in_zh,
                "in_en": in_en,
                "message": f"术语「{zh_term}/{en_term}」未在中英两侧同时出现，请确认是否漏译或未缩写展开",
            })

    consistent = not core_diff_zh and not core_diff_en
    if consistent and (literal_diff_zh or literal_diff_en):
        msg = ("数值数量在中英两侧一致（仅单位/精度写法不同："
               f"中文独有 {literal_diff_zh}，英文独有 {literal_diff_en}），建议统一单位写法")
    elif consistent:
        msg = "中英数值完全一致"
    else:
        msg = (f"数值数量不一致：中文独有 {core_diff_zh}，英文独有 {core_diff_en}；"
               "需人工确认（可能是中英各自补充了不同数据，属实质性不一致）")

    return {
        "numbers_zh": sorted(zh_set),
        "numbers_en": sorted(en_set),
        "numbers_only_in_zh": literal_diff_zh,
        "numbers_only_in_en": literal_diff_en,
        "numbers_consistent": consistent,
        "term_issues": term_issues,
        "terms_consistent": not term_issues,
        "message": msg,
    }


def resolve_range(lang, min_w, max_w):
    """归一化字数区间：双边、单边（另一端不限），两者均未给时用该语言默认。"""
    if min_w is None and max_w is None:
        return DEFAULT_RANGES[lang]
    lo = min_w if min_w is not None else 0
    hi = max_w if max_w is not None else INF
    return (lo, hi)


def range_text(rng):
    lo, hi = rng
    if hi == INF:
        return f"≥{lo}" if lo else "不限"
    if lo == 0:
        return f"≤{hi}"
    return f"{lo}-{hi}"


def analyze(raw: str, lang: str, min_w=None, max_w=None):
    text = clean_text(raw)
    c = counts_of(text, lang)
    if lang == "en":
        primary_metric, primary = "words_en", c["words_en"]
        # 只把同为"词数"量纲的指标拿来比区间；chars_no_space 是字符数，仅供参考，
        # 拿它去比词数区间会产生"其他口径越界"的误报
        alts = []
    else:
        primary_metric, primary = "han_chars", c["han_chars"]
        # word_msword 同为字数口径，可与区间比较；chars_no_space 是字符数，仅列入 counts
        alts = ["word_msword"]
    rng = resolve_range(lang, min_w, max_w)
    within = rng[0] <= primary <= rng[1]
    # 其他口径是否越界（用于显式声明歧义）
    alt_out = []
    for m in alts:
        v = c.get(m, 0)
        if not (rng[0] <= v <= rng[1]):
            alt_out.append({m: v})
    return {
        "lang": lang,
        "counts": c,
        "primary_metric": primary_metric,
        "primary_count": primary,
        "primary_range": [rng[0], None if rng[1] == INF else rng[1]],
        "primary_range_text": range_text(rng),
        "within_range": within,
        "alternative_metrics_out_of_range": alt_out,
        "note": (
            f"主口径 {primary_metric}={primary}，要求 {range_text(rng)}，"
            + ("达标" if within else "未达标")
            + ("；但其他口径越界，交付时必须显式声明口径歧义" if alt_out else "")
        ),
        "numbers": sorted(set(extract_numbers(text))),
    }


def main():
    ap = argparse.ArgumentParser(
        description="摘要字数统计与中英一致性检查",
        epilog=("退出码：0 通过 | 2 字数越界或用法错误 | 3 中英数值数量不一致。"
                f"默认区间：中文 {range_text(DEFAULT_RANGES['zh'])} 汉字，英文 {range_text(DEFAULT_RANGES['en'])} 词"),
    )
    ap.add_argument("--input", help="单语摘要文件路径")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="单语模式下的语言")
    ap.add_argument("--min", dest="min_w", type=int, help="下限（含）；双语模式下作用于中文侧")
    ap.add_argument("--max", dest="max_w", type=int, help="上限（含）；双语模式下作用于中文侧")
    ap.add_argument("--min-en", dest="min_en", type=int, help="双语模式下英文侧下限（含）")
    ap.add_argument("--max-en", dest="max_en", type=int, help="双语模式下英文侧上限（含）")
    ap.add_argument("--zh", help="中文摘要路径（双语模式）")
    ap.add_argument("--en", help="英文摘要路径（双语模式）")
    ap.add_argument("--terms", action="append", default=[],
                    help='术语对照，如 "CNN=convolutional neural network"（可重复）')
    ap.add_argument("--output", help="JSON 输出路径（默认 stdout）")
    ap.add_argument("--version", action="version", version=f"word_count.py {__version__}")
    args = ap.parse_args()

    def bad(msg):
        print(json.dumps({"error": msg}, ensure_ascii=False))
        sys.exit(2)

    if args.min_w is not None and args.max_w is not None and args.min_w > args.max_w:
        bad("--min 不能大于 --max")
    if args.min_en is not None and args.max_en is not None and args.min_en > args.max_en:
        bad("--min-en 不能大于 --max-en")

    report = {}
    exit_code = 0

    try:
        if args.zh and args.en:
            zh_raw, en_raw = load_text(args.zh), load_text(args.en)
            report = {
                "zh": analyze(zh_raw, "zh", args.min_w, args.max_w),
                "en": analyze(en_raw, "en", args.min_en, args.max_en),
                "bilingual": compare_bilingual(clean_text(zh_raw), clean_text(en_raw), args.terms),
            }
            if not report["bilingual"]["numbers_consistent"]:
                exit_code = 3
            if not report["zh"]["within_range"] or not report["en"]["within_range"]:
                exit_code = exit_code or 2
        elif args.input:
            report = analyze(load_text(args.input), args.lang, args.min_w, args.max_w)
            if not report["within_range"]:
                exit_code = 2
        else:
            bad("需要 --input 或 --zh/--en")
    except OSError as e:
        bad(f"无法读取输入文件：{e}")

    out = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"report written: {args.output}")
    else:
        print(out)
    if "zh" in report:
        print(report["zh"]["note"])
        print(report["en"]["note"])
        print("双语比对：" + report["bilingual"]["message"])
    else:
        print(report["note"])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()