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
    console.log("🚀 Inicializando sistema Drag and Drop...", {
      frm: frm,
      docName: frm.doc.name,
      availableWidgets: availableWidgets,
    });

    // Guardar referencia al formulario
    State.setFrm(frm);

    // Guardar nombre del documento
    State.state.docName = frm.doc.name;

    // Guardar widgets disponibles
    State.setAvailableWidgets(availableWidgets);

    // Detectar modo oscuro
    State.detectDarkMode();

    // Aplicar clase dark al wrapper si es necesario
    const wrapper = document.getElementById("dragDropApp");
    if (wrapper && State.state.isDark) {
      wrapper.classList.add("dark");
    }

    // Cargar layout existente desde el backend
    frappe.call({
      method: "daltek.daltek.doctype.daltek.daltek.get_layout",
      args: { doc_name: frm.doc.name },
      callback: function (response) {
        if (response.message && response.message.success) {
          const layout = response.message.layout || [];

          console.log(`📂 Layout cargado: ${layout.length} widgets`);

          // Inicializar GridStack
          const grid = Grid.initialize();

          if (!grid) {
            console.error("❌ No se pudo inicializar GridStack");
            return;
          }

          console.log("✅ GridStack inicializado");

          // Renderizar widgets existentes
          layout.forEach((widget) => {
            // Evitar renderizar widgets que ya se renderizaron inmediatamente
            const renderedIds = window.DragDropWidgets.renderedWidgetIds || {};
            if (renderedIds[widget.id]) {
              console.log(
                `⏭️  Widget ${widget.id} ya renderizado, saltando...`,
              );
              State.addWidget(widget);
              return;
            }

            if (widget.type === "echart") {
              // Renderizar EChart
              Widgets.renderEChartWidget(widget);
            } else {
              // Renderizar widget tradicional
              Grid.renderWidget(widget);
            }

            // Añadir al estado
            State.addWidget(widget);
          });

          // Renderizar sidebar
          Widgets.renderAvailableWidgets();

          // Inicializar eventos de configuración de widgets
          Widgets.initializeConfigEvents();

          console.log("✅ Sistema Drag and Drop inicializado correctamente");
        } else {
          console.error("❌ Error cargando layout:", response.message?.error);
        }
      },
      error: function (err) {
        console.error("❌ Error de conexión al cargar layout:", err);
      },
    });
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
