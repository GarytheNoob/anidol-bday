#!/usr/bin/env python3
"""把新输入的 groups 合并进 data/ 中已有的同名同日条目。

输入格式与 add_birthdays.py 相同（生日<TAB>类型<TAB>名字<TAB>组1;组2;...），
其中「生日 + 名字」用于定位已有条目；类型仅用于提示，不参与匹配。

对每行输入：
- 若 data/ 里找不到同日同名条目 → 报错退出，不做任何写入；
- 若已存在 → 新 groups 与原 groups 取并集去重（原顺序在前，新值按需追加），
  全新或无变化时原样保留并打印结果。

groups 仍须满足 slug 规则（小写字母、数字、连字符）。
"""

from pathlib import Path

from add_birthdays import NAMES, SLUG, normalize_date, read_rows
import json
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    list_path = sys.argv[1]
    sep = sys.argv[2] if len(sys.argv) > 2 else "auto"  # auto | tsv | csv
    root = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).resolve().parent.parent / "data"

    changed = False
    for ln, (date, kind, name, groups) in read_rows(list_path, sep):
        mm, dd = normalize_date(date, ln)
        tags = [g for g in (s.strip() for s in groups.split(";")) if g]
        invalid = [g for g in tags if not SLUG.match(g)]
        if invalid:
            print(f"第 {ln} 行 groups 含非法值 {', '.join(map(repr, invalid))}，"
                  f"只允许小写字母/数字/连字符")
            sys.exit(1)

        day_file = root / mm / f"{dd}.json"
        existing = json.loads(day_file.read_text(encoding="utf-8")) if day_file.exists() else []
        target = next((e for e in existing if e["name"] == name), None)
        if target is None:
            print(f"第 {ln} 行: {mm}/{dd}.json 中没有名为 {name!r} 的条目，拒绝合并")
            sys.exit(1)

        old = target["groups"]
        merged = list(old) + [g for g in tags if g not in old]
        if merged == old:
            print(f"`{NAMES[kind] if kind in NAMES else target['type']}` {name}: groups 已是并集，无变化")
            continue
        target["groups"] = merged
        day_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed = True
        print(f"`{NAMES[kind]}` {name} ({mm}/{dd}.json): groups 合并完成 {old} + {tags} → {merged}")

    print("完成。" if changed else "完成（无改动）。")


if __name__ == "__main__":
    main()
