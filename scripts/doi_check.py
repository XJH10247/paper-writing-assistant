#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOI / arXiv ID 批量真实性验证脚本（引用检查模块用）

数据源与路由（命中即返回）：
  1. CrossRef   https://api.crossref.org/works/{doi}      —— 期刊/会议/图书主源，覆盖面最广
  2. DataCite   https://api.datacite.org/dois/{doi}       —— 数据集/软件/预印本（如 10.48550/arXiv.*）
  3. arXiv      https://export.arxiv.org/api/query?id_list= —— 预印本，仅用于无 "10." 前缀的裸 arXiv ID

  即：带 "10." 前缀的标识按 1 → 2 顺序回退；裸 arXiv ID 只走 3。可用 --sources 收窄。

用途：
  1. 检查 DOI 是否有效（not_found →疑似虚构或抄错）
  2. 比对 DOI 指向文献标题与用户条目标题是否一致（title_mismatch →疑似张冠李戴）
  3. 按标题检索候选 DOI（为缺 DOI 条目补全，CrossRef + DataCite 双源）
  4. 识别重复条目（同一标题被多个 DOI 引用，或同一 DOI 出现在多条文献中）

仅使用 Python 标准库，无需第三方依赖，无需鉴权（Python 3.8+）。

默认 User-Agent 只含技能名与版本号（paper-writing-assistant/<version>），**不携带仓库地址、
账号或任何个人信息**，因此也不会被写入 CrossRef / DataCite / arXiv 的访问日志。
联网前若想按 CrossRef 礼貌抓取政策留下可联系的邮箱，自己设置环境变量（限流时数据源能找到你）：
  set PWA_USER_AGENT=paper-writing-assistant/1.0.0 (mailto:you@example.org)

若要以子进程、重定向等方式消费 stdout，注意 Windows 简体中文环境的控制台默认是 GBK；
脚本已自行把 stdout/stderr 切到 UTF-8，仍失败时会降级为仅输出 GBK 可编码字符。
反过来，宿主用管道捕获时（如 PowerShell 5.1 的 `… | Select-Object`）会按 GBK 解码这些 UTF-8 字节，
中文看着乱码但**退出码与 --output 落盘的 JSON 不受影响**；需要人读结论时优先用 --output 写文件再读。

用法示例：
  # 从文件中自动提取所有 DOI / arXiv ID 并验证
  python doi_check.py --input references.txt --output doi_report.json

  # 直接验证若干 DOI（逗号分隔）
  python doi_check.py --dois "10.1038/s41586-021-03819-2,10.1109/CVPR.2016.90"

  # 生成期望标题对照文件（推荐：--gen-expect 后人工校对，标题误提取会污染比对结果）
  python doi_check.py --input references.txt --gen-expect expect.json
  #   ↓ 人工打开 expect.json 校正 title 字段
  python doi_check.py --input references.txt --expect expect.json --output doi_report.json

  # 按标题检索候选 DOI（为无 DOI 条目补全）
  python doi_check.py --search "Attention is all you need"

  # 仅做重复条目检测（离线，不联网；必须配 --input）
  python doi_check.py --input references.txt --duplicates-only

  # 全流程：提取 + 验证 + 标题比对 + 重复检测
  python doi_check.py --input references.txt --expect expect.json --check-duplicates --output doi_report.json

  # 收窄数据源（例如只查 CrossRef）
  python doi_check.py --input references.txt --sources crossref

  # 查看版本（与 CHANGELOG.md 中的版本号一致）
  python doi_check.py --version

expect.json 格式（--gen-expect 自动生成，建议人工校正）：
  [
    {"doi": "10.1038/s41586-021-03819-2", "title": "Highly accurate protein structure prediction with AlphaFold"},
    {"arxiv": "1706.03762", "title": "Attention is all you need"}
  ]

输出 JSON 报告结构：
  {
    "results": [
      {
        "id": "10.1038/...",              # 统一标识（DOI 或 arXiv ID）
        "doi": "10.1038/...",            # 无 DOI 时为空串
        "arxiv_id": "1706.03762",        # 非 arXiv 时为空串
        "status": "valid | title_mismatch | not_found | error",
        "source": "crossref | datacite | arxiv | local",  # 命中数据源
        "similarity": 0.97,              # 仅做了标题比对时存在
        "registry_title": "...",         # 权威库返回标题
        "registry_year": 2021,
        "registry_journal": "...",
        "registry_authors": ["..."],
        "registry_type": "journal-article",
        "tried_sources": ["crossref", "datacite"],   # 实际请求过的源
        "message": "..."                            # error / 高风险时的人读说明
      }
    ],
    "duplicates": [
      {"type": "same_title",   "title": "...", "entries": ["2", "4"], "message": "..."},
      {"type": "repeated_id",  "identifier": "10.xxxx/y", "entries": ["1", "5"], "message": "..."},
      {"type": "near_title",   "titles": ["...", "..."], "similarity": 0.93,
       "entries": ["3", "7"], "message": "..."}
    ],
    "coverage": {"entries_parsed": 8, "entries_without_identifier": 1, "message": "..."},
    "summary": {"total": 10, "valid": 8, "title_mismatch": 1, "not_found": 0, "error": 1,
                "duplicates": 2},
    "sources_used": ["crossref", "datacite"],   # 本轮实际请求过的源（非 --sources 的复述）
    "similarity_threshold": 0.85,
    "generated_at": "2026-10-10T05:00:00Z"
  }

  其中 duplicates / coverage 仅在传--check-duplicates 时出现。

状态说明：
  valid           标识可解析（若做了标题比对且相似度 >= 0.85）
  title_mismatch  标识有效但标题与条目明显不符（相似度 < 0.85）→ 高风险，人工复核
  not_found       所配置数据源均明确返回查不到 → 高风险，疑似虚构或抄错
  error           网络/限流/解析失败，或被 --sources 排除 → 不作为结论

退出码：
  0  未发现高风险条目与重复条目
  1  发现高风险条目（not_found / title_mismatch），或检测到重复条目，或 --search 无候选
  2  用法/输入错误（缺少输入、未找到任何标识、无法读取文件）
  3  未发现高风险条目，但有 error 条目因网络/限流未能验证，需重试

重要：error 与 not_found 语义完全不同。
  error = 我们不知道（网络问题）；not_found = 权威库说查不到（文献可能有问题）。
  报告中不得把 error 当作"文献有问题"的证据；网络失败一律不降级为 not_found。
"""

import argparse
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

__version__ = "1.0.0"

# 默认 User-Agent 刻意不含仓库地址与账号：这个串会随每个出站请求发给三方 API 并被记录，
# fork 或个人版要自报身份时一律通过 PWA_USER_AGENT 注入（见 AGENTS.md「发布前自查」）。
PROJECT_NAME = "paper-writing-assistant"


def _force_utf8_console():
    """Windows 简体中文环境的默认控制台编码是 GBK，print 含 emoji 的提示会抛
    UnicodeEncodeError 并以退出码 1 终止（而非约定的退出码）。这里统一改为 UTF-8 输出。
    失败时静默降级：下方所有面向终端的字符串均只含 GBK 可编码字符。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass


_force_utf8_console()

CROSSREF_API = "https://api.crossref.org/works/"
CROSSREF_SEARCH = "https://api.crossref.org/works?query.bibliographic="
DATACITE_API = "https://api.datacite.org/dois/"
DATACITE_SEARCH = "https://api.datacite.org/dois?query="
ARXIV_API = "https://export.arxiv.org/api/query?id_list="

USER_AGENT = os.environ.get(
    "PWA_USER_AGENT",
    f"{PROJECT_NAME}/{__version__}",
)
HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}
# 礼貌限速：约 1 请求/秒（多源回退会放大请求数，日志过多时调大）
REQUEST_INTERVAL = 1.0
TIMEOUT = 20
# 标题相似度阈值，低于此值判为 title_mismatch
SIMILARITY_THRESHOLD = 0.85

# ---------------------------------------------------------------- 标识提取

# DOI：10. + 注册号(4-9位) + / + 后缀；后缀到空白或结束标点为止
DOI_PATTERN = re.compile(
    r"10\.\d{4,9}/[^\s\"'<>，。；、）)\]】]+",
    re.IGNORECASE,
)

# 裸arXiv ID：新式 2103.00020(01..99) / 旧式 cs/0701001
ARXIV_NEW_PATTERN = re.compile(
    r"(?<!\d)(\d{4}\.\d{4,5})(?:v\d+)?(?!\d)"
)
ARXIV_OLD_PATTERN = re.compile(
    r"(?<![\w./])([a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?(?!\d)"
)

# 裸 arXiv ID 误匹配时用于过滤的精确值（如 DOI 前缀本身）
_ARXIV_STOPWORDS = {"10.48550", "0000.0000"}

# 去除题名中常见的尾部噪声
_TITLE_TAIL_JUNK = re.compile(
    r"(?:\[\s*(?:J|C|M|D|P|EB/OL|EB/OL)\s*\]"
    r"|\b(?:In|Vol|No|Iss|pp?|pp?\.?|Retrieved|Available|doi:?|DOI:?)\b\.?).*$",
    re.IGNORECASE,
)


def normalize_text(s: str) -> str:
    """标题归一化：小写、去标点、压空白。"""
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_similarity(a: str, b: str) -> float:
    """标题相似度，0-1。中文与英文均适用。"""
    na, nb = normalize_text(a), normalize_text(b)
    if not na or not nb:
        return 0.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


def extract_dois(text: str):
    """提取 DOI 并去重（保持出现顺序）。注意：不会提取 10.48550/arXiv.* 之外的 DataCite 之外的伪前缀。"""
    seen, out = set(), []
    for m in DOI_PATTERN.finditer(text):
        doi = m.group(0).rstrip(".,;:")
        if doi.endswith("."):
            doi = doi[:-1]
        if len(doi.split("/", 1)[-1]) < 3:  # 后缀过短，多半是误匹配
            continue
        if doi.lower() not in seen:
            seen.add(doi.lower())
            out.append(doi)
    return out


def extract_arxiv_ids(text: str):
    """
    提取裸 arXiv ID。
    会跳过已被 DOI_PATTERN 覆盖的 10.48550/arXiv.* 形式（那类按 DOI 走 DataCite）。
    """
    spans = [(m.start(), m.end()) for m in DOI_PATTERN.finditer(text)]
    seen, out = set(), []

    def in_doi_span(pos):
        return any(s <= pos < e for s, e in spans)

    candidates = []
    for m in ARXIV_NEW_PATTERN.finditer(text):
        if not in_doi_span(m.start(1)):
            candidates.append(m.group(1))
    for m in ARXIV_OLD_PATTERN.finditer(text):
        if not in_doi_span(m.start(1)):
            candidates.append(m.group(1))

    for cand in candidates:
        k = cand.lower()
        if k in seen or k in _ARXIV_STOPWORDS:
            continue
        seen.add(k)
        out.append(cand)
    return out


# ---------------------------------------------------------------- HTTP


def http_get(url: str, accept: str = "application/json"):
    """GET 请求。返回 (parsed_or_text, error_or_None)。"""
    req = urllib.request.Request(url, headers={**HEADERS, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            if "json" in (resp.headers.get("Content-Type") or ""):
                return json.loads(raw), None
            return raw, None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, "not_found"
        if e.code in (429, 503):
            return None, "rate_limited"
        return None, f"http_{e.code}"
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return None, f"network_error: {e}"
    except json.JSONDecodeError:
        return None, "invalid_response"


def http_get_json(url: str):
    return http_get(url, accept="application/json")


# 服务返回 200 但内容不可用（解析失败/空响应）也归此类，一律不当作"文献不存在"
_TRANSIENT_KINDS = {"rate_limited", "invalid_response", "empty_response"}


def is_transient(err) -> bool:
    """判定错误属于"我们查不到"（网络/限流/解析），而非"权威库说查不到"。"""
    if not err:
        return False
    if err == "not_found":
        return False
    return err in _TRANSIENT_KINDS or str(err).startswith(("network_error", "timeout", "http_"))


# ---------------------------------------------------------------- 数据源


def fetch_crossref(doi: str):
    data, err = http_get_json(CROSSREF_API + urllib.parse.quote(doi, safe="/"))
    if err:
        return None, err
    msg = (data or {}).get("message", {})
    if not msg:
        return None, "empty_response"
    return _pack_crossref(msg, doi), None


def _pack_crossref(msg: dict, doi: str) -> dict:
    titles = msg.get("title") or [""]
    container = msg.get("container-title") or [""]
    authors = []
    for a in (msg.get("author") or [])[:5]:
        name = " ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name", "")
        if name:
            authors.append(name)
    return {
        "title": (titles[0] or "").strip(),
        "year": _extract_year(msg),
        "journal": (container[0] or "").strip(),
        "authors": authors,
        "type": msg.get("type", ""),
        "doi": (msg.get("DOI") or doi).lower(),
    }


def fetch_datacite(doi: str):
    data, err = http_get_json(DATACITE_API + urllib.parse.quote(doi, safe="/"))
    if err:
        return None, err
    attrs = ((data or {}).get("data") or {}).get("attributes") or {}
    if not attrs:
        return None, "empty_response"
    titles = attrs.get("titles") or []
    title = titles[0].get("title", "") if titles else ""
    container = attrs.get("container") or {}
    journal = container.get("title", "") if isinstance(container, dict) else ""
    # DataCite 早期记录可能仍用 container-title（deprecated）
    if not journal and isinstance(container, dict):
        journal = container.get("container-title", "") or ""
    authors = []
    for a in (attrs.get("creators") or [])[:5]:
        nm = a.get("name") or a.get("givenName", "")
        if a.get("familyName"):
            nm = f"{a.get('givenName', '')} {a['familyName']}".strip()
        if nm:
            authors.append(nm)
    return {
        "title": (title or "").strip(),
        "year": attrs.get("publicationYear"),
        "journal": (journal or "").strip(),
        "authors": authors,
        "type": attrs.get("types", {}).get("resourceTypeGeneral", "") if isinstance(attrs.get("types"), dict) else "",
        "doi": (attrs.get("doi") or doi).lower(),
        "publisher": attrs.get("publisher", ""),
    }, None


_ARXIV_NS = "{http://www.w3.org/2005/Atom}"


def fetch_arxiv(arxiv_id: str):
    """
    用 arXiv API 校验裸 arXiv ID。
    返回 Atom XML，这里用轻量正则解析（无需第三方库）。
    """
    url = ARXIV_API + urllib.parse.quote(arxiv_id) + "&max_results=1"
    text, err = http_get(url, accept="application/atom+xml")
    if err:
        return None, err
    if not text:
        return None, "empty_response"
    m = re.search(r"opensearch:totalResults[^>]*>(\d+)<", text)
    if m and m.group(1) == "0":
        return None, "not_found"
    # 关键：只从 <entry> 内取字段，避免误取 feed 级的 <title>
    em = re.search(r"<entry>(.*?)</entry>", text, re.DOTALL)
    if not em:
        return None, "not_found"
    entry = em.group(1)
    title = _xml_text(entry, "title")
    if not title:
        return None, "not_found"
    published = _xml_text(entry, "published")
    year = published[:4] if published[:4].isdigit() else None
    authors = [_unescape(a).strip() for a in re.findall(r"<name>([^<]+)</name>", entry)][:5]
    entry_id = _xml_text(entry, "id")
    m2 = re.search(r"arxiv\.org/abs/([^\s<]+?)(?:v\d+)?$", entry_id)
    return {
        "title": title,
        "year": year,
        "journal": "arXiv preprint",
        "authors": [a for a in authors if a],
        "type": "preprint",
        "doi": f"10.48550/arXiv.{m2.group(1)}" if m2 else "",
        "url": entry_id,
    }, None


def _unescape(s: str) -> str:
    s = (s.replace("&amp;", "&").replace("&lt;", "<")
          .replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'"))
    return re.sub(r"\s+", " ", s).strip()


def _xml_text(text: str, tag: str) -> str:
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", text, re.DOTALL)
    return _unescape(m.group(1)) if m else ""


def _extract_year(msg: dict):
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (msg.get(key) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            return parts[0][0]
    return None


def search_crossref(title: str, limit: int = 3):
    url = f"{CROSSREF_SEARCH}{urllib.parse.quote(title)}&rows={limit}&select=DOI,title,author,container-title,issued"
    data, err = http_get_json(url)
    if err:
        return None, err
    items = []
    for it in ((data or {}).get("message", {}).get("items") or []):
        titles = it.get("title") or [""]
        items.append({
            "doi": it.get("DOI", ""),
            "title": (titles[0] or "").strip(),
            "year": _extract_year(it),
            "journal": ((it.get("container-title") or [""])[0] or "").strip(),
            "journal_full": ((it.get("container-title") or [""])[0] or "").strip(),
            "source": "crossref",
            "similarity": round(title_similarity(title, titles[0]), 3),
        })
    return items, None


def search_datacite(title: str, limit: int = 3):
    url = f"{DATACITE_SEARCH}{urllib.parse.quote(title)}&page[size]={limit}"
    data, err = http_get_json(url)
    if err:
        return None, err
    items = []
    for it in ((data or {}).get("data") or []):
        attrs = it.get("attributes") or {}
        titles = attrs.get("titles") or []
        t = titles[0].get("title", "") if titles else ""
        container = attrs.get("container") or {}
        journal = container.get("title", "") if isinstance(container, dict) else ""
        doi = it.get("id", "")
        items.append({
            "doi": doi,
            "title": (t or "").strip(),
            "year": attrs.get("publicationYear"),
            "journal": (journal or "").strip(),
            "source": "datacite",
            "similarity": round(title_similarity(title, t), 3),
        })
    return items, None


def search_title(title: str, limit: int = 3):
    """CrossRef + DataCite 双源检索，合并按相似度降序返回。"""
    out, errs = [], {}
    for fn in (search_crossref, search_datacite):
        items, err = fn(title, limit)
        if err:
            errs[fn.__name__] = err
        else:
            out.extend(items or [])
    out.sort(key=lambda x: x["similarity"], reverse=True)
    return out[:limit], errs


# ---------------------------------------------------------------- 校验主逻辑


def check_identifier(ident: str, expect_title: str = "", sources=None):
    """
    校验单个标识（DOI 或裸 arXiv ID）。
    带 "10." 前缀 → 按 sources 中的 CrossRef / DataCite 顺序回退；
    裸 arXiv ID → 只走 arXiv API。sources 为 None 时全量回退。
    """
    wanted = [s.strip().lower() for s in (sources or ["crossref", "datacite", "arxiv"])] or \
             ["crossref", "datacite", "arxiv"]
    result = {"id": ident, "doi": "", "arxiv_id": ""}
    is_arxiv_bare = not ident.lower().startswith("10.")
    if is_arxiv_bare:
        result["arxiv_id"] = ident
        registry = [("arxiv", fetch_arxiv, ident)] if "arxiv" in wanted else []
        blocked_hint = "--sources 未包含 arxiv"
    else:
        result["doi"] = ident
        registry = [(name, fn, ident)
                    for name, fn in (("crossref", fetch_crossref), ("datacite", fetch_datacite))
                    if name in wanted]
        blocked_hint = "--sources 未包含任何 DOI 数据源（crossref/datacite）"
    if not registry:
        result.update({
            "status": "error",
            "source": "local",
            "tried_sources": [],
            "message": f"{blocked_hint}，本条未能验证；请去掉 --sources 限制或补上对应数据源",
        })
        return result

    tried, meta, source = [], None, ""
    transient = []
    for name, fn, arg in registry:
        tried.append(name)
        got, err = fn(arg)
        if err == "not_found":
            # 该源明确说查不到，继续试下一个源
            continue
        if is_transient(err):
            transient.append(f"{name}:{err}")   # 网络类问题，不当作"查不到"
            continue
        if err:
            transient.append(f"{name}:{err}")
            continue
        if got:
            meta, source = got, name
            break

    result["tried_sources"] = tried
    if meta is None:
        if transient and len(transient) == len(tried):
            result.update({
                "status": "error",
                "source": "local",
                "message": f"数据源访问异常（{'; '.join(transient)}），本条未能验证，不能据此判断文献真伪，请稍后重试",
            })
        elif transient:
            result.update({
                "status": "error",
                "source": "local",
                "message": (f"部分数据源未能返回（{'; '.join(transient)}），其余数据源均无此标识；"
                            "本条按未能验证处理，不得判为文献有问题，请重试"),
            })
        else:
            result.update({
                "status": "not_found",
                "source": "local",
                "message": "所配置数据源（" + "/".join(tried) + "）均明确返回查不到，疑似虚构或抄错，请人工核对原文",
            })
        return result

    result["source"] = source
    result["registry_title"] = meta.get("title", "")
    result["registry_year"] = meta.get("year")
    result["registry_journal"] = meta.get("journal", "")
    result["registry_authors"] = meta.get("authors", [])
    result["registry_type"] = meta.get("type", "")
    if meta.get("publisher"):
        result["registry_publisher"] = meta["publisher"]
    if meta.get("url"):
        result["registry_url"] = meta["url"]

    if expect_title:
        sim = title_similarity(expect_title, meta.get("title", ""))
        result["similarity"] = round(sim, 3)
        result["expect_title"] = expect_title
        if sim < SIMILARITY_THRESHOLD:
            result["status"] = "title_mismatch"
            result["message"] = (
                f"{source} 上该标识有效，但指向文献标题与条目标题相似度仅 {sim:.2f}"
                f"（阈值 {SIMILARITY_THRESHOLD}），疑似张冠李戴，请人工复核"
            )
            return result
    result["status"] = "valid"
    return result


# ---------------------------------------------------------------- 标题提取与重复检测


# GB/T 7714-2015 文献类型标识
_TYPE_MARK = re.compile(r"\[([JCDMPS]|EB/OL|N/|J/OL)\]")
# 条目行起始标记：[1] / 1. / (1)
_ENTRY_MARK = re.compile(r"^\s*(?:[\[（(]\s*(\d{1,3})\s*[\]）)]|(\d{1,3})\s*[.、])\s*")


def parse_entries(text: str):
    """
    把文献表切成逐条 entry。
    - 表内有编号行首标记（[1] / 1. / （1））：按编号切分，无编号行归为上一条的续行。
    - 整表都没有编号（APA/MLA 著者-出版年制、Word 导出等）：每条非空行独立成条。
    返回 [{index, label, raw, line_no}]
    """
    lines = text.splitlines()
    numbered = any(_ENTRY_MARK.match(l) for l in lines if l.strip())
    if not numbered:
        return [{"index": i, "label": None, "raw": l.strip(), "line_no": n}
                for i, (n, l) in enumerate(
                    [(n, l) for n, l in enumerate(lines, 1) if l.strip()], 1)]

    entries, cur = [], None
    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue
        m = _ENTRY_MARK.match(line)
        if m or cur is None:
            if m and cur is not None:
                entries.append(cur)
            label = (m.group(1) or m.group(2)) if m else None
            cur = {"index": len(entries) + 1, "label": label, "raw": line.strip(), "line_no": line_no}
        else:
            # 上一条的续行（换行排版的文献表）
            cur["raw"] += " " + line.strip()
    if cur is not None:
        entries.append(cur)
    return entries


def extract_title_of_entry(raw: str) -> str:
    """
    从单条文献中提取题名。优先按 GB/T 7714 结构（`作者. 题名[类型]. 出处`），
    其次识别引号题名（APA/IEEE），最后退化为最长片段。
    """
    s = _ENTRY_MARK.sub("", raw.strip())

    # 1) IEEE 会议式：Title," in Proceedings of ...
    q = re.search(r'["“]([^"”]{10,300})["”]\s*,\s*(?:in\s+)?[A-Z]', s)
    if q:
        return q.group(1).strip()

    # 2) GB/T 7714：首个 ". " 之后、[类型标识] 之前
    tm = _TYPE_MARK.search(s)
    head = s[: tm.start()] if tm else s
    # 作者段以 ". " 分隔；取最后一个作者分隔点之后的内容作为题名
    # （多作者含 "et al." / "等" 时不宜取第一个，故取候选中最像题名的一段）
    parts = re.split(r"\.\s+", head)
    cands = [p.strip(" ,，;；:、.") for p in parts]
    cands = [c for c in cands if len(c) >= 12 and not re.fullmatch(r"[\d\s,\-–—]+", c)]
    # 过滤掉明显的作者段（含 et al / 等 / 大量姓名缩写）
    def author_like(c):
        return bool(re.search(r"\bet\s+al\b|\b等\b", c, re.I)) or \
            len(re.findall(r"\b[A-Z]{2,}\b", c)) >= 4
    title_cands = [c for c in cands if not author_like(c)]
    if title_cands:
        # 题名通常是紧邻类型标识或末尾的最后一段
        return title_cands[-1][:300]

    # 3) APA 无引号：Title. Journal, ...
    if cands:
        return max(cands, key=len)[:300]
    return re.sub(r"\s+", " ", s).strip()[:300]


def entry_identifiers(raw: str):
    """取出该条中出现的所有标识（DOI + 裸 arXiv ID）。"""
    ids = [m.group(0).rstrip(".,;:") for m in DOI_PATTERN.finditer(raw)]
    ids += extract_arxiv_ids(raw)
    out, seen = [], set()
    for i in ids:
        if i.lower() not in seen:
            seen.add(i.lower())
            out.append(i)
    return out


def extract_titles_by_doi(text: str):
    """
    逐条提取 (标识, 题名)，用于 --gen-expect。
    注意：题名为启发式提取，**必须人工校正后再用于比对**，否则会误判 title_mismatch。
    """
    pairs, seen = [], set()
    for e in parse_entries(text):
        title = extract_title_of_entry(e["raw"])
        title = re.sub(r"\s+", " ", title).strip(" .")
        if len(title) < 10:
            continue
        ids = entry_identifiers(e["raw"]) or [""]
        for i in ids:
            k = i.lower()
            if k in seen:
                continue
            seen.add(k)
            item = {"title": title[:300]}
            if i:
                if i.lower().startswith("10."):
                    item["doi"] = i
                else:
                    item["arxiv"] = i
            item["entry_label"] = e["label"] or str(e["index"])
            pairs.append(item)
    return pairs


def detect_duplicates(text: str, expect_pairs=None):
    """
    离线重复条目检测（不联网）：
    - repeated_id：同一标识出现在多条文献中（应合并）
    - same_title：不同条目的题名实质相同（同一文献被重复列出）
    - near_title：题名高度相似但标识不同（同一文献的不同版本/不同出处）
    """
    entries = parse_entries(text)
    id_owner = defaultdict(set)      # 标识 -> 条目 key 集合
    title_owner = defaultdict(set)   # 归一化题名 -> 条目 key 集合
    title_raw = {}
    no_id = 0

    for e in entries:
        key = e["label"] or f"L{e['line_no']}"
        ids = entry_identifiers(e["raw"])
        if not ids:
            no_id += 1
        for i in ids:
            id_owner[i.lower()].add(key)
        t = extract_title_of_entry(e["raw"])
        n = normalize_text(_TITLE_TAIL_JUNK.sub("", t))
        if n and len(n) >= 10:
            title_owner[n].add(key)
            title_raw.setdefault(n, t)

    dups = []
    for i, keys in id_owner.items():
        if len(keys) > 1:
            dups.append({
                "type": "repeated_id",
                "identifier": i,
                "entries": sorted(keys),
                "message": f"标识 {i} 在条目 {sorted(keys)} 中重复出现，应合并为一条",
            })

    for n, keys in title_owner.items():
        if len(keys) > 1:
            dups.append({
                "type": "same_title",
                "title": title_raw.get(n, n),
                "entries": sorted(keys),
                "message": f"条目 {sorted(keys)} 的题名实质相同（{title_raw.get(n, n)[:80]}），疑为同一文献重复列出，应合并",
            })

    # 近似题名：包含关系或高相似
    norms = [n for n in title_owner if len(title_owner[n]) == 1]
    for i in range(len(norms)):
        for j in range(i + 1, len(norms)):
            a, b = norms[i], norms[j]
            ratio = title_similarity(a, b)
            if a in b or b in a or ratio >= 0.92:
                keys = title_owner[a] | title_owner[b]
                if len(keys) > 1:
                    dups.append({
                        "type": "near_title",
                        "titles": [title_raw.get(a, a)[:150], title_raw.get(b, b)[:150]],
                        "similarity": round(ratio, 3),
                        "entries": sorted(keys),
                        "message": f"条目 {sorted(keys)} 题名高度相似（{ratio:.2f}）但标识不同，疑似同一文献的不同版本，需人工判断",
                    })
    #摘要行不计入问题数，单独作为 coverage 字段返回
    coverage = {
        "entries_parsed": len(entries),
        "entries_without_identifier": no_id,
        "message": f"共解析 {len(entries)} 条，其中 {no_id} 条未发现 DOI/arXiv ID，无法自动验证真实性",
    }
    return {"duplicates": dups, "coverage": coverage}


# ---------------------------------------------------------------- 主流程


def _load_expect(path: str):
    """载入期望对照。键统一为小写标识（doi 或 arxiv id）。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    m = {}
    for item in data:
        key = item.get("doi") or item.get("arxiv") or item.get("id") or ""
        if key:
            m[key.strip().lower()] = (item.get("title") or "").strip()
    return m


def _collect_ids(text: str):
    """统一收集 DOI 与裸 arXiv ID，保留顺序并去重。"""
    out, seen = [], set()
    for i in extract_dois(text) + extract_arxiv_ids(text):
        k = i.lower()
        if k not in seen:
            seen.add(k)
            out.append(i)
    return out


def main():
    parser = argparse.ArgumentParser(
        description="DOI / arXiv ID 批量验证（CrossRef + DataCite + arXiv 多源回退）",
        epilog=("退出码：0 无风险项 | 1 发现 not_found/title_mismatch 或重复条目 | "
                "2 用法/输入错误 | 3 有条目因网络原因未能验证，需重试"),
    )
    parser.add_argument("--input", help="文献表/纯文本文件路径（自动提取 DOI 与 arXiv ID）")
    parser.add_argument("--dois", help="逗号分隔的 DOI / arXiv ID 列表")
    parser.add_argument("--expect", help="期望标题对照 JSON（[{doi,title}] 或 [{arxiv,title}]）")
    parser.add_argument("--gen-expect", dest="gen_expect",
                        help="从输入文件自动生成期望对照 JSON 并退出（结果需人工校正）")
    parser.add_argument("--search", help="按标题检索候选 DOI（CrossRef+DataCite，返回 top3）")
    parser.add_argument("--check-duplicates", action="store_true", help="验证同时附加检测重复条目（重复检测本身离线）")
    parser.add_argument("--duplicates-only", action="store_true", help="仅做重复条目检测，不联网，必须配 --input")
    parser.add_argument("--sources", default="crossref,datacite,arxiv",
                        help="限定数据源，逗号分隔，可选 crossref/datacite/arxiv（默认全部；DOI 走 crossref→datacite，裸 arXiv ID 走 arxiv）")
    parser.add_argument("--interval", type=float, default=REQUEST_INTERVAL,
                        help=f"请求间隔秒数（默认 {REQUEST_INTERVAL}，被限流时调大）")
    parser.add_argument("--output", help="报告输出 JSON 路径（默认打印到 stdout）")
    parser.add_argument("--version", action="version", version=f"doi_check.py {__version__}")
    args = parser.parse_args()

    valid_sources = {"crossref", "datacite", "arxiv"}
    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    unknown = [s for s in sources if s not in valid_sources]
    if unknown:
        print(json.dumps({"error": f"--sources 不认识的取值：{unknown}，可选 {sorted(valid_sources)}"}, ensure_ascii=False))
        sys.exit(2)
    if not sources:
        sources = sorted(valid_sources)
    if not args.input and not args.dois and not args.search:
        print(json.dumps({"error": "至少需要一个输入：--input / --dois / --search（--duplicates-only 必须配 --input）"}, ensure_ascii=False))
        sys.exit(2)

    # 模式一：标题检索
    if args.search:
        items, errs = search_title(args.search)
        print(json.dumps({"query": args.search, "candidates": items, "source_errors": errs},
                         ensure_ascii=False, indent=2))
        sys.exit(0 if items else 1)

    # 读取输入文本
    text = ""
    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError as e:
            print(json.dumps({"error": f"无法读取 --input 文件：{e}"}, ensure_ascii=False))
            sys.exit(2)
    if args.dois:
        text += "\n" + args.dois.replace(",", "\n")

    # 模式二：生成期望对照文件
    if args.gen_expect:
        pairs = extract_titles_by_doi(text)
        with open(args.gen_expect, "w", encoding="utf-8") as f:
            json.dump(pairs, f, ensure_ascii=False, indent=2)
        print(f"expect file written: {args.gen_expect} ({len(pairs)} pairs)")
        print("注意：标题为启发式提取，请务必人工校正后再用于 --expect 比对，否则会产生误报的 title_mismatch")
        sys.exit(0)

    # 模式三：仅重复检测（离线）
    if args.duplicates_only:
        if not args.input:
            print(json.dumps({"error": "--duplicates-only 需要 --input 指向的文献表文件"}, ensure_ascii=False))
            sys.exit(2)
        dup = detect_duplicates(text)
        dups = dup["duplicates"]
        print(json.dumps({"duplicates": dups, "count": len(dups), "coverage": dup["coverage"]},
                         ensure_ascii=False, indent=2))
        sys.exit(1 if dups else 0)

    # 模式四：批量验证
    ids = _collect_ids(text)
    if not ids:
        print(json.dumps({"error": "未在输入中找到任何 DOI 或 arXiv ID"}, ensure_ascii=False))
        sys.exit(2)

    expect_map = {}
    if args.expect:
        try:
            expect_map = _load_expect(args.expect)
        except (OSError, json.JSONDecodeError) as e:
            print(json.dumps({"error": f"无法读取 --expect 对照文件：{e}"}, ensure_ascii=False))
            sys.exit(2)

    results = []
    for i, ident in enumerate(ids):
        if i > 0 and args.interval > 0:
            time.sleep(args.interval)
        results.append(check_identifier(ident, expect_map.get(ident.lower(), ""), sources))

    tried_union = []
    for r in results:
        for t in r.get("tried_sources") or []:
            if t not in tried_union:
                tried_union.append(t)

    report = {
        "results": results,
        "summary": {"total": len(results)},
        "sources_used": tried_union,          # 本轮实际请求过的源
        "sources_requested": sources,
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    for status in ("valid", "title_mismatch", "not_found", "error"):
        report["summary"][status] = sum(1 for r in results if r["status"] == status)

    if args.check_duplicates:
        dup = detect_duplicates(text)
        report["duplicates"] = dup["duplicates"]
        report["summary"]["duplicates"] = len(dup["duplicates"])
        report["coverage"] = dup["coverage"]

    out = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"report written: {args.output}")
        print(json.dumps(report["summary"], ensure_ascii=False))
    else:
        print(out)

    # 退出码：高风险项优先于"未能验证"，两者均不存在时返回 0
    high_risk = report["summary"]["not_found"] + report["summary"]["title_mismatch"]
    dups_found = report["summary"].get("duplicates", 0)
    if high_risk or dups_found:
        sys.exit(1)
    if report["summary"]["error"]:
        sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()