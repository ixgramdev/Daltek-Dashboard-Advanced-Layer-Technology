// Manejo del DOM y renderizado UI
// Se ejecuta en el contexto del campo HTML de ERPNext

(function (window) {
  "use strict";

  window.DragDropUI = window.DragDropUI || {};

  const getState = () => window.DragDropState.state;

  // Referencias al DOM
  const canvas = document.getElementById("ddCanvas");
  const gridContainer = document.getElementById("ddGridContainer");
  const sidebar = document.getElementById("ddSidebar");
  const widgetList = document.getElementById("ddWidgetList");

  window.DragDropUI.dom = {
    canvas,
    gridContainer,
    sidebar,
    widgetList,
  };

  // Crear HTML de un widget
  window.DragDropUI.createWidgetHTML = function (widget) {
    return `
      <div class="grid-stack-item-content">
        <div class="dd-widget-card" style="background: ${
          widget.properties.color
        };">
          <div class="dd-widget-header">
            <h5 class="dd-widget-title">${widget.properties.title}</h5>
            <button class="dd-widget-config-btn" data-widget-id="${
              widget.id
            }">⚙</button>
          </div>
          <span class="dd-widget-number">${widget.properties.number || 0}</span>
          <div class="dd-widget-resize-handle"></div>
        </div>
      </div>
    `;
  };

  // Crear HTML de preview de widget para sidebar
  window.DragDropUI.createWidgetPreview = function (widget) {
    const div = document.createElement("div");
    div.className = "dd-widget-item";
    div.innerHTML = widget.previewHtml;
    div.draggable = true;
    div.dataset.widgetType = widget.type;
    div.dataset.widgetId = widget.id;
    return div;
  };

  // Renderizar lista de widgets disponibles en el sidebar
  window.DragDropUI.renderWidgetList = function (widgets) {
    widgetList.innerHTML = "";
    widgets.forEach((widget) => {
      const preview = this.createWidgetPreview(widget);
      widgetList.appendChild(preview);
    });
  };

  // Mostrar diálogo para editar widget
  window.DragDropUI.showEditDialog = function (widget, callback) {
    const newTitle = prompt("Nuevo título:", widget.properties.title);
    if (newTitle !== null && newTitle.trim() !== "") {
      callback(newTitle);
    }
  };

  // Actualizar el título de un widget en el DOM
  window.DragDropUI.updateWidgetTitle = function (nodeElement, newTitle) {
    const titleElement = nodeElement.querySelector(".dd-widget-title");
    if (titleElement) {
      titleElement.textContent = newTitle;
    }
  };

  // Crear elemento ghost para drag
  window.DragDropUI.createDragGhost = function (element, event) {
    const ghost = element.cloneNode(true);
    ghost.style.position = "absolute";
    ghost.style.pointerEvents = "none";
    ghost.style.opacity = "0.8";
    ghost.style.zIndex = "9999";
    ghost.style.left = event.pageX + "px";
    ghost.style.top = event.pageY + "px";
    document.body.appendChild(ghost);
    return ghost;
  };

  // Actualizar posición del ghost durante el drag
  window.DragDropUI.updateGhostPosition = function (ghost, event) {
    ghost.style.left = event.pageX - ghost.offsetWidth / 2 + "px";
    ghost.style.top = event.pageY - ghost.offsetHeight / 2 + "px";
  };

  // Remover ghost del DOM
  window.DragDropUI.removeGhost = function (ghost) {
    if (ghost && ghost.parentNode) {
      document.body.removeChild(ghost);
    }
  };

  // Verificar si el cursor está sobre el canvas
  window.DragDropUI.isOverCanvas = function (event) {
    const canvasRect = canvas.getBoundingClientRect();
    return (
      event.clientX >= canvasRect.left &&
      event.clientX <= canvasRect.right &&
      event.clientY >= canvasRect.top &&
      event.clientY <= canvasRect.bottom
    );
  };

  // Calcular posición en el grid basada en coordenadas del mouse
  window.DragDropUI.calculateGridPosition = function (event, grid) {
    const canvasRect = canvas.getBoundingClientRect();
    const offsetX = event.clientX - canvasRect.left;
    const offsetY = event.clientY - canvasRect.top;
    const cellWidth = canvas.offsetWidth / grid.getColumn();
    const cellHeight = grid.getCellHeight();
    const col = Math.floor(offsetX / cellWidth);
    const row = Math.floor(offsetY / cellHeight);
    return { x: col, y: row };
  };
})(window);
