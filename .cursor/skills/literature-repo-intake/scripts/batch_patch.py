#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply many anchored edits across many files atomically.

Why this exists
---------------
Registering one item in a documentation repo touches 5-12 files. Editing them
one tool call at a time is slow, and building several patches from the *same
pristine text* silently keeps only the last one per file. This script reads each
file once, applies every patch for that file in order to ONE in-memory buffer,
and writes once -- after validating every anchor. Either everything applies or
nothing is written.

Spec file (JSON)
----------------
{
  "repo": ".",                          // optional; relative paths resolve here
  "patches": [
    {"file": "docs/a.md", "op": "replace",
     "old": "unique text", "new": "replacement", "label": "optional"},
    {"file": "docs/a.md", "op": "insert_after",
     "marker": "| Q1-16 |", "text": "| Q1-17 | ... |"},
    {"file": "docs/a.md", "op": "append", "text": "..."}
  ]
}

- replace      : "old" must occur EXACTLY once (literal, after EOL normalisation).
- insert_after : "marker" must occur EXACTLY once; "text" is inserted after the
                 end of the line that contains it. EOLs of existing lines are
                 preserved (safe for CRLF/LF mixed repos).
- append       : appended at end of file; a trailing EOL is ensured first.

Usage
-----
  python batch_patch.py spec.json [--dry-run] [--repo PATH]

Exit codes
----------
  0  all patches applied (or validated, with --dry-run)
  1  validation failed -- NOTHING was written
  2  usage / IO error
"""

import argparse
import json
import sys


def read_text(path):
    return path.read_bytes().decode('utf-8')


def write_text(path, text):
    path.write_bytes(text.encode('utf-8'))


def dominant_eol(raw):
    return '\r\n' if '\r\n' in raw else '\n'


def apply_ops(raw, ops):
    """Apply ops in order to one buffer. Return (new_raw, failures)."""
    buf = raw
    eol = dominant_eol(raw)
    failures = []

    for idx, op in enumerate(ops):
        kind = op.get('op')
        label = op.get('label') or '%s#%d' % (kind, idx)

        if kind == 'replace':
            old = op['old'].replace('\n', eol)
            new = op['new'].replace('\n', eol)
            n = buf.count(old)
            if n != 1:
                failures.append((label, 'replace anchor found %d times (need exactly 1)' % n))
                continue
            buf = buf.replace(old, new, 1)

        elif kind == 'insert_after':
            marker = op['marker']
            if len(marker) < 4:
                failures.append((label, 'marker %r is too short to be safe' % marker))
                continue
            n = buf.count(marker)
            if n != 1:
                failures.append((label, 'marker found %d times (need exactly 1)' % n))
                continue
            at = buf.find(marker)
            line_end = buf.find(eol, at)
            if line_end == -1:                      # marker on the last line, no EOL
                buf = buf + eol + op['text']
            else:
                cut = line_end + len(eol)
                buf = buf[:cut] + op['text'].replace('\n', eol) + eol + buf[cut:]

        elif kind == 'append':
            text = op['text'].replace('\n', eol)
            if not buf.endswith(eol):
                buf += eol
            buf += text

        else:
            failures.append((label, 'unknown op %r' % kind))

    return buf, failures


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('spec')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--repo', default=None)
    args = ap.parse_args(argv[1:])

    from pathlib import Path

    spec_path = Path(args.spec).resolve()
    try:
        # utf-8-sig tolerates a BOM: PowerShell 5.1 `Set-Content -Encoding UTF8`
        # and several Windows editors write one, and json.loads rejects it.
        spec = json.loads(spec_path.read_text(encoding='utf-8-sig'))
    except Exception as exc:                        # noqa: BLE001
        print('ERROR: cannot read spec %s: %s' % (spec_path, exc))
        return 2

    repo = Path(args.repo) if args.repo else Path(spec.get('repo') or '.').resolve()
    if not repo.is_absolute():
        repo = (spec_path.parent / repo).resolve()

    patches = spec.get('patches') or []
    if not patches:
        print('ERROR: spec has no "patches"')
        return 2

    # ---- group by file, preserving first-appearance order -------------------
    order = []
    by_file = {}
    for patch in patches:
        f = patch.get('file')
        if not f:
            print('ERROR: patch without "file": %r' % (patch,))
            return 2
        if f not in by_file:
            order.append(f)
            by_file[f] = []
        by_file[f].append(patch)

    results = {}
    failures = []

    for rel in order:
        path = repo / rel
        if not path.exists():
            failures.append((rel, 'file does not exist'))
            continue
        raw = read_text(path)
        new_raw, file_failures = apply_ops(raw, by_file[rel])
        for label, reason in file_failures:
            failures.append(('%s :: %s' % (rel, label), reason))
        results[rel] = (path, new_raw, len(by_file[rel]))

    if failures:
        print('VALIDATION FAILED -- nothing written')
        for where, reason in failures:
            print('  [FAIL] %-70s %s' % (where, reason))
        return 1

    total = 0
    for rel in order:
        path, new_raw, count = results[rel]
        total += count
        if args.dry_run:
            print('  [ok]   %-70s %d patch(es) validated' % (rel, count))
        else:
            write_text(path, new_raw)
            print('  [ok]   %-70s %d patch(es) applied' % (rel, count))

    print('%s: %d patch(es) across %d file(s)'
          % ('DRY RUN' if args.dry_run else 'DONE', total, len(order)))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                               # noqa: BLE001
        pass
    sys.exit(main(sys.argv))
