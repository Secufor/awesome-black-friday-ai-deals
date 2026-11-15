# Contributing

Thanks for adding a deal. Submitting your own product is fine; just say so in the PR or issue.

## What gets accepted

- A Black Friday / Cyber Monday deal that is **live now** (or announced with dates for this year).
- An AI tool, developer tool or API, creator / video / design tool, or productivity, SEO or marketing software.
- The offer is written on a page the vendor controls (site, pricing page, blog, or their official social post). That page goes in `source_url`.
- Links have **no affiliate, referral or tracking parameters** (`?ref=`, `?via=`, `utm_*`...). The CI check rejects them.
- One plain sentence of description. No "best", "revolutionary" or emoji.

## Option 1: open an issue (no code)

Use the [Submit a deal](../../issues/new?template=submit-deal.yml) form. We'll add it.

## Option 2: pull request

1. Add one object to `data/deals.json`:

```json
{
  "name": "Example",
  "url": "https://example.com",
  "category": "AI tools",
  "description": "Turns meeting recordings into searchable notes.",
  "deal": "40% off annual plans",
  "code": "BF40",
  "ends": "2026-12-02",
  "source_url": "https://example.com/black-friday",
  "verified_on": "2026-11-20",
  "lifetime": false
}
```

   - `category` is one of: `AI tools`, `Developer tools & APIs`, `Creator, video & design`, `Productivity, SEO & marketing`.
   - `code` is `null` when no code is needed. `ends` is `YYYY-MM-DD` or `"not stated"`.
2. Run `python3 scripts/build_readme.py` (Python 3, no dependencies). It validates the data and rebuilds `README.md`. Don't edit the tables in `README.md` by hand.
3. Commit both files and open the PR.

The order inside each section is alphabetical; the script handles it.
