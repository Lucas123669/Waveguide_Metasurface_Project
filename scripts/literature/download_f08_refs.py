# -*- coding: utf-8 -*-
"""Download F08 case-reference PDFs (OA sources) into literature/材料体系分类/<system>/pdfs/.

Usage:
  python scripts/literature/download_f08_refs.py scripts/literature/manifests/f08_download_manifest.json

manifest.json format (list of dicts):
[
  {"id": "F-11", "title": "...", "journal": "...", "year": 2016,
   "system": "TiO2", "filename": "F_11_Devlin_2016_..._PNAS.pdf",
   "url": "https://...pdf", "note": "...", "status": "oa"|"need_subscription"}
]
Only entries with a usable "url" are downloaded. On success a local temp file is
verified to start with %PDF before it is written to the destination.
"""
import io, json, os, sys, time, urllib.request

PROXY = os.environ.get("HTTPS_PROXY") or "http://127.0.0.1:7897"
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

def fetch(url, max_redirects=8, timeout=60):
    proxy = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
    opener = urllib.request.build_opener(proxy)
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/pdf,*/*"})
    with opener.open(req, timeout=timeout) as r:
        return r.read(), r.headers

def looks_pdf(data):
    return data[:5] == b"%PDF-"

def download(item, out_dir):
    url = item.get("url")
    if not url or item.get("status") == "need_subscription":
        return {"ok": False, "reason": "no_oa_url"}
    fname = item["filename"]
    dest = os.path.join(out_dir, fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return {"ok": True, "skipped_existing": True}
    try:
        data, hdrs = fetch(url)
    except Exception as e:
        return {"ok": False, "reason": f"fetch_error: {e}"}
    if not looks_pdf(data):
        # sometimes servers serve pdf via redirect/HTML page -> report
        return {"ok": False, "reason": f"not_pdf (got {len(data)} bytes, head={data[:60]!r})"}
    os.makedirs(out_dir, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return {"ok": True, "bytes": len(data), "ctype": hdrs.get("Content-Type", "")}

def main():
    manifest_path = sys.argv[1]
    with io.open(manifest_path, encoding="utf-8") as f:
        items = json.load(f)
    out_dir = os.path.join(ROOT, "literature", "材料体系分类")
    results = []
    for it in items:
        d = os.path.join(out_dir, it["system"], "pdfs")
        r = download(it, d)
        r["id"] = it["id"]
        r["title"] = it["title"]
        results.append(r)
        print(f"{r['id']:>6}  {'OK' if r['ok'] else 'FAIL'}  {r.get('reason','')}  {it.get('filename','')}")
    n_ok = sum(1 for r in results if r["ok"])
    print(f"\n{len(results)} items, {n_ok} downloaded.")

if __name__ == "__main__":
    main()
