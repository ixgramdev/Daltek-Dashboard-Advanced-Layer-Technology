function populateTableSelect() {
  tableSelect.innerHTML = '<option value="">-- Elige una tabla --</option>';
  Object.keys(mockDB).forEach((name) => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    tableSelect.appendChild(opt);
  });
}

function handleTableChange() {
  const table = tableSelect.value;
  state.table = table;

  colsSection.style.display = "none";
  filtersSection.style.display = "none";
  state.selectedCols = [];
  state.filters = [];
  colsList.innerHTML = "";
  filtersContainer.innerHTML = "";

  if (!table) {
    tableHint.textContent = "Selecciona una tabla para continuar.";
    return;
  }

  tableHint.textContent = `Tabla seleccionada: ${table}`;
  metaTable.textContent = table;

  colsSelect.innerHTML = '<option value="">-- elige columna --</option>';
  mockDB[table].cols.forEach((col) => {
    const opt = document.createElement("option");
    opt.value = col;
    opt.textContent = col;
    colsSelect.appendChild(opt);
  });

  colsSection.style.display = "block";
}

function handleAddColumn() {
  const col = colsSelect.value;
  if (!col) return;
  if (!state.selectedCols.includes(col)) {
    state.selectedCols.push(col);
    renderSelectedCols();
  }
  metaCols.textContent = state.selectedCols.join(", ");
  filtersSection.style.display = "block";
}

function handleSelectAllColumns() {
  if (!state.table) return;
  state.selectedCols = [...mockDB[state.table].cols];
  renderSelectedCols();
  metaCols.textContent = state.selectedCols.join(", ");
  filtersSection.style.display = "block";
}

function addFilterRow() {
  if (!state.table) return;

  const row = document.createElement("div");
  row.className = "filter-row";

  const colSel = document.createElement("select");
  colSel.innerHTML = '<option value="">-- columna --</option>';
  mockDB[state.table].cols.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    colSel.appendChild(opt);
  });

  const opSel = document.createElement("select");
  ["=", "!=", ">", "<", ">=", "<=", "LIKE"].forEach((op) => {
    const opt = document.createElement("option");
    opt.value = op;
    opt.textContent = op;
    opSel.appendChild(opt);
  });

  const valInput = document.createElement("input");
  valInput.type = "text";
  valInput.placeholder = "valor";

  const removeBtn = document.createElement("button");
  removeBtn.className = "remove";
  removeBtn.textContent = "🗑";
  removeBtn.addEventListener("click", () => {
    row.remove();
    updateFiltersState();
  });

  [colSel, opSel, valInput].forEach((el) =>
    el.addEventListener("change", updateFiltersState),
  );

  row.appendChild(colSel);
  row.appendChild(opSel);
  row.appendChild(valInput);
  row.appendChild(removeBtn);

  filtersContainer.appendChild(row);

  updateFiltersState();
}

function updateFiltersState() {
  const rows = [...filtersContainer.children];
  const filters = [];

  rows.forEach((r) => {
    const [colSel, opSel, valInput] = r.querySelectorAll("select,select,input");
    const col = colSel.value;
    const op = opSel.value;
    const val = valInput.value.trim();
    if (col && op && val !== "") filters.push({ col, op, val });
  });

  state.filters = filters;

  metaFilters.textContent = filters.length
    ? filters.map((f) => `${f.col} ${f.op} ${f.val}`).join(" AND ")
    : "—";
}
