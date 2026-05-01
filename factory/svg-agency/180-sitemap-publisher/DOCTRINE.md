# DOCTRINE — Process 180 Sitemap Publisher
## Locked rules. Auditor enforces. Violations halt sitemap rendering or SEO indexing.

| # | Rule | Source | Gate |
|---|------|--------|------|
| D-180-01 | SitemapEntry is the canonical shape for all sitemap data. Required fields: site, site_label, path, title, url, parent, depth, priority, changefreq, last_modified. No additional fields may be added to the public response without a DOCTRINE amendment. | sitemap.ts SitemapEntry interface | §5 stop — schema drift breaks downstream consumers (MapEngine, XML generator) |
| D-180-02 | GET /sitemap returns all entries across all sites. GET /sitemap/:site returns entries filtered to one site slug. These are the only two sanctioned read paths. No other routes may be added to the sitemap endpoint without a BAR. | sitemap.ts route definitions | §8 stop — unauthorized routes bypass the single-source-of-truth constraint |
| D-180-03 | Static site entries are the authoritative source for sitemap data. The INSURANCE_INFORMATICS_ENTRIES array in sitemap.ts is the canonical registry for insuranceinformatics.com URLs. Dynamic generation from D1 or external sources requires a separate BAR and updated DOCTRINE. | sitemap.ts INSURANCE_INFORMATICS_ENTRIES | pre-flight — mixing static + dynamic sources without a declared join contract breaks idempotency |
| D-180-04 | depth is computed from pathDepth() — the number of path segments. parent is computed from parentPath() — the path minus the last segment. slugToTitle() converts hyphenated slugs to title-cased display strings. These three helper functions are the only sanctioned path-metadata derivations. | sitemap.ts slugToTitle(), pathDepth(), parentPath() | pre-flight — re-implementing path derivation in callers creates drift |
| D-180-05 | priority values must be between 0.0 and 1.0 inclusive. changefreq must be one of: always, hourly, daily, weekly, monthly, yearly, never. Values outside these enums are rejected at the sitemap XML generation layer. | XML sitemap spec + sitemap.ts SitemapEntry | §8 stop — out-of-range values break sitemap XML validation |
| D-180-06 | site slug in GET /sitemap/:site must match a registered site in the static entries array. Unknown site slugs return an empty array, not a 404. This is intentional — callers must not treat 200+empty as an error. | sitemap.ts GET /sitemap/:site handler | §8 stop — treating empty-array response as error causes false alarms |
| D-180-07 | The sitemap endpoint is read-only. No write, update, or delete operations are permitted on sitemap data via this endpoint. Sitemap data changes require a code deploy (static entries update) and a BAR. | BAR-322 scope | §9 stop — write operations on a read-only endpoint violate process scope |
| D-180-08 | last_modified is an ISO 8601 date string (YYYY-MM-DD format). It must reflect the actual last content modification date, not the current date at request time. Stale last_modified values degrade SEO crawl efficiency. | SitemapEntry + XML sitemap spec | pre-flight — dynamic last_modified = current date is a known anti-pattern |
| D-180-09 | url is the fully qualified canonical URL (https://). path is the relative path (/). Both are required. url must be derivable from path by prepending the site's base URL. No relative urls in the url field. | SitemapEntry interface | §5 stop — relative URLs in the url field break XML sitemap validation |
| D-180-10 | This process is scoped to insuranceinformatics.com sitemap data only. Adding sitemaps for other domains requires a separate process number and DOCTRINE. | BAR-322 scope | pre-flight — multi-domain sitemap without separate docs is a governance violation |

## Cross-references
- UT §5 CONTRACT references D-180-01 (SitemapEntry shape)
- UT §4 IMO references D-180-02 (read paths), D-180-03 (static source)
- UT §8 INGEST CHECKLIST references D-180-05 (enum validation), D-180-08 (last_modified)
- UT §9 PERMISSIONS references D-180-07 (read-only)

## Document Control
| Field | Value |
|---|---|
| Created | 2026-04-30 |
| BAR | BAR-322 |
| Authority | inherited from imo-creator (sovereign) + Barton-Processes (parent) |
| Locked | yes — only the process owner amends |
| Inherits | KEY.md + Bedrock + Atlas §1.6 |
| Rule Count | 10 (D-180-01 through D-180-10) |
