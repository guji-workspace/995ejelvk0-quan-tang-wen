#!/usr/bin/env python3
"""册号迁 3 位第二步（A31 11-03，cv #967 后）：R2 页表 pages/995ejelvk0/NN/rXXX.json 复制到 0NN/，vol 改 0NN，
prev_sha256 按新链重算，加 migrated_from；旧表不删。--dry-run 只列。--pointers 再把 by-ws/995ejelvk0/0NN.json 改指 0NN。"""
import hashlib, json, sys
from open_guji_cv.datastore import sources as S
from open_guji_cv.datastore.client import WorkerSource
dry = "--dry-run" in sys.argv
src = WorkerSource()
B = "995ejelvk0"
keys = S._list(src, f"source/pages/{B}/")
vols = sorted({k.split("/")[3] for k in keys if len(k.split("/")[3]) == 2})
n_t = n_p = 0
for v in vols:
    nv = f"{int(v):03d}"
    revs = sorted(int(k.rsplit("/r", 1)[1][:-5]) for k in keys if k.split("/")[3] == v and k.endswith(".json") and "/r" in k)
    prev_bytes = None
    for r in revs:
        old_key = f"source/pages/{B}/{v}/r{r:03d}.json"
        new_key = f"source/pages/{B}/{nv}/r{r:03d}.json"
        t = json.loads(S._get(src, old_key))
        t["vol"] = nv
        t["migrated_from"] = old_key
        if t.get("prev_sha256") and prev_bytes is not None:
            t["prev_sha256"] = hashlib.sha256(prev_bytes).hexdigest()
        data = json.dumps(t, ensure_ascii=False, indent=1).encode("utf-8")
        if S._exists(src, new_key):
            data = S._get(src, new_key)
            print(f"有了 {new_key}")
        elif dry:
            print(f"[dry] {old_key} → {new_key}（{t.get('n_pages')} 页）")
        else:
            S._put(src, new_key, data)
            n_t += 1
        prev_bytes = data
    if "--pointers" in sys.argv:
        pk = S.pointer_key(B, nv)
        rec = {"ws": B, "book": nv, "book_id": B, "vol": nv}
        if dry:
            print(f"[dry] {pk} → {B}/{nv}")
        else:
            S._put(src, pk, json.dumps(rec, ensure_ascii=False).encode("utf-8"))
            n_p += 1
print(f"册 {len(vols)}，新写页表 {n_t}，改指针 {n_p}")
