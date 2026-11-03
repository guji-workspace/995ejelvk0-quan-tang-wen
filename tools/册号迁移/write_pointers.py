#!/usr/bin/env python3
"""册号迁 3 位：给 R2 补 by-ws/995ejelvk0/<0NN>.json 指针，指回原 2 位页表（cv norm_vol 仍是 2 位，页表不搬）。
只增不改；已有且相同跳过。用正式令牌（GUJI_DATA_TOKEN=$GUJI_DATA_TOKEN_PROD）。--dry-run 只列。"""
import sys
from open_guji_cv.datastore import sources as S
from open_guji_cv.datastore.client import WorkerSource
dry = "--dry-run" in sys.argv
src = WorkerSource()
vols = sorted({k.split("/")[3] for k in S._list(src, "source/pages/995ejelvk0/")})
n = 0
for v in vols:
    if len(v) != 2:
        continue
    book = f"{int(v):03d}"
    print(("[dry] " if dry else "") + f"{S.pointer_key('995ejelvk0', book)} → 995ejelvk0/{v}")
    if not dry:
        S.write_pointer(src, "995ejelvk0", book, "995ejelvk0", v)
    n += 1
print(f"{n} 个指针")
