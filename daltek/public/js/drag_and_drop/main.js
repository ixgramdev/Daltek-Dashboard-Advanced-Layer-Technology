// Inicialización del sistema Drag and Drop
// Se ejecuta en el contexto del campo HTML de ERPNext

(function (window) {
  "use strict";

  // Esperar a que todos los módulos estén cargados
  if (
    !window.DragDropState ||
    !window.DragDropUI ||
    !window.DragDropGrid ||
    !window.DragDropWidgets
  ) {
    console.error("Drag and Drop: Módulos no cargados correctamente");
    return;
  }

  // Verificar que GridStack esté disponible
  if (typeof GridStack === "undefined") {
    console.error("Drag and Drop: GridStack no está cargado");
    return;
  }

  const State = window.DragDropState;
  const UI = window.DragDropUI;
  const Grid = window.DragDropGrid;
  const Widgets = window.DragDropWidgets;

  // Función de inicialización principal
  window.initDragDropSystem = function (frm, availableWidgets) {
    console.log("Inicializando sistema Drag and Drop...", {
      frm: frm,
      availableWidgets: availableWidgets,
    });

    // Guardar referencia al formulario
    State.setFrm(frm);

    // Guardar widgets disponibles
    State.setAvailableWidgets(availableWidgets);

    // Detectar modo oscuro
    State.detectDarkMode();

    // Aplicar clase dark al wrapper si es necesario
    const wrapper = document.getElementById("dragDropApp");
    if (wrapper && State.state.isDark) {
      wrapper.classList.add("dark");
    }

    // Inicializar GridStack
    const grid = Grid.initialize();

    if (!grid) {
      console.error("No se pudo inicializar GridStack");
      return;
    }

    console.log("GridStack inicializado:", grid);

    // Renderizar widgets disponibles en el sidebar
    Widgets.renderAvailableWidgets();

    // Renderizar widgets existentes en el canvas
    Grid.renderExistingWidgets();

    console.log("Sistema Drag and Drop inicializado correctamente");
  };

  // Exportar función de inicialización
  window.DragDropSystem = {
    init: window.initDragDropSystem,
    State: State,
    UI: UI,
    Grid: Grid,
    Widgets: Widgets,
  };
})(window);
