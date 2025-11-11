function escapeSql(s) {
  return s.replace(/'/g, "''");
}

function buildSQL() {
  const state = window.QueryBuilderState.state;
  const select = state.selectedCols.join(", ");
  const from = state.tableName || state.table; // Usar tableName si está disponible

  let where = "";
  if (state.filters.length) {
    const conds = state.filters.map((f) => {
      if (f.op === "LIKE") {
        const v = f.val.includes("%") ? f.val : `%${f.val}%`;
        return `${f.col} LIKE '${escapeSql(v)}'`;
      }

      const isNum = !isNaN(Number(f.val));
      const isBool = ["true", "false"].includes(f.val.toLowerCase());

      if (isNum || isBool) return `${f.col} ${f.op} ${f.val}`;
      return `${f.col} ${f.op} '${escapeSql(f.val)}'`;
    });

    where = " WHERE " + conds.join(" AND ");
  }

  return `SELECT ${select} FROM \`${from}\`${where}`;
}

function parseVal(v) {
  if (v.toLowerCase() === "true") return true;
  if (v.toLowerCase() === "false") return false;
  if (!isNaN(Number(v))) return Number(v);
  return v;
}

function executeMockQuery() {
  let rows = [...mockDB[state.table].rows];

  state.filters.forEach((f) => {
    const cmpVal = parseVal(f.val);
    rows = rows.filter((r) => {
      const val = r[f.col];
      switch (f.op) {
        case "=":
          return val == cmpVal;
        case "!=":
          return val != cmpVal;
        case ">":
          return Number(val) > Number(cmpVal);
        case "<":
          return Number(val) < Number(cmpVal);
        case ">=":
          return Number(val) >= Number(cmpVal);
        case "<=":
          return Number(val) <= Number(cmpVal);
        case "LIKE":
          const needle = f.val.replace(/%/g, "").toLowerCase();
          return String(val).toLowerCase().includes(needle);
      }
    });
  });

  return rows.map((r) => {
    const obj = {};
    state.selectedCols.forEach((c) => (obj[c] = r[c]));
    return obj;
  });
}
