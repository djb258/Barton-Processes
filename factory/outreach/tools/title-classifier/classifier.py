"""
Title Classifier — Snap-On Tool
Sub-Hub: 28 (title-classifier)

Classifies messy job title strings into CEO, CFO, HR, or REJECT.
Uses 3-tier architecture: Exact dict → Regex patterns → RapidFuzz fallback.
Designed for reuse across any process that needs title→role mapping.

Tournament-validated: 6 LLMs unanimous on regex+fuzzy architecture.
Taxonomy from GPT-5 (weighted phrases), structure from Sonnet (3-tier),
caching from Kimi (LRU for repeated titles).

Usage:
    from classifier import TitleClassifier
    tc = TitleClassifier()
    result = tc.classify("CEO PDRI by Pearson, Author & Speaker", company="PDRI by Pearson")
    # result.bucket = "CEO", result.confidence = 100, result.tier = "EXACT"

Batch:
    results = tc.classify_batch(records)  # [{"context": str, "company": str}]
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
from functools import lru_cache
from rapidfuzz import fuzz, process


# ═══════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════

@dataclass
class ClassifyResult:
    original: str
    cleaned: str
    extracted_title: str
    bucket: str             # CEO | CFO | HR | REJECT
    confidence: int         # 0-100
    tier: str               # EXACT | REGEX | FUZZY | REJECT
    matched_phrase: str     # what triggered the match
    reason: str             # human-readable explanation


# ═══════════════════════════════════════════════════════════════
# TAXONOMY — The Constants (locked)
# ═══════════════════════════════════════════════════════════════
# Phrase → (bucket, base_confidence)
# Longer phrases checked first (sorted by length desc at init)

PHRASE_TAXONOMY = {
    # ── CEO (Executive Leadership) ─────────────────────────────
    "chief executive officer": ("CEO", 100),
    "president and chief executive officer": ("CEO", 100),
    "president & ceo": ("CEO", 100),
    "president and ceo": ("CEO", 100),
    "chairman and ceo": ("CEO", 98),
    "chairman & ceo": ("CEO", 98),
    "co-founder and ceo": ("CEO", 98),
    "founder and ceo": ("CEO", 98),
    "ceo": ("CEO", 100),
    "president": ("CEO", 90),
    "owner": ("CEO", 88),
    "owner and president": ("CEO", 92),
    "founder": ("CEO", 86),
    "co-founder": ("CEO", 86),
    "cofounder": ("CEO", 86),
    "managing director": ("CEO", 92),
    "executive director": ("CEO", 88),
    "managing partner": ("CEO", 90),
    "principal": ("CEO", 82),
    "general manager": ("CEO", 84),
    "chief operating officer": ("CEO", 86),
    "coo": ("CEO", 86),
    "executive vice president": ("CEO", 80),
    "evp": ("CEO", 78),
    "senior vice president": ("CEO", 76),
    "svp": ("CEO", 76),
    "chairman": ("CEO", 88),
    "chairwoman": ("CEO", 88),
    "chairperson": ("CEO", 88),
    "proprietor": ("CEO", 82),

    # ── CFO (Finance / Accounting) ─────────────────────────────
    "chief financial officer": ("CFO", 100),
    "cfo": ("CFO", 100),
    "chief accounting officer": ("CFO", 96),
    "cao": ("CFO", 88),
    "corporate controller": ("CFO", 96),
    "financial controller": ("CFO", 96),
    "controller": ("CFO", 94),
    "comptroller": ("CFO", 94),
    "vice president of finance": ("CFO", 92),
    "vice president finance": ("CFO", 92),
    "vp of finance": ("CFO", 92),
    "vp finance": ("CFO", 92),
    "finance director": ("CFO", 92),
    "director of finance": ("CFO", 92),
    "head of finance": ("CFO", 90),
    "treasurer": ("CFO", 90),
    "accounting director": ("CFO", 88),
    "director of accounting": ("CFO", 88),
    "finance manager": ("CFO", 80),
    "accounting manager": ("CFO", 80),
    "financial director": ("CFO", 90),
    "senior accountant": ("CFO", 72),
    "staff accountant": ("CFO", 68),
    "tax director": ("CFO", 82),
    "audit director": ("CFO", 82),
    "payroll director": ("CFO", 78),
    "payroll manager": ("CFO", 76),
    "fp&a manager": ("CFO", 78),
    "financial planning and analysis": ("CFO", 78),

    # ── HR (Human Resources / Benefits) ────────────────────────
    "chief human resources officer": ("HR", 100),
    "chro": ("HR", 100),
    "chief people officer": ("HR", 98),
    "chief talent officer": ("HR", 96),
    "vice president of human resources": ("HR", 94),
    "vice president human resources": ("HR", 94),
    "vp of human resources": ("HR", 94),
    "vp human resources": ("HR", 94),
    "vp of hr": ("HR", 92),
    "vp hr": ("HR", 92),
    "vp people": ("HR", 90),
    "head of people": ("HR", 90),
    "head of hr": ("HR", 90),
    "head of human resources": ("HR", 90),
    "human resources director": ("HR", 92),
    "director of human resources": ("HR", 92),
    "hr director": ("HR", 92),
    "people director": ("HR", 88),
    "human resources manager": ("HR", 86),
    "hr manager": ("HR", 86),
    "hr generalist": ("HR", 78),
    "human resources generalist": ("HR", 78),
    "hr business partner": ("HR", 76),
    "hrbp": ("HR", 76),
    "people operations manager": ("HR", 88),
    "director of people operations": ("HR", 88),
    "people operations": ("HR", 86),
    "people and culture manager": ("HR", 86),
    "talent acquisition manager": ("HR", 84),
    "talent acquisition director": ("HR", 86),
    "talent acquisition": ("HR", 82),
    "talent manager": ("HR", 80),
    "recruiting manager": ("HR", 80),
    "recruiter": ("HR", 74),
    "benefits administrator": ("HR", 90),
    "benefits manager": ("HR", 88),
    "benefits director": ("HR", 90),
    "compensation manager": ("HR", 86),
    "compensation director": ("HR", 88),
    "compensation and benefits manager": ("HR", 92),
    "compensation and benefits": ("HR", 90),
    "total rewards": ("HR", 88),
    "employee relations manager": ("HR", 84),
    "employee relations": ("HR", 82),
    "personnel manager": ("HR", 82),
    "personnel director": ("HR", 86),
    "workforce development manager": ("HR", 80),
    "learning and development manager": ("HR", 78),
    "organizational development": ("HR", 78),
    "hr coordinator": ("HR", 72),
    "hr specialist": ("HR", 72),
}

# ── Negative patterns (reject BEFORE fuzzy) ────────────────────
NEGATIVE_WORDS = {
    "sales", "marketing", "software", "engineer", "engineering",
    "developer", "product", "business development", "customer success",
    "customer service", "project manager", "program manager",
    "account executive", "consultant", "advisor", "speaker", "author",
    "professor", "physician", "attorney", "realtor", "designer",
    "nurse", "creative", "advertising", "public relations",
    "supply chain", "logistics", "manufacturing", "research",
    "scientist", "data analyst", "quality", "regulatory", "legal",
    "counsel", "lawyer", "medical", "clinical", "insurance agent",
    "real estate", "teacher", "intern", "student", "assistant"
}

# ── Site/platform words (garbage) ──────────────────────────────
SITE_WORDS = {
    "linkedin", "facebook", "instagram", "twitter", "x",
    "zoominfo", "rocketreach", "crunchbase", "bloomberg",
    "contactout", "glassdoor", "indeed", "youtube"
}

# ── Credential suffixes ────────────────────────────────────────
CREDENTIALS = {
    "shrm-scp", "shrm-cp", "phr", "sphr", "gphr",
    "cpa", "cfa", "mba", "esq", "phd", "md", "jd",
    "msc", "ma", "ba", "pmp", "cma", "cgma"
}

# ── Company suffixes ───────────────────────────────────────────
COMPANY_SUFFIXES = {
    "llc", "inc", "corp", "corporation", "co", "company",
    "ltd", "plc", "group", "partners", "services", "holdings",
    "enterprises", "associates", "solutions", "consulting"
}

# ── Title indicator words ──────────────────────────────────────
TITLE_WORDS = {
    "chief", "officer", "director", "manager", "president", "vice",
    "vp", "evp", "svp", "owner", "founder", "partner", "principal",
    "administrator", "controller", "accounting", "finance", "financial",
    "human", "resources", "hr", "people", "talent", "benefits",
    "recruiting", "recruiter", "executive", "general", "treasurer",
    "accountant", "comptroller", "head", "chairman", "ceo", "cfo",
    "coo", "chro", "cpo"
}


# ═══════════════════════════════════════════════════════════════
# PRE-COMPILED REGEX (built once at import)
# ═══════════════════════════════════════════════════════════════

RE_MULTI_SPACE = re.compile(r"\s+")
RE_PARENS = re.compile(r"[\(\)\[\]\{\}]")

# Credential stripping
RE_CREDENTIALS = re.compile(
    r"(?:,\s*|\s+)(?:" + "|".join(re.escape(c) for c in CREDENTIALS) + r")\b\.?",
    re.IGNORECASE
)

# "at Company" extraction
RE_AT_COMPANY = re.compile(r"^(?P<title>.+?)\s+(?:at|@)\s+(?P<company>.+)$", re.IGNORECASE)

# Commentary tails
RE_COMMENTARY = re.compile(
    r",\s*(?:author|speaker|writer|consultant|advisor|board\s+member|investor|"
    r"certified|professional|graduate|volunteer)\b.*$",
    re.IGNORECASE
)

# VP with functional department (for negative matching)
RE_VP_WITH_DEPT = re.compile(
    r"\b(?:vice\s+president|vp)\s+(?:of\s+)?(?:sales|marketing|it|engineering|"
    r"technology|operations|product|legal|admin|business\s+development|"
    r"customer|supply\s+chain|manufacturing|research)\b",
    re.IGNORECASE
)

# Director/Manager with non-target department
RE_DIRECTOR_NONTARGET = re.compile(
    r"\b(?:director|manager)\s+(?:of\s+)?(?:sales|marketing|it|engineering|"
    r"software|product|legal|business\s+development|operations|"
    r"customer|supply\s+chain|manufacturing|research|technology)\b",
    re.IGNORECASE
)

# Sorted phrases for matching (longest first to match most specific)
SORTED_PHRASES = sorted(PHRASE_TAXONOMY.keys(), key=len, reverse=True)
PHRASE_PATTERNS = [
    (re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE), phrase, bucket, conf)
    for phrase, (bucket, conf) in [(p, PHRASE_TAXONOMY[p]) for p in SORTED_PHRASES]
]

# Fuzzy lexicon
FUZZY_LEXICON = [(phrase, bucket, conf) for phrase, (bucket, conf) in PHRASE_TAXONOMY.items()]
FUZZY_STRINGS = [x[0] for x in FUZZY_LEXICON]


# ═══════════════════════════════════════════════════════════════
# CLASSIFIER
# ═══════════════════════════════════════════════════════════════

class TitleClassifier:
    """
    3-tier title classifier: Exact → Regex → Fuzzy → Reject.
    Reusable tool for any process needing title→role mapping.
    """

    def __init__(self):
        # Build normalized exact-match dict for O(1) lookups
        self._exact_map = {
            self._normalize(phrase): (bucket, conf)
            for phrase, (bucket, conf) in PHRASE_TAXONOMY.items()
        }

    @staticmethod
    def _normalize(s: str) -> str:
        if not s:
            return ""
        s = unicodedata.normalize("NFKC", s)
        s = s.replace("\u2019", "'").replace("\u2018", "'")
        s = s.replace("\u2013", "-").replace("\u2014", "-")
        s = RE_PARENS.sub(" ", s)
        s = s.lower().strip()
        s = RE_MULTI_SPACE.sub(" ", s)
        return s

    def _clean(self, context: str, company: str = "") -> str:
        """Stage 1: Strip garbage, platforms, credentials, company names."""
        if not context:
            return ""

        s = self._normalize(context)

        # Standalone garbage
        if s.strip() in SITE_WORDS:
            return ""

        # Strip platform mentions
        for site in SITE_WORDS:
            s = re.sub(rf"\b{site}\b", " ", s)

        # Strip separators + content after them if it's a platform/company
        # "Name - Company | LinkedIn" → "Name"
        parts = re.split(r"\s*[|]\s*|\s+[-–—]\s+", s)
        kept = []
        for p in parts:
            p = p.strip()
            if not p or p in SITE_WORDS:
                continue
            kept.append(p)
        s = " | ".join(kept) if kept else ""

        # Strip credentials
        prev = None
        while prev != s:
            prev = s
            s = RE_CREDENTIALS.sub("", s).strip(" ,-|")

        # Strip commentary tails
        s = RE_COMMENTARY.sub("", s).strip(" ,-|")

        # Strip known company name
        if company:
            comp_norm = self._normalize(company)
            if comp_norm:
                s = re.sub(rf"\b{re.escape(comp_norm)}\b", " ", s)
                s = re.sub(rf"\s+(?:at|@)\s*$", "", s)

        s = RE_MULTI_SPACE.sub(" ", s).strip(" ,-|")
        return s

    def _extract_title(self, cleaned: str) -> str:
        """Stage 2: Isolate the title portion from cleaned context."""
        if not cleaned:
            return ""

        # Pattern: "title at company"
        m = RE_AT_COMPANY.match(cleaned)
        if m:
            candidate = m.group("title").strip(" ,-|")
            if candidate:
                return candidate

        # Split on remaining separators, keep most title-like chunk
        chunks = [c.strip(" ,-|") for c in re.split(r"\s*[|]\s*|\s+[-]\s+", cleaned) if c.strip()]
        if len(chunks) > 1:
            ranked = sorted(chunks, key=self._title_likeness, reverse=True)
            if ranked and self._title_likeness(ranked[0]) > 0:
                return ranked[0]

        # Handle comma-separated: "CEO, Author & Speaker" → "CEO"
        if "," in cleaned:
            first_part = cleaned.split(",")[0].strip()
            if self._title_likeness(first_part) > 0:
                return first_part

        # Use whole string if title-like
        if self._title_likeness(cleaned) > 0:
            return cleaned

        # Last resort — check if it's just company junk
        if self._looks_like_company(cleaned):
            return ""

        return cleaned

    @staticmethod
    def _title_likeness(s: str) -> int:
        tokens = s.lower().split()
        score = 0
        for t in tokens:
            if t in TITLE_WORDS:
                score += 3
            if t in COMPANY_SUFFIXES:
                score -= 3
            if t in SITE_WORDS:
                score -= 5
        return score

    @staticmethod
    def _looks_like_company(s: str) -> bool:
        if not s:
            return True
        tokens = s.lower().split()
        has_title = any(t in TITLE_WORDS for t in tokens)
        has_company = any(t in COMPANY_SUFFIXES for t in tokens)
        if has_company and not has_title:
            return True
        if not has_title and len(tokens) <= 5:
            return True
        return False

    def _has_negative_hint(self, title: str) -> bool:
        """Check for non-target functional keywords."""
        t = title.lower()
        # VP/Director with wrong department
        if RE_VP_WITH_DEPT.search(title):
            return True
        if RE_DIRECTOR_NONTARGET.search(title):
            return True
        # Standalone negative words
        for neg in NEGATIVE_WORDS:
            if re.search(rf"\b{re.escape(neg)}\b", t):
                return True
        return False

    @lru_cache(maxsize=10000)
    def _classify_cached(self, title_normalized: str) -> Tuple[str, int, str, str]:
        """Cached classification for repeated titles. Returns (bucket, conf, tier, phrase)."""

        # ── TIER 1: Exact dict lookup (O(1)) ──────────────────
        if title_normalized in self._exact_map:
            bucket, conf = self._exact_map[title_normalized]
            return bucket, conf, "EXACT", title_normalized

        # ── Check negatives before regex/fuzzy ─────────────────
        if self._has_negative_hint(title_normalized):
            # Allow override for very strong matches
            for pat, phrase, bucket, conf in PHRASE_PATTERNS:
                if pat.search(title_normalized) and conf >= 94:
                    return bucket, conf, "REGEX", phrase
            return "REJECT", 0, "REJECT", "negative_hint"

        # ── TIER 2: Regex phrase patterns ──────────────────────
        best_bucket = ""
        best_conf = 0
        best_phrase = ""
        for pat, phrase, bucket, conf in PHRASE_PATTERNS:
            if pat.search(title_normalized):
                if conf > best_conf:
                    best_bucket = bucket
                    best_conf = conf
                    best_phrase = phrase
        if best_conf >= 70:
            return best_bucket, best_conf, "REGEX", best_phrase

        # ── TIER 3: RapidFuzz fallback ─────────────────────────
        results = process.extract(
            title_normalized,
            FUZZY_STRINGS,
            scorer=fuzz.token_set_ratio,
            limit=3,
            score_cutoff=72,
        )
        if results:
            top_phrase, top_score, top_idx = results[0]
            _, fuzzy_bucket, base_conf = FUZZY_LEXICON[top_idx]
            # Blend fuzzy score with base confidence
            confidence = int(0.5 * base_conf + 0.5 * top_score)
            confidence = max(50, min(confidence, 88))  # Cap fuzzy at 88
            return fuzzy_bucket, confidence, "FUZZY", top_phrase

        return "REJECT", 0, "REJECT", "no_match"

    def classify(self, context: str, company: str = "") -> ClassifyResult:
        """Full pipeline: clean → extract → classify."""
        cleaned = self._clean(context, company)
        title = self._extract_title(cleaned)

        if not title:
            return ClassifyResult(
                original=context, cleaned=cleaned, extracted_title="",
                bucket="REJECT", confidence=0, tier="REJECT",
                matched_phrase="", reason="empty after cleaning"
            )

        norm = self._normalize(title)
        bucket, conf, tier, phrase = self._classify_cached(norm)

        reason = f"{tier.lower()}: matched '{phrase}'" if bucket != "REJECT" else phrase
        return ClassifyResult(
            original=context, cleaned=cleaned, extracted_title=title,
            bucket=bucket, confidence=conf, tier=tier,
            matched_phrase=phrase, reason=reason
        )

    def classify_batch(self, records: List[Dict], context_key: str = "context",
                       company_key: str = "company") -> List[ClassifyResult]:
        """Batch classify. Pure Python loop — fast enough for 27K."""
        return [
            self.classify(r.get(context_key, ""), r.get(company_key, ""))
            for r in records
        ]


# ═══════════════════════════════════════════════════════════════
# SMOKE TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import time

    tc = TitleClassifier()

    test_cases = [
        ("General Manager at Ocean Reef Resort - LinkedIn", "Ocean Reef Resort"),
        ("CEO PDRI by Pearson, Author & Speaker", "PDRI by Pearson"),
        ("Chief Executive Officer | LinkedIn", ""),
        ("Executive Vice President at The Center for Leadership", "The Center for Leadership"),
        ("Ocean Lakes Service Corp. - LinkedIn", "Ocean Lakes Service Corp."),
        ("Facebook", ""),
        ("Owner at Freedom Flooring LLC | LinkedIn", "Freedom Flooring LLC"),
        ("Global Director of HR at Horseware | SHRM-SCP", "Horseware"),
        ("Director of Business Development | LinkedIn", ""),
        ("Vice President of Sales, Export & Foodservice", ""),
        ("Controller at Acme Corp", "Acme Corp"),
        ("Benefits Administrator", ""),
        ("President and CEO", ""),
        ("Software Engineer at Google - LinkedIn", "Google"),
        ("Sales Manager | TechCorp", "TechCorp"),
        ("VP of Human Resources at BigBank | SHRM-CP", "BigBank"),
        ("Chief People Officer | People Co. | LinkedIn", "People Co."),
        ("Treasurer at First National", "First National"),
        ("HR Manager", ""),
        ("Managing Partner", ""),
    ]

    print(f"{'CONTEXT':<52} {'EXTRACTED':<28} {'BUCKET':<8} {'CONF':>4} {'TIER':<6}")
    print("-" * 110)

    for ctx, company in test_cases:
        r = tc.classify(ctx, company)
        ctx_short = ctx[:50] + ".." if len(ctx) > 50 else ctx
        title_short = r.extracted_title[:26] + ".." if len(r.extracted_title) > 26 else r.extracted_title
        print(f"{ctx_short:<52} {title_short:<28} {r.bucket:<8} {r.confidence:>4} {r.tier:<6}")

    # Performance benchmark
    print("\n--- Performance Benchmark ---")
    large = [{"context": ctx, "company": co} for ctx, co in test_cases] * 1350  # ~27K
    t0 = time.perf_counter()
    results = tc.classify_batch(large)
    elapsed = time.perf_counter() - t0
    print(f"{len(large):,} records in {elapsed:.2f}s ({len(large)/elapsed:,.0f} rec/sec)")

    # Distribution
    from collections import Counter
    dist = Counter(r.bucket for r in results)
    for bucket, cnt in dist.most_common():
        print(f"  {bucket}: {cnt:,} ({cnt/len(results)*100:.1f}%)")
