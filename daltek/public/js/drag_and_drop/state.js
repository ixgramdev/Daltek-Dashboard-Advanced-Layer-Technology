// Estado global del sistema Drag and Drop
// Se ejecuta en el contexto del campo HTML de ERPNext

(function (window) {
  "use strict";

  // Namespace para evitar conflictos globales
  window.DragDropState = window.DragDropState || {};

  // Estado de la aplicación
  window.DragDropState.state = {
    frm: null, // Referencia al formulario de Frappe
    grid: null, // Instancia de GridStack
    widgets: [], // Widgets actualmente en el canvas
    availableWidgets: [], // Widgets disponibles para añadir
    isDark: false, // Modo oscuro activado
  };

  // Métodos para manipular el estado
  window.DragDropState.setFrm = function (frm) {
    this.state.frm = frm;
  };

  window.DragDropState.setGrid = function (grid) {
    this.state.grid = grid;
  };

  window.DragDropState.setAvailableWidgets = function (widgets) {
    this.state.availableWidgets = widgets;
  };

  window.DragDropState.getWidgets = function () {
    if (!this.state.frm || !this.state.frm.doc.layout) {
      return [];
    }
    let layout = this.state.frm.doc.layout;
    if (typeof layout === "string") {
      try {
        layout = JSON.parse(layout);
      } catch (e) {
        layout = [];
      }
    }
    return Array.isArray(layout) ? layout : [];
  };

  window.DragDropState.saveWidgets = function (widgets) {
    if (this.state.frm) {
      this.state.frm.set_value("layout", JSON.stringify(widgets));
    }
  };

  window.DragDropState.updateWidget = function (id, updates) {
    const widgets = this.getWidgets();
    const widget = widgets.find((w) => w.id === id);
    if (widget) {
      Object.assign(widget, updates);
      this.saveWidgets(widgets);
    }
  };

  window.DragDropState.addWidget = function (widget) {
    const widgets = this.getWidgets();
    widgets.push(widget);
    this.saveWidgets(widgets);
  };

  window.DragDropState.removeWidget = function (id) {
    const widgets = this.getWidgets();
    const filtered = widgets.filter((w) => w.id !== id);
    this.saveWidgets(filtered);
  };

  window.DragDropState.detectDarkMode = function () {
    const isDark =
      document.body.classList.contains("dark") ||
      document.documentElement.getAttribute("data-theme") === "dark";
    this.state.isDark = isDark;
    return isDark;
  };
})(window);
