# CLAIMS.md

Every number that appears in the abstract, TL;DR, poster, or explorer maps to a
script and a results file here. A claim with no row in this table does not ship.

**Status legend:** ⬜ not yet computed · 🟡 computed, not validated · ✅ computed + validated + CI'd

| # | Claim (as it would appear) | Value | Script | Results file | Status |
|---|---|---|---|---|---|
| C1 | ACL Anthology papers ingested | **127,851** (1,719 volumes, 1952–2026) | `src/ingest_acl.py` | `data/interim/acl_papers.csv` | ✅ |
| C2 | Share carrying a DOI | **54.8%** | `src/ingest_acl.py` | `data/interim/acl_papers.csv` | ✅ |
| C3 | Papers matched to OpenAlex | **69,327** = 98.9% of DOI-bearing, **88.1% of core venues** (Zhang 2025: ~85%) | `src/join_openalex.py` | `data/interim/acl_openalex.csv` | ✅ |
| C4 | Distinct patents citing ACL papers | **9,048** (26,085 links, 5,008 papers, 100% applicant) | `src/join_patents.py` | `results/patent_links.csv` | 🟡 |
| C4b | Distinct patents citing speech/speaker-ID papers | **7,071** (17,565 links, 2,284 papers) | `src/probe_speaker_id.py` | `results/speaker_id_probe.json` | 🟡 |
| C4c | Patent-proximity rate, text NLP vs speech | **7.2% vs 13.7%** — NOT yet matched on era/venue type | `src/join_patents.py`, `src/probe_speaker_id.py` | both | 🟡 |
| C5 | Share of citing patents classified surveillance | — pilot n=60 (non-random) all `neither`; not quotable | `src/classify_patents.py` | `results/patent_labels.csv` | ⬜ |
| C5b | Classifier positive control vs rubric worked examples | **6/7**; miss = speaker diarization coded `neither` not `dual_use_ambiguous` (conservative bias) | `src/classify_patents.py` | — | ✅ |
| C6 | Patent-proximity by subfield (pooled) | corpus 7.23% — **right-censored, descriptive only, do not quote** | `src/subfields_acl.py` | `results/subfield_rates.json` | ⚠️ superseded by C6b |
| C6b | Patent-proximity by subfield, papers <=2019 | base **20.57%**; dialogue_qa **33.80%**, summarization 33.56%, speech_asr 22.43% (ns), authorship **10.38%** (below) | `src/subfields_acl.py --max-year 2019` | `results/subfield_rates_le2019.json` | ✅ |
| C6c | **H1 proper** — rate vs *surveillance-classified* patents | — NOT YET TESTED. C6/C6b measure any-patent citation, which is H1's denominator, not H1 | `src/classify_patents.py` | — | ⬜ blocked on key |
| C7 | Control: same rate for non-NLP CS papers | — | `src/analysis.py` | `results/h1_control.csv` | ⬜ |
| C8 | Time trend odds ratio (H2) | — | `src/analysis.py` | `results/h2_trend.json` | ⬜ |
| C9 | Military funding acknowledgment rate by subfield (H3) | — | `src/funding.py` | `results/h3_funding.csv` | ⬜ |
| C10 | Spearman ρ, funding rate vs surveillance rate (H3) | — | `src/analysis.py` | `results/h3_rho.json` | ⬜ |
| C11 | Human–model Cohen's κ on the 200-patent gold set | — | `src/validate_labels.py` | `results/kappa.json` | ⬜ |
| C12 | Human–human Cohen's κ (Adrian vs Michael) | — | `src/validate_labels.py` | `results/kappa.json` | ⬜ |

## Verified facts used as framing (not our results)

These are other people's numbers. Each was checked by opening the source.

| Fact | Source | Checked |
|---|---|---|
| Prior work mapped 24,821 ACL papers → 21,104 OpenAlex (85%) → 20,218 patent links | Zhang, ACL 2025 Short 488–494, arXiv:2505.16061 | ✅ |
| CV: >19k papers → >23k patents, >11k surveillance, ~5× growth 1990s→2010s | Kalluri et al., *Nature* 2025, DOI 10.1038/s41586-025-08972-6 | ✅ |
| Kalluri et al. classified patents with a **keyword list**, not an LLM (their App. F.1) | same | ✅ |
| Edition 1: 16 accepted, 3 empirical, 2 of 3 clear orals empirical | ICLR virtual program + workshop site | ✅ |
| Reliance on Science v65 is OpenAlex-keyed (`oaid`), USPTO-only, 2015–2025 | Zenodo 10.5281/zenodo.21493744, header read directly | ✅ |

## Citation corrections already found in the original brief

| As briefed | Correct |
|---|---|
| Lermen, Paleka, Carlini & Tramèr, arXiv:2602.16800 | Lermen, Paleka, **Swanson, Aerni**, Carlini & Tramèr, *Large-scale online deanonymization with LLMs* |
| Kalluri et al., "The Surveillance AI Pipeline" | Journal version is **retitled** "Computer-vision research powers surveillance technology," *Nature* 2025 |

## Flagged for re-verification before Phase 3

- AuthBench language list and Macko et al.'s 11-language list were read via
  model-summarized fetches, not the PDFs. Open both directly.
- Widder/Gururaja/Suchman journal name — SAGE 403s to fetchers; DOI prefix
  suggests *Big Data & Society*. Confirm by hand.

---

## CURRENT STATUS — 2026-09-12 (supersedes conflicting rows above)

Primary specification is **assignee-redacted** (rubric v1.2). All classified rates are
**provisional**: 1,012 treatment and 366 control patents classified.

| # | Claim | Value | Script | Results | Status |
|---|---|---|---|---|---|
| C5 | Surveillance share, ACL-citing patents | **7/1,012 = 0.69%** [0.31, 1.35] | `classify_patents.py --redact-assignee`, `analysis.py` | `patent_labels.csv`, `analysis.json` | 🟡 provisional |
| C5s | Same, assignee shown (sensitivity) | 10/978 = 1.02% [0.53, 1.81] | `classify_patents.py` | `patent_labels_assignee_shown.csv` | sensitivity only |
| C7 | Control: science-citing, no ACL | **1/366 = 0.27%** [0.03, 1.27]; RR 1.95x [0.36, 4.34]; p = 0.69 | `build_control.py`, `analysis.py` | `control_labels.csv` | 🟡 underpowered |
| C16 | ACL-citing share of science-citing patents | 9,048 / 2,748,170 = **0.33%** | `build_control.py` | `control_meta.json` | ✅ |
| C6c | H1: surveillance rate by subfield | **0 of 10** significant, BH q < 0.05; min p = 0.093 (1 event) | `analysis.py` | `analysis.json` | ✅ null, underpowered |
| C8 | H2: time trend | 0.65% -> 0.73%, overlapping CIs | `analysis.py` | `analysis.json` | 🟡 |
| C13 | In-text-citation ablation | 0/89, CI [0, 2.78] | `analysis.py` | `analysis.json` | ⚠️ uninformative, not support |
| C14 | IPC convergent validity | F1 0.121; of 26 surveillance-class patents, 21 coded `neither` | `analysis.py` | `analysis.json` | ✅ class-based methods overcount |
| C15 | Applicant-name bias in LLM labels | **4 of 16** non-`neither` labels (25%) flip under redaction | `redaction_test.py` | `redaction_test.csv` | ✅ |
| C11/C12 | Human agreement | pending coding, Sun 13 Sept | `agreement.py` | `agreement.json` | ⬜ |

**Withdrawn:** positive control 6/7 (circular); redaction test 0/60 (uninformative);
H1 `***` flags (bootstrap artifact); in-text ablation as support; 1.02% as headline
(assignee-biased).
