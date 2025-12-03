// widget_config.js - Interfaz gráfica para configurar widgets
// Gestiona la configuración de etiqueta, consulta, colores, guardar y eliminar

(function (window) {
  "use strict";

  window.WidgetConfig = window.WidgetConfig || {};

  const State = window.DragDropState;
  const UI = window.DragDropUI;

  // Propiedades privadas de la clase
  const config = {
    currentWidget: null,
    currentModalId: null,
    availableQueries: [],
  };

  /**
   * Mostrar modal de configuración de widget
   * @param {Object} widget - Objeto del widget a configurar
   */
  window.WidgetConfig.showConfigModal = function (widget) {
    config.currentWidget = widget;

    // Crear el modal
    const modalHTML = this.createModalHTML(widget);
    const modalId = "widget-config-modal-" + widget.id;
    config.currentModalId = modalId;

    // Agregar backdrop y modal al DOM
    const backdrop = document.createElement("div");
    backdrop.className = "widget-config-backdrop";
    backdrop.id = modalId + "-backdrop";

    const modalContainer = document.createElement("div");
    modalContainer.className = "widget-config-modal";
    modalContainer.id = modalId;
    modalContainer.innerHTML = modalHTML;

    document.body.appendChild(backdrop);
    document.body.appendChild(modalContainer);

    // Listeners para cerrar modal
    backdrop.addEventListener("click", () => {
      this.closeConfigModal(modalId);
    });

    const closeBtn = modalContainer.querySelector(".widget-config-close");
    closeBtn.addEventListener("click", () => {
      this.closeConfigModal(modalId);
    });

    // Listeners para los botones de acción
    const saveBtn = modalContainer.querySelector(".widget-config-save");
    const deleteBtn = modalContainer.querySelector(".widget-config-delete");
    const cancelBtn = modalContainer.querySelector(".widget-config-cancel");

    saveBtn.addEventListener("click", () => {
      this.saveWidgetConfig(widget, modalContainer);
    });

    deleteBtn.addEventListener("click", () => {
      this.deleteWidget(widget, modalId);
    });

    cancelBtn.addEventListener("click", () => {
      this.closeConfigModal(modalId);
    });

    // Cargar las queries disponibles
    this.loadAvailableQueries(widget, modalContainer);
  };

  /**
   * Crear HTML del modal de configuración
   * @param {Object} widget - Objeto del widget
   * @returns {string} HTML del modal
   */
  window.WidgetConfig.createModalHTML = function (widget) {
    const currentColor = widget.properties?.color || "#ffffff";
    const currentLabel = widget.properties?.title || widget.label || "Widget";
    const currentQuery = widget.query_id || "";

    return `
      <div class="widget-config-header">
        <h3 class="widget-config-title">Configurar Widget</h3>
        <button class="widget-config-close">×</button>
      </div>

      <div class="widget-config-body">
        <!-- Campo Etiqueta/Label -->
        <div class="widget-config-group">
          <label for="widget-config-label" class="widget-config-label">
            Etiqueta del Widget
          </label>
          <input
            type="text"
            id="widget-config-label"
            class="widget-config-input widget-config-label-input"
            placeholder="Ingrese la etiqueta"
            value="${currentLabel}"
            maxlength="100"
          />
          <small class="widget-config-hint">Máximo 100 caracteres</small>
        </div>

        <!-- Campo Consulta -->
        <div class="widget-config-group">
          <label for="widget-config-query" class="widget-config-label">
            Consulta/Dataset
          </label>
          <select
            id="widget-config-query"
            class="widget-config-select widget-config-query-select"
          >
            <option value="">-- Seleccione una consulta --</option>
          </select>
          <small class="widget-config-hint">Seleccione el dataset que alimentará el widget</small>
        </div>

        <!-- Campo Color -->
        <div class="widget-config-group">
          <label for="widget-config-color" class="widget-config-label">
            Color de Fondo
          </label>
          <div class="widget-config-color-picker">
            <input
              type="color"
              id="widget-config-color"
              class="widget-config-color-input"
              value="${currentColor}"
            />
            <span class="widget-config-color-value">${currentColor}</span>
          </div>
          <small class="widget-config-hint">Seleccione el color de fondo del widget</small>
        </div>

        <!-- Previsualización -->
        <div class="widget-config-group">
          <label class="widget-config-label">Vista Previa</label>
          <div
            class="widget-config-preview"
            id="widget-config-preview"
            style="background: ${currentColor};"
          >
            <div class="widget-config-preview-content">
              <p id="widget-preview-label">${currentLabel}</p>
              <small id="widget-preview-query">
                ${
                  currentQuery
                    ? "Query: " + currentQuery
                    : "Sin consulta asignada"
                }
              </small>
            </div>
          </div>
        </div>
      </div>

      <div class="widget-config-footer">
        <button class="widget-config-btn widget-config-delete" type="button">
          🗑️ Eliminar
        </button>
        <div class="widget-config-actions">
          <button class="widget-config-btn widget-config-cancel" type="button">
            Cancelar
          </button>
          <button class="widget-config-btn widget-config-save" type="button">
            💾 Guardar
          </button>
        </div>
      </div>
    `;
  };

  /**
   * Cargar lista de queries disponibles desde el backend
   * @param {Object} widget - Objeto del widget
   * @param {Element} modalContainer - Contenedor del modal
   */
  window.WidgetConfig.loadAvailableQueries = function (widget, modalContainer) {
    const querySelect = modalContainer.querySelector(
      ".widget-config-query-select",
    );

    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.get_available_queries",
      args: {
        doc_name: State.state.docName,
      },
      callback: (response) => {
        if (response.message && response.message.queries) {
          const queries = response.message.queries;
          config.availableQueries = queries;

          // Limpiar opciones previas
          querySelect.innerHTML =
            '<option value="">-- Seleccione una consulta --</option>';

          // Agregar opciones
          queries.forEach((query) => {
            const option = document.createElement("option");
            option.value = query.id || query.name;
            option.textContent = query.label || query.name;
            if (
              widget.query_id &&
              widget.query_id === (query.id || query.name)
            ) {
              option.selected = true;
            }
            querySelect.appendChild(option);
          });

          // Agregar listener para cambios en el select
          querySelect.addEventListener("change", () => {
            this.updatePreview(modalContainer);
          });
        }
      },
      error: (err) => {
        console.error("Error cargando queries:", err);
        frappe.msgprint({
          title: __("Error"),
          message: __("No se pudieron cargar las consultas disponibles"),
          indicator: "red",
        });
      },
    });
  };

  /**
   * Actualizar vista previa en tiempo real
   * @param {Element} modalContainer - Contenedor del modal
   */
  window.WidgetConfig.updatePreview = function (modalContainer) {
    const labelInput = modalContainer.querySelector(
      ".widget-config-label-input",
    );
    const colorInput = modalContainer.querySelector(
      ".widget-config-color-input",
    );
    const querySelect = modalContainer.querySelector(
      ".widget-config-query-select",
    );
    const preview = modalContainer.querySelector("#widget-config-preview");
    const previewLabel = modalContainer.querySelector("#widget-preview-label");
    const previewQuery = modalContainer.querySelector("#widget-preview-query");
    const colorValue = modalContainer.querySelector(
      ".widget-config-color-value",
    );

    // Actualizar color
    const newColor = colorInput.value;
    preview.style.background = newColor;
    colorValue.textContent = newColor;

    // Actualizar label
    const newLabel = labelInput.value || "Widget";
    previewLabel.textContent = newLabel;

    // Actualizar query
    const selectedQueryValue = querySelect.value;
    const selectedQuery = config.availableQueries.find(
      (q) => (q.id || q.name) === selectedQueryValue,
    );
    previewQuery.textContent = selectedQuery
      ? "Query: " + (selectedQuery.label || selectedQuery.name)
      : "Sin consulta asignada";
  };

  /**
   * Agregar listeners para actualizar preview en tiempo real
   * @param {Element} modalContainer - Contenedor del modal
   */
  window.WidgetConfig.attachPreviewListeners = function (modalContainer) {
    const labelInput = modalContainer.querySelector(
      ".widget-config-label-input",
    );
    const colorInput = modalContainer.querySelector(
      ".widget-config-color-input",
    );
    const querySelect = modalContainer.querySelector(
      ".widget-config-query-select",
    );

    labelInput.addEventListener("input", () => {
      this.updatePreview(modalContainer);
    });

    colorInput.addEventListener("change", () => {
      this.updatePreview(modalContainer);
    });

    // El querySelect ya tiene listener agregado en loadAvailableQueries
  };

  /**
   * Guardar configuración del widget
   * @param {Object} widget - Objeto del widget
   * @param {Element} modalContainer - Contenedor del modal
   */
  window.WidgetConfig.saveWidgetConfig = function (widget, modalContainer) {
    const labelInput = modalContainer.querySelector(
      ".widget-config-label-input",
    );
    const colorInput = modalContainer.querySelector(
      ".widget-config-color-input",
    );
    const querySelect = modalContainer.querySelector(
      ".widget-config-query-select",
    );

    const newLabel = labelInput.value.trim();
    const newColor = colorInput.value;
    const newQueryId = querySelect.value;

    // Validar
    if (!newLabel) {
      frappe.msgprint({
        title: __("Validación"),
        message: __("La etiqueta del widget es obligatoria"),
        indicator: "orange",
      });
      return;
    }

    // Mostrar loading
    const saveBtn = modalContainer.querySelector(".widget-config-save");
    const originalText = saveBtn.textContent;
    saveBtn.textContent = "Guardando...";
    saveBtn.disabled = true;

    // Llamar al backend para guardar
    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.update_widget",
      args: {
        doc_name: State.state.docName,
        widget_id: widget.id,
        label: newLabel,
        color: newColor,
        query_id: newQueryId || null,
      },
      callback: (response) => {
        if (response.message && response.message.success) {
          // Actualizar el widget en el DOM
          this.updateWidgetInDOM(widget.id, newLabel, newColor);

          // Actualizar el estado
          const widgetIndex = State.state.widgets.findIndex(
            (w) => w.id === widget.id,
          );
          if (widgetIndex !== -1) {
            State.state.widgets[widgetIndex].properties.title = newLabel;
            State.state.widgets[widgetIndex].properties.color = newColor;
            State.state.widgets[widgetIndex].query_id = newQueryId || null;
          }

          frappe.show_alert(
            {
              message: __("Widget actualizado exitosamente"),
              indicator: "green",
            },
            3,
          );

          // Cerrar modal
          this.closeConfigModal(config.currentModalId);
        } else {
          frappe.msgprint({
            title: __("Error"),
            message:
              response.message?.error ||
              __("Error al guardar la configuración"),
            indicator: "red",
          });
          saveBtn.textContent = originalText;
          saveBtn.disabled = false;
        }
      },
      error: (err) => {
        console.error("Error guardando widget:", err);
        frappe.msgprint({
          title: __("Error de conexión"),
          message: __("No se pudo guardar la configuración del widget"),
          indicator: "red",
        });
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
      },
    });
  };

  /**
   * Actualizar el widget en el DOM después de guardar
   * @param {string} widgetId - ID del widget
   * @param {string} newLabel - Nueva etiqueta
   * @param {string} newColor - Nuevo color
   */
  window.WidgetConfig.updateWidgetInDOM = function (
    widgetId,
    newLabel,
    newColor,
  ) {
    const gridItem = document.querySelector(`[data-gs-id="${widgetId}"]`);
    if (gridItem) {
      const card = gridItem.querySelector(".dd-widget-card");
      if (card) {
        card.style.background = newColor;
      }
      const title = gridItem.querySelector(".dd-widget-title");
      if (title) {
        title.textContent = newLabel;
      }
    }
  };

  /**
   * Eliminar widget
   * @param {Object} widget - Objeto del widget
   * @param {string} modalId - ID del modal
   */
  window.WidgetConfig.deleteWidget = function (widget, modalId) {
    // Confirmación
    frappe.confirm(
      __(
        "¿Está seguro de que desea eliminar este widget? Esta acción no se puede deshacer.",
      ),
      () => {
        // Usuario confirmó
        const grid = State.state.grid;

        // Remover del DOM
        const gridItem = document.querySelector(`[data-gs-id="${widget.id}"]`);
        if (gridItem) {
          grid.removeWidget(gridItem, true);
        }

        // Llamar al backend para eliminar
        frappe.call({
          method: "daltek.daltek.doctype.daltek.daltek.delete_widget",
          args: {
            doc_name: State.state.docName,
            widget_id: widget.id,
          },
          callback: (response) => {
            if (response.message && response.message.success) {
              // Actualizar el estado
              const widgetIndex = State.state.widgets.findIndex(
                (w) => w.id === widget.id,
              );
              if (widgetIndex !== -1) {
                State.state.widgets.splice(widgetIndex, 1);
              }

              frappe.show_alert(
                {
                  message: __("Widget eliminado exitosamente"),
                  indicator: "green",
                },
                3,
              );
            } else {
              frappe.msgprint({
                title: __("Error"),
                message:
                  response.message?.error || __("Error al eliminar el widget"),
                indicator: "red",
              });
            }
          },
          error: (err) => {
            console.error("Error eliminando widget:", err);
            frappe.msgprint({
              title: __("Error de conexión"),
              message: __("No se pudo eliminar el widget"),
              indicator: "red",
            });
          },
        });

        // Cerrar modal
        this.closeConfigModal(modalId);
      },
      () => {
        // Usuario canceló
        console.log("Eliminación cancelada");
      },
    );
  };

  /**
   * Cerrar modal de configuración
   * @param {string} modalId - ID del modal
   */
  window.WidgetConfig.closeConfigModal = function (modalId) {
    const modal = document.getElementById(modalId);
    const backdrop = document.getElementById(modalId + "-backdrop");

    if (modal) {
      modal.classList.add("closing");
      setTimeout(() => {
        modal.remove();
      }, 200);
    }

    if (backdrop) {
      backdrop.classList.add("closing");
      setTimeout(() => {
        backdrop.remove();
      }, 200);
    }

    config.currentWidget = null;
    config.currentModalId = null;
  };
})(window);
