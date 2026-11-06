#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identify a paper PDF in one shot: page count, SHA-256, DOI, metadata, page-1 text.

Use this first when a user drops a PDF: it gives you everything needed to match
the paper against a repository's index (title, journal, DOI) and to record the
file's integrity (bytes + hash) in a source ledger.

Usage
-----
  python -X utf8 pdf_info.py PATH.pdf [--pages N] [--chars N]

  --pages  how many leading pages to mine for a DOI (default 3)
  --chars  how much page-1 text to print (default 1500)

Output is JSON. Requires PyMuPDF (`import pymupdf`, older name `fitz`).
"""

import argparse
import hashlib
import json
import re
import sys


def load_pymupdf():
    try:
        import pymupdf  # noqa: F401
        return pymupdf
    except ImportError:
        try:
            import fitz as pymupdf  # noqa: F401
            return pymupdf
        except ImportError:
            return None


def flat(text):
    return re.sub(r'\s+', ' ', text or '').strip()


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('pdf')
    ap.add_argument('--pages', type=int, default=3)
    ap.add_argument('--chars', type=int, default=1500)
    args = ap.parse_args(argv[1:])

    from pathlib import Path

    path = Path(args.pdf)
    if not path.exists():
        print('ERROR: no such file: %s' % path)
        return 2

    data = path.read_bytes()
    info = {
        'path': str(path),
        'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest().upper(),
    }

    pymupdf = load_pymupdf()
    if pymupdf is None:
        info['error'] = 'PyMuPDF not installed; only size and hash are available'
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 3

    doc = pymupdf.open(path)
    if doc.is_encrypted:
        try:
            doc.authenticate('')
        except Exception:                           # noqa: BLE001
            pass

    meta = doc.metadata or {}
    info.update({
        'pages': doc.page_count,
        'meta_title': (meta.get('title') or '').strip(),
        'meta_subject': (meta.get('subject') or '').strip(),
        'meta_creator': (meta.get('creator') or '').strip(),
        'meta_creation_date': (meta.get('creationDate') or '').strip(),
    })

    head = []
    doi = ''
    for i in range(min(max(args.pages, 1), doc.page_count)):
        try:
            text = doc[i].get_text()
        except Exception:                           # noqa: BLE001
            continue
        if i == 0:
            head.append(flat(text))
        if not doi:
            match = re.search(r'10\.\d{4,9}/[^\s"<>,;)\]]+', flat(text))
            if match:
                doi = match.group(0).rstrip('.').rstrip(')')

    info['doi'] = doi
    info['page1'] = head[0][:args.chars] if head else ''
    doc.close()

    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                               # noqa: BLE001
        pass
    sys.exit(main(sys.argv))
