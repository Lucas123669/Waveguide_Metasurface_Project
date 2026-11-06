---
name: literature-repo-intake
description: Ingest a paper (PDF, plus optional supplementary material) into a curated literature repository and publish it. Identifies the paper from the PDF, claims the next stable ID from the remote's current state, archives the file with the repo's naming convention, writes the reading note, syncs every index in one batched patch, runs the repo's health check, then commits and pushes with a fast transport fallback and SHA verification. Use when the user says "把这(两)篇文献上传/入库/推到 GitHub", drops a paper PDF and asks to put it in the repository, asks to add a paper to a literature library, or wants a paper's reading note registered across a docs repo.
---

# Literature repo intake (fast path)

One paper, from "user drops a PDF" to "pushed and verified", in as few round-trips as possible.
**The repo is the authority** for naming, numbering and which indexes must change. Read it; never guess.

## Non-negotiables

These five rules each came from a real failure; skipping one costs a full redo.

1. **Fetch the remote BEFORE doing any work.**
   Other writers may have committed since your last pull, and they may already hold the ID you planned.
   Fetch first, then read the index files **from the remote**, then claim an ID.

2. **Transfer over HTTPS-through-proxy first; SSH is the fallback.**
   Direct SSH to GitHub can crawl (~10 KiB/s: a 164-object fetch stalled past 10 minutes), while
   HTTPS through the repo's configured `http.proxy` finished the same fetch in seconds.
   Try HTTPS, fall back to SSH, and add low-speed abort guards so a stalled transfer fails fast
   instead of hanging (see `scripts/fast_push.ps1`).

3. **One batched patch, not twenty edits.**
   Registering one paper usually touches 5–12 files. Do it in a single `scripts/batch_patch.py` run
   with per-anchor assertions and all-or-nothing writes.

4. **Commit message goes in a file**: `git commit -F msgfile`. Never a multi-line `-m` inside a
   shell wrapper — it gets split into pathspecs and every commit fails.

5. **Remote wins on ID collisions.** If another writer already took the number you planned,
   **renumber yours** to the next free ID. Drop your own unpushed commits and redo on top of the
   fetched remote. Never force push, never rewrite someone else's commit.

## Workflow

### Step 0 — Preflight (one shell call, read before writing)

```powershell
cd <repo>
git fetch --no-tags <remote-or-url> <branch>:refs/remotes/origin/<branch>
git log --oneline -5 origin/<branch>
git status --short --branch
```

Then read, in this order, the repo's **own** statements of convention:

- root `README.md` and the machine-readable state file (`project_config.json` or equivalent)
- the literature entry point (`literature/README.md` or similar)
- the **index of record** for stable IDs (e.g. `literature/文献清单.md`), plus any newer taxonomy
  index (`多维分类索引.md`) — if a `docs/decisions/` entry says an older index is deprecated, obey
  the newer decision and do **not** "restore" the old one
- the target sub-directory `README.md` (naming, ID scheme, how supplementary files are named)
- the **health-check script** you will run later (`scripts/maintenance/*check*`, `make check`, …)
- one existing note of the same kind, to copy structure and tone

### Step 1 — Identify and dedupe

```powershell
python scripts/pdf_info.py <path-to-pdf>          # title, pages, SHA-256, DOI, page-1 text
```

- Grep the repo for the DOI and the title before anything else. Same DOI already present →
  update the existing entry, do not create a second one.
- Extract the full text when you write the note (`pymupdf`, see `reference.md`).

### Step 2 — Claim the ID from the remote state

Read the **remote's** index file (just fetched) and pick the next free number in the correct series.
Confirm the physical location against the repo's placement rules, and confirm whether the ID series
still owns a directory or whether placement is now independent of numbering.

### Step 3 — Archive the files

- Copy (never move) into the location the repo specifies, using the repo's file-name pattern.
- Name supplementary material exactly as the repo names it (`*_补充材料.pdf`, `*_supporting.pdf`, …)
  and put it beside the main PDF.
- **Verify integrity**: compare SHA-256 of source and destination; record page count, byte count and
  hash in the repo's source/verification ledger if it keeps one.
- Delete any temporary scripts/artifacts before committing.

### Step 4 — Write the reading note

Follow the structure of existing notes of the same class (quick note vs close-reading note).
Mandatory content: bibliographic block, one-sentence summary, motivation, key parameters **with
units**, key results, method, fabrication, cross-references to notes already in the repo,
implications, open questions, terminology traps.

Rules that keep the library trustworthy:

- Mark every number with its **evidence level** (原文 / 补材 / 仿真 / 唯一实现) when it could be misquoted.
- State **efficiency/metric denominators** explicitly; metrics with different denominators are not comparable.
- If the supplementary material is missing, gate its values: "not citable until the supplement is filed".
  When it arrives later, un-gate the note and fold the numbers in — do not leave a stale caveat.
- Record discrepancies you find in the paper instead of smoothing them over.

### Step 5 — Register across the indexes (one batched patch)

Write one patch spec and apply it once:

```powershell
python scripts/batch_patch.py patch.json --dry-run   # validate every anchor first
python scripts/batch_patch.py patch.json
```

Patch by **unique short anchor** or by **unique line marker**, never by transcribing a long line that
contains full-width punctuation — those anchors fail on a single invisible character difference.
Typical target set: ID registry, taxonomy/secondary index, the target sub-directory README, the
series README, both navigation guides, the BibTeX file, and the machine-readable state file.
If the repo's policy says single-paper intake is **not** a changelog entry, do not add one.

### Step 6 — Health check

Run the repo's own checker and require a clean result before committing:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/maintenance/check_docs.ps1
```

(Bypass is needed where the execution policy is Restricted.) Require **0 broken links** and valid
JSON. Fix broken links caused by your paths before going on — do not commit a red check.

### Step 7 — Commit

```powershell
# subject: English imperative, <= 72 chars; body: what / why / which boundary applies
git add -A
git commit -F .git/INTAKE_MSG.txt
if ($LASTEXITCODE -ne 0) { Write-Error 'COMMIT FAILED'; exit 1 }
Remove-Item .git/INTAKE_MSG.txt
```

Put boundaries in the body that must travel with the change: metric denominators, missing
supplementary material, licensing limits, and any "do not quote until verified" gate.

### Step 8 — Push and verify

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/fast_push.ps1 -Repo <repo> -Branch main
```

Require the script's final line `RESULT: REMOTE SHA MATCHES LOCAL`. Verify the remote SHA yourself
with `git ls-remote` — never trust the `git push` exit code or its progress output alone.

### Step 9 — Report

Say: paper identified (title/journal/year/DOI), ID assigned and **why that ID** (including any
renumbering), files added, indexes changed, health-check numbers, commit SHA, remote SHA match, and
the evidence boundaries the reader must not violate.

## Scripts

| Script | Use |
| --- | --- |
| `scripts/pdf_info.py` | One-shot PDF identification: pages, SHA-256, DOI, page-1 text. |
| `scripts/batch_patch.py` | Apply many anchored edits across many files atomically; validates first. |
| `scripts/fast_push.ps1` | Push HTTPS→SSH with low-speed guards, then verify remote SHA. |

Run them; do not re-implement them inline.

## Reference

- [reference.md](reference.md) — worked example, index file map, patch spec format, pitfall table,
  commit message template, and cross-platform notes.
