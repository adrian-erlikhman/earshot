# Earshot

**Which language technologies end up in surveillance patents?**

Adrian Erlikhman · Michael Tarekegn
Submission in progress — AI for Peace workshop @ NeurIPS 2026 (Paris, Dec 12–13).

---

## The question

When a company patents an invention, it must list the research papers the
invention builds on. That list is a public legal record. So research can be
traced forward into products by reading receipts rather than guessing.

Kalluri et al. did this for computer vision ([*Nature* 2025](https://www.nature.com/articles/s41586-025-08972-6),
preprint [arXiv:2309.15084](https://arxiv.org/abs/2309.15084)): 19,000 CV papers →
23,000 citing patents → 11,000+ surveillance patents, ~5× growth from the 1990s
to the 2010s.

**Nobody has done it for language and speech.** Earshot does.

Speech matters more than the paper count suggests: speaker identification —
recovering *who* is talking from a recording — is deployed at borders, in
policing, and in asylum determination.

## Status

Work in progress. Numbers below are **preliminary** and several are not yet
defensible; see `CLAIMS.md` for what is validated and what is not.

| | |
|---|---|
| ACL Anthology papers ingested | 127,851 (1,719 volumes, 1952–2026) |
| mapped to OpenAlex | 69,327 (98.9% of DOI-bearing; 88.1% of core venues) |
| patents citing ACL papers | **9,048** (26,085 links, 5,008 papers) |
| patents citing speech / speaker-ID papers | **7,071** (17,565 links, 2,284 papers) |
| patent classification | not started |
| API spend | $0.00 |

## What is NOT claimed

- **Not** "first to link NLP papers to patents." [Yu Zhang, ACL 2025 Short
  488–494](https://aclanthology.org/2025.acl-short.37/) built that pipeline
  already (24,821 papers → 20,218 patent links). The contribution here is asking
  what the citing patents are *for*, and covering speech, which he did not.
- The preliminary "speech is ~2× more patent-proximate than text NLP" figure
  (13.7% vs 7.2%) compared two differently-constructed corpora and is **not
  usable as stated**. `src/build_arms.py` rebuilds every arm identically from one
  source to replace it.

## Method

```
ACL Anthology XML ─┐
                   ├─→ OpenAlex ids ─→ Reliance on Science ─→ citing patents ─→ LLM classifier ─→ rates by subfield
OpenAlex subfield ─┘   (patent→paper citations)                                      ↑
queries (speech,                                                            200-patent gold set
speaker ID, MT, …)                                                          hand-labelled by both
                                                                            authors; Cohen's κ
```

Every LLM label is validated against a human gold set. **If human–model κ < 0.6,
the model's labels do not carry a headline number** — we report the hand-labelled
sample only and say so.

## Data

All public, all free, none redistributed here.

| Source | Access |
|---|---|
| ACL Anthology | `codeload.github.com/acl-org/acl-anthology` (58 MB) |
| OpenAlex | free API, no key |
| Reliance on Science v65 | [Zenodo 10.5281/zenodo.21493744](https://zenodo.org/records/21493744) · 1.4 GB · CC BY-NC 4.0 |

`data/` is gitignored; everything in it regenerates from `src/`.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env          # add keys

python -m src.ingest_acl      # ACL Anthology  -> data/interim/acl_papers.csv
python -m src.join_openalex   # + OpenAlex ids -> data/interim/acl_openalex.csv
python -m src.fetch_ros       # Reliance on Science (1.4 GB, resumable)
python -m src.join_patents    # citing patents -> results/patent_links.csv
python -m src.build_arms      # per-subfield rates -> results/arms.json
```

## Ethics

Public records only; no personal data. We report **assignee organisations**,
never named inventors. We **do not** build, optimise, or release any surveillance
or attribution capability — only aggregate counts and the classification rubric.
The workshop's call explicitly rejects normalising military and surveillance AI,
and the critical frame here is the point of the work, not decoration.

## Repo map

- `CLAUDE.md` — project brief, decisions, hard constraints, claims we must not make
- `LOG.md` — pre-registered analysis plan (written before any results), daily log, API spend
- `CLAIMS.md` — every number → the script and results file that produced it
- `DECISION.md` — the six candidate topics, scored, and why this one won
- `src/` — pipeline; `results/` — committed outputs; `paper/` — abstract drafts
