// Steps - Lógica de los pasos del Query Builder

(function (window) {
  "use strict";

  window.QueryBuilderSteps = window.QueryBuilderSteps || {};

  const getState = () => window.QueryBuilderState.state;
  const getMockDB = () => window.QueryBuilderState.mockDB;
  const dom = window.QueryBuilderUI.dom;

  window.QueryBuilderSteps.populateTableSelect = function () {
    dom.tableSelect.innerHTML =
      '<option value="">-- Cargando DocTypes... --</option>';

    frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "DocType",
        fields: ["name", "module", "custom"],
        filters: {
          istable: 0,
          issingle: 0,
          is_virtual: 0,
        },
        limit_page_length: 0,
        order_by: "name",
      },
      callback: function (response) {
        dom.tableSelect.innerHTML =
          '<option value="">-- Selecciona un DocType --</option>';

        if (response.message && response.message.length > 0) {
          console.log("DocTypes encontrados:", response.message.length);

          const standardDoctypes = response.message.filter((dt) => !dt.custom);
          const customDoctypes = response.message.filter((dt) => dt.custom);

          if (standardDoctypes.length > 0) {
            const standardGroup = document.createElement("optgroup");
            standardGroup.label = "DocTypes Estándar";

            standardDoctypes.forEach(function (doctype) {
              const opt = document.createElement("option");
              opt.value = "tab" + doctype.name.replace(/\s/g, "");
              opt.textContent = doctype.name + " (" + doctype.module + ")";
              opt.setAttribute("data-doctype", doctype.name);
              standardGroup.appendChild(opt);
            });

            dom.tableSelect.appendChild(standardGroup);
          }

          if (customDoctypes.length > 0) {
            const customGroup = document.createElement("optgroup");
            customGroup.label = "DocTypes Personalizados";

            customDoctypes.forEach(function (doctype) {
              const opt = document.createElement("option");
              opt.value = "tab" + doctype.name.replace(/\s/g, "");
              opt.textContent = doctype.name + " (Custom)";
              opt.setAttribute("data-doctype", doctype.name);
              customGroup.appendChild(opt);
            });

            dom.tableSelect.appendChild(customGroup);
          }

          console.log(
            "DocTypes cargados - Estándar:",
            standardDoctypes.length,
            "Custom:",
            customDoctypes.length,
          );
        } else {
          dom.tableSelect.innerHTML =
            '<option value="">-- No se encontraron DocTypes --</option>';
          console.warn("No se encontraron DocTypes");
        }
      },
      error: function (error) {
        console.error("Error obteniendo DocTypes:", error);
        dom.tableSelect.innerHTML =
          '<option value="">-- Error cargando DocTypes --</option>';
        frappe.msgprint("Error al cargar los DocTypes: " + error.message);
      },
    });
  };

  window.QueryBuilderSteps.handleTableChange = function () {
    const state = getState();
    const selectedOption = dom.tableSelect.selectedOptions[0];
    const table = dom.tableSelect.value;

    state.table = table;
    dom.colsSection.style.display = "none";
    dom.filtersSection.style.display = "none";
    state.selectedCols = [];
    state.filters = [];
    dom.colsList.innerHTML = "";
    dom.filtersContainer.innerHTML = "";

    if (!table) {
      dom.tableHint.textContent = "Selecciona un DocType para continuar.";
      return;
    }

    const doctypeName = selectedOption.getAttribute("data-doctype");
    dom.tableHint.textContent = `DocType seleccionado: ${doctypeName}`;
    dom.metaTable.textContent = doctypeName;

    dom.colsSelect.innerHTML =
      '<option value="">-- Cargando campos... --</option>';

    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.get_doctype_fields",
      args: {
        doctype_name: doctypeName,
      },
      callback: function (response) {
        dom.colsSelect.innerHTML =
          '<option value="">-- Selecciona campo --</option>';

        if (response.message && response.message.success) {
          const fields = response.message.all_fields;

          state.doctypeName = doctypeName;
          state.tableName = response.message.table_name;
          state.availableFields = fields;

          fields.forEach((field) => {
            const opt = document.createElement("option");
            opt.value = field.fieldname;
            opt.textContent = field.label + " (" + field.fieldtype + ")";
            dom.colsSelect.appendChild(opt);
          });

          dom.colsSection.style.display = "block";
        }
      },
      error: function (error) {
        console.error("Error obteniendo campos del DocType:", error);
        dom.colsSelect.innerHTML =
          '<option value="">-- Error cargando campos --</option>';
        frappe.msgprint("Error al cargar los campos: " + error.message);
      },
    });
  };

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

  window.QueryBuilderSteps.handleSelectAllColumns = function () {
    const state = getState();

    if (!state.table) return;

    const allOptions = [...dom.colsSelect.options].slice(1);
    state.selectedCols = allOptions.map((option) => option.value);

    window.QueryBuilderUI.renderSelectedCols();
    dom.metaCols.textContent = state.selectedCols.join(", ");
    dom.filtersSection.style.display = "block";
  };

  window.QueryBuilderSteps.addFilterRow = function () {
    const state = getState();

    if (!state.table) return;

    const row = document.createElement("div");
    row.className = "filter-row";

    const colSel = document.createElement("select");
    colSel.innerHTML = '<option value="">-- columna --</option>';

    [...dom.colsSelect.options].slice(1).forEach((option) => {
      const opt = document.createElement("option");
      opt.value = option.value;
      opt.textContent = option.textContent;
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
