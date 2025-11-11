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
  window.DragDropWidgets.handleDrop = function (event, widgetData) {
    const grid = State.state.grid;
    if (!grid) {
      console.error("Grid no disponible");
      return;
    }

    const position = UI.calculateGridPosition(event, grid);
    Grid.addWidget(widgetData, position);
  };

  // Renderizar la lista de widgets disponibles
  window.DragDropWidgets.renderAvailableWidgets = function () {
    const widgets = State.state.availableWidgets;
    UI.renderWidgetList(widgets);
    window.DragDropWidgets.initializeDragEvents();
  };
})(window);
