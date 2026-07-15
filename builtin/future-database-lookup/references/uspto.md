# USPTO Public APIs

## ⚠️ Overview (2026-07-15)

The USPTO API landscape has changed significantly. All confirmed findings:

| Service | Domain | Status |
|---------|--------|--------|
| PatentsView (old) | `patentsview.org` | 🔴 301 → data.uspto.gov (migrated) |
| PatentsView Search | `search.patentsview.org` | 🔴 DNS NXDOMAIN (dead) |
| PatentsView API | `api.patentsview.org` | 🔴 301 (dead) |
| PEDS | `ped.uspto.gov` | 🔴 DNS intermittent (unstable) |
| New USPTO API | `api.uspto.gov` | 🟢 Alive, needs AWS API Gateway key |
| Patent Public Search | `ppubs.uspto.gov` | 🟢 Web UI, no public API |
| Bulk Data | `bulkdata.uspto.gov` | 🟢 FTP/bulk downloads |

---

## Option A: New USPTO API Gateway (Recommended — requires API key)

```
Base URL: https://api.uspto.gov
Auth:     X-Api-Key header (AWS API Gateway)
```

The `api.uspto.gov` gateway is active and returns `MissingAuthenticationTokenException` without a key.

**To get an API key:**
1. Register at https://developer.uspto.gov/user/register
2. Create an application to obtain an API key
3. Pass the key via `X-Api-Key` header

## Option B: Patent Public Search (Web UI)

```
https://ppubs.uspto.gov/pubwebapp/
```
Full-text patent search via web interface. No documented public API endpoint.

## Option C: USPTO Bulk Data (for batch processing)

```
https://bulkdata.uspto.gov/
```
Full patent data in XML/JSON for offline/batch processing. Not a live search API but the most complete data source.

## Option D: PEDS — Patent Examination Data System (May Be Unstable)

**URL**: `https://ped.uspto.gov/api/queries`
**Method**: POST

For patent prosecution status data:
```json
{
  "searchText": "applicationNumberText:16123456",
  "fl": "*",
  "mm": "100%",
  "df": "patentTitle",
  "facet": "false",
  "sort": "applId asc",
  "start": 0
}
```

⚠️ DNS is intermittent — may require retries.

## Option E: TSDR — Trademark Status

```
GET https://tsdr.uspto.gov/documentxml/status/{serial_number}
GET https://tsdr.uspto.gov/documentxml/status/rn{registration_number}
```
XML only. No JSON. Rate limited. Requires knowing the serial/registration number.

---

## Alternative Patent Databases (Free / No API Key)

| Service | URL | API | Notes |
|---------|-----|-----|-------|
| **EPO OPS** | https://www.epo.org/searching-for-patents/data/web-services/ops.html | REST+API key (free reg) | 4 req/sec, worldwide |
| **Google Patents** | https://patents.google.com/ | Web UI + BigQuery | Google Cloud account needed for BigQuery |
| **The Lens** | https://www.lens.org/ | REST+API key (free) | Requires human verification |
| **Espacenet** | https://worldwide.espacenet.com/ | Web UI | Cloudflare-protected |
| **USPTO Bulk** | https://bulkdata.uspto.gov/ | FTP/HTTP download | Not a live search API |
