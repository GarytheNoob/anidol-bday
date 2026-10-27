#!/usr/bin/env node
/**
 * 校验 data/ 下所有 JSON 数据。
 * 零依赖：手写校验逻辑，CI 与本地均可直接 node scripts/validate.js 运行。
 */
const fs = require("fs");
const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data");
const MMDD = /^\d{2}-\d{2}$/;

const errors = [];

function push(msg) {
  errors.push(msg);
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch (e) {
    push(`JSON 解析失败: ${file} (${e.message})`);
    return null;
  }
}

function checkDate(file, where, date, optional) {
  if (date == null) {
    if (!optional) push(`${file}: ${where} 缺少必填的 birthday (MM-DD)`);
    return;
  }
  if (typeof date !== "string" || !MMDD.test(date)) {
    push(`${file}: ${where} birthday 格式应为 MM-DD，实际为 ${JSON.stringify(date)}`);
    return;
  }
  const [, m, d] = date.match(/^(\d{2})-(\d{2})$/);
  const month = Number(m);
  const day = Number(d);
  if (month < 1 || month > 12 || day < 1 || day > 31) {
    push(`${file}: ${where} birthday 不是合法日期: ${date}`);
  }
}

// 1. 企划目录
const franchisesFile = path.join(DATA_DIR, "franchises.json");
const franchises = readJson(franchisesFile);
const franchiseIds = new Set();
if (franchises) {
  (franchises.franchises || []).forEach((f) => {
    if (!f.id || !f.name) push("franchises.json: 每个企划需要 id 和 name");
    else franchiseIds.add(f.id);
  });
}

// 2. 各企划数据文件
const frDir = path.join(DATA_DIR, "franchises");
const charSeen = new Set();
for (const file of fs.readdirSync(frDir)) {
  if (!file.endsWith(".json")) continue;
  const full = path.join(frDir, file);
  const data = readJson(full);
  if (!data) continue;

  if (!franchiseIds.has(data.franchise)) {
    push(`${file}: franchise "${data.franchise}" 未在 franchises.json 中注册`);
  }
  const chars = data.characters || [];
  if (chars.length === 0) push(`${file}: characters 为空`);

  for (const c of chars) {
    const label = `${file}: 角色 ${c.id || "(无 id)"}`;
    if (!c.id) push(`${label} 缺少 id`);
    else if (charSeen.has(c.id)) push(`${label} id 重复`);
    else charSeen.add(c.id);
    if (!c.name) push(`${label} 缺少 name`);
    checkDate(file, `角色 ${c.id}`, c.birthday, false);

    (c.casts || []).forEach((cast, i) => {
      if (!cast.name) push(`${label} casts[${i}] 缺少 name`);
      checkDate(file, `${c.id} 的声优 ${cast.name || `casts[${i}]`}`, cast.birthday, true);
    });
  }
}

if (errors.length) {
  console.error(`发现 ${errors.length} 个问题:`);
  errors.forEach((e) => console.error(" - " + e));
  process.exit(1);
}
console.log(`OK: 校验通过 (企划 ${franchiseIds.size} 个, 角色 ${charSeen.size} 位)`);
