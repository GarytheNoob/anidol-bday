# anidol-bday

一个二次元偶像企划的生日数据库。按日期维护静态 JSON 文件，记录各角色与声优的生日信息。

## 数据结构

`data/` 下按月组织，每个日期一个 JSON 文件，存有当天生日的所有条目：

```
data/
  01/01.json
  ...
  12/31.json
data/sources/          # 人工维护的源列表与原始资料
```

每个条目的格式：

```json
{ "name": "高坂穂乃果", "type": "character", "groups": ["lovelive", "mu-s"] }
```

- `name`：角色或声优的名字；
- `type`：`character`（角色）/ `seiyuu`（声优）/ `others`（其他）；
- `groups`：所属企划与团体，slug 格式（仅小写字母、数字、连字符），首项为企划名，其后为所属团名，如 `lovelive;nijigasaki`、`bangdream;mygo`。

同一个日期下同名的条目是唯一条目：同一人可能同时隶属多个企划，或既当角色声优又生于同日，均通过多个 `groups` 并列体现。

## 工具脚本

所有脚本位于 `scripts/`，零第三方依赖：

- **`add_birthdays.py`**：从 TSV/CSV 生日列表批量添加条目。同日同名且内容一致会跳过；同日同名但内容不同会拒绝（视为冲突）。
  ```sh
  python3 scripts/add_birthdays.py data/sources/lovelive.tsv
  ```
- **`update_group.py`**：定位某日期下同名的已有条目，把新输入的 `groups` 与其合并保存，用于给已存在的人补充所属企划/团体。
  ```sh
  python3 scripts/update_group.py 合并列表.tsv
  ```

源列表统一放在 `data/sources/`，可直接以 PR 形式修改。

## 免责声明

本仓库与 Love Live!、BanG Dream! 等任何相关企划、公司或机构**无关**；不隶属于任何官方，也不代表任何官方立场。数据由社群整理，仅供参考，请以官方公告为准。

## 参与贡献

欢迎通过 Pull Request 提交数据修正、新增企划或脚本改进——报告中的疏漏与错误同样欢迎指出，先开 issue 讨论亦可。

## License

仓库暂未指定开源许可，数据的可靠性请自行判断，使用后果自负。
