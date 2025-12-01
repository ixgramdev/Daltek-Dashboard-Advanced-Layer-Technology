// Lógica de GridStack y manejo del grid
// Se ejecuta en el contexto del campo HTML de ERPNext

(function (window) {
  "use strict";

  window.DragDropGrid = window.DragDropGrid || {};

  const State = window.DragDropState;
  const UI = window.DragDropUI;

  // Inicializar GridStack
  window.DragDropGrid.initialize = function () {
    const grid = GridStack.init(
      {
        column: 12,
        cellHeight: 40,
        verticalMargin: 10,
        disableOneColumnMode: false,
        oneColumnModeDomSort: true,
        disableResize: false,
        float: false,
        staticGrid: false,
        maxRow: 0,
      },
      UI.dom.gridContainer,
    );

    State.setGrid(grid);

    // Listener para cambios en el grid
    grid.on("change", function (event, items) {
      window.DragDropGrid.handleGridChange(items);
    });

    return grid;
  };

  // Manejar cambios en el grid (movimiento/resize)
  window.DragDropGrid.handleGridChange = function (items) {
    let widgets = State.getWidgets();
    if (!Array.isArray(widgets)) widgets = [];

    // Actualizar solo los widgets afectados
    items.forEach((item) => {
      const idx = widgets.findIndex((w) => w.id === item.el.dataset.widgetId);
      if (idx !== -1) {
        widgets[idx].position = {
          col: item.x,
          row: item.y,
          width: item.w,
          height: item.h,
        };
      }
    });
    State.saveWidgets(widgets);
  };

  // Añadir un widget al grid (SOLO para widgets tradicionales, NO para ECharts)
  window.DragDropGrid.addWidget = function (widgetData, position) {
    const grid = State.state.grid;
    if (!grid) {
      console.error("Grid no inicializado");
      return;
    }

    // ⚠️ NO usar esta función para widgets tipo "echart"
    // Los ECharts se renderizan con DragDropWidgets.renderEChartWidget()
    if (widgetData.type === "echart") {
      console.warn(
        "⚠️ No usar addWidget() para ECharts, usar renderEChartWidget()",
      );
      return;
    }

    // Usar un id único pero consistente para el widget
    const id = widgetData.id + "_" + Date.now();
    const node = document.createElement("div");
    node.className = "grid-stack-item";
    node.dataset.widgetId = id;
    node.dataset.widgetType = widgetData.type;

    node.innerHTML = UI.createWidgetHTML({
      id: id,
      type: widgetData.type,
      properties: { ...widgetData.options },
    });

    node.setAttribute("gs-x", position.x);
    node.setAttribute("gs-y", position.y);
    node.setAttribute("gs-w", 2);
    node.setAttribute("gs-h", 4);

    grid.addWidget(node, { x: position.x, y: position.y, w: 2, h: 4 });

    State.addWidget({
      id: id,
      type: widgetData.type,
      position: { col: position.x, row: position.y, width: 2, height: 4 },
      properties: { ...widgetData.options },
    });

    // Añadir event listener al botón de configuración
    const configBtn = node.querySelector(".dd-widget-config-btn");
    if (configBtn) {
      configBtn.addEventListener("click", () => {
        window.DragDropGrid.handleWidgetConfig(id, node);
      });
    }
  };

  // Renderizar widget tradicional (NO EChart) en el grid
  window.DragDropGrid.renderWidget = function (widget) {
    const grid = State.state.grid;
    if (!grid) {
      console.error("Grid no inicializado");
      return;
    }

    // Crear nodo del widget
    const node = document.createElement("div");
    node.className = "grid-stack-item";
    node.dataset.widgetId = widget.id;
    node.dataset.widgetType = widget.type;

    node.innerHTML = UI.createWidgetHTML(widget);

    // Setear atributos para GridStack
    node.setAttribute("gs-x", widget.position.col || widget.position.x || 0);
    node.setAttribute("gs-y", widget.position.row || widget.position.y || 0);
    node.setAttribute("gs-w", widget.position.width || 2);
    node.setAttribute("gs-h", widget.position.height || 4);

    grid.addWidget(node, {
      x: widget.position.col || widget.position.x || 0,
      y: widget.position.row || widget.position.y || 0,
      w: widget.position.width || 2,
      h: widget.position.height || 4,
    });

    // Añadir event listener al botón de configuración
    const configBtn = node.querySelector(".dd-widget-config-btn");
    if (configBtn) {
      configBtn.addEventListener("click", () => {
        window.DragDropGrid.handleWidgetConfig(widget.id, node);
      });
    }
  };

  // Renderizar widgets existentes en el grid (DEPRECATED - usar main.js)
  window.DragDropGrid.renderExistingWidgets = function () {
    console.warn(
      "⚠️ renderExistingWidgets() está deprecated. Los widgets se cargan desde main.js",
    );
    const grid = State.state.grid;
    const widgets = State.getWidgets();

    if (!grid || !widgets || widgets.length === 0) {
      return;
    }

    widgets.forEach((widget) => {
      if (widget.type === "echart") {
        // Los ECharts se renderizan con su función específica
        window.DragDropWidgets.renderEChartWidget(widget);
      } else {
        // Widgets tradicionales
        window.DragDropGrid.renderWidget(widget);
      }
    });
  };

  // Manejar configuración de widget
  window.DragDropGrid.handleWidgetConfig = function (widgetId, nodeElement) {
    const widgets = State.getWidgets();
    const widget = widgets.find((w) => nodeElement.dataset.widgetId === w.id);

    if (!widget) return;

    UI.showEditDialog(widget, (newTitle) => {
      widget.properties.title = newTitle;
      UI.updateWidgetTitle(nodeElement, newTitle);
      State.saveWidgets(widgets);
    });
  };

  // Remover un widget del grid
  window.DragDropGrid.removeWidget = function (widgetId) {
    const grid = State.state.grid;
    if (!grid) return;

    const node = UI.dom.gridContainer.querySelector(
      `[data-widget-id="${widgetId}"]`,
    );
    if (node) {
      grid.removeWidget(node);
      State.removeWidget(widgetId);
    }
  };
})(window);
