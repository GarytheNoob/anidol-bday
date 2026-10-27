#!/usr/bin/env python3
"""从生日列表批量写入各日期 JSON。

数据格式（每行一个条目，Tab 或 CSV 逗号分隔，田野按顺序）：

    生日<TAB>类型<TAB>名字<TAB>组1;组2;...

例（groups 必须是小写 slug：仅小写字母、数字、连字符）：

    12-10	seiyuu	新田 恵海	love-live;u-s
    08-03	character	高坂 穂乃果	love-live;u-s

- 生日为 MM-DD（闰日 02-29 允许，写入 02/29.json）。
- 类型必须是 character / seiyuu / others。
- 组用分号分隔，每个值须匹配 ^[a-z0-9]+(-[a-z0-9]+)*$，可留空。
- 以 `#` 开头的行是注释，空行跳过。

- 若同一日期下已有同名条目（不论类型）：
  - 内容完全一致（name + type + groups 全一致）则跳过；
  - 否则拒绝添加并退出，保留原数据。合并 groups 请用 update_group.py。
- 月份目录与日期文件不存在时会自动创建。
"""

import csv
import json
import re
import sys
from pathlib import Path

VALID_TYPES = {"character", "seiyuu", "others"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAMES = {
    "seiyuu": "声优",
    "character": "角色",
    "others": "其他",
}


def read_rows(path, sep):
    rows = []
    for ln, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            if sep == "auto":
                parts = line.split("\t") if "\t" in line else next(csv.reader([line]))
            elif sep == "tsv":
                parts = line.split("\t")
            else:
                parts = next(csv.reader([line]))
        except csv.Error as e:
            print(f"第 {ln} 行解析失败: {e}")
            sys.exit(1)
        if len(parts) != 4:
            print(f"第 {ln} 行字段数不是 4: {line!r}")
            sys.exit(1)
        rows.append((ln, [p.strip() for p in parts]))
    return rows


def normalize_date(mmdd, ln):
    try:
        month, day = map(int, mmdd.split("-"))
    except ValueError:
        print(f"第 {ln} 行生日格式非法: {mmdd!r}")
        sys.exit(1)
    if not 1 <= month <= 12:
        print(f"第 {ln} 行月份非法: {mmdd!r}")
        sys.exit(1)
    # 大月 1,3,5,7,8,10,12 为 31 天，其余 30 天；2 月允许 29（闰日，归 02/29.json）
    dmax = (31 if month in (1, 3, 5, 7, 8, 10, 12) else 30) if month != 2 else 29
    if not 1 <= day <= dmax:
        print(f"第 {ln} 行日期非法: {mmdd}")
        sys.exit(1)
    return f"{month:02d}", f"{day:02d}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    list_path = sys.argv[1]
    sep = sys.argv[2] if len(sys.argv) > 2 else "auto"  # auto | tsv | csv
    root = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).resolve().parent.parent / "data"

    for ln, (date, kind, name, groups) in read_rows(list_path, sep):
        mm, dd = normalize_date(date, ln)
        if kind not in VALID_TYPES:
            print(f"第 {ln} 行类型非法: {kind!r}")
            sys.exit(1)
        tags = [g for g in (s.strip() for s in groups.split(";")) if g]
        invalid = [g for g in tags if not SLUG.match(g)]
        if invalid:
            print(f"第 {ln} 行 groups 含非法值 {', '.join(map(repr, invalid))}，"
                  f"只允许小写字母/数字/连字符")
            sys.exit(1)
        entry = {
            "name": name,
            "type": kind,
            "groups": tags,
        }
        day_file = root / mm / f"{dd}.json"
        day_file.parent.mkdir(parents=True, exist_ok=True)
        existing = json.loads(day_file.read_text(encoding="utf-8")) if day_file.exists() else []
        # 同日同名（不论类型）视为已有条目，拒绝添加；交给 update_group.py 处理
        clash = next((e for e in existing if e["name"] == name), None)
        if clash is not None:
            if clash == entry:
                print(f"`{NAMES[kind]} {name}` 已在 {mm}/{dd}.json，跳过")
            else:
                print(f"拒绝: {mm}/{dd}.json 已有名为 {name!r} 的条目 {clash}，"
                      f"如需合并 groups 请用 update_group.py")
                sys.exit(1)
            continue
        existing.append(entry)
        day_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"已写入 {mm}/{dd}.json: `{NAMES[kind]} {name}`")

    print("完成，建议跑一遍 validate.py")


if __name__ == "__main__":
    main()
