#!/usr/bin/env python3
"""全唐文册号 2 位 → 3 位（01–99 → 001–099），改中心库数据目录的一份拷贝。

用法：
    python3 migrate_vol3.py <数据目录 995ejelvk0> <输出目录> [--report report.json]

只改「册号」本身，不改事件 id、批次名、注释：
  路径：books/NN.yaml、feedback/anchors/NN.jsonl、feedback/bindings/NN/、feedback/anchor_patches/NN/、
        output/glyph_store/patches/v2_NN_*.png
  内容（JSON／JSONL 逐值、TSV 首列、册 yaml 的 id／raw_dir 两行）：
    格 key   NN:页:列:位…        → 0NN:页:列:位…
    实例 id  v2:NN:…             → v2:0NN:…
    图名     v2_NN_…             → v2_0NN_…
    字段 book／vol／volume 值为 NN → 0NN
  基础配置 config/book_defaults.yaml 加 book_id／book_title／volume_width: 3。
100–248 册本来就是 3 位，不动。PNG 等二进制原样拷。
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import shutil
import sys
from pathlib import Path

NN = re.compile(r"^(0[1-9]|[1-9][0-9])$")
CELL = re.compile(r"^(0[1-9]|[1-9][0-9]):(\d+:\d+:.+)$")
INST = re.compile(r"^v2:(0[1-9]|[1-9][0-9]):(.+)$")
IMG = re.compile(r"^v2_(0[1-9]|[1-9][0-9])_(.+)$")
VOL_FIELDS = {"book", "vol", "volume"}
STAT: collections.Counter = collections.Counter()


def p3(n: str) -> str:
    return f"{int(n):03d}"


def fix_str(s: str, field: str | None) -> str:
    if field in VOL_FIELDS and NN.match(s):
        STAT["field:" + field] += 1
        return p3(s)
    m = CELL.match(s)
    if m:
        STAT["cell_key"] += 1
        return f"{p3(m.group(1))}:{m.group(2)}"
    m = INST.match(s)
    if m:
        STAT["instance_id"] += 1
        return f"v2:{p3(m.group(1))}:{m.group(2)}"
    m = IMG.match(s)
    if m:
        STAT["img_name"] += 1
        return f"v2_{p3(m.group(1))}_{m.group(2)}"
    if s.startswith("{") and s.endswith("}"):
        try:
            inner = json.loads(s)
        except ValueError:
            return s
        new = fix(inner)
        if new != inner:
            STAT["nested_json"] += 1
            return json.dumps(new, ensure_ascii=False)
    return s


def fix(o, field: str | None = None):
    if isinstance(o, dict):
        return {fix_str(k, None) if isinstance(k, str) else k: fix(v, k) for k, v in o.items()}
    if isinstance(o, list):
        return [fix(v, field) for v in o]
    if isinstance(o, str):
        return fix_str(o, field)
    return o


def new_rel(rel: Path) -> Path:
    parts = list(rel.parts)
    if parts[0] == "books" and len(parts) == 2 and NN.match(rel.stem) and rel.suffix == ".yaml":
        parts[1] = p3(rel.stem) + ".yaml"
    elif parts[:2] == ["feedback", "anchors"] and len(parts) == 3 and NN.match(Path(parts[2]).stem):
        parts[2] = p3(Path(parts[2]).stem) + Path(parts[2]).suffix
    elif parts[:2] in (["feedback", "bindings"], ["feedback", "anchor_patches"]) and len(parts) >= 3 and NN.match(parts[2]):
        parts[2] = p3(parts[2])
    elif parts[:3] == ["output", "glyph_store", "patches"] and len(parts) == 4:
        m = IMG.match(parts[3])
        if m:
            parts[3] = f"v2_{p3(m.group(1))}_{m.group(2)}"
    out = Path(*parts)
    if out != rel:
        STAT["renamed:" + "/".join(rel.parts[:2])] += 1
    return out


def dumps_like(orig_line: str, obj) -> str:
    """尽量照原行的分隔符写回。"""
    compact = '", "' not in orig_line and '":"' in orig_line
    if compact:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(obj, ensure_ascii=False)


def fix_text(rel: Path, text: str) -> str:
    suf = rel.suffix
    if suf == ".jsonl":
        out = []
        for line in text.split("\n"):
            if not line.strip():
                out.append(line)
                continue
            obj = json.loads(line)
            new = fix(obj)
            out.append(line if new == obj else dumps_like(line, new))
        return "\n".join(out)
    if suf == ".json":
        obj = json.loads(text)
        new = fix(obj)
        if new == obj:
            return text
        indent = 1 if text.startswith("{\n ") and not text.startswith("{\n  ") else (2 if text.startswith("{\n  ") else None)
        s = json.dumps(new, ensure_ascii=False, indent=indent) if indent else dumps_like(text.split("\n")[0], new)
        return s + ("\n" if text.endswith("\n") else "")
    if suf == ".tsv":
        out = []
        for line in text.split("\n"):
            cols = line.split("\t")
            if cols and cols[0]:
                cols[0] = fix_str(cols[0], None)
            out.append("\t".join(cols))
        return "\n".join(out)
    if suf == ".yaml" and rel.parts[0] == "books":
        def sub_id(m):
            STAT["yaml:id"] += 1
            return f'{m.group(1)}"{p3(m.group(2))}"'
        def sub_raw(m):
            STAT["yaml:raw_dir"] += 1
            return f"{m.group(1)}{p3(m.group(2))}"
        text = re.sub(r'(?m)^(id:\s*)"(0[1-9]|[1-9][0-9])"', sub_id, text)
        text = re.sub(r"(?m)^(raw_dir:\s*data_full/)(0[1-9]|[1-9][0-9])\b", sub_raw, text)
        return text
    if rel.as_posix() == "config/book_defaults.yaml":
        if "volume_width:" not in text:
            head = ("# 2026-11-03 册号统一 3 位（Sheldon 定，guji-manager doc/参考/册配置.md「册号」）\n"
                    "book_id: 995ejelvk0\nbook_title: 欽定全唐文\nvolume_width: 3\n")
            STAT["book_defaults:added"] += 1
            return head + text
        return text
    return text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--report", type=Path)
    a = ap.parse_args(argv)
    if a.dst.exists():
        print(f"输出目录已存在：{a.dst}", file=sys.stderr)
        return 2
    seen: dict[Path, Path] = {}
    for f in sorted(a.src.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(a.src)
        if rel.parts[0].startswith("."):          # .central-state.json 等原样
            out_rel = rel
        else:
            out_rel = new_rel(rel)
        if out_rel in seen:
            print(f"撞名：{rel} 与 {seen[out_rel]} → {out_rel}", file=sys.stderr)
            return 3
        seen[out_rel] = rel
        dst = a.dst / out_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel.parts[0].startswith(".") or f.suffix not in (".json", ".jsonl", ".tsv", ".yaml"):
            shutil.copy2(f, dst)
            continue
        text = f.read_text(encoding="utf-8")
        new = fix_text(rel, text)
        if new != text:
            STAT["files_changed"] += 1
        dst.write_text(new, encoding="utf-8")
    STAT["files_total"] = len(seen)
    rep = dict(sorted(STAT.items()))
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if a.report:
        a.report.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
