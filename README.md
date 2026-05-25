# IB Revision Bank

Curated, merged question bank for IB Mathematics (AA & AI) and IB Physics —
pulled from publicly available revision sources and grouped by syllabus topic.

**Live:** https://ib.mycosmic.dev/ (once DNS is wired) / https://cosmiccrusader23.github.io/ib-maths-bank/ (always).

## Sources (v1)

| Source | Subject | What it gives us | Status |
|---|---|---|---|
| [pestle](https://pestle.pages.dev/) | Maths AA, AI, Physics | 815 + 835 + 1305 questions tagged with topic + subtopic from real IB papers | implemented |
| [Christos Nikolaidis](https://www.christosnikolaidis.com/en/maa-exercise/) | Maths AA | 70 PDF worksheet bundles by syllabus subtopic | implemented (links + metadata) |
| Save My Exams archive (`smearchive.pages.dev`) | All | Returns 403 to scrapers — Cloudflare bot challenge | blocked |
| ibdocs.re (ThinkIB / StudyIB / IB QB PDFs) | All | JS-obfuscated anti-scrape challenge — needs headless browser | blocked |
| Madas Maths | A-level (not IB) | Topic booklets for A-level. Not IB-aligned, dropped from v1 | parked |

Auth-walled or pirated-only sources (Revision Village, ibtaskmaker, Alcumus)
are stubbed in `etl/ib_etl/sources/_stub.py` — drop a real loader when you
have credentials.

### To unblock the blocked sources

- **smearchive / ibdocs**: needs a headless browser (Playwright). The recipe
  would be: `playwright.chromium.launch()` → solve any JS challenge → enumerate
  the directory listing → download the PDFs → OCR-extract questions. Worth
  doing in a follow-up since both have great content.
- **Revision Village / ibtaskmaker**: drop a session cookie into
  `etl/.env` then write a loader that includes `Cookie: ...` in requests.

## Layout

- `etl/` — Python ETL: scrapers + SQLite + JSON export
  - `etl/ib_etl/sources/<source>.py` — one module per source
  - `etl/ib_etl/db.py` — schema (subject + topic_id + everything else)
  - `etl/ib_etl/topics.py` — per-subject syllabus taxonomy
  - `etl/ib_etl/export.py` — SQLite → per-subject/per-topic JSON
- `site/` — Next.js static site
- `data/` — local SQLite (gitignored, regenerable)

## Run

```bash
cd etl
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m ib_etl ingest pestle christos     # ~70MB download, one-off
python -m ib_etl export                     # writes site/public/data/

cd ../site
pnpm install
pnpm dev                                    # browse at localhost:3000
pnpm build                                  # static export to site/out/
```

### Deploy

GitHub Actions is committed (`.github/workflows/deploy.yml`) but currently
fails because the GitHub account is billing-locked. Until that's resolved
the site is deployed manually:

```bash
# from repo root, after a successful pnpm build
git worktree add /tmp/pages gh-pages
cd /tmp/pages
git reset --hard origin/gh-pages
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
rsync -a /Users/cosmic/Documents/funni/ib-maths-bank/site/out/ ./
git add -A && git commit -m "Build" && git push origin gh-pages
cd .. && git -C ../ib-maths-bank worktree remove /tmp/pages --force
```

## Topic taxonomy

- **Maths AA / AI** use the IB MAA/MAI top-level groupings (1–5):
  Number & algebra, Functions, Geometry & trig, Stats & prob, Calculus.
- **Physics** uses the 12 core topics (1–12) plus 4 options (a–d).

Each question is tagged with `subject`, `topic_id`, `subtopic` (where the
source provides one), `level` (`SL`/`HL`/`BOTH`), `paper`, `year`, `session`,
and the original source URL.
