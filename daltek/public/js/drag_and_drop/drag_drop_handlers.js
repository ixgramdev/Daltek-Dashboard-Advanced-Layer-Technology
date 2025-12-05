// Manejo de drag and drop de widgets desde el sidebar
// Se ejecuta en el contexto del campo HTML de ERPNext

(function (window) {
  "use strict";

  window.DragDropWidgets = window.DragDropWidgets || {};

  const State = window.DragDropState;
  const UI = window.DragDropUI;
  const Grid = window.DragDropGrid;

  // Función auxiliar para recargar el formulario
  const reloadForm = function () {
    const frm = State.state.frm;
    if (frm) {
      setTimeout(() => {
        frm.reload_doc();
      }, 300);
    }
  };

  // Inicializar eventos de drag and drop para los widgets
  window.DragDropWidgets.initializeDragEvents = function () {
    const widgets = State.state.availableWidgets;

    widgets.forEach((widgetData, index) => {
      const widgetElement = UI.dom.widgetList.children[index];
      if (!widgetElement) return;

      widgetElement.addEventListener("mousedown", (e) => {
        window.DragDropWidgets.handleDragStart(e, widgetData, widgetElement);
      });
    });
  };

  // Ejecuta las funciones en dependencia del movimiento del mouse
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
  window.DragDropWidgets.handleDrop = function (event, widgetData) {
    const grid = State.state.grid;
    if (!grid) {
      console.error("Grid no disponible");
      return;
    }

    const position = UI.calculateGridPosition(event, grid);

    // Usar dimensiones recomendadas del widget o valores por defecto
    const defaultWidth =
      widgetData.default_width || widgetData.grid_config?.w || 6;
    const defaultHeight =
      widgetData.default_height || widgetData.grid_config?.h || 4;
    const minWidth = widgetData.min_width || widgetData.grid_config?.minW || 4;
    const minHeight =
      widgetData.min_height || widgetData.grid_config?.minH || 3;

    // Crear widget base con propiedades generales
    const widget = {
      label: widgetData.label,
      type: widgetData.type,
      position: {
        x: position.x,
        y: position.y,
        width: defaultWidth,
        height: defaultHeight,
        min_width: minWidth,
        min_height: minHeight,
      },
      created_at: new Date().toISOString(),
    };

    // Preparar datos del widget según su tipo
    console.log(widgetData);
    if (widgetData.type === "echart") {
      // EChart widget
      widget.chart_type = widgetData.chart_type;
      console.log("Chart type asignado:", widget.chart_type);
      widget.echart_data = widgetData.default_data;
      widget.echart_config = widgetData.default_config;
      widget.properties = {
        title: widgetData.name,
        position: {
          x: position.x,
          y: position.y,
        },
      };
    } else {
      // Widget tradicional (card, table, etc.)
      widget.properties = widgetData.default_properties;
    }

    // Llamar al endpoint único de WidgetService
    window.DragDropWidgets.createWidget(widget);
  };

  // Crear widget mediante backend - Endpoint único
  window.DragDropWidgets.createWidget = function (widget) {
    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.add_widget",
      args: {
        doc_name: State.state.docName,
        widget: JSON.stringify(widget),
      },
      freeze: true,
      freeze_message: __("Creando widget..."),
      callback: function (response) {
        if (response.message && response.message.success) {
          const createdWidget = response.message.widget;

          console.log(" Widget creado en backend:", createdWidget.id);

          // Renderizar inmediatamente en el cliente
          if (createdWidget.type === "echart") {
            window.DragDropWidgets.renderEChartWidget(createdWidget);
          } else {
            window.DragDropWidgets.renderGenericWidget(createdWidget);
          }

          // Actualizar estado
          State.addWidget(createdWidget);

          // Marcar widget como ya renderizado para evitar duplicados en recarga
          window.DragDropWidgets.renderedWidgetIds =
            window.DragDropWidgets.renderedWidgetIds || {};
          window.DragDropWidgets.renderedWidgetIds[createdWidget.id] = true;

          frappe.show_alert(
            {
              message: __("Widget creado exitosamente"),
              indicator: "green",
            },
            3,
          );

          // Recargar el formulario para sincronizar con la DB
          reloadForm();
        } else {
          frappe.msgprint({
            title: __("Error"),
            message: response.message?.error || __("Error creando widget"),
            indicator: "red",
          });
        }
      },
      error: function (err) {
        console.error(" Error llamando al backend:", err);
        frappe.msgprint({
          title: __("Error de conexión"),
          message: __("No se pudo conectar con el servidor"),
          indicator: "red",
        });
      },
    });
  };

  // Renderizar EChart en el canvas
  window.DragDropWidgets.renderEChartWidget = function (widget) {
    const grid = State.state.grid;
    if (!grid) {
      console.error(" Grid no inicializado");
      return;
    }

    console.log(" Renderizando EChart:", widget);

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
    node.setAttribute("gs-x", position.x || 0);
    node.setAttribute("gs-y", position.y || 0);
    node.setAttribute("gs-w", position.width || 8);
    node.setAttribute("gs-h", position.height || 6);

    // Agregar al grid usando makeWidget() (GridStack v11+)
    grid.makeWidget(node);

    // Actualizar posición
    grid.update(node, {
      x: position.x || 0,
      y: position.y || 0,
      w: position.width || 8,
      h: position.height || 6,
    });

    console.log(" Nodo agregado al grid, esperando DOM...");

    // Esperar a que el DOM se actualice
    setTimeout(() => {
      // Inicializar EChart
      const chartContainer = document.getElementById(`echart_${widget.id}`);

      console.log(
        " Buscando contenedor:",
        `echart_${widget.id}`,
        chartContainer,
      );

      if (chartContainer && typeof echarts !== "undefined") {
        console.log(
          " Inicializando EChart con config:",
          widget.echart_config,
        );

        const chart = echarts.init(chartContainer);
        chart.setOption(widget.echart_config);

        // Guardar instancia para futuras actualizaciones
        State.state.echartInstances = State.state.echartInstances || {};
        State.state.echartInstances[widget.id] = chart;

        // Resize automático
        window.addEventListener("resize", () => chart.resize());

        console.log(` EChart renderizado exitosamente: ${widget.id}`);
      } else {
        console.error(" No se pudo inicializar EChart:", widget.id);
        console.error(" - Contenedor encontrado:", !!chartContainer);
        console.error(
          " - ECharts disponible:",
          typeof echarts !== "undefined",
        );
        if (typeof echarts === "undefined") {
          console.error(" ECharts.js no está cargado. Verifica hooks.py");
        }
      }
    }, 200);
  };

  // Renderizar widget genérico (card, table, etc.) en el canvas
  window.DragDropWidgets.renderGenericWidget = function (widget) {
    const grid = State.state.grid;
    if (!grid) {
      console.error(" Grid no inicializado");
      return;
    }

    console.log(" Renderizando widget genérico:", widget);

    // Crear nodo del DOM
    const node = document.createElement("div");
    node.className = "grid-stack-item";
    node.dataset.widgetId = widget.id;
    node.dataset.widgetType = widget.type;

    // HTML del contenedor del widget
    node.innerHTML = `
      <div class="grid-stack-item-content">
        <div class="dd-widget-card generic-widget">
          <div class="dd-widget-header">
            <h5 class="dd-widget-title">${
              widget.properties?.title || widget.type || "Widget"
            }</h5>
            <button class="dd-widget-config-btn" data-widget-id="${widget.id}">
              <i class="fa fa-cog"></i>
            </button>
          </div>
          <div class="dd-widget-body">
            <div id="widget_${widget.id}" class="widget-container"
                 style="width: 100%; height: 100%;"></div>
          </div>
        </div>
      </div>
    `;

    // Configurar posición
    const position = widget.position || {};
    node.setAttribute("gs-x", position.x || 0);
    node.setAttribute("gs-y", position.y || 0);
    node.setAttribute("gs-w", position.width || 6);
    node.setAttribute("gs-h", position.height || 4);

    // Agregar al grid usando makeWidget() (GridStack v11+)
    grid.makeWidget(node);

    // Actualizar posición
    grid.update(node, {
      x: position.x || 0,
      y: position.y || 0,
      w: position.width || 6,
      h: position.height || 4,
    });

    console.log(" Widget genérico agregado al grid:", widget.id);
  };

  // Renderizar la lista de widgets disponibles
  window.DragDropWidgets.renderAvailableWidgets = function () {
    const widgets = State.state.availableWidgets;
    UI.renderWidgetList(widgets);
    window.DragDropWidgets.initializeDragEvents();
  };

  // Inicializar eventos de configuración para los botones de config
  window.DragDropWidgets.initializeConfigEvents = function () {
    // Usar event delegation para capturar clics en botones de config
    document.addEventListener("click", (e) => {
      const configBtn = e.target.closest(".dd-widget-config-btn");
      if (!configBtn) return;

      e.stopPropagation();
      e.preventDefault();

      const widgetId = configBtn.dataset.widgetId;
      if (!widgetId) {
        console.error("Widget ID no encontrado");
        return;
      }

      // Buscar el widget en el estado
      const widget = State.state.widgets.find((w) => w.id === widgetId);
      if (!widget) {
        console.error("Widget no encontrado en el estado:", widgetId);
        return;
      }

      // Abrir modal de configuración
      if (window.WidgetConfig && window.WidgetConfig.showConfigModal) {
        window.WidgetConfig.showConfigModal(widget);

        // Adjuntar listeners para preview en tiempo real
        setTimeout(() => {
          if (
            window.WidgetConfig &&
            window.WidgetConfig.attachPreviewListeners
          ) {
            const modalId = "widget-config-modal-" + widgetId;
            const modal = document.getElementById(modalId);
            if (modal) {
              window.WidgetConfig.attachPreviewListeners(modal);
            }
          }
        }, 100);
      } else {
        console.error("WidgetConfig no disponible");
      }
    });
  };
})(window);
