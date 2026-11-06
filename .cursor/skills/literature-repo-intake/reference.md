# Reference — literature repo intake

Worked example, file map, patch spec, pitfalls, templates.

---

## 1. Worked example (Waveguide_Metasurface_Project, 2026-09)

User dropped `sciadv.adn4372.pdf` and said "帮我把这边文献上传到github仓库的对应位置".

| Step | What actually happened | Time cost if skipped |
| --- | --- | --- |
| Identify | `pdf_info.py` → Wang et al., *Sci. Adv.* 10(12), eadn4372 (2024), UGR grating coupler | — |
| Pick location | User chose the cross-system group (`材料体系分类/通用交叉/`) over the Si 1550 nm series | Re-doing the whole registration |
| Archive | `Q1_13_Wang_2024_*.pdf`, SHA-256 checked against source | — |
| Note | Reading note written from extracted full text | — |
| Register | 10 index files synced in **one** batched patch | 20+ tool round-trips |
| Check | `check_docs.ps1` → 0 broken links | Red CI on the shared repo |
| Commit | Message in `.git/*.txt`, `git commit -F` | `pathspec did not match` loop |
| Push | **HTTPS first** (fast) | SSH stalled at ~10 KiB/s |

**The expensive lesson**: the first attempt registered the paper as `Q1-13`, and only when pushing
was rejected did it emerge that a collaborator had already published `Q1-13 … Q1-16` for four other
papers. Two local commits had to be dropped and the entire registration redone as `Q1-17`.
`git fetch` before choosing the number would have cost one command and saved the redo — hence
"fetch before you work" is rule #1.

The second lesson: the registration was first written as one Python script that computed every patch
from the *pristine* file text and then wrote each result in turn, so each write overwrote the
previous one and only the last patch per file survived. Hence `batch_patch.py` accumulates per file
and writes once.

---

## 2. Registering one paper — typical index set

Find the repo's real set by grepping the ID pattern (e.g. `Q1-1`, `L0`) rather than assuming. A
documentation-heavy library usually needs all of:

| Purpose | Example file |
| --- | --- |
| Registry of record: ID, DOI, status, journal tier | `literature/文献清单.md` |
| Taxonomy / multi-label index (newer convention) | `literature/多维分类索引.md` |
| Deprecated compatibility index — **do not restore statistics** | `literature/分区全景索引.md` |
| Physical location README (the folder the PDF lives in) | `literature/材料体系分类/通用交叉/README.md` |
| Series README (numbering range, location list, topic views) | `literature/Q1_L01相关/README_本文件夹说明.md` |
| Navigation guides | `docs/guides/AI_接手指南.md`, `docs/guides/文献库指南.md` |
| BibTeX | `references/references.bib` |
| Machine-readable state | `project_config.json` |
| Source / integrity ledger, when the repo keeps one | `literature/Q1_L01相关/SOURCES_2026-09-15.md` |

Rules of thumb:

- If a `docs/decisions/` entry supersedes an index, follow the **newer** decision.
- If the repo says single-item intake is not a changelog entry, do not touch `CHANGELOG.md`.
- Cross-directory references must use the alias form the taxonomy mandates
  (here: `Si-1550:A2` rather than bare `A2`).
- Never leave a stale caveat behind: if the supplement arrives later, un-gate the note.

---

## 3. Patch spec example

```json
{
  "repo": ".",
  "patches": [
    {
      "file": "literature/文献清单.md",
      "op": "insert_after",
      "marker": "| Q1-16 |",
      "text": "| Q1-17 | Q1 · 中科院一区 Top(OA) | 导模/单向辐射 | <title> | <doi-url> | 已读,笔记完成 | <remarks> |",
      "label": "registry row"
    },
    {
      "file": "references/references.bib",
      "op": "append",
      "text": "\n@article{Wang2024UGR,\n  author = {...},\n  title  = {...},\n  year   = {2024},\n  doi    = {10.1126/sciadv.adn4372}\n}\n",
      "label": "bib entry"
    },
    {
      "file": "project_config.json",
      "op": "replace",
      "old": "\"primary_papers\": [\"Q1-16\", \"F-08\"",
      "new": "\"primary_papers\": [\"Q1-16\", \"Q1-17\", \"F-08\"",
      "label": "state file"
    },
    {
      "file": "literature/文献清单.md",
      "op": "replace",
      "old": "Q1-12 位于通用交叉目录",
      "new": "Q1-12 与 Q1-17 位于通用交叉目录",
      "label": "location sentence"
    }
  ]
}
```

Two patches target the same file on purpose: `batch_patch.py` applies them in order to one buffer,
so both survive. Verify with `--dry-run` first.

### Anchor selection

- Prefer a **short, unique, ASCII-heavy** fragment: `| Q1-16 |`, `does not exist`, a DOI, a path.
- Avoid transcribing long lines that contain CJK quotes (`"…"`), full-width brackets, or non-breaking
  hyphens — one invisible codepoint difference fails the anchor.
- When the target *is* such a line, insert **after a marker line** instead of replacing the line.
- If an anchor fails, do not retry blindly: grep the file for the shortest stable fragment and use
  that (`grep`/`rg` the ID, then read ±3 lines).

---

## 4. Pitfalls (all observed in practice)

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| Worked before fetching | Push rejected `fetch first`; ID already taken | Fetch first, claim the ID from the remote |
| Multiple patches built from pristine text | Only the last patch per file survives | `batch_patch.py` (accumulates, writes once) |
| Multi-line `git commit -m` in a shell wrapper | `pathspec '…' did not match` | Message to a file, `git commit -F` |
| Slow transfer | Fetch stalls at ~10 KiB/s for 10+ min | HTTPS through the configured proxy; low-speed guards |
| Trusting `git push` output | "GREEN" but nothing landed | `git ls-remote` and compare with `git rev-parse` |
| Mixed CRLF/LF | Whole-file diff after a "small" edit | Don't split/join whole files; patch by insertion |
| Temp script left behind | Accidental commit of `_tmp_*.py` | Delete before `git add -A`; check `git status` |
| PowerShell execution policy | `UnauthorizedAccess` running a `.ps1` | `powershell -NoProfile -ExecutionPolicy Bypass -File …` |
| Assigning `$args`/`$input`/`$error` | Silent misbehaviour in scripts | Use distinct names (`$gitArgs`) |
| CJK console encoding | `UnicodeEncodeError: 'gbk' codec` from Python | `python -X utf8` and/or `sys.stdout.reconfigure(encoding='utf-8')` |
| BOM from PowerShell `Set-Content -Encoding UTF8` | `Unexpected UTF-8 BOM (decode using utf-8-sig)` | Read specs with `encoding='utf-8-sig'` (batch_patch.py already does) |
| Force-pushing over a collaborator | Destroyed history | Never force push; renumber your own entry |

---

## 5. Commit message template

```
<Verb> <ID>: <short description> (<first author> <year>, <journal>)

Archive <authors>, "<title>", <journal> <volume>(<issue>), <article> (<year>)
and register it as <ID>.

Placement: <where the file lives and why>.

Renumbering (only when applicable): prepared as <old ID>, but the remote
already assigned <old ID> to <other paper>; the stable ID continues as <new ID>.
No collaborator history was rewritten.

Indexes synced: <list>.

Evidence boundary: <metric denominators; missing supplement; licensing;
"do not quote until verified" gates>.

<Health-check result>.
```

Subject: English imperative, ≤72 characters. Body: what / why / boundary.

---

## 6. Cross-platform notes

- `batch_patch.py` and `pdf_info.py` are pure Python 3 + stdlib (`pdf_info.py` needs PyMuPDF).
- `fast_push.ps1` is PowerShell; on macOS/Linux use the same logic in shell:

```bash
# HTTPS first, abort if the transfer drops below 1 KB/s for 60 s
GIT_TERMINAL_PROMPT=0 git -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=60 \
    push "$HTTPS_URL" main:main
# fallback
git -c core.sshCommand='ssh -o ConnectTimeout=20 -o BatchMode=yes' push "$SSH_URL" main:main
# verify
git ls-remote "$HTTPS_URL" refs/heads/main; git rev-parse main
```

- Repos often carry the proxy in `.git/config` (`http.proxy`); git picks it up automatically, and
  SSH never uses it — which is exactly why SSH can be the slow path.

---

## 7. Scoping and portability

- Personal scope: `~/.agents/skills/literature-repo-intake/` (or `~/.cursor/skills/…` where that is
  the active directory) — available in every project for this user.
- Project scope: copy the whole folder to `<repo>/.cursor/skills/literature-repo-intake/` and commit
  it, so every agent working on that repo inherits the same procedure.
- Portable hand-off: the folder is self-contained (no absolute paths except documented examples), so
  zipping it and dropping it into another machine's skills directory is enough.
