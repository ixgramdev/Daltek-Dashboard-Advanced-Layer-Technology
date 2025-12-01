// Manejo de drag and drop de widgets desde el sidebar
// Se ejecuta en el contexto del campo HTML de ERPNext

(function (window) {
  "use strict";

  window.DragDropWidgets = window.DragDropWidgets || {};

  const State = window.DragDropState;
  const UI = window.DragDropUI;
  const Grid = window.DragDropGrid;

  // Inicializar eventos de drag and drop para los widgets
  window.DragDropWidgets.initializeDragEvents = function () {
    const widgets = State.state.availableWidgets;

    widgets.forEach((widget, index) => {
      const widgetElement = UI.dom.widgetList.children[index];
      if (!widgetElement) return;

      widgetElement.addEventListener("mousedown", (e) => {
        window.DragDropWidgets.handleDragStart(e, widget, widgetElement);
      });
    });
  };

  // Manejar inicio del drag
  window.DragDropWidgets.handleDragStart = function (
    event,
    widgetData,
    widgetElement,
  ) {
    event.preventDefault();

    const ghost = UI.createDragGhost(widgetElement, event);

    const onMouseMove = (moveEvent) => {
      UI.updateGhostPosition(ghost, moveEvent);
    };

    const onMouseUp = (upEvent) => {
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
      UI.removeGhost(ghost);

      if (UI.isOverCanvas(upEvent)) {
        window.DragDropWidgets.handleDrop(upEvent, widgetData);
      }
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  };

  // Manejar drop del widget en el canvas
  window.DragDropWidgets.handleDrop = function (event, widgetTemplate) {
    const grid = State.state.grid;
    if (!grid) {
      console.error("Grid no disponible");
      return;
    }

    const position = UI.calculateGridPosition(event, grid);

    // Crear widget base con propiedades generales
    const widget = {
      id: `${widgetTemplate.id}_${Date.now()}`, // ID único
      name: widgetTemplate.name,
      label: widgetTemplate.label,
      type: widgetTemplate.type,
      position: position,
      created_at: new Date().toISOString(),
    };

    // 🔍 DETECTAR SI ES ECHART → Llamar al backend
    if (widgetTemplate.type === "echart") {
      console.log(`🎨 Widget EChart detectado: ${widgetTemplate.chart_type}`);

      // Preparar datos para el backend
      const echartPayload = {
        doc_name: State.state.docName,
        chart_type: widgetTemplate.chart_type,
        chart_data: JSON.stringify(widgetTemplate.default_data),
        chart_config: JSON.stringify(widgetTemplate.default_config),
        widget_properties: JSON.stringify({
          title: widgetTemplate.name,
          position: position,
        }),
      };

      // Llamar al backend para crear el EChart
      window.DragDropWidgets.createEChartWidget(echartPayload, widget);
    } else {
      // Widget tradicional (card, table, etc.)
      widget.properties = widgetTemplate.default_properties;
      Grid.addWidget(widgetTemplate, position);
    }
  };

  // 📡 Crear EChart mediante backend
  window.DragDropWidgets.createEChartWidget = function (payload, widgetBase) {
    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.add_widget_echart",
      args: payload,
      freeze: true,
      freeze_message: __("Creando gráfico..."),
      callback: function (response) {
        if (response.message && response.message.success) {
          const createdWidget = response.message.widget;

          console.log("✅ EChart creado en backend:", createdWidget.id);

          // Fusionar datos del backend con widget base
          const finalWidget = {
            ...widgetBase,
            id: createdWidget.id,
            echart_data: createdWidget.echart_data,
            echart_config: createdWidget.echart_config,
            properties: createdWidget.properties,
          };

          // Renderizar en el grid
          window.DragDropWidgets.renderEChartWidget(finalWidget);

          // Actualizar estado
          State.addWidget(finalWidget);

          frappe.show_alert(
            {
              message: __("Gráfico creado exitosamente"),
              indicator: "green",
            },
            3,
          );
        } else {
          frappe.msgprint({
            title: __("Error"),
            message: response.message?.error || __("Error creando gráfico"),
            indicator: "red",
          });
        }
      },
      error: function (err) {
        console.error("❌ Error llamando al backend:", err);
        frappe.msgprint({
          title: __("Error de conexión"),
          message: __("No se pudo conectar con el servidor"),
          indicator: "red",
        });
      },
    });
  };

  // 🎨 Renderizar EChart en el canvas
  window.DragDropWidgets.renderEChartWidget = function (widget) {
    const grid = State.state.grid;
    if (!grid) {
      console.error("❌ Grid no inicializado");
      return;
    }

    console.log("🎨 Renderizando EChart:", widget);

    // Crear nodo del DOM
    const node = document.createElement("div");
    node.className = "grid-stack-item";
    node.dataset.widgetId = widget.id;
    node.dataset.widgetType = "echart";

    // HTML del contenedor del chart
    node.innerHTML = `
      <div class="grid-stack-item-content">
        <div class="dd-widget-card echart-widget">
          <div class="dd-widget-header">
            <h5 class="dd-widget-title">${
              widget.properties?.title || "Chart"
            }</h5>
            <button class="dd-widget-config-btn" data-widget-id="${widget.id}">
              <i class="fa fa-cog"></i>
            </button>
          </div>
          <div class="dd-widget-body">
            <div id="echart_${widget.id}" class="echart-container"
                 style="width: 100%; height: 100%;"></div>
          </div>
        </div>
      </div>
    `;

    // Configurar posición
    const position = widget.position || {};
    node.setAttribute("gs-x", position.x || position.col || 0);
    node.setAttribute("gs-y", position.y || position.row || 0);
    node.setAttribute("gs-w", position.width || 6);
    node.setAttribute("gs-h", position.height || 4);

    // Agregar al grid
    grid.addWidget(node, {
      x: position.x || position.col || 0,
      y: position.y || position.row || 0,
      w: position.width || 6,
      h: position.height || 4,
    });

    console.log("✅ Nodo agregado al grid, esperando DOM...");

    // Esperar a que el DOM se actualice
    setTimeout(() => {
      // Inicializar EChart
      const chartContainer = document.getElementById(`echart_${widget.id}`);

      console.log(
        "🔍 Buscando contenedor:",
        `echart_${widget.id}`,
        chartContainer,
      );

      if (chartContainer && typeof echarts !== "undefined") {
        console.log(
          "📊 Inicializando EChart con config:",
          widget.echart_config,
        );

        const chart = echarts.init(chartContainer);
        chart.setOption(widget.echart_config);

        // Guardar instancia para futuras actualizaciones
        State.state.echartInstances = State.state.echartInstances || {};
        State.state.echartInstances[widget.id] = chart;

        // Resize automático
        window.addEventListener("resize", () => chart.resize());

        console.log(`✅ EChart renderizado exitosamente: ${widget.id}`);
      } else {
        console.error("❌ No se pudo inicializar EChart:", widget.id);
        console.error("   - Contenedor encontrado:", !!chartContainer);
        console.error(
          "   - ECharts disponible:",
          typeof echarts !== "undefined",
        );
        if (typeof echarts === "undefined") {
          console.error("⚠️ ECharts.js no está cargado. Verifica hooks.py");
        }
      }
    }, 200);
  };

  // Renderizar la lista de widgets disponibles
  window.DragDropWidgets.renderAvailableWidgets = function () {
    const widgets = State.state.availableWidgets;
    UI.renderWidgetList(widgets);
    window.DragDropWidgets.initializeDragEvents();
  };
})(window);
