/**
 * Data Mapper UI - Interfaz principal de configuración
 */

(function (window) {
  "use strict";

  window.DataMapperUI = window.DataMapperUI || {};

  const DataMapperUI = {
    currentFrm: null,
    currentQueryId: null,
    currentQueryData: null,
    currentConfig: {},
    previewData: null,

    /**
     * Inicializa el Data Mapper UI
     */
    init: function (frm, queryId) {
      this.currentFrm = frm;
      this.currentQueryId = queryId;
      this.currentConfig = {
        transformations: {
          group_by: [],
          aggregations: {},
          filters: [],
          sort: null,
          limit: null,
        },
        widget_mapping: {
          type: "echart",
          chart_type: "line",
          x_axis: null,
          y_axes: [],
        },
      };

      this.render();
      this.loadQueryMetadata();
    },

    /**
     * Renderiza la interfaz completa
     */
    render: function () {
      const container = $(
        '<div class="data-mapper-container" style="padding: 20px;"></div>'
      );

      // Header
      container.append(`
        <div class="data-mapper-header" style="margin-bottom: 20px;">
          <h3>🗂️ Configuración del Data Mapper</h3>
          <p style="color: #666;">Transforma y mapea datos de la query a tu widget</p>
        </div>
      `);

      // Sección 1: Datos crudos
      container.append(`
        <div class="section-raw-data" style="margin-bottom: 30px;">
          <h4>1️⃣ Vista Previa de Datos Crudos</h4>
          <div id="raw-data-preview" style="max-height: 300px; overflow: auto; border: 1px solid #ddd; padding: 10px;">
            <div class="text-center text-muted">Cargando datos...</div>
          </div>
          <div id="raw-data-stats" style="margin-top: 10px; font-size: 12px; color: #666;"></div>
        </div>
      `);

      // Sección 2: Configuración de transformación
      container.append(`
        <div class="section-transformation" style="margin-bottom: 30px;">
          <h4>2️⃣ Configuración de Transformación</h4>
          
          <div class="form-group" style="margin-bottom: 15px;">
            <label>Tipo de Widget</label>
            <select id="widget-type-select" class="form-control">
              <option value="echart">📊 Gráfico (EChart)</option>
              <option value="table">📋 Tabla</option>
              <option value="card">🎴 Tarjeta/KPI</option>
              <option value="heatmap">🔥 Heatmap</option>
            </select>
          </div>

          <div id="chart-type-container" class="form-group" style="margin-bottom: 15px;">
            <label>Tipo de Gráfico</label>
            <select id="chart-type-select" class="form-control">
              <option value="line">Líneas</option>
              <option value="bar">Barras</option>
              <option value="pie">Pie</option>
              <option value="area">Área</option>
              <option value="scatter">Dispersión</option>
            </select>
          </div>

          <div class="aggregation-section" style="margin-top: 20px;">
            <h5>⚙️ Agregación</h5>
            <div id="group-by-container"></div>
            <div id="aggregations-container"></div>
            <button class="btn btn-sm btn-default" id="add-aggregation-btn">+ Agregar Métrica</button>
          </div>

          <div class="filter-section" style="margin-top: 20px;">
            <h5>🔍 Filtros</h5>
            <div id="filters-container"></div>
            <button class="btn btn-sm btn-default" id="add-filter-btn">+ Agregar Filtro</button>
          </div>

          <div class="mapping-section" style="margin-top: 20px;">
            <h5>📊 Mapeo a Ejes</h5>
            <div id="axis-mapping-container"></div>
          </div>

          <div class="sort-limit-section" style="margin-top: 20px;">
            <h5>🔀 Ordenamiento y Límites</h5>
            <div id="sort-limit-container"></div>
          </div>
        </div>
      `);

      // Sección 3: Preview transformado
      container.append(`
        <div class="section-transformed" style="margin-bottom: 30px;">
          <h4>3️⃣ Vista Previa de Datos Transformados</h4>
          <button class="btn btn-primary btn-sm" id="refresh-preview-btn">🔄 Actualizar Preview</button>
          <div id="transformed-preview" style="margin-top: 15px; max-height: 400px; overflow: auto; border: 1px solid #ddd; padding: 10px;">
            <div class="text-center text-muted">Configure transformaciones y haga clic en "Actualizar Preview"</div>
          </div>
        </div>
      `);

      // Botones de acción
      container.append(`
        <div class="data-mapper-actions" style="text-align: right;">
          <button class="btn btn-default" id="cancel-mapper-btn">❌ Cancelar</button>
          <button class="btn btn-success" id="save-mapper-btn">✅ Guardar Widget</button>
        </div>
      `);

      // Mostrar en dialog
      const dialog = new frappe.ui.Dialog({
        title: "Data Mapper - Configuración de Widget",
        size: "extra-large",
        fields: [
          {
            fieldtype: "HTML",
            fieldname: "mapper_html",
            options: container.html(),
          },
        ],
      });

      dialog.show();
      dialog.$wrapper.find(".modal-dialog").css("max-width", "90%");

      // Asignar eventos después de mostrar
      this.attachEvents(dialog);
    },

    /**
     * Carga metadata de la query
     */
    loadQueryMetadata: function () {
      const self = this;

      frappe.call({
        method:
          "daltek.daltek.doctype.daltek.daltek.get_column_metadata",
        args: {
          doc_name: this.currentFrm.doc.name,
          query_id: this.currentQueryId,
        },
        callback: function (r) {
          if (r.message && r.message.success) {
            self.currentQueryData = r.message;
            self.renderRawDataPreview();
            self.renderGroupByOptions();
            self.renderAggregationOptions();
            self.renderFilterOptions();
            self.renderAxisMapping();
            self.renderSortLimit();
          } else {
            frappe.msgprint({
              title: "Error",
              message: r.message?.error || "Error cargando metadata de la query",
              indicator: "red",
            });
          }
        },
      });
    },

    /**
     * Renderiza preview de datos crudos
     */
    renderRawDataPreview: function () {
      // Implementar tabla simple con primeras filas
      const columns = this.currentQueryData.columns || [];
      const preview = $("#raw-data-preview");

      if (columns.length === 0) {
        preview.html('<div class="text-muted">No hay columnas disponibles</div>');
        return;
      }

      let html = '<table class="table table-bordered table-sm"><thead><tr>';
      columns.forEach((col) => {
        html += `<th>${col.name} <small>(${col.type})</small></th>`;
      });
      html += "</tr></thead><tbody>";

      // Mostrar valores de muestra
      const maxRows = Math.max(...columns.map((c) => c.sample_values?.length || 0));
      for (let i = 0; i < maxRows; i++) {
        html += "<tr>";
        columns.forEach((col) => {
          const val = col.sample_values?.[i] || "";
          html += `<td>${val}</td>`;
        });
        html += "</tr>";
      }

      html += "</tbody></table>";
      preview.html(html);

      // Stats
      $("#raw-data-stats").html(
        `<strong>${columns.length}</strong> columnas disponibles`
      );
    },

    /**
     * Renderiza opciones de agrupación
     */
    renderGroupByOptions: function () {
      const columns = this.currentQueryData.columns || [];
      const container = $("#group-by-container");

      let html = '<div class="form-group"><label>Agrupar por:</label><div>';

      columns.forEach((col) => {
        const checked = this.currentConfig.transformations.group_by.includes(col.name)
          ? "checked"
          : "";
        html += `
          <label style="margin-right: 15px; font-weight: normal;">
            <input type="checkbox" class="group-by-checkbox" data-column="${col.name}" ${checked}>
            ${col.name}
          </label>
        `;
      });

      html += "</div></div>";
      container.html(html);
    },

    /**
     * Renderiza opciones de agregación
     */
    renderAggregationOptions: function () {
      const container = $("#aggregations-container");
      const aggregations = this.currentConfig.transformations.aggregations;

      let html = '<div class="aggregations-list" style="margin-top: 10px;">';

      Object.keys(aggregations).forEach((alias) => {
        const agg = aggregations[alias];
        html += `
          <div class="aggregation-item" style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
            <input type="text" class="form-control" style="width: 200px; display: inline-block; margin-right: 10px;" value="${alias}" placeholder="Nombre">
            = 
            <select class="form-control" style="width: 150px; display: inline-block; margin: 0 10px;">
              <option value="sum" ${agg.func === "sum" ? "selected" : ""}>SUM</option>
              <option value="avg" ${agg.func === "avg" ? "selected" : ""}>AVG</option>
              <option value="count" ${agg.func === "count" ? "selected" : ""}>COUNT</option>
              <option value="min" ${agg.func === "min" ? "selected" : ""}>MIN</option>
              <option value="max" ${agg.func === "max" ? "selected" : ""}>MAX</option>
            </select>
            (
            <select class="form-control" style="width: 150px; display: inline-block; margin: 0 10px;">
              ${this.currentQueryData.columns
                .map(
                  (c) =>
                    `<option value="${c.name}" ${c.name === agg.column ? "selected" : ""}>${c.name}</option>`
                )
                .join("")}
            </select>
            )
            <button class="btn btn-sm btn-danger" onclick="DataMapperUI.removeAggregation('${alias}')">🗑️</button>
          </div>
        `;
      });

      html += "</div>";
      container.html(html);
    },

    /**
     * Renderiza opciones de filtros
     */
    renderFilterOptions: function () {
      const container = $("#filters-container");
      // Similar a aggregations
      container.html('<div class="text-muted">Filtros: (implementar)</div>');
    },

    /**
     * Renderiza mapeo de ejes
     */
    renderAxisMapping: function () {
      const columns = this.currentQueryData.columns || [];
      const container = $("#axis-mapping-container");

      let html = '<div class="form-group"><label>Eje X:</label><select id="x-axis-select" class="form-control">';
      html += '<option value="">-- Seleccionar --</option>';
      columns.forEach((col) => {
        html += `<option value="${col.name}">${col.name}</option>`;
      });
      html += "</select></div>";

      html += '<div class="form-group"><label>Series Y:</label><div>';
      columns.forEach((col) => {
        html += `
          <label style="margin-right: 15px; font-weight: normal;">
            <input type="checkbox" class="y-axis-checkbox" data-column="${col.name}">
            ${col.name}
          </label>
        `;
      });
      html += "</div></div>";

      container.html(html);
    },

    /**
     * Renderiza sort y limit
     */
    renderSortLimit: function () {
      const columns = this.currentQueryData.columns || [];
      const container = $("#sort-limit-container");

      let html = '<div class="row">';
      html += '<div class="col-md-6"><div class="form-group"><label>Ordenar por:</label>';
      html += '<select id="sort-column-select" class="form-control"><option value="">-- Sin ordenar --</option>';
      columns.forEach((col) => {
        html += `<option value="${col.name}">${col.name}</option>`;
      });
      html += '</select></div></div>';

      html += '<div class="col-md-3"><div class="form-group"><label>Orden:</label>';
      html += '<select id="sort-order-select" class="form-control">';
      html += '<option value="asc">Ascendente</option>';
      html += '<option value="desc">Descendente</option>';
      html += '</select></div></div>';

      html += '<div class="col-md-3"><div class="form-group"><label>Límite:</label>';
      html += '<input type="number" id="limit-input" class="form-control" placeholder="Sin límite">';
      html += '</div></div>';

      html += "</div>";
      container.html(html);
    },

    /**
     * Asigna eventos a los elementos
     */
    attachEvents: function (dialog) {
      const self = this;

      // Event: Actualizar preview
      dialog.$wrapper.find("#refresh-preview-btn").on("click", function () {
        self.refreshPreview();
      });

      // Event: Guardar widget
      dialog.$wrapper.find("#save-mapper-btn").on("click", function () {
        self.saveWidget();
        dialog.hide();
      });

      // Event: Cancelar
      dialog.$wrapper.find("#cancel-mapper-btn").on("click", function () {
        dialog.hide();
      });

      // Event: Cambio de tipo de widget
      dialog.$wrapper.find("#widget-type-select").on("change", function () {
        const widgetType = $(this).val();
        self.currentConfig.widget_mapping.type = widgetType;

        // Mostrar/ocultar opciones según tipo
        if (widgetType === "echart") {
          dialog.$wrapper.find("#chart-type-container").show();
        } else {
          dialog.$wrapper.find("#chart-type-container").hide();
        }
      });

      // Event: Cambio de tipo de gráfico
      dialog.$wrapper.find("#chart-type-select").on("change", function () {
        self.currentConfig.widget_mapping.chart_type = $(this).val();
      });

      // Event: Group by checkboxes
      dialog.$wrapper.find(".group-by-checkbox").on("change", function () {
        const column = $(this).data("column");
        const checked = $(this).is(":checked");

        if (checked) {
          if (!self.currentConfig.transformations.group_by.includes(column)) {
            self.currentConfig.transformations.group_by.push(column);
          }
        } else {
          self.currentConfig.transformations.group_by = self.currentConfig.transformations.group_by.filter(
            (c) => c !== column
          );
        }
      });

      // Event: Agregar agregación
      dialog.$wrapper.find("#add-aggregation-btn").on("click", function () {
        const alias = prompt("Nombre de la métrica:");
        if (alias) {
          self.currentConfig.transformations.aggregations[alias] = {
            column: self.currentQueryData.columns[0]?.name || "",
            func: "sum",
          };
          self.renderAggregationOptions();
        }
      });
    },

    /**
     * Refresca el preview de datos transformados
     */
    refreshPreview: function () {
      const self = this;

      // Actualizar config desde UI
      this.updateConfigFromUI();

      frappe.call({
        method:
          "daltek.daltek.doctype.daltek.daltek.get_mapper_preview_by_id",
        args: {
          doc_name: this.currentFrm.doc.name,
          query_id: this.currentQueryId,
          mapper_config: JSON.stringify(this.currentConfig),
        },
        callback: function (r) {
          if (r.message && r.message.success) {
            self.previewData = r.message;
            self.renderTransformedPreview();
          } else {
            frappe.msgprint({
              title: "Error",
              message: r.message?.error || "Error transformando datos",
              indicator: "red",
            });
          }
        },
      });
    },

    /**
     * Actualiza config desde elementos UI
     */
    updateConfigFromUI: function () {
      // X axis
      this.currentConfig.widget_mapping.x_axis = $("#x-axis-select").val();

      // Y axes
      const yAxes = [];
      $(".y-axis-checkbox:checked").each(function () {
        yAxes.push($(this).data("column"));
      });
      this.currentConfig.widget_mapping.y_axes = yAxes;

      // Sort
      const sortColumn = $("#sort-column-select").val();
      if (sortColumn) {
        this.currentConfig.transformations.sort = {
          column: sortColumn,
          order: $("#sort-order-select").val(),
        };
      } else {
        this.currentConfig.transformations.sort = null;
      }

      // Limit
      const limit = parseInt($("#limit-input").val());
      this.currentConfig.transformations.limit = limit || null;
    },

    /**
     * Renderiza preview de datos transformados
     */
    renderTransformedPreview: function () {
      const container = $("#transformed-preview");
      const data = this.previewData.data;

      if (!data) {
        container.html('<div class="text-muted">No hay datos transformados</div>');
        return;
      }

      // Si es formato tabla
      if (data.rows) {
        let html = '<table class="table table-bordered table-sm"><thead><tr>';
        data.columns.forEach((col) => {
          html += `<th>${col.label}</th>`;
        });
        html += "</tr></thead><tbody>";

        data.rows.slice(0, 10).forEach((row) => {
          html += "<tr>";
          data.columns.forEach((col) => {
            html += `<td>${row[col.field] || ""}</td>`;
          });
          html += "</tr>";
        });

        html += "</tbody></table>";
        html += `<div style="margin-top: 10px;"><strong>${data.count}</strong> registros totales (mostrando 10)</div>`;
        container.html(html);
      } else {
        container.html("<pre>" + JSON.stringify(data, null, 2) + "</pre>");
      }
    },

    /**
     * Guarda el widget con la configuración
     */
    saveWidget: function () {
      const widgetData = {
        type: this.currentConfig.widget_mapping.type,
        chart_type: this.currentConfig.widget_mapping.chart_type,
        title: prompt("Título del widget:") || "Widget sin título",
        data_source: {
          type: "query",
          query_id: this.currentQueryId,
        },
        mapper_config: this.currentConfig,
        position: {
          col: 0,
          row: 0,
          width: 6,
          height: 8,
        },
      };

      frappe.call({
        method: "daltek.daltek.doctype.daltek.daltek.add_widget",
        args: {
          doc_name: this.currentFrm.doc.name,
          widget: JSON.stringify(widgetData),
        },
        callback: function (r) {
          if (r.message && r.message.success) {
            frappe.msgprint({
              title: "Éxito",
              message: "Widget guardado correctamente",
              indicator: "green",
            });
            // Recargar formulario
            cur_frm.reload_doc();
          } else {
            frappe.msgprint({
              title: "Error",
              message: r.message?.error || "Error guardando widget",
              indicator: "red",
            });
          }
        },
      });
    },

    /**
     * Remueve una agregación
     */
    removeAggregation: function (alias) {
      delete this.currentConfig.transformations.aggregations[alias];
      this.renderAggregationOptions();
    },
  };

  // Exportar
  window.DataMapperUI = DataMapperUI;
})(window);
