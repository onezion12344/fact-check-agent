# Google Photos Third-Party API Limitation (May 2025)

> Source: MultCloud official help page (February 2026 post), wikiHow, Cloudwards
> Status: Verified 2026-06-26

## The Change

**As of May 7, 2025, Google updated its Google Photos API.** This change fundamentally broke third-party migration tools (MultCloud, CloudHQ, etc.) that previously could transfer entire photo libraries between accounts.

## What Broke

| Capability | Before May 2025 | After May 2025 |
|:-----------|:---------------:|:--------------:|
| List all existing albums | ✅ Full access | ❌ **Only albums created via the tool itself** |
| List all existing photos | ✅ Full access | ❌ **Only photos uploaded via the tool itself** |
| Transfer entire library | ✅ One-click | ❌ **Manual "Add More Photos" — max 2,000 at a time, expires 7 days** |
| Preserve metadata (dates, geo) | ✅ | ❌ **Lost — photos reflect transfer date** |
| Keep original resolution | ✅ | ❌ **Compressed to "high quality"** |

Source: multcloud.com/help/add-and-transfer-googlephotos.html

## Impact on Recommendations

**If user asks about migrating Google Photos between accounts:**
- ✅ **Partner Sharing** is the only method that preserves quality, dates, and location — it's built into Google Photos, not a third-party tool
- ❌ Do NOT recommend MultCloud or CloudHQ without noting these severe limitations
- ❌ Google Takeout works but creates 240+ ZIP files for 500GB (tedious)

## Migration Methods Comparison (Current 2026)

| Method | Quality | Dates/Geo | Albums | Effort |
|:-------|:-------:|:---------:|:------:|:------|
| **Partner Sharing** | ✅ Original | ✅ Preserved | ❌ Lost | 10 min setup |
| **Google Takeout** | ✅ Original | ✅ Preserved | ✅ Kept in ZIP | Days (download→upload) |
| **MultCloud** (post-2025) | ❌ Compressed | ❌ Lost | ❌ Lost | Manual, 2000/batch |

## Data Point

Google community thread (Oct 2025): User with 500GB photos reported Takeout created **240 ZIP files** — "tedious to download and reupload."
