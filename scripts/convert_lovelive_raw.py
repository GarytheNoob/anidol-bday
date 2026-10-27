#!/usr/bin/env python3
"""把 Love Live! 系列的中文维基风格生日列表（领域原文）转换为
add_birthdays.py 可识别的 TSV。

规则：
- `X月Y日` → MM-DD
- キャラ → character，キャスト → seiyuu
- 去掉声优名后的 `（...役）` 后缀（含 `〜2023年3月` 之类的备注）
- 所有条目 groups 首项为 lovelive，其后为所属团体的 slug

用法：
    python3 scripts/convert_lovelive_raw.py raw_lovelive.txt > data/sources/lovelive.tsv
"""

import re
import sys
from pathlib import Path

# 团体原名 → slug
GROUP_MAP = {
    "μ\'s": "mu-s",
    "Aqours": "aqours",
    "虹ヶ咲": "nijigasaki",
    "Liella!": "liella",
    "蓮ノ空": "hasunosora",
    "いきづらい部！": "ikizulive",
    "Saint Snow": "saint-snow",
    "Sunny Passion": "sunny-passion",
    # スーパースター!! 为动画标题；其角色/声优归属 Liella!
    "スーパースター!!": "liella",
    "虹ヶ咲（東雲学院）": "nijigasaki",
}

DATE = re.compile(r"^(\d{1,2})月(\d{1,2})日$")
SUFFIX = re.compile(r"（[^（）]*役[^（）]*）$")  # （…役…）结尾


def convert(line):
    line = line.strip()
    if not line:
        return None
    parts = line.split("\t")
    if len(parts) != 4:
        print(f"跳过字段数异常的行: {line!r}", file=sys.stderr)
        return None
    date_s, name, kind_raw, group_raw = (p.strip() for p in parts)
    m = DATE.match(date_s)
    if not m:
        print(f"跳过日期异常的行: {line!r}", file=sys.stderr)
        return None
    mm, dd = m.group(1), m.group(2)

    if kind_raw == "キャラ":
        kind = "character"
    elif kind_raw == "キャスト":
        kind = "seiyuu"
        name = SUFFIX.sub("", name).strip()  # 去掉声优名后的（xx役）
    else:
        print(f"跳过类型异常的行: {line!r}", file=sys.stderr)
        return None

    # 兼容连带括号的整体写法（如 虹ヶ咲（東雲学院））与标题写法（スーパースター!!）
    mapped = GROUP_MAP.get(group_raw)
    if mapped is None:
        mapped = next((v for k, v in GROUP_MAP.items() if group_raw.startswith(k)), None)
    if mapped is None:
        print(f"跳过未知团体 {group_raw!r} 的行: {line!r}", file=sys.stderr)
        return None

    date = f"{int(mm):02d}-{int(dd):02d}"
    return f"{date}\t{kind}\t{name}\tlovelive;{mapped}"


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
        out = convert(line)
        if out:
            print(out)


if __name__ == "__main__":
    main()
