"""
KEY BUILDER CONSTANTS — The guard rails

Every element on a page must fit into one of these defined buckets.
If it doesn't fit → unidentified. No guessing. No loose patterns.

Each bucket is a constant: named, described, formatted.
The value that fills it is the variable.

Used by: page-parser.py (PROC-301), any future page parsing process
This IS a Snap-On Tool — reusable across any process that reads a page.
"""

# ═══════════════════════════════════════════════════════════════
# THE BUCKETS — If it doesn't fit one of these, it's unidentified
# ═══════════════════════════════════════════════════════════════

BUCKETS = {
    "company": {
        "id": "KB-01",
        "description": "Company or organization name",
        "format": "TEXT, proper case or ALL CAPS, 2-100 chars",
    },
    "position": {
        "id": "KB-02",
        "description": "Job position/role — a defined role in the organization",
        "format": "TEXT, one of the known position constants below",
    },
    "title": {
        "id": "KB-03",
        "description": "Full job title string containing a position keyword",
        "format": "TEXT, contains a position keyword + optional qualifiers, 3-120 chars",
    },
    "person_name": {
        "id": "KB-04",
        "description": "A human person's name — first and last minimum",
        "format": "TEXT, title case, 2-4 words, first word capitalized, last word capitalized, 4-50 chars",
    },
    "email": {
        "id": "KB-05",
        "description": "An email address — personal (not generic)",
        "format": "TEXT, user@domain.tld, user is not info/contact/admin/support/hello/office/sales/hr/careers",
    },
    "linkedin_url": {
        "id": "KB-06",
        "description": "A LinkedIn personal profile URL",
        "format": "TEXT, URL matching https://linkedin.com/in/{slug}",
    },
    "phone": {
        "id": "KB-07",
        "description": "A phone number",
        "format": "TEXT, matches (NNN) NNN-NNNN or NNN-NNN-NNNN or +1NNNNNNNNNN",
    },
    "unidentified": {
        "id": "KB-99",
        "description": "Element that does not fit any defined bucket — stored, not discarded",
        "format": "TEXT, any — the raw text content of the element",
    },
}


# ═══════════════════════════════════════════════════════════════
# POSITION CONSTANTS — The known positions we recognize
# ═══════════════════════════════════════════════════════════════
# If a text matches one of these, it's a POSITION (KB-02).
# If a text CONTAINS one of these inside a longer string, it's a TITLE (KB-03).

POSITIONS = {
    # C-Suite
    "CEO", "CFO", "COO", "CTO", "CIO", "CHRO", "CMO", "CPO", "CLO", "CSO",

    # Long-form C-Suite
    "Chief Executive Officer",
    "Chief Financial Officer",
    "Chief Operating Officer",
    "Chief Technology Officer",
    "Chief Information Officer",
    "Chief Human Resources Officer",
    "Chief Marketing Officer",
    "Chief People Officer",
    "Chief Legal Officer",
    "Chief Security Officer",
    "Chief Administrative Officer",
    "Chief Strategy Officer",
    "Chief Revenue Officer",

    # Executive
    "President",
    "Vice President",
    "Senior Vice President",
    "Executive Vice President",
    "Managing Director",
    "Managing Partner",
    "Executive Director",
    "General Manager",

    # Director-level
    "Director",
    "Senior Director",
    "Associate Director",

    # Owner/Founder
    "Owner",
    "Co-Owner",
    "Founder",
    "Co-Founder",
    "Principal",
    "Partner",

    # Finance-specific
    "Controller",
    "Comptroller",
    "Treasurer",
    "Finance Director",
    "VP Finance",
    "VP of Finance",
    "Director of Finance",

    # HR-specific
    "HR Director",
    "Director of HR",
    "Director of Human Resources",
    "VP HR",
    "VP of HR",
    "VP Human Resources",
    "VP of Human Resources",
    "Head of HR",
    "Head of People",
    "Head of Talent",
    "Benefits Manager",
    "Benefits Director",
    "Benefits Administrator",

    # Board
    "Board Member",
    "Board Chair",
    "Chairman",
    "Chairwoman",
    "Chair",
}

# Lowercase set for matching
POSITIONS_LOWER = {p.lower() for p in POSITIONS}


# ═══════════════════════════════════════════════════════════════
# CLASSIFICATION RULES — strict, no guessing
# ═══════════════════════════════════════════════════════════════

import re

# Person name: STRICT rules
# Must have 2-4 words, each starting with uppercase
# Must NOT contain any of these
NAME_REJECT_WORDS = {
    # Navigation / UI
    "home", "about", "contact", "services", "team", "careers", "news", "blog",
    "products", "resources", "support", "login", "sign", "menu", "close",
    "search", "submit", "read", "learn", "view", "click", "more", "see",
    "share", "follow", "subscribe", "download", "upload", "edit", "save",
    "profile", "settings", "account", "dashboard", "report", "featured",
    "properties", "listings", "testimonials", "reviews", "gallery",
    "schedule", "appointment", "request", "quote", "estimate",
    "recent", "popular", "trending", "latest", "archived", "saved",

    # Company structure words
    "inc", "llc", "ltd", "corp", "corporation", "company", "co", "group",
    "services", "solutions", "partners", "associates", "agency", "center",
    "foundation", "institute", "university", "college", "hospital",
    "insurance", "financial", "consulting", "management", "technology",

    # Page structure
    "privacy", "policy", "terms", "conditions", "copyright", "reserved",
    "cookie", "disclaimer", "sitemap", "accessibility",

    # Generic headings
    "our", "the", "meet", "why", "how", "what", "get", "your", "we",
    "leadership", "executive", "management", "staff", "directory",
    "expertise", "experience", "interest", "vehicles", "small", "business",
}

# Emails to reject (generic/role-based)
GENERIC_EMAIL_PREFIXES = {
    "info", "contact", "admin", "support", "hello", "office", "sales", "hr",
    "careers", "jobs", "team", "general", "enquiries", "mail", "help",
    "webmaster", "postmaster", "noreply", "no-reply", "billing", "press",
    "media", "marketing", "reception", "feedback", "service",
}

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
LINKEDIN_RE = re.compile(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+')
POSITION_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(p) for p in sorted(POSITIONS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE
)


def classify_element(text, href=None, company_name=""):
    """
    Classify a text element into a bucket. Strict rules only.
    Returns (bucket, confidence, matched_value)
    """
    if not text or len(text.strip()) < 2:
        return "unidentified", 0, None

    text = text.strip()
    lower = text.lower()

    # ── LinkedIn URL (check href first, then text) ──────────
    check_url = href or text
    if LINKEDIN_RE.search(check_url):
        return "linkedin_url", 95, LINKEDIN_RE.search(check_url).group()

    # ── Email ────────────────────────────────────────────────
    email_match = EMAIL_RE.search(text)
    if email_match and len(text) < 60:
        addr = email_match.group()
        prefix = addr.split("@")[0].lower()
        # Reject bad domains in the email itself
        if any(x in addr.lower() for x in ['example', 'wix', 'wordpress', 'sentry', 'jquery', '.png', '.jpg']):
            return "unidentified", 0, None
        if prefix in GENERIC_EMAIL_PREFIXES:
            return "unidentified", 0, None  # Generic emails are unidentified, not useful for person fill
        return "email", 90, addr

    # ── Phone ────────────────────────────────────────────────
    if PHONE_RE.search(text) and len(text) < 30:
        return "phone", 80, PHONE_RE.search(text).group()

    # ── Position (exact match — the whole text IS a position) ─
    if lower.strip().rstrip('.,:;') in POSITIONS_LOWER:
        return "position", 95, text.strip()

    # ── Title (contains a position keyword in longer text) ───
    if POSITION_RE.search(text) and len(text) < 120:
        match = POSITION_RE.search(text)
        return "title", 85, text

    # ── Company name match ───────────────────────────────────
    if company_name:
        co_lower = company_name.lower()
        if co_lower in lower or lower in co_lower:
            return "company", 80, text

    # ── Person name (STRICT) ────────────────────────────────
    words = text.split()
    if 2 <= len(words) <= 4 and 4 <= len(text) <= 50:
        # Every word must start with uppercase (allow single char initials like "J.")
        all_cap_start = all(
            (w[0].isupper() or (len(w) <= 2 and w.endswith('.')))
            for w in words if len(w) > 0
        )
        # No reject words
        no_reject = not any(w.lower().rstrip('.,;:') in NAME_REJECT_WORDS for w in words)
        # No numbers
        no_numbers = not any(c.isdigit() for c in text)
        # No special chars
        no_special = not any(c in text for c in ['@', 'http', '/', '\\', '<', '>', '=', '{', '}', '#', '&'])
        # Not all caps (unless very short like "TOM SMITH" — allow if 2 words)
        not_all_caps = not text.isupper() or len(words) == 2
        # Not matching company name
        company_match = False
        if company_name:
            co_words = set(company_name.lower().split())
            name_words = set(lower.split())
            if co_words and len(name_words & co_words) / max(len(co_words), 1) > 0.4:
                company_match = True

        if all_cap_start and no_reject and no_numbers and no_special and not_all_caps and not company_match:
            # Strip common suffixes for validation
            clean = re.sub(r',?\s*(RN|CNA|LPN|MD|PhD|DDS|DMD|CPA|Esq|Jr|Sr|II|III|IV)\.?$', '', text, flags=re.I).strip()
            clean_words = clean.split()
            if len(clean_words) >= 2:
                return "person_name", 75, text

    # ── Everything else → unidentified ───────────────────────
    return "unidentified", 0, None
