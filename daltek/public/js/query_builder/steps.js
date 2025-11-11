// Steps - Lógica de los pasos del Query Builder
// Se ejecuta en el contexto del campo HTML de ERPNext

(function (window) {
  "use strict";

  window.QueryBuilderSteps = window.QueryBuilderSteps || {};

  const getState = () => window.QueryBuilderState.state;
  const getMockDB = () => window.QueryBuilderState.mockDB;
  const dom = window.QueryBuilderUI.dom;

  // Poblar el selector de tablas
  window.QueryBuilderSteps.populateTableSelect = function () {
    const mockDB = getMockDB();

    dom.tableSelect.innerHTML =
      '<option value="">-- Elige una tabla --</option>';
    Object.keys(mockDB).forEach((name) => {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      dom.tableSelect.appendChild(opt);
    });
  };

  // Manejar cambio de tabla
  window.QueryBuilderSteps.handleTableChange = function () {
    const state = getState();
    const mockDB = getMockDB();
    const table = dom.tableSelect.value;

    state.table = table;
    dom.colsSection.style.display = "none";
    dom.filtersSection.style.display = "none";
    state.selectedCols = [];
    state.filters = [];
    dom.colsList.innerHTML = "";
    dom.filtersContainer.innerHTML = "";

    if (!table) {
      dom.tableHint.textContent = "Selecciona una tabla para continuar.";
      return;
    }

    dom.tableHint.textContent = `Tabla seleccionada: ${table}`;
    dom.metaTable.textContent = table;

    dom.colsSelect.innerHTML = '<option value="">-- elige columna --</option>';
    mockDB[table].cols.forEach((col) => {
      const opt = document.createElement("option");
      opt.value = col;
      opt.textContent = col;
      dom.colsSelect.appendChild(opt);
    });

    dom.colsSection.style.display = "block";
  };

  // Agregar una columna
  window.QueryBuilderSteps.handleAddColumn = function () {
    const state = getState();
    const col = dom.colsSelect.value;

    if (!col) return;
    if (!state.selectedCols.includes(col)) {
      state.selectedCols.push(col);
      window.QueryBuilderUI.renderSelectedCols();
    }
    dom.metaCols.textContent = state.selectedCols.join(", ");
    dom.filtersSection.style.display = "block";
  };

  // Seleccionar todas las columnas
  window.QueryBuilderSteps.handleSelectAllColumns = function () {
    const state = getState();
    const mockDB = getMockDB();

    if (!state.table) return;
    state.selectedCols = [...mockDB[state.table].cols];
    window.QueryBuilderUI.renderSelectedCols();
    dom.metaCols.textContent = state.selectedCols.join(", ");
    dom.filtersSection.style.display = "block";
  };

  // Agregar fila de filtro
  window.QueryBuilderSteps.addFilterRow = function () {
    const state = getState();
    const mockDB = getMockDB();

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
      window.QueryBuilderSteps.updateFiltersState();
    });

    [colSel, opSel, valInput].forEach((el) =>
      el.addEventListener(
        "change",
        window.QueryBuilderSteps.updateFiltersState,
      ),
    );

    row.appendChild(colSel);
    row.appendChild(opSel);
    row.appendChild(valInput);
    row.appendChild(removeBtn);

    dom.filtersContainer.appendChild(row);
    window.QueryBuilderSteps.updateFiltersState();
  };

  // Actualizar estado de filtros
  window.QueryBuilderSteps.updateFiltersState = function () {
    const state = getState();
    const rows = [...dom.filtersContainer.children];
    const filters = [];

    rows.forEach((r) => {
      const [colSel, opSel, valInput] = r.querySelectorAll(
        "select,select,input",
      );
      const col = colSel.value;
      const op = opSel.value;
      const val = valInput.value.trim();
      if (col && op && val !== "") filters.push({ col, op, val });
    });

    state.filters = filters;

    dom.metaFilters.textContent = filters.length
      ? filters.map((f) => `${f.col} ${f.op} ${f.val}`).join(" AND ")
      : "—";
  };
})(window);
