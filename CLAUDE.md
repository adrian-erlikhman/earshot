# CLAUDE.md — Earshot (AI for Peace @ NeurIPS 2026)

Project brief, decisions, gotchas and commands. Kept current so a fresh session can
pick up cold. **Last updated 2026-09-12 (night).**

## What this is

**Earshot** — a submission to the **AI for Peace workshop @ NeurIPS 2026** (2nd
edition, Paris, Dec 12 or 13). Team: **Adrian Erlikhman** (presenting author, attends in
person, solo) and **Michael Tarekegn**. Repo: `adrian-erlikhman/earshot` (**public**).

**Thesis.** We link ACL Anthology papers to the USPTO patents that cite them and classify
what those patents are *for*. Surveillance-classified patents are rare among NLP-citing
patents and, compared within the same grant era, not distinguishable from science-citing
patents in general. The public patent record cannot settle whether NLP research feeds
surveillance — citations show proximity, not transmission. The solid contributions are
methodological: authentication vs identification, the unreliability of technology classes
as a surveillance proxy, and applicant-name bias in LLM labels.

**Recommended title:** *Proximity, Not Transmission: What the Patent Record Can and Cannot
Show About NLP and Surveillance.*

## Hard constraints (verified from source, 2026-09-10)

- **Submission is a Google Form with pasted text. No file upload.** Abstract field
  **2,500 characters max**, references included. Separate TL;DR **300 characters max**.
  **The hero figure cannot be submitted** — poster only.
- Deadline **Mon 21 Sept AoE = Tue 22 Sept 05:00 Pacific**. Decisions Sept 29.
- Single-blind. Poster / talk / both. Published, novel and in-progress work accepted.
- In-person attendance is a gating form question; no travel funding.
- **Never submit to the venue or post publicly.** Adrian and Michael do that. Emails to
  Michael go out only on Adrian's explicit request.

## Status — 2026-09-12 (night)

Authoritative: the **FINAL STATUS** block at the bottom of `CLAIMS.md`, checked against
the results files by `tools/verify_brief.py`. Narrative: `LOG.md`. Writing guide and
draft abstract: `paper/BRIEF.md` / `.pdf`.

- **Pipeline:** 127,851 ACL papers → 69,327 in OpenAlex → 26,085 links → 9,048 citing
  USPTO records (8,553 granted, 487 pre-grant application publications, 8 other). Zhang
  replication: 24,829 papers vs his 24,821. 91.6% of links are front-page-only.
- **Headline (seed-42 random sample, assignee hidden, granted patents):** 11 of 2,374 =
  0.46% surveillance [0.25, 0.80].
- **Era-matched comparison with the control:** Mantel–Haenszel OR 1.03 [0.38, 2.78],
  p = 0.95. The crude comparison is era-confounded — never quote it.
- **H1:** 0 of 10 subfields significant. **H2:** no trend.
- **Applicant-name bias:** 10 of 31 non-neutral labels (32%) flip when the assignee is
  hidden, in both directions.
- **Technology classes:** 69 patents in surveillance-related IPC classes; the rubric codes
  2 surveillance, 64 neither. Not yet human-validated.
- **Pending:** gold-set coding Sunday 13 Sept; Michael's 50-link check. The speech arm is
  parked (OpenAlex rate limits) and is not needed for the abstract.

## Claims we must NOT make

- ❌ "First to link NLP papers to patents." False — Zhang, ACL 2025 (arXiv:2505.16061).
- ❌ Any crude treatment-vs-control ratio. Report only the era-matched result, as a bound.
- ❌ "Examiners overcount surveillance." Examiners assign technology classes and never
  judged surveillance. Say: technology classes are a poor proxy for surveillance.
- ❌ "Most examiner-class patents are assistants." Nearly half (29 of 64), by title.
- ❌ "Keyword proxies overcount." Never tested.
- ❌ "Reliance on Science v65 covers 2015–2025 grants." False — it reaches before 1976
  and includes pre-grant application publications.
- ❌ Subfield concentration, or its absence, as a strong finding. Too few events.
- Noa Garcia, the workshop's General Chair, co-authored the computer-vision version
  (Garcia & Katirai, FAccT 2026). Every adjacent claim must be exact.

## Classification protocol

- Rubric: `configs/patent_rubric.md` with **AMENDMENT v1.1** (gate = per-class F1 on
  `surveillance`, not omnibus kappa) and **v1.2** (assignee **hidden** for the model AND
  both coders).
- Model: `google/gemini-2.5-flash-lite`, temperature 0; deterministic on re-call.
- Primary labels: `results/patent_labels.csv` (**seed-42 sample only**) and
  `results/control_labels.csv`. Full treatment fetch: `patent_labels_all_fetched.csv`.
  Assignee-shown sensitivity labels: `*_assignee_shown.csv` (from the old truncated run).
- Gold set: `data/goldset/`, 200 items stratified by model label x surveillance-type IPC,
  weights in `strata.json`, answer key gitignored. Built before the sampling fix, so items
  skew 2018–2023 — valid for agreement, not for population rates.
- **Blinding is honor-system.** `results/patent_labels.csv` is public. Adrian has seen
  model labels for several surveillance items; Michael has not, so Michael's labels are the
  reference there. Both coders are authors. Filled sheets are emailed, not committed, until
  both are done. Never send Michael item-level results before coding.

## Ethics position

- Public data only. No PII. No deanonymization of real people.
- We do not build, optimize or release any surveillance or attribution capability.
  Aggregates and the rubric only.
- Report assignee organizations, never named inventors.

## Data sources

| Source | Access | Notes |
|---|---|---|
| ACL Anthology XML | `codeload.github.com/acl-org/acl-anthology/tar.gz/refs/heads/master` | 127,851 papers. Old ID scheme: `P19.xml` = ACL 2019, `D` EMNLP, `N` NAACL — `venue_key` maps these |
| OpenAlex API | `api.openalex.org`, `mailto` polite pool | 429s on sustained paging |
| Reliance on Science v65 | Zenodo `10.5281/zenodo.21493744`, `pcs_oa_uspto.csv` | 1.44 GB, CC BY-NC 4.0, OpenAlex-keyed. USPTO records from **before 1976 through 2025, including pre-grant application publications**. `reftype` 99.998% `app` |
| Patent text | freepatentsonline.com HTML | full abstract + IPC; granted patents only (application publications 404); **one connection** |

## Environment and data gotchas — read before touching the pipeline

- **Patent text.** Legacy PatentsView API retired (redirects to USPTO's transition-guide
  page — not a sandbox block). `api.uspto.gov` needs a key. EPO OPS needs registration.
  Google Patents returned 503 after ~219 requests. FreePatentsOnline works, but reset
  connections at 4 workers: single connection with a delay.
- **Sampling.** Never fetch in sorted-id order and stop partway: "US10..." sorts before
  "US9...", silently dropping grant years. Fetch order is randomized. Check the grant-year
  mix with `tools/check_abstract.py` before quoting any rate.
- **Grant era confounds comparisons.** Always stratify by era (`src/compare_arms.py`).
- **Caching.** md5 keys, never Python `hash()`. Never cache a transient failure as a
  permanent miss.
- **OpenAlex `sample`** pages only with `page=`; `cursor=` silently stops after one page.
- **Rare events.** Exact Jeffreys intervals; bootstrap on zero-event cells fakes
  significance. Subfield tests: Fisher exact + Benjamini–Hochberg.
- **Windows.** `PYTHONIOENCODING=utf-8`. Long bash heredocs of markdown fail to parse —
  write files with the file-write tool or a Python script. `.gitattributes` marks PDFs
  binary.
- **Stale files.** `results/STALE_*` are from a capped speech run, gitignored.

## Pipeline

```bash
pip install -r requirements.txt
cp .env.example .env                                    # OPENROUTER_API_KEY

python -m src.ingest_acl
python -m src.join_openalex --pass doi
python -m src.fetch_ros
python -m src.join_patents                              # -> results/patent_links.csv
python -m src.build_control --n 2500                    # -> results/control_patents.csv
python -m src.fetch_patent_meta --source fpo --sample 2500 --seed 42 --workers 1 --delay 1.5
python -m src.fetch_patent_meta --source fpo --ids results/control_patents.csv --cache-dir control_meta --workers 1 --delay 1.5
python -m src.classify_patents --redact-assignee --out patent_labels.csv   # then restrict to seed-42 sample
python -m src.classify_patents --redact-assignee --meta-dir control_meta --out control_labels.csv
python -m src.compare_arms                              # headline rate + era-matched comparison
python -m src.analysis --max-year 2019                  # H1, H2, technology classes, owners
python -m src.redaction_test                            # applicant-name bias
python -m src.build_goldset --n 200
python -m src.agreement                                 # after coding
python tools/check_abstract.py                          # sample representativeness
python tools/verify_brief.py                            # rebuild BRIEF.pdf + check numbers against results
```

## Conventions

- Every LLM call cached by md5(model + prompt + params); model pinned; cost logged.
- Every number in the abstract maps to a script and a results file in `CLAIMS.md`.
- Every citation verified by opening its page; stored in `paper/refs.bib`.
- Exact intervals for rare events, era stratification for comparisons, null results
  reported straight.
- `data/raw/` and `data/interim/` are gitignored and regenerable from `src/`.
