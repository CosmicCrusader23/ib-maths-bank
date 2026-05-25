# IB Maths Bank

Curated, merged question bank for IB Mathematics — Analysis & Approaches (AA) and
Applications & Interpretation (AI), HL and SL — pulled from publicly available
revision sources and grouped by syllabus topic.

## Sources (v1)

| Source | What it gives us | Status |
|---|---|---|
| [pestle](https://pestle.pages.dev/) | 815 AA + 835 AI questions tagged with topic + subtopic from real IB papers | implemented |
| [Christos Nikolaidis](https://www.christosnikolaidis.com/en/maa-exercise/) | 225 PDF exercise sheets organised by AA syllabus subtopic | implemented (metadata + links) |
| Save My Exams archive | exam-style questions per topic | planned |
| ThinkIB / StudyIB | topic-organised practice | planned (auth needed) |
| Madas Maths | A-level booklets by topic | planned |
| IB QuestionBank (ibdocs.re) | original IB QB PDFs | planned |

Auth-walled or pirated-only sources (Revision Village, ibtaskmaker, Alcumus) are
left as stubs — drop a cookie/token in `etl/.env` when you have one.

## Layout

- `etl/` — Python ETL: scrapers + SQLite + JSON export
  - `etl/ib_etl/sources/<source>.py` — one module per source
  - `etl/ib_etl/db.py` — schema
  - `etl/ib_etl/topics.py` — canonical IB MAA topic taxonomy
  - `etl/ib_etl/export.py` — SQLite → per-topic JSON for the site
- `site/` — Next.js static site (browse questions by topic / subtopic / source)
- `data/` — committed artefacts: `questions.db` (SQLite) + `site/public/data/*.json`

## Run

```bash
cd etl
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m ib_etl.ingest pestle      # ~50MB download, one-off
python -m ib_etl.ingest christos
python -m ib_etl.export             # writes site/public/data/*.json

cd ../site
pnpm install
pnpm dev                            # browse locally
pnpm build                          # static export to site/out/
```

## Topic taxonomy

We use the IB MAA HL syllabus topics as the canonical grouping:

1. Number and algebra
2. Functions
3. Geometry and trigonometry
4. Statistics and probability
5. Calculus

Each question is tagged with `topic`, optional `subtopic` (where the source
provides one), `level` (`SL` / `AHL` / `AI-SL` / `AI-HL`), and the original
source URL.
