# CLAIMS.md

Every number that appears in the abstract, TL;DR, poster, or explorer maps to a
script and a results file here. A claim with no row in this table does not ship.

**Status legend:** ⬜ not yet computed · 🟡 computed, not validated · ✅ computed + validated + CI'd

| # | Claim (as it would appear) | Value | Script | Results file | Status |
|---|---|---|---|---|---|
| C1 | ACL Anthology papers ingested | **127,851** (1,719 volumes, 1952–2026) | `src/ingest_acl.py` | `data/interim/acl_papers.csv` | ✅ |
| C2 | Share carrying a DOI | **54.8%** | `src/ingest_acl.py` | `data/interim/acl_papers.csv` | ✅ |
| C3 | Papers matched to OpenAlex | **69,327** = 98.9% of DOI-bearing, **88.1% of core venues** (Zhang 2025: ~85%) | `src/join_openalex.py` | `data/interim/acl_openalex.csv` | ✅ |
| C4 | Distinct patents citing NLP papers | — | `src/fetch_ros.py` | `results/patent_links.csv` | ⬜ |
| C5 | Share of citing patents classified surveillance | — | `src/classify_patents.py` | `results/patent_labels.csv` | ⬜ |
| C6 | Surveillance-citation rate, `speaker_id_voice` (H1) | — | `src/analysis.py` | `results/h1_subfield_rates.csv` | ⬜ |
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
