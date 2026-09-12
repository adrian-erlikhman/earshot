# Titles, pitch, poster outline

## Three title options

**1. Earshot: What Are the Patents Citing NLP Research Actually For?**
Plain, and the question is the contribution. Signals measurement rather than
position-taking, which matters at a venue where 13 of 16 accepted papers had no
artifact.

**2. Authentication Is Not Identification: Classifying the Patents That Cite
Language-Technology Research**
Leads with the distinction that does the analytic work. Strongest for this
audience — it says in the title that we thought about the hard case instead of
keyword-matching "voice".

**3. Proximity, Not Transmission: What the Patent Record Can and Cannot Show
About NLP's Path Into Surveillance**
Leads with the limitation. Safest against the reviewer who knows that front-page
citations evidence disclosure rather than use — and it survives a null result
unchanged.

**Recommendation: 2.** It is the most memorable, it is honest about where the
difficulty lies, and it reads as a finding rather than a topic. Fall back to 3 if
the classified rate comes in low, because then the limitation *is* the paper.

---

## Two-sentence pitch

> Everyone in this debate argues about whether NLP research ends up in
> surveillance systems, and nobody has counted. We linked 127,851 ACL Anthology
> papers to the 9,048 patents citing them, classified every patent against a
> written rubric that separates verifying a claimed identity from picking someone
> out of a population, and report both what the record shows and how much of the
> question it cannot settle.

---

## Poster outline — Paris, Dec 12 or 13

Landscape, read left to right in three columns. The figure is the centre of
gravity; the poster is not the abstract enlarged.

### Column 1 — the claim

- **Title**, authors, and a QR to the repo and the interactive explorer.
- **One sentence, set large:** the argument about whether NLP gets militarised
  has been running on acknowledgments and anecdote. Here is the count.
- **What is already known:** Kalluri et al. did this for computer vision —
  19k papers, 23k patents, 11k surveillance, ~5× growth. Zhang linked NLP papers
  to patents but never asked what the patents were for.
- **The gap, in one line:** nobody has asked what the patents do.

### Column 2 — the hero figure and the rubric

- **HERO FIGURE.** Sankey. Left: NLP subfields. Right: patent application classes
  (biometric identification, border/immigration, policing, content moderation,
  military C2, commercial/other). Ribbon width = citing patents. Colour = label.
  Everything else on the poster exists to make this figure legible.
  *This figure cannot be submitted with the abstract — the Google Form is text
  only — so the poster is the only place it appears.*
- **The two distinctions**, in a box, because they are the contribution:
  - *Operator vs subject* — if the person analysed is also the user and the
    beneficiary, it is not surveillance.
  - *Authentication vs identification* — verifying a claimed identity is not
    determining who someone is from a population.
- **Three worked examples** from the rubric, as a strip: the call-centre
  voiceprint pair (verification → `neither`, fraud-database match →
  `surveillance`), and machine translation of intercepted communications.
  These are what people will argue with us about, so put them up front.

### Column 3 — evidence, limits, and what we would need

- **Pipeline strip:** 127,851 papers → 69,327 OpenAlex → 26,085 links → 9,048
  patents → classified. With the replication stamp: *24,829 vs Zhang's 24,821.*
- **Validation panel:** confusion matrix, per-class F1 with CI, Gwet's AC1 and
  Cohen's κ side by side, and a one-line note on why κ is the wrong gate under
  skewed prevalence. Disclose that both coders are the authors.
- **Limits, given their own panel rather than small print:**
  1. 91.6% of our links are applicant-added front-page citations — disclosure,
     not demonstrated use. We measure proximity, not transmission.
  2. Patent abstracts are drafted to avoid naming an application, so a low rate
     bounds what the record can show, not what the field does.
- **Closing panel — "what would settle this":** the data that does not exist.
  Application-level disclosure, procurement linkage, deployment records. This is
  the panel that starts conversations, and it is the one to stand next to.

### Practical notes

- The QR goes to the repo, which is public, and to the static explorer on GitHub
  Pages. Test both on phone data, not venue wifi.
- Print A0 matte. Bring a second flat copy in a tube as insurance.
- Two-minute version for a passing reader: the title, the two distinctions, the
  Sankey. Nothing else needs to be read to get the point.
- **If the classified rate comes back near zero**, swap the hero figure for the
  coverage-and-limits panel and lead with the second finding: the citation trail
  both sides appeal to cannot settle this, and here is how far short it falls.
  That version of the poster is not a consolation — it is a cleaner argument.
