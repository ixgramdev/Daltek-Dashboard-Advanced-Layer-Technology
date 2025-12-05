// Steps - Lógica de los pasos del Query Builder

(function (window) {
  "use strict";

  window.QueryBuilderSteps = window.QueryBuilderSteps || {};

  const getState = () => window.QueryBuilderState.state;
  const getMockDB = () => window.QueryBuilderState.mockDB;
  const dom = window.QueryBuilderUI.dom;

  window.QueryBuilderSteps.populateTableSelect = function () {
    const searchInput = document.getElementById("search");
    const dropdown = document.getElementById("dropdown");

    if (!searchInput || !dropdown) {
      console.error("Elementos de búsqueda no encontrados"); // Revisar si se puede pasar este mensaje del lado del server (Validando)
      return;
    }

    dropdown.innerHTML =
      '<div class="dropdown-item">Cargando DocTypes...</div>';
    dropdown.style.display = "block";

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
        dropdown.innerHTML = "";

        if (response.message && response.message.length > 0) {
          const standardDoctypes = response.message.filter((dt) => !dt.custom);
          const customDoctypes = response.message.filter((dt) => dt.custom);

          if (standardDoctypes.length > 0) {
            const groupTitle = document.createElement("div");
            groupTitle.className = "dropdown-group-title";
            groupTitle.textContent = "DocTypes Estándar";
            dropdown.appendChild(groupTitle);

            standardDoctypes.forEach(function (doctype) {
              const item = document.createElement("div");
              item.className = "dropdown-item";
              item.dataset.value = "tab" + doctype.name.replace(/\s/g, "");
              item.dataset.doctype = doctype.name;
              item.textContent = `${doctype.name} (${doctype.module})`;

              item.addEventListener("click", function () {
                selectDoctype(item, searchInput, dropdown);
              });

              dropdown.appendChild(item);
            });
          }

          if (customDoctypes.length > 0) {
            const groupTitle = document.createElement("div");
            groupTitle.className = "dropdown-group-title";
            groupTitle.textContent = "DocTypes Personalizados";
            dropdown.appendChild(groupTitle);

            customDoctypes.forEach(function (doctype) {
              const item = document.createElement("div");
              item.className = "dropdown-item";
              item.dataset.value = "tab" + doctype.name.replace(/\s/g, "");
              item.dataset.doctype = doctype.name;
              item.textContent = `${doctype.name} (Custom)`;

              item.addEventListener("click", function () {
                selectDoctype(item, searchInput, dropdown);
              });

              dropdown.appendChild(item);
            });
          }

          window.QueryBuilderSteps.allDoctypeItems = Array.from(
            dropdown.querySelectorAll(".dropdown-item"),
          );
        } else {
          dropdown.innerHTML =
            '<div class="dropdown-item">No se encontraron DocTypes</div>';
        }

        dropdown.style.display = "none";
      },
      error: function (error) {
        console.error("Error obteniendo DocTypes:", error);
        dropdown.innerHTML =
          '<div class="dropdown-item">Error cargando DocTypes</div>';
        frappe.msgprint("Error al cargar los DocTypes: " + error.message);
      },
    });
  };

  // NUEVA FUNCIÓN: Seleccionar un DocType
  function selectDoctype(item, searchInput, dropdown) {
    searchInput.value = item.textContent;
    searchInput.dataset.value = item.dataset.value;
    searchInput.dataset.doctype = item.dataset.doctype;
    dropdown.style.display = "none";

    // Ejecutar la lógica de cambio de tabla
    window.QueryBuilderSteps.handleTableChange();
  }

  // NUEVA FUNCIÓN: Poblar el dropdown de campos con grupos por tipo
  window.QueryBuilderSteps.populateFieldsDropdown = function (fields) {
    const fieldsDropdown = dom.fieldsDropdown;

    if (!fieldsDropdown) {
      console.error("Dropdown de campos no encontrado");
      return;
    }

    fieldsDropdown.innerHTML = "";

    // Agrupar campos por tipo
    const fieldsByType = {};
    fields.forEach((field) => {
      const type = field.fieldtype || "Otros";
      if (!fieldsByType[type]) {
        fieldsByType[type] = [];
      }
      fieldsByType[type].push(field);
    });

    // Ordenar los tipos y crear grupos
    const sortedTypes = Object.keys(fieldsByType).sort();

    sortedTypes.forEach((type) => {
      // Crear título del grupo
      const groupTitle = document.createElement("div");
      groupTitle.className = "dropdown-group-title";
      groupTitle.textContent = type;
      fieldsDropdown.appendChild(groupTitle);

      // Agregar campos del grupo
      fieldsByType[type].forEach((field) => {
        const item = document.createElement("div");
        item.className = "dropdown-item";
        item.dataset.value = field.fieldname;
        item.dataset.label = field.label;
        item.dataset.fieldtype = field.fieldtype;
        item.textContent = `${field.label} (${field.fieldname})`;

        item.addEventListener("click", function () {
          selectField(item);
        });

        fieldsDropdown.appendChild(item);
      });
    });

    // Guardar todos los items para filtrado
    window.QueryBuilderSteps.allFieldItems = Array.from(
      fieldsDropdown.querySelectorAll(".dropdown-item"),
    );
  };

  // NUEVA FUNCIÓN: Seleccionar un campo
  function selectField(item) {
    const fieldsSearch = dom.fieldsSearch;
    const fieldsDropdown = dom.fieldsDropdown;

    if (!fieldsSearch || !fieldsDropdown) return;

    fieldsSearch.value = item.textContent;
    fieldsSearch.dataset.value = item.dataset.value;
    fieldsSearch.dataset.label = item.dataset.label;
    fieldsDropdown.style.display = "none";
  }

  // FUNCIÓN MODIFICADA: Manejar cambio de tabla
  window.QueryBuilderSteps.handleTableChange = function () {
    const state = getState();
    const searchInput = document.getElementById("search");

    if (!searchInput || !searchInput.dataset.value) {
      dom.tableHint.textContent = "Selecciona un DocType para continuar.";
      return;
    }

    const table = searchInput.dataset.value;
    const doctypeName = searchInput.dataset.doctype;

    state.table = table;
    dom.colsSection.style.display = "none";
    dom.filtersSection.style.display = "none";
    state.selectedCols = [];
    state.filters = [];
    dom.colsList.innerHTML = "";
    dom.filtersContainer.innerHTML = "";

    dom.tableHint.textContent = `DocType seleccionado: ${doctypeName}`;

    // Mostrar estado de carga en el dropdown de campos
    if (dom.fieldsDropdown) {
      dom.fieldsDropdown.innerHTML =
        '<div class="dropdown-item">Cargando campos...</div>';
      dom.fieldsDropdown.style.display = "none";
    }

    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.get_doctype_fields",
      args: {
        doctype_name: doctypeName,
      },
      callback: function (response) {
        if (response.message && response.message.success) {
          const fields = response.message.all_fields;

          state.doctypeName = doctypeName;
          state.tableName = response.message.table_name;
          state.availableFields = fields;

          // Poblar el dropdown de campos con grupos por tipo
          window.QueryBuilderSteps.populateFieldsDropdown(fields);

          dom.colsSection.style.display = "block";
        }
      },
      error: function (error) {
        console.error("Error obteniendo campos del DocType:", error);
        if (dom.fieldsDropdown) {
          dom.fieldsDropdown.innerHTML =
            '<div class="dropdown-item">Error cargando campos</div>';
        }
        frappe.msgprint("Error al cargar los campos: " + error.message);
      },
    });
  };

  window.QueryBuilderSteps.handleAddColumn = function () {
    const state = getState();
    const fieldsSearch = dom.fieldsSearch;

    if (!fieldsSearch || !fieldsSearch.dataset.value) {
      frappe.msgprint("Por favor, selecciona un campo del dropdown");
      return;
    }

    const col = fieldsSearch.dataset.value;

    if (!col) return;
    if (!state.selectedCols.includes(col)) {
      state.selectedCols.push(col);
      window.QueryBuilderUI.renderSelectedCols();

      // Triggear auto-guardado cuando se agregan columnas
      if (
        window.QueryBuilderViews &&
        window.QueryBuilderViews.triggerAutoSave
      ) {
        window.QueryBuilderViews.triggerAutoSave();
      }
    }

    // Limpiar el campo de búsqueda después de agregar
    fieldsSearch.value = "";
    delete fieldsSearch.dataset.value;
    delete fieldsSearch.dataset.label;

    dom.filtersSection.style.display = "block";
  };

  window.QueryBuilderSteps.handleSelectAllColumns = function () {
    const state = getState();

    if (!state.table || !state.availableFields) return;

    // Seleccionar todos los campos disponibles
    state.selectedCols = state.availableFields.map((field) => field.fieldname);

    window.QueryBuilderUI.renderSelectedCols();
    dom.filtersSection.style.display = "block";

    // Triggear auto-guardado cuando se seleccionan todas las columnas
    if (window.QueryBuilderViews && window.QueryBuilderViews.triggerAutoSave) {
      window.QueryBuilderViews.triggerAutoSave();
    }
  };

  window.QueryBuilderSteps.addFilterRow = function () {
    const state = getState();

    if (!state.table || !state.availableFields) return;

    const row = document.createElement("div");
    row.className = "filter-row";

    const colSel = document.createElement("select");
    colSel.innerHTML = '<option value="">-- columna --</option>';

    // Usar los campos disponibles del estado
    state.availableFields.forEach((field) => {
      const opt = document.createElement("option");
      opt.value = field.fieldname;
      opt.textContent = `${field.label} (${field.fieldtype})`;
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
    removeBtn.textContent = "";
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

    // Triggear auto-guardado cuando se actualizan los filtros
    if (window.QueryBuilderViews && window.QueryBuilderViews.triggerAutoSave) {
      window.QueryBuilderViews.triggerAutoSave();
    }
  };
})(window);
