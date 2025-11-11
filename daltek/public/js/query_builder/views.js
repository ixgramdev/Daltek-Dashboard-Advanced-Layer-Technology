// Views - Manejo de vistas del Query Builder

(function (window) {
  "use strict";

  window.QueryBuilderViews = window.QueryBuilderViews || {};

  // Elementos DOM
  const queriesListView = document.getElementById("queriesListView");
  const queryBuilderView = document.getElementById("queryBuilderView");
  const newQueryBtn = document.getElementById("newQueryBtn");
  const backToListBtn = document.getElementById("backToListBtn");
  const queriesList = document.getElementById("queriesList");
  const saveQueryBtn = document.getElementById("saveQueryBtn");

  // Estado actual de la vista
  let currentView = "list"; // 'list' o 'builder'
  let currentQuery = null; // Query en edición
  let savedQueries = []; // Lista de consultas guardadas

  /**
   * Mostrar vista de listado
   */
  window.QueryBuilderViews.showListView = function () {
    currentView = "list";
    queriesListView.style.display = "block";
    queryBuilderView.style.display = "none";

    // Renderizar lista de consultas
    renderQueriesList();
  };

  /**
   * Mostrar vista de creación/edición
   */
  window.QueryBuilderViews.showBuilderView = function (query = null) {
    currentView = "builder";
    currentQuery = query;
    queriesListView.style.display = "none";
    queryBuilderView.style.display = "block";

    if (query) {
      // Cargar datos de la consulta para edición
      loadQueryForEditing(query);
    } else {
      // Nueva consulta - limpiar formulario
      resetBuilder();
    }
  };

  /**
   * Renderizar lista de consultas
   */
  function renderQueriesList() {
    if (savedQueries.length === 0) {
      queriesList.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📊</div>
          <div class="empty-state-title">No hay consultas guardadas</div>
          <div class="empty-state-description">
            Comienza creando tu primera consulta SQL para visualizar datos
          </div>
        </div>
      `;
      return;
    }

    queriesList.innerHTML = "";
    savedQueries.forEach((query) => {
      const card = createQueryCard(query);
      queriesList.appendChild(card);
    });
  }

  /**
   * Crear tarjeta de consulta
   */
  function createQueryCard(query) {
    const card = document.createElement("div");
    card.className = "query-card";
    card.dataset.queryId = query.id || query.name;

    const header = document.createElement("div");
    header.className = "query-card-header";

    const title = document.createElement("div");
    title.className = "query-card-title";
    title.textContent = query.name || "Consulta sin nombre";

    const actions = document.createElement("div");
    actions.className = "query-card-actions";

    const editBtn = document.createElement("button");
    editBtn.textContent = "Editar";
    editBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      window.QueryBuilderViews.showBuilderView(query);
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete";
    deleteBtn.textContent = "Eliminar";
    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteQuery(query);
    });

    actions.appendChild(editBtn);
    actions.appendChild(deleteBtn);

    header.appendChild(title);
    header.appendChild(actions);

    const description = document.createElement("div");
    description.className = "query-card-description";
    description.textContent = query.description || "Sin descripción disponible";

    const meta = document.createElement("div");
    meta.className = "query-card-meta";
    meta.innerHTML = `
      <span>📋 ${query.doctype || "N/A"}</span>
      <span>📊 ${query.columns ? query.columns.length : 0} columnas</span>
      <span>🔍 ${query.filters ? query.filters.length : 0} filtros</span>
    `;

    card.appendChild(header);
    card.appendChild(description);
    card.appendChild(meta);

    // Click en la tarjeta para ver/ejecutar
    card.addEventListener("click", () => {
      window.QueryBuilderViews.showBuilderView(query);
    });

    return card;
  }

  /**
   * Cargar consulta para edición
   */
  function loadQueryForEditing(query) {
    console.log("Cargando consulta para edición:", query);

    // TODO: Cargar DocType, campos y filtros
    // Esto se implementará cuando tengamos la persistencia de datos
    // El nombre y descripción se cargarán en el modal cuando se presione "Guardar"
  }

  /**
   * Limpiar el constructor
   */
  function resetBuilder() {
    // Resetear el estado del Query Builder
    if (window.QueryBuilderState) {
      window.QueryBuilderState.state = {
        table: "",
        doctypeName: "",
        tableName: "",
        selectedCols: [],
        filters: [],
        availableFields: [],
      };
    }

    // Limpiar UI
    const dom = window.QueryBuilderUI?.dom;
    if (dom) {
      const searchInput = document.getElementById("search");
      if (searchInput) {
        searchInput.value = "";
        searchInput.dataset.value = "";
        searchInput.dataset.doctype = "";
      }

      const fieldsSearch = document.getElementById("fieldsSearch");
      if (fieldsSearch) {
        fieldsSearch.value = "";
        fieldsSearch.dataset.fieldname = "";
      }

      if (dom.colsList) dom.colsList.innerHTML = "";
      if (dom.filtersContainer) dom.filtersContainer.innerHTML = "";
      if (dom.tableHint)
        dom.tableHint.textContent = "Selecciona un DocType para continuar.";

      if (dom.colsSection) dom.colsSection.style.display = "none";
      if (dom.filtersSection) dom.filtersSection.style.display = "none";
    }
  }

  /**
   * Eliminar consulta
   */
  function deleteQuery(query) {
    frappe.confirm(
      `¿Estás seguro de que deseas eliminar la consulta "${query.name}"?`,
      () => {
        // TODO: Implementar eliminación en backend
        savedQueries = savedQueries.filter((q) => q.id !== query.id);
        renderQueriesList();

        frappe.show_alert({
          message: "Consulta eliminada correctamente",
          indicator: "green",
        });
      },
    );
  }

  /**
   * Mostrar modal para guardar consulta
   */
  window.QueryBuilderViews.saveCurrentQuery = function () {
    const state = window.QueryBuilderState?.state;

    // Validar antes de abrir el modal
    if (!state || !state.table) {
      frappe.msgprint("Por favor selecciona un DocType");
      return;
    }

    if (!state.selectedCols || state.selectedCols.length === 0) {
      frappe.msgprint("Por favor selecciona al menos una columna");
      return;
    }

    // Si estamos editando, pre-llenar los campos del modal
    const modalNameInput = document.getElementById("modalQueryName");
    const modalDescInput = document.getElementById("modalQueryDescription");

    if (currentQuery) {
      modalNameInput.value = currentQuery.name || "";
      modalDescInput.value = currentQuery.description || "";
    } else {
      modalNameInput.value = "";
      modalDescInput.value = "";
    }

    // Mostrar el modal
    showSaveModal();
  };

  /**
   * Mostrar modal de guardado
   */
  function showSaveModal() {
    const modal = document.getElementById("saveQueryModal");
    if (modal) {
      modal.classList.add("show");
      // Enfocar el campo de nombre
      setTimeout(() => {
        const nameInput = document.getElementById("modalQueryName");
        if (nameInput) nameInput.focus();
      }, 100);
    }
  }

  /**
   * Ocultar modal de guardado
   */
  function hideSaveModal() {
    const modal = document.getElementById("saveQueryModal");
    if (modal) {
      modal.classList.remove("show");
    }
  }

  /**
   * Confirmar y guardar la consulta desde el modal
   */
  function confirmSave() {
    const modalNameInput = document.getElementById("modalQueryName");
    const modalDescInput = document.getElementById("modalQueryDescription");

    const queryName = modalNameInput?.value.trim();
    const queryDescription = modalDescInput?.value.trim();

    if (!queryName) {
      frappe.msgprint("Por favor ingresa un nombre para la consulta");
      modalNameInput?.focus();
      return;
    }

    const state = window.QueryBuilderState?.state;

    const query = {
      id: currentQuery?.id || Date.now().toString(),
      name: queryName,
      doctype: state.doctypeName,
      table: state.table,
      columns: state.selectedCols,
      filters: state.filters || [],
      description: queryDescription || `Consulta sobre ${state.doctypeName}`,
      created_at: currentQuery?.created_at || new Date().toISOString(),
      modified_at: new Date().toISOString(),
    };

    // TODO: Implementar guardado en backend
    // Por ahora guardamos en memoria
    if (currentQuery) {
      // Actualizar consulta existente
      const index = savedQueries.findIndex((q) => q.id === currentQuery.id);
      if (index !== -1) {
        savedQueries[index] = query;
      }
    } else {
      // Nueva consulta
      savedQueries.push(query);
    }

    frappe.show_alert({
      message: currentQuery
        ? "Consulta actualizada correctamente"
        : "Consulta guardada correctamente",
      indicator: "green",
    });

    // Cerrar modal y volver al listado
    hideSaveModal();
    window.QueryBuilderViews.showListView();
  }

  /**
   * Cargar consultas guardadas (simulado por ahora)
   */
  window.QueryBuilderViews.loadSavedQueries = function () {
    // TODO: Implementar carga desde backend
    // Por ahora usamos datos de ejemplo
    savedQueries = [
      {
        id: "1",
        name: "Ventas del mes",
        doctype: "Sales Invoice",
        columns: ["name", "customer", "grand_total"],
        filters: [],
        description: "Consulta de ventas del mes actual",
        created_at: new Date().toISOString(),
      },
      {
        id: "2",
        name: "Clientes activos",
        doctype: "Customer",
        columns: ["name", "customer_name", "territory"],
        filters: [{ col: "disabled", op: "=", val: "0" }],
        description: "Lista de clientes activos en el sistema",
        created_at: new Date().toISOString(),
      },
    ];

    renderQueriesList();
  };

  // Event Listeners
  if (newQueryBtn) {
    newQueryBtn.addEventListener("click", () => {
      window.QueryBuilderViews.showBuilderView();
    });
  }

  if (backToListBtn) {
    backToListBtn.addEventListener("click", () => {
      window.QueryBuilderViews.showListView();
    });
  }

  if (saveQueryBtn) {
    saveQueryBtn.addEventListener("click", () => {
      window.QueryBuilderViews.saveCurrentQuery();
    });
  }

  // Event Listeners del Modal
  const closeModalBtn = document.getElementById("closeModalBtn");
  const cancelModalBtn = document.getElementById("cancelModalBtn");
  const confirmSaveBtn = document.getElementById("confirmSaveBtn");
  const saveQueryModal = document.getElementById("saveQueryModal");
  const modalQueryName = document.getElementById("modalQueryName");

  if (closeModalBtn) {
    closeModalBtn.addEventListener("click", hideSaveModal);
  }

  if (cancelModalBtn) {
    cancelModalBtn.addEventListener("click", hideSaveModal);
  }

  if (confirmSaveBtn) {
    confirmSaveBtn.addEventListener("click", confirmSave);
  }

  // Cerrar modal al hacer clic fuera de él
  if (saveQueryModal) {
    saveQueryModal.addEventListener("click", (e) => {
      if (e.target === saveQueryModal) {
        hideSaveModal();
      }
    });
  }

  // Cerrar modal con tecla ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && saveQueryModal?.classList.contains("show")) {
      hideSaveModal();
    }
  });

  // Guardar con Enter en el campo de nombre
  if (modalQueryName) {
    modalQueryName.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        confirmSave();
      }
    });
  }

  // Exportar funciones públicas
  window.QueryBuilderViews.getSavedQueries = () => savedQueries;
  window.QueryBuilderViews.getCurrentQuery = () => currentQuery;
  window.QueryBuilderViews.resetBuilder = resetBuilder;
})(window);
