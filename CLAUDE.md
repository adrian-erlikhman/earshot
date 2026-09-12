# CLAUDE.md — Earshot (AI for Peace @ NeurIPS 2026)

Project brief, decisions, gotchas and commands. Kept current so a fresh session can
pick up cold. **Last updated 2026-09-12.**

## What this is

**Earshot** — a submission to the **AI for Peace workshop @ NeurIPS 2026** (2nd
edition, Paris, Dec 12 or 13). Team: **Adrian Erlikhman** (presenting author, attends
in person, solo) and **Michael Tarekegn**. Repo: `adrian-erlikhman/earshot` (**public**).

**Current thesis.** We link ACL Anthology papers to the USPTO patents that cite them
and classify what those patents are *for*. The pre-registered framing now leads:
surveillance-classified patents appear rare among NLP-citing patents, and the public
patent record cannot settle whether NLP research feeds surveillance — citations show
proximity, not transmission. The solid contributions are methodological:
authentication vs identification, examiner-class overcounting, and applicant-name bias
in LLM labels.

**Recommended title:** *Proximity, Not Transmission: What the Patent Record Can and
Cannot Show About NLP's Path Into Surveillance.*

## Hard constraints (verified from source, 2026-09-10)

- **Submission is a Google Form with pasted text. No file upload.**
  - Abstract field **2,500 characters max**; references count against it.
  - Separate TL;DR field **300 characters max**.
  - **The hero figure cannot be submitted** — poster only.
- Deadline **Mon 21 Sept AoE = Tue 22 Sept 05:00 Pacific**. Decisions Sept 29.
- Single-blind. Poster / talk / both. Published, novel and in-progress work accepted.
- In-person attendance is a gating form question; no travel funding.
- **Never submit to the venue or post publicly.** Adrian and Michael do that. Emails to
  Michael go out only on Adrian's explicit request.

## Status snapshot — 2026-09-12

Authoritative table: the latest status block at the bottom of `CLAIMS.md`.
Full narrative: `LOG.md`. Writing guide for the abstract: `paper/BRIEF.md` / `.pdf`.

- **Locked:** 127,851 ACL papers → 69,327 in OpenAlex → 26,085 links → 9,048 distinct
  citing patents. Zhang replication: 24,829 papers vs his 24,821. 91.6% of our links
  are front-page-only (62.3% for patents generally). ACL-citing patents are 0.33% of
  the 2,748,170 science-citing patents in RoS v65.
- **Holds in kind:** applicant-name bias — hiding the assignee changed 4 of 16
  non-neither labels (25%).
- **WITHDRAWN pending refetch:** the 0.69% surveillance rate and the control
  comparison. Both classified arms were fetched in sorted patent-id order and stopped
  partway, so they are truncated by grant date (see the sampling gotcha). H1 (0 of 10
  subfields), H2 and the IPC result (2 of 26) must be rerun on representative labels.
- **Running:** random-order metadata fetch, treatment (seed-42 sample of 2,500) then
  control (2,500), single FPO connection. Speech/speaker-ID arm waits on OpenAlex.
- **Pending humans:** gold-set coding, Sunday 13 Sept; Michael's 50-link check.

## Claims we must NOT make

- ❌ "First to link NLP papers to patents." False — Yu Zhang, ACL 2025 Short 488–494
  (arXiv:2505.16061). Framing: *prior work measured whether NLP reaches patents; we ask
  what those patents do.*
- ❌ Any classified rate as a population estimate until the random-order fetch
  finishes and `tools/check_abstract.py` shows a representative grant-year mix.
- ❌ "Keyword proxies overcount." Never tested — only examiner IPC classes were.
- ❌ "Examiner classes systematically overcount" as settled. Rests on 26 patents whose
  labels are not yet human-validated.
- ❌ A treatment-vs-control finding or null. Underpowered (~4,300 per arm needed).
- ❌ Subfield concentration, or its absence, as a finding. Too few events.
- Noa Garcia, the workshop's General Chair, co-authored the computer-vision version
  (Garcia & Katirai, FAccT 2026). Every adjacent claim must be exact.

## Classification protocol

- Rubric: `configs/patent_rubric.md`, with **AMENDMENT v1.1** (the gate is per-class
  F1 on `surveillance`, not omnibus kappa, which collapses under skewed prevalence) and
  **v1.2** (the assignee is **redacted** for the model AND both coders).
- Primary labels: `results/patent_labels.csv`, `results/control_labels.csv`
  (assignee-redacted). Sensitivity: `*_assignee_shown.csv`.
- Model: `google/gemini-2.5-flash-lite`, temperature 0; deterministic on re-call.
- Gold set: `data/goldset/` — 200 items, stratified by model label x surveillance-type
  IPC class, with weights in `strata.json`. The answer key
  `_model_labels_DO_NOT_OPEN_BEFORE_CODING.csv` is **gitignored**.
- **Blinding is honor-system.** `results/patent_labels.csv` is public. Adrian has seen
  model labels for several surveillance items; Michael has not, so Michael's labels are
  the reference for those items. Both coders are authors: agreement is internal
  consistency, not independent validation. Filled sheets are emailed, not committed,
  until both are done.
- **The gold set was built from the date-truncated labels.** Rebuild or augment it
  once representative labels exist.

## Ethics position

- Public data only. No PII. No deanonymization of real people.
- We do not build, optimize or release any surveillance or attribution capability.
  Aggregates and the rubric only.
- The critical frame is the point of the work, not decoration.
- Report assignee organizations, never named inventors.

## Data sources

| Source | Access | Notes |
|---|---|---|
| ACL Anthology XML | `codeload.github.com/acl-org/acl-anthology/tar.gz/refs/heads/master` | 58.1 MB, 1,719 volumes, 127,851 papers. Old ID scheme: `P19.xml` = ACL 2019, `D` EMNLP, `N` NAACL — `venue_key` maps these |
| OpenAlex API | `api.openalex.org`, `mailto` polite pool | 429s on sustained paging |
| Reliance on Science v65 | Zenodo `10.5281/zenodo.21493744`, `pcs_oa_uspto.csv` | 1.44 GB, CC BY-NC 4.0, OpenAlex-keyed, USPTO 2015–2025. `reftype` is 99.998% `app`, no `unk` |
| Patent text | freepatentsonline.com HTML | full abstract + IPC codes; **one connection only** |

## Environment and data gotchas — read before touching the pipeline

- **Patent text access.** The legacy PatentsView API is **retired** and redirects to
  USPTO's transition-guide page (a byte-identical 20,666-byte response). That page is
  *not* a sandbox block — an earlier note said so and was wrong. `api.uspto.gov` needs a
  key (401). EPO OPS needs registration (403). Google Patents started returning 503 on
  every surface after ~219 requests. **FreePatentsOnline works**, but reset connections
  at 4 workers: run it single-connection with a delay.
- **Sampling.** Never fetch in sorted-id order and stop partway: "US10..." sorts before
  "US9...", which silently drops whole grant years. Fetch order is now random. Check the
  grant-year mix with `tools/check_abstract.py` before quoting any rate.
- **Caching.** Cache keys use md5, never Python `hash()` (randomized per process).
  Never cache a transient failure as a permanent miss.
- **OpenAlex `sample`** pages only with `page=`; `cursor=` silently stops after one page.
- **Rare-event statistics.** Use exact Jeffreys intervals for binary rates; bootstrap
  intervals on zero-event cells collapse to [0, 0] and fake significance. Subfield tests
  are Fisher exact + Benjamini–Hochberg, as pre-registered.
- **Windows.** Set `PYTHONIOENCODING=utf-8` (cp1252 console). Long bash heredocs of
  markdown have failed to parse — write files with the file-write tool or a Python
  script. `.gitattributes` marks PDFs binary.
- **Stale files.** `results/STALE_*` are outputs from a capped speech run, gitignored.
  Never use.

## Pipeline

```bash
pip install -r requirements.txt
cp .env.example .env                                    # OPENROUTER_API_KEY

python -m src.ingest_acl                                # ACL Anthology -> data/interim/acl_papers.csv
python -m src.join_openalex --pass doi                  # + OpenAlex ids
python -m src.fetch_ros                                 # Reliance on Science v65 (1.4 GB)
python -m src.join_patents                              # -> results/patent_links.csv
python -m src.build_control --n 2500                    # -> results/control_patents.csv
python -m src.fetch_patent_meta --source fpo --sample 2500 --seed 42 --workers 1 --delay 1.5
python -m src.fetch_patent_meta --source fpo --ids results/control_patents.csv --cache-dir control_meta --workers 1 --delay 1.5
python -m src.classify_patents --redact-assignee                                   # treatment
python -m src.classify_patents --redact-assignee --meta-dir control_meta --out control_labels.csv
python -m src.analysis --max-year 2019                  # all headline numbers
python -m src.redaction_test                            # applicant-name bias
python -m src.build_goldset --n 200                     # coding sheets
python -m src.agreement                                 # after coding
python tools/check_abstract.py                          # length + sample representativeness
python tools/verify_brief.py                            # rebuild + verify paper/BRIEF.pdf
```

## Conventions

- Every LLM call cached by md5(model + prompt + params); model pinned; cost logged.
- Every number in the abstract maps to a script and a results file in `CLAIMS.md`.
- Every citation verified by opening its page; stored in `paper/refs.bib`. Never cite
  from memory.
- Exact intervals for rare events, chance baselines, at least one ablation, and null
  results reported straight.
- `data/raw/` and `data/interim/` are gitignored and regenerable from `src/`.
