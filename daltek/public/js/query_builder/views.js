(function (window) {
  "use strict";

  window.QueryBuilderViews = window.QueryBuilderViews || {};

  const queriesListView = document.getElementById("queriesListView");
  const queryBuilderView = document.getElementById("queryBuilderView");
  const newQueryBtn = document.getElementById("newQueryBtn");
  const backToListBtn = document.getElementById("backToListBtn");
  const queriesList = document.getElementById("queriesList");
  const saveQueryBtn = document.getElementById("saveQueryBtn");

  let currentView = "list";
  let currentQuery = null;
  let savedQueries = [];
  let autoSaveTimer = null;
  const AUTO_SAVE_DELAY = 2000; // 2 segundos de debounce

  function getCurrentDocName() {
    if (window.cur_frm && window.cur_frm.doc) {
      return window.cur_frm.doc.name;
    }
    return null;
  }

  window.QueryBuilderViews.showListView = function () {
    currentView = "list";
    queriesListView.style.display = "block";
    queryBuilderView.style.display = "none";

    renderQueriesList();
  };

  window.QueryBuilderViews.showBuilderView = function (query = null) {
    currentView = "builder";
    currentQuery = query;
    queriesListView.style.display = "none";
    queryBuilderView.style.display = "block";

    if (query) {
      loadQueryForEditing(query);
    } else {
      resetBuilder();
    }
  };

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

    card.addEventListener("click", () => {
      window.QueryBuilderViews.showBuilderView(query);
    });

    return card;
  }

  function loadQueryForEditing(query) {
    if (window.QueryBuilderState) {
      const state = window.QueryBuilderState.state;

      state.doctypeName = query.doctype;
      state.table = query.doctype;
      state.tableName = query.doctype;
      state.selectedCols = query.columns || [];
      state.filters = query.filters || [];

      frappe.call({
        method: "daltek.daltek.doctype.daltek.daltek.get_doctype_fields",
        args: {
          doctype_name: query.doctype,
        },
        callback: function (response) {
          if (response.message && response.message.success) {
            state.tableName = response.message.table_name;
            state.table = response.message.table_name;
            state.availableFields = response.message.all_fields;

            const searchInput = document.getElementById("search");
            if (searchInput) {
              const isCustom = response.message.is_custom || false;
              const displayValue = isCustom
                ? `${query.doctype} (Custom)`
                : query.doctype;
              const datasetValue = isCustom
                ? "tab" + query.doctype.replace(/\s/g, "")
                : query.doctype;

              searchInput.value = displayValue;
              searchInput.dataset.value = datasetValue;
              searchInput.dataset.doctype = query.doctype;
            }

            if (
              window.QueryBuilderSteps &&
              window.QueryBuilderSteps.handleTableChange
            ) {
              window.QueryBuilderSteps.handleTableChange();

              setTimeout(() => {
                state.selectedCols = query.columns || [];

                if (window.QueryBuilderUI.renderSelectedCols) {
                  window.QueryBuilderUI.renderSelectedCols();
                }

                state.filters = query.filters || [];
                if (query.filters && query.filters.length > 0) {
                  const dom = window.QueryBuilderUI?.dom;
                  if (dom && dom.filtersContainer) {
                    dom.filtersContainer.innerHTML = "";
                    query.filters.forEach((filter) => {
                      window.QueryBuilderSteps.addFilterRow();
                      const lastRow = dom.filtersContainer.lastElementChild;
                      if (lastRow) {
                        const selects = lastRow.querySelectorAll("select");
                        const input = lastRow.querySelector("input");
                        if (selects[0]) selects[0].value = filter.col;
                        if (selects[1]) selects[1].value = filter.op;
                        if (input) input.value = filter.val;
                      }
                    });
                    window.QueryBuilderSteps.updateFiltersState();
                  }
                }
              }, 100);
            }
          } else {
            frappe.msgprint(
              `Error cargando campos del DocType: ${query.doctype}`,
            );
          }
        },
        error: function (error) {
          frappe.msgprint(
            `Error de conexión al cargar DocType: ${error.message}`,
          );
        },
      });
    }
  }

  function resetBuilder() {
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

  function deleteQuery(query) {
    frappe.confirm(
      `¿Estás seguro de que deseas eliminar la consulta "${query.name}"?`,
      () => {
        const docName = getCurrentDocName();
        if (!docName) {
          frappe.msgprint("No se puede eliminar: documento no guardado");
          return;
        }

        frappe.call({
          method: "daltek.daltek.doctype.daltek.daltek.delete_query",
          args: {
            doc_name: docName,
            query_id: query.id,
          },
          callback: function (response) {
            if (response.message && response.message.success) {
              frappe.show_alert({
                message: "Consulta eliminada correctamente",
                indicator: "green",
              });

              savedQueries = savedQueries.filter((q) => q.id !== query.id);
              renderQueriesList();
            } else {
              frappe.msgprint(
                response.message?.error || "Error eliminando la consulta",
              );
            }
          },
          error: function (error) {
            frappe.msgprint("Error de conexión al eliminar consulta");
          },
        });
      },
    );
  }

  window.QueryBuilderViews.saveCurrentQuery = function () {
    const state = window.QueryBuilderState?.state;

    if (!state || (!state.table && !state.doctypeName)) {
      frappe.msgprint("Por favor selecciona un DocType");
      return;
    }

    if (!state.selectedCols || state.selectedCols.length === 0) {
      frappe.msgprint("Por favor selecciona al menos una columna");
      return;
    }

    const modalNameInput = document.getElementById("modalQueryName");
    const modalDescInput = document.getElementById("modalQueryDescription");

    if (currentQuery) {
      modalNameInput.value = currentQuery.name || "";
      modalDescInput.value = currentQuery.description || "";
    } else {
      modalNameInput.value = "";
      modalDescInput.value = "";
    }

    showSaveModal();
  };

  function showSaveModal() {
    const modal = document.getElementById("saveQueryModal");
    if (modal) {
      modal.classList.add("show");

      setTimeout(() => {
        const nameInput = document.getElementById("modalQueryName");
        if (nameInput) {
          nameInput.focus();
        }
      }, 100);
    }
  }

  function hideSaveModal() {
    const modal = document.getElementById("saveQueryModal");
    if (modal) {
      modal.classList.remove("show");
    }
  }

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
    const docName = getCurrentDocName();

    if (!docName) {
      frappe.msgprint("Debes guardar el documento Daltek primero"); // Esto debe ser cambiado que si no se a creado el dashboard ejecutar una validacion
      return; // En caso de estar ok los campos guardar y usar docName nuevo (if false) frappe.throw
    }

    const queryData = {
      id: currentQuery?.id || null,
      name: queryName,
      doctype: state.doctypeName || "",
      columns: state.selectedCols || [],
      filters: state.filters || [],
      description: queryDescription || `Consulta sobre ${state.doctypeName}`,
      created_by: frappe.session.user,
      created_at: currentQuery?.created_at || new Date().toISOString(),
    };

    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.save_query",
      args: {
        doc_name: docName,
        query_data: JSON.stringify(queryData),
      },
      callback: function (response) {
        if (response.message && response.message.success) {
          frappe.show_alert({
            message: currentQuery
              ? "Consulta actualizada"
              : "Consulta guardada",
            indicator: "green",
          });

          savedQueries = response.message.queries || [];
          currentQuery = response.message.saved_query;

          renderQueriesList();
          hideSaveModal();

          // Volver automáticamente a la vista de lista de consultas
          window.QueryBuilderViews.showListView();
        } else {
          frappe.msgprint(
            response.message?.error || "Error guardando la consulta",
          );
        }
      },
      error: function (error) {
        frappe.msgprint("Error de conexión al guardar consulta");
        frappe.show_alert({
          message: "Error de red al guardar",
          indicator: "red",
        });
      },
    });
  }

  window.QueryBuilderViews.loadSavedQueries = function () {
    const docName = getCurrentDocName();

    if (!docName || docName.startsWith("new-")) {
      savedQueries = [];
      renderQueriesList();
      return;
    }

    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.get_all_queries",
      args: {
        doc_name: docName,
      },
      callback: function (response) {
        if (response.message && response.message.success) {
          savedQueries = response.message.queries || [];
          renderQueriesList();
        } else {
          console.error("Error cargando consultas:", response.message);
          savedQueries = [];
          renderQueriesList();
        }
      },
      error: function (error) {
        console.error("Error de conexión al cargar consultas:", error);
        savedQueries = [];
        renderQueriesList();
      },
    });
  };

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

  if (saveQueryModal) {
    saveQueryModal.addEventListener("click", (e) => {
      if (e.target === saveQueryModal) {
        hideSaveModal();
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const saveQueryModal = document.getElementById("saveQueryModal");
      if (saveQueryModal && saveQueryModal.classList.contains("show")) {
        hideSaveModal();
      }
    }
  });

  if (modalQueryName) {
    modalQueryName.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        confirmSave();
      }
    });
  }

  // --- AUTO-GUARDADO ---  Analizar esta sección cuidadosamente

  function triggerAutoSave() {
    // Limpiar timer anterior si existe
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer);
    }

    // Programar nuevo auto-guardado con debounce
    autoSaveTimer = setTimeout(() => {
      performAutoSave();
    }, AUTO_SAVE_DELAY);
  }

  function performAutoSave() {
    const state = window.QueryBuilderState?.state;
    const docName = getCurrentDocName();

    // Validaciones básicas
    if (!docName || docName.startsWith("new-")) {
      return; // No auto-guardar en documentos no guardados
    }

    if (!state || (!state.table && !state.doctypeName)) {
      return; // No hay tabla seleccionada
    }

    if (!state.selectedCols || state.selectedCols.length === 0) {
      return; // No hay columnas seleccionadas
    }

    // Preparar datos del query
    const queryData = {
      id: currentQuery?.id || null,
      name: currentQuery?.name || `Query ${new Date().toLocaleTimeString()}`,
      doctype: state.doctypeName || "",
      columns: state.selectedCols || [],
      filters: state.filters || [],
      description:
        currentQuery?.description || `Auto-guardado: ${state.doctypeName}`,
      created_by: frappe.session.user,
      created_at: currentQuery?.created_at || new Date().toISOString(),
    };

    // Llamar al método de auto-guardado sin commit
    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.save_query",
      args: {
        doc_name: docName,
        query_data: JSON.stringify(queryData),
      },
      async: true, // Asíncrono para no bloquear UI
      callback: function (response) {
        if (response.message && response.message.success) {
          // Actualizar currentQuery con el resultado
          currentQuery = response.message.saved_query;

          // Mostrar indicador sutil de guardado
          const saveIndicator = document.getElementById("autoSaveIndicator");
          if (saveIndicator) {
            saveIndicator.textContent = "✓ Guardado";
            saveIndicator.style.color = "green";

            setTimeout(() => {
              saveIndicator.textContent = "";
            }, 2000);
          }
        }
      },
      error: function (error) {
        console.error("Error en auto-guardado:", error);
      },
    });
  }

  // Exponer función para que otros módulos puedan triggerar auto-save
  window.QueryBuilderViews.triggerAutoSave = triggerAutoSave;
  window.QueryBuilderViews.getSavedQueries = () => savedQueries;
  window.QueryBuilderViews.getCurrentQuery = () => currentQuery;
  window.QueryBuilderViews.resetBuilder = resetBuilder;
})(window);
